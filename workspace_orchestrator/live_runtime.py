from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
import uuid
from dataclasses import asdict, dataclass
from importlib import import_module, invalidate_caches
from pathlib import Path

from .agent_profiles import (
    append_department_milestone as append_department_milestone_report,
    append_private_memory_note as append_private_memory_entry,
)
from .contracts import DelegationResult
from .delegation import describe_run, load_handoff_package
from .handoff import (
    build_handoff_for_subproject,
    build_task_request_from_intake,
    default_research_plan,
    materialize_handoff_package,
)
from .intake import find_latest_intake_file, parse_intake_file
from .openai_runtime import DEFAULT_OPENAI_MODEL, build_root_runtime_spec, build_subproject_runtime_spec, detect_agents_sdk, instantiate_agents_sdk_bundle
from .organization import build_root_organization, build_subproject_organization
from .runtime_state import begin_root_runtime_status, finalize_root_runtime_status
from .runs import write_json
from .visibility import can_read_path
from .workspace import build_snapshot


ROOT_SESSION_DB = "root_sessions.sqlite"
SUBPROJECT_SESSION_DB = "subproject_sessions.sqlite"
GOOGLE_OPENAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
OPENROUTER_OPENAI_BASE_URL = "https://openrouter.ai/api/v1"
DEBUG_LOG_PATH = Path("debug-03c635.log")
DEBUG_SESSION_ID = "03c635"


def _debug_log(run_id: str, hypothesis_id: str, location: str, message: str, data: dict[str, object]) -> None:
    payload = {
        "sessionId": DEBUG_SESSION_ID,
        "id": f"log_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}",
        "timestamp": int(time.time() * 1000),
        "location": location,
        "message": message,
        "data": data,
        "runId": run_id,
        "hypothesisId": hypothesis_id,
    }
    try:
        with DEBUG_LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


@dataclass(frozen=True)
class LiveRunSummary:
    scope: str
    team_id: str
    entry_agent_id: str
    model: str
    session_id: str
    session_db_path: str | None
    final_output: str
    prompt: str
    intake_file: str | None = None
    run_id: str | None = None
    project_name: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class LiveRuntimeError(RuntimeError):
    """Friendly runtime error raised for user-facing launch failures."""


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def ensure_openai_api_key(root: Path) -> str:
    openrouter_test_mode = os.environ.get("ASM_OPENROUTER_TEST_MODE", "").strip().lower()
    # region agent log
    _debug_log(
        run_id="pre-fix",
        hypothesis_id="H1-H2",
        location="workspace_orchestrator/live_runtime.py:ensure_openai_api_key:entry",
        message="Entering key bootstrap",
        data={
            "has_openai_api_key_env": bool(os.environ.get("OPENAI_API_KEY")),
            "has_google_api_key_env": bool(os.environ.get("GOOGLE_API_KEY")),
            "has_gemini_api_key_env": bool(os.environ.get("GEMINI_API_KEY")),
            "has_openrouter_api_key_env": bool(os.environ.get("OPENROUTER_API_KEY")),
            "has_openai_base_url_env": bool(os.environ.get("OPENAI_BASE_URL")),
            "openrouter_test_mode": openrouter_test_mode,
        },
    )
    # endregion
    # Fail-fast for OpenRouter test mode: if the dedicated key is not present,
    # do not fall back to OPENAI_API_KEY (it tends to break with invalid keys).
    # This keeps operator debugging straightforward.
    openrouter_test_enabled = openrouter_test_mode in {"1", "true", "yes", "on"}
    if openrouter_test_enabled and not (os.environ.get("OPENROUTER_API_KEY")):
        env_path = root / ".env"
        values = _parse_env_file(env_path)
        if not values.get("OPENROUTER_API_KEY"):
            raise RuntimeError(
                "OPENROUTER_API_KEY is missing but ASM_OPENROUTER_TEST_MODE=1 is enabled. "
                "Put OPENROUTER_API_KEY into environment or root .env to run `launch-openrouter-test`."
            )

    if os.environ.get("OPENAI_API_KEY"):
        # If a Google-style key is stored in OPENAI_API_KEY, route traffic to
        # the Google OpenAI-compatible endpoint automatically.
        if os.environ["OPENAI_API_KEY"].startswith("AIza"):
            os.environ.setdefault("OPENAI_BASE_URL", GOOGLE_OPENAI_BASE_URL)
        # In OpenRouter test mode, always prioritize OpenRouter key if present.
        if openrouter_test_mode in {"1", "true", "yes", "on"} and os.environ.get("OPENROUTER_API_KEY"):
            os.environ["OPENAI_API_KEY"] = os.environ["OPENROUTER_API_KEY"]
            os.environ["OPENAI_BASE_URL"] = OPENROUTER_OPENAI_BASE_URL
            # region agent log
            _debug_log(
                run_id="pre-fix",
                hypothesis_id="H1",
                location="workspace_orchestrator/live_runtime.py:ensure_openai_api_key:openrouter_override_env",
                message="OpenRouter test mode override (env)",
                data={"openrouter_base_url": os.environ["OPENAI_BASE_URL"]},
            )
            # endregion
            return os.environ["OPENAI_API_KEY"]
        # region agent log
        _debug_log(
            run_id="pre-fix",
            hypothesis_id="H1",
            location="workspace_orchestrator/live_runtime.py:ensure_openai_api_key:env_openai_branch",
            message="Using OPENAI_API_KEY from environment",
            data={
                "google_style_key_detected": os.environ["OPENAI_API_KEY"].startswith("AIza"),
                "openai_base_url_set": bool(os.environ.get("OPENAI_BASE_URL")),
                "openai_base_url": os.environ.get("OPENAI_BASE_URL", ""),
            },
        )
        # endregion
        return os.environ["OPENAI_API_KEY"]
    if os.environ.get("OPENROUTER_API_KEY"):
        os.environ["OPENAI_API_KEY"] = os.environ["OPENROUTER_API_KEY"]
        os.environ.setdefault("OPENAI_BASE_URL", OPENROUTER_OPENAI_BASE_URL)
        return os.environ["OPENAI_API_KEY"]
    if os.environ.get("GOOGLE_API_KEY"):
        os.environ["OPENAI_API_KEY"] = os.environ["GOOGLE_API_KEY"]
        os.environ.setdefault("OPENAI_BASE_URL", GOOGLE_OPENAI_BASE_URL)
        return os.environ["OPENAI_API_KEY"]
    if os.environ.get("GEMINI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = os.environ["GEMINI_API_KEY"]
        os.environ.setdefault("OPENAI_BASE_URL", GOOGLE_OPENAI_BASE_URL)
        return os.environ["OPENAI_API_KEY"]

    env_path = root / ".env"
    values = _parse_env_file(env_path)
    key = values.get("OPENAI_API_KEY")
    openrouter_test_enabled = openrouter_test_mode in {"1", "true", "yes", "on"}
    if openrouter_test_enabled and values.get("OPENROUTER_API_KEY"):
        key = values.get("OPENROUTER_API_KEY")
        os.environ["OPENAI_BASE_URL"] = OPENROUTER_OPENAI_BASE_URL
        os.environ["OPENAI_API_KEY"] = key
        # region agent log
        _debug_log(
            run_id="pre-fix",
            hypothesis_id="H1",
            location="workspace_orchestrator/live_runtime.py:ensure_openai_api_key:openrouter_override_envfile",
            message="OpenRouter test mode override (.env)",
            data={"openrouter_base_url": os.environ["OPENAI_BASE_URL"]},
        )
        # endregion
        return key
    if not key:
        openrouter_key = values.get("OPENROUTER_API_KEY")
        google_key = values.get("GOOGLE_API_KEY") or values.get("GEMINI_API_KEY")
        if openrouter_key:
            key = openrouter_key
            os.environ.setdefault("OPENAI_BASE_URL", OPENROUTER_OPENAI_BASE_URL)
        elif google_key:
            key = google_key
            os.environ.setdefault("OPENAI_BASE_URL", GOOGLE_OPENAI_BASE_URL)
    elif key.startswith("AIza"):
        # Some users store a Google key under OPENAI_API_KEY.
        os.environ.setdefault("OPENAI_BASE_URL", GOOGLE_OPENAI_BASE_URL)
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY (or GOOGLE_API_KEY / GEMINI_API_KEY / OPENROUTER_API_KEY) is missing. "
            "Put it in the environment or in the root .env file."
        )
    os.environ["OPENAI_API_KEY"] = key
    return key


def _env_value(root: Path, key: str, default: str | None = None) -> str | None:
    if key in os.environ:
        return os.environ[key]
    return _parse_env_file(root / ".env").get(key, default)


def _normalize_model_name(model: str | None) -> str | None:
    if not model:
        return model
    compact = model.strip().lower().replace("_", "-")
    aliases = {
        "gemini 2.5 flash": "gemini-2.5-flash",
        "gemini-2.5 flash": "gemini-2.5-flash",
        "gemini 2.5 pro": "gemini-2.5-pro",
        "gemini-2.5 pro": "gemini-2.5-pro",
    }
    return aliases.get(compact, compact)


def ensure_agents_sdk_available(auto_install: bool = False) -> None:
    availability = detect_agents_sdk()
    if availability.available:
        return
    if not auto_install:
        raise RuntimeError(
            "OpenAI Agents SDK is not installed. Enable auto-install or install openai-agents first."
        )

    subprocess.run(
        [sys.executable, "-m", "pip", "install", "openai-agents"],
        check=True,
        text=True,
    )
    invalidate_caches()
    availability = detect_agents_sdk()
    if not availability.available:
        raise RuntimeError("OpenAI Agents SDK installation finished but the package is still unavailable.")


def _sessions_dir(root: Path) -> Path:
    path = root / ".agent_workspace" / "sessions"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _fallback_sessions_dir() -> Path:
    path = Path(tempfile.gettempdir()) / "Agentic_Solve_Math" / "sessions"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _build_session(agents_module, root: Path, session_id: str, filename: str):
    session_cls = getattr(agents_module, "SQLiteSession", None)
    if session_cls is None:
        return None
    primary_path = _sessions_dir(root) / filename
    try:
        return session_cls(session_id, db_path=str(primary_path))
    except (sqlite3.Error, OSError):
        fallback_path = _fallback_sessions_dir() / filename
        return session_cls(session_id, db_path=str(fallback_path))


def _latest_intake_path(root: Path, intake_file: str | Path | None = None) -> Path | None:
    if intake_file:
        return Path(intake_file)
    intake_dir = root / "kaggle_intake"
    if not intake_dir.exists():
        return None
    try:
        return find_latest_intake_file(intake_dir)
    except FileNotFoundError:
        return None


def _workspace_overview_payload(root: Path) -> dict[str, object]:
    snapshot = build_snapshot(root)
    return snapshot.to_dict()


def build_root_launch_prompt(root: Path, prompt: str | None = None, intake_file: str | Path | None = None) -> str:
    snapshot = build_snapshot(root)
    intake_path = _latest_intake_path(root, intake_file)
    intake_summary = "No intake file found."
    if intake_path:
        brief = parse_intake_file(intake_path)
        intake_summary = json.dumps(brief.to_dict(), ensure_ascii=False, indent=2)

    base_prompt = prompt or (
        "Start the root multi-agent orchestration cycle. Inspect the workspace, parse the latest intake, "
        "identify the best target subproject, create a handoff, activate the matching subproject team, "
        "and summarize the produced artifacts and next actions."
    )
    return "\n\n".join(
        (
            base_prompt,
            "Workspace snapshot:",
            json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2),
            "Latest intake summary:",
            intake_summary,
        )
    )


def build_subproject_launch_prompt(root: Path, run_id: str, prompt: str | None = None) -> str:
    package = load_handoff_package(root, run_id)
    base_prompt = prompt or (
        "Start the subproject commander cycle. Use the handoff context, inspect local files, do targeted research, "
        "and make sure a structured subproject result is recorded before finishing."
    )
    return "\n\n".join(
        (
            base_prompt,
            "Handoff package:",
            json.dumps(package.to_dict(), ensure_ascii=False, indent=2),
        )
    )


def _read_text_with_guard(root: Path, agent_id: str, path_str: str) -> str:
    org = build_root_organization(root) if agent_id.startswith("root.") else build_subproject_organization(
        root, agent_id.split(".")[1]
    )
    manifest = org.get_agent(agent_id)
    path = (root / path_str).resolve() if not Path(path_str).is_absolute() else Path(path_str).resolve()
    if not can_read_path(manifest, path):
        raise PermissionError(f"{agent_id} may not read {path}")
    return path.read_text(encoding="utf-8")


def _decorate_tool(agents_module, func):
    decorator = getattr(agents_module, "function_tool")
    return decorator(func)


def _visible_project_files(root: Path, agent_id: str, project_root: Path, limit: int) -> list[str]:
    org = build_root_organization(root) if agent_id.startswith("root.") else build_subproject_organization(
        root, agent_id.split(".")[1]
    )
    manifest = org.get_agent(agent_id)
    files: list[str] = []
    for path in sorted(project_root.rglob("*")):
        if not path.is_file():
            continue
        if not can_read_path(manifest, path):
            continue
        files.append(str(path.relative_to(project_root)))
        if len(files) >= limit:
            break
    return files


def _build_root_reader_tools(root: Path, agents_module, agent_id: str) -> list[object]:
    def get_workspace_overview() -> str:
        """Return the current root workspace snapshot as JSON."""

        return json.dumps(_workspace_overview_payload(root), ensure_ascii=False, indent=2)

    def parse_latest_intake() -> str:
        """Parse the latest root intake markdown file and return the structured brief as JSON."""

        intake_path = _latest_intake_path(root)
        if intake_path is None:
            return json.dumps({"status": "missing_intake"}, ensure_ascii=False, indent=2)
        brief = parse_intake_file(intake_path)
        return json.dumps(brief.to_dict(), ensure_ascii=False, indent=2)

    def read_root_document(path: str) -> str:
        """Read a root-level document that is visible to the current root agent."""

        return _read_text_with_guard(root, agent_id, path)

    def runtime_summary(project_name: str = "", run_id: str = "") -> str:
        """Return the runtime summary for the root team or a specific subproject as JSON."""

        if project_name:
            payload = build_subproject_runtime_spec(root, project_name, run_id=run_id or None).to_dict()
        else:
            payload = build_root_runtime_spec(root, run_id=run_id or None).to_dict()
        return json.dumps(payload, ensure_ascii=False, indent=2)

    functions = (
        get_workspace_overview,
        parse_latest_intake,
        read_root_document,
        runtime_summary,
    )
    return [_decorate_tool(agents_module, func) for func in functions]


def _build_root_orchestrator_tools(root: Path, agents_module) -> list[object]:
    reader_tools = _build_root_reader_tools(root, agents_module, "root.orchestrator")

    def build_handoff(project_name: str, objective: str, research_questions: list[str] | None = None) -> str:
        """Create a root-owned handoff package for a target subproject and return its ids as JSON."""

        intake_path = _latest_intake_path(root)
        if intake_path is None:
            raise FileNotFoundError("Cannot build a handoff without an intake markdown file.")
        brief = parse_intake_file(intake_path)
        task_request = build_task_request_from_intake(
            brief,
            objective=objective,
            requested_by="root.orchestrator",
        )
        research_plan = default_research_plan(
            objective=objective,
            research_questions=tuple(research_questions or (objective,)),
        )
        package = build_handoff_for_subproject(
            root,
            project_name=project_name,
            task_request=task_request,
            research_plan=research_plan,
            requester_agent_id="root.orchestrator",
        )
        run_dir = materialize_handoff_package(root, package)
        return json.dumps(
            {
                "run_id": package.run_id,
                "handoff_id": package.handoff_id,
                "run_dir": str(run_dir),
                "target_agent_id": package.target_agent_id,
            },
            ensure_ascii=False,
            indent=2,
        )

    def show_run(run_id: str) -> str:
        """Inspect a prepared root-owned run directory and return its JSON description."""

        return json.dumps(describe_run(root, run_id), ensure_ascii=False, indent=2)

    def run_subproject_team(run_id: str, max_turns: int = 12) -> str:
        """Launch the generic root-managed subproject commander runtime for a prepared run."""

        result = run_subproject_commander(
            root,
            run_id,
            max_turns=max_turns,
            auto_install=False,
        )
        return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)

    functions = (
        build_handoff,
        show_run,
        run_subproject_team,
    )
    return reader_tools + [_decorate_tool(agents_module, func) for func in functions]


def _build_root_history_tools(root: Path, agents_module, agent_id: str) -> list[object]:
    reader_tools = _build_root_reader_tools(root, agents_module, agent_id)

    def show_run(run_id: str) -> str:
        """Inspect a prepared root-owned run directory and return its JSON description."""

        return json.dumps(describe_run(root, run_id), ensure_ascii=False, indent=2)

    def append_root_research_note(title: str, body: str) -> str:
        """Append a manual research note to the root research journal."""

        journal_path = root / "rules" / "logs" / "RESEARCH_JOURNAL.md"
        section = "\n\n".join(
            (
                "---",
                f"## Manual note | {title}",
                body,
            )
        )
        with journal_path.open("a", encoding="utf-8") as handle:
            handle.write("\n" + section + "\n")
        return json.dumps({"journal_path": str(journal_path), "title": title}, ensure_ascii=False, indent=2)

    functions = (
        show_run,
        append_root_research_note,
    )
    return reader_tools + [_decorate_tool(agents_module, func) for func in functions]


def _build_subproject_reader_tools(root: Path, run_id: str, agents_module, agent_id: str) -> list[object]:
    package = load_handoff_package(root, run_id)
    project_name = package.routing_decision.target_name
    project_root = root / project_name

    def get_handoff_context() -> str:
        """Return the current handoff package for this subproject run as JSON."""

        return json.dumps(package.to_dict(), ensure_ascii=False, indent=2)

    def list_project_files(limit: int = 200) -> str:
        """List visible files in the subproject root as JSON."""

        files = _visible_project_files(root, agent_id, project_root, limit)
        return json.dumps(files, ensure_ascii=False, indent=2)

    def read_project_file(relative_path: str) -> str:
        """Read a UTF-8 text file from the subproject root."""

        target = (project_root / relative_path).resolve()
        if project_root.resolve() not in target.parents and target != project_root.resolve():
            raise PermissionError(f"Path escapes subproject root: {relative_path}")
        return _read_text_with_guard(root, agent_id, str(target))

    functions = (
        get_handoff_context,
        list_project_files,
        read_project_file,
    )
    return [_decorate_tool(agents_module, func) for func in functions]


def _build_agent_profile_tools(root: Path, agents_module, agent_id: str, rank: str) -> list[object]:
    def append_private_memory_note(title: str, body: str, tags: list[str] | None = None) -> str:
        """Append a private durable memory note for the current agent."""

        path = append_private_memory_entry(
            root,
            agent_id,
            title=title,
            body=body,
            tags=tuple(tags or ()),
        )
        return json.dumps({"memory_path": str(path), "agent_id": agent_id}, ensure_ascii=False, indent=2)

    functions = [append_private_memory_note]

    if rank == "head":

        def record_department_milestone(title: str, summary: str, next_actions: list[str] | None = None) -> str:
            """Append a user-facing milestone entry for this department head."""

            path = append_department_milestone_report(
                root,
                agent_id,
                title=title,
                summary=summary,
                next_actions=tuple(next_actions or ()),
            )
            return json.dumps({"reports_path": str(path), "agent_id": agent_id}, ensure_ascii=False, indent=2)

        functions.append(record_department_milestone)

    return [_decorate_tool(agents_module, func) for func in functions]


def _build_subproject_commander_tools(root: Path, run_id: str, agents_module, agent_id: str) -> list[object]:
    reader_tools = _build_subproject_reader_tools(root, run_id, agents_module, agent_id)
    package = load_handoff_package(root, run_id)
    result_path = root / ".agent_workspace" / "runs" / run_id / "subproject_result.json"

    def record_subproject_result(
        status: str,
        summary: str,
        canonical_paths: list[str] | None = None,
    ) -> str:
        """Write the canonical subproject_result.json artifact for the current run."""

        payload = DelegationResult(
            handoff_id=package.handoff_id,
            produced_by=package.target_agent_id,
            status=status,
            summary=summary,
            canonical_paths=tuple(canonical_paths or ()),
        )
        write_json(result_path, payload.to_dict())
        return json.dumps({"result_path": str(result_path), "status": status}, ensure_ascii=False, indent=2)

    functions = (
        record_subproject_result,
    )
    return reader_tools + [_decorate_tool(agents_module, func) for func in functions]


def _build_subproject_history_tools(root: Path, run_id: str, agents_module, agent_id: str) -> list[object]:
    reader_tools = _build_subproject_reader_tools(root, run_id, agents_module, agent_id)
    package = load_handoff_package(root, run_id)
    project_name = package.routing_decision.target_name
    project_root = root / project_name

    def append_subproject_note(title: str, body: str) -> str:
        """Append a local historian note inside the subproject agent workspace."""

        notes_dir = project_root / ".agent_workspace"
        notes_dir.mkdir(parents=True, exist_ok=True)
        notes_path = notes_dir / "history_notes.md"
        section = "\n\n".join(
            (
                f"## {title}",
                body,
            )
        )
        with notes_path.open("a", encoding="utf-8") as handle:
            handle.write("\n" + section + "\n")
        return json.dumps({"notes_path": str(notes_path), "title": title}, ensure_ascii=False, indent=2)

    functions = (
        append_subproject_note,
    )
    return reader_tools + [_decorate_tool(agents_module, func) for func in functions]


def _build_root_extra_tools_by_agent_id(root: Path, agents_module) -> dict[str, list[object]]:
    org = build_root_organization(root)
    web_search_cls = getattr(agents_module, "WebSearchTool", None)
    mapping: dict[str, list[object]] = {
        manifest.agent_id: _build_agent_profile_tools(root, agents_module, manifest.agent_id, manifest.rank)
        for manifest in org.agents
    }
    mapping["root.orchestrator"] = [
        *mapping.get("root.orchestrator", ()),
        *_build_root_orchestrator_tools(root, agents_module),
    ]
    for manifest in org.agents:
        extras = list(mapping.get(manifest.agent_id, ()))
        if web_search_cls is not None and any(
            tool_name in {"web_search", "paper_search", "source_classification"} for tool_name in manifest.allowed_tools
        ):
            extras.append(web_search_cls())
        if manifest.agent_id == "root.06_editorial_and_history.history_scribe":
            extras.extend(_build_root_history_tools(root, agents_module, manifest.agent_id))
        if extras:
            mapping[manifest.agent_id] = extras
    return mapping


def _build_subproject_extra_tools_by_agent_id(root: Path, run_id: str, agents_module) -> dict[str, list[object]]:
    package = load_handoff_package(root, run_id)
    project_name = package.routing_decision.target_name
    org = build_subproject_organization(root, project_name)
    entry_agent_id = f"subproject.{project_name}.commander"
    web_search_cls = getattr(agents_module, "WebSearchTool", None)
    mapping: dict[str, list[object]] = {
        manifest.agent_id: _build_agent_profile_tools(root, agents_module, manifest.agent_id, manifest.rank)
        for manifest in org.agents
    }
    mapping[entry_agent_id] = [
        *mapping.get(entry_agent_id, ()),
        *_build_subproject_commander_tools(root, run_id, agents_module, entry_agent_id),
    ]
    for manifest in org.agents:
        extras = list(mapping.get(manifest.agent_id, ()))
        if web_search_cls is not None and any(
            tool_name in {"web_search", "paper_search", "baseline_scan"} for tool_name in manifest.allowed_tools
        ):
            extras.append(web_search_cls())
        if manifest.agent_id.endswith(".local_historian"):
            extras.extend(_build_subproject_history_tools(root, run_id, agents_module, manifest.agent_id))
        if extras:
            mapping[manifest.agent_id] = extras
    return mapping


def _final_output_text(result) -> str:
    final_output = getattr(result, "final_output", None)
    if final_output is None:
        return ""
    if isinstance(final_output, str):
        return final_output
    return str(final_output)


def _friendly_runtime_error(exc: Exception) -> LiveRuntimeError:
    message = str(exc)
    error_name = exc.__class__.__name__
    if error_name == "RateLimitError" or "insufficient_quota" in message:
        return LiveRuntimeError(
            "Configured LLM API quota is unavailable for the active key. "
            "The runtime path is wired correctly, but the account needs active quota or billing."
        )
    if error_name == "APIConnectionError":
        return LiveRuntimeError(
            "LLM API connection failed. Check network access, proxy settings, or firewall restrictions."
        )
    return LiveRuntimeError(f"Live runtime failed: {message}")


def _configure_agents_sdk_transport(agents_module) -> None:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("OPENAI_BASE_URL", "")
    is_google_route = api_key.startswith("AIza") or ("generativelanguage.googleapis.com" in base_url)
    is_openrouter_route = "openrouter.ai" in base_url or bool(os.environ.get("OPENROUTER_API_KEY"))
    if not is_google_route and not is_openrouter_route:
        return
    set_default_openai_api = getattr(agents_module, "set_default_openai_api", None)
    if is_google_route and callable(set_default_openai_api):
        set_default_openai_api("chat_completions")
    set_tracing_disabled = getattr(agents_module, "set_tracing_disabled", None)
    if callable(set_tracing_disabled):
        set_tracing_disabled(True)
        # region agent log
        _debug_log(
            run_id="post-fix",
            hypothesis_id="H3",
            location="workspace_orchestrator/live_runtime.py:_configure_agents_sdk_transport",
            message="Forced chat_completions (Google) and disabled tracing export for proxy route",
            data={
                "is_google_route": is_google_route,
                "is_openrouter_route": is_openrouter_route,
                "openai_base_url": base_url,
                "tracing_disabled": True,
            },
        )
        # endregion


def run_root_orchestrator(
    root: Path,
    prompt: str | None = None,
    intake_file: str | Path | None = None,
    model: str | None = None,
    session_id: str = "root-main",
    max_turns: int | None = None,
    auto_install: bool | None = None,
) -> LiveRunSummary:
    root = root.resolve()
    ensure_openai_api_key(root)
    resolved_model = _normalize_model_name(model or _env_value(root, "ASM_OPENAI_MODEL", None))
    if os.environ.get("ASM_OPENROUTER_TEST_MODE", "").strip().lower() in {"1", "true", "yes", "on"}:
        resolved_model = None
    # region agent log
    _debug_log(
        run_id="pre-fix",
        hypothesis_id="H2-H3",
        location="workspace_orchestrator/live_runtime.py:run_root_orchestrator:after_config",
        message="Resolved runtime config",
        data={
            "resolved_model": resolved_model or "",
            "openai_base_url": os.environ.get("OPENAI_BASE_URL", ""),
            "api_key_is_google_style": bool(os.environ.get("OPENAI_API_KEY", "").startswith("AIza")),
        },
    )
    # endregion
    resolved_max_turns = int(_env_value(root, "ASM_ROOT_MAX_TURNS", "12")) if max_turns is None else max_turns
    resolved_auto_install = (
        (_env_value(root, "ASM_AUTO_INSTALL", "1") != "0") if auto_install is None else auto_install
    )
    ensure_agents_sdk_available(auto_install=resolved_auto_install)
    agents_module = import_module("agents")
    _configure_agents_sdk_transport(agents_module)
    run_config = None
    if os.environ.get("ASM_OPENROUTER_TEST_MODE", "").strip().lower() in {"1", "true", "yes", "on"}:
        # OpenRouter model ids are frequently namespaced like "qwen/qwen3-...:free".
        # The SDK's MultiProvider must be instructed to treat unknown prefixes as literal model ids.
        try:
            from agents.models.multi_provider import MultiProvider
            from agents.run_config import RunConfig

            run_config = RunConfig(
                model_provider=MultiProvider(
                    openai_api_key=os.environ.get("OPENAI_API_KEY"),
                    openai_base_url=os.environ.get("OPENAI_BASE_URL"),
                    openai_prefix_mode="model_id",
                    unknown_prefix_mode="model_id",
                )
            )
            # region agent log
            _debug_log(
                run_id="pre-fix",
                hypothesis_id="H5",
                location="workspace_orchestrator/live_runtime.py:run_root_orchestrator:run_config",
                message="Configured MultiProvider unknown_prefix_mode=model_id for OpenRouter test",
                data={
                    "openai_base_url": os.environ.get("OPENAI_BASE_URL", ""),
                    "openai_prefix_mode": "model_id",
                    "unknown_prefix_mode": "model_id",
                },
            )
            # endregion
        except Exception as exc:  # pragma: no cover
            _debug_log(
                run_id="pre-fix",
                hypothesis_id="H5-H6",
                location="workspace_orchestrator/live_runtime.py:run_root_orchestrator:run_config_error",
                message="Failed to configure MultiProvider for OpenRouter test",
                data={"error_type": exc.__class__.__name__, "error_message": str(exc)[:200]},
            )
    bundle = instantiate_agents_sdk_bundle(
        build_root_runtime_spec(root),
        entry_agent_id="root.orchestrator",
        model=resolved_model,
        expansion_depth=2,
        extra_tools_by_agent_id=_build_root_extra_tools_by_agent_id(root, agents_module),
    )
    runner = getattr(agents_module, "Runner")
    session = _build_session(agents_module, root, session_id, ROOT_SESSION_DB)
    launch_prompt = build_root_launch_prompt(root, prompt=prompt, intake_file=intake_file)
    effective_model = resolved_model or bundle.team_spec.get_agent(bundle.entry_agent_id).preferred_model
    intake_path = _latest_intake_path(root, intake_file)
    begin_root_runtime_status(
        root,
        team_id=bundle.team_spec.team_id,
        entry_agent_id=bundle.entry_agent_id,
        model=effective_model,
        session_id=session_id,
        intake_file=str(intake_path) if intake_path else None,
        prompt=launch_prompt,
    )
    try:
        result = runner.run_sync(
            bundle.entry_agent,
            launch_prompt,
            session=session,
            max_turns=resolved_max_turns,
            run_config=run_config,
        )
    except Exception as exc:  # pragma: no cover - exercised through fake runtime tests
        # region agent log
        _debug_log(
            run_id="pre-fix",
            hypothesis_id="H3-H4",
            location="workspace_orchestrator/live_runtime.py:run_root_orchestrator:runner_exception",
            message="Runner threw exception",
            data={
                "error_type": exc.__class__.__name__,
                "error_message": str(exc)[:500],
                "openai_base_url": os.environ.get("OPENAI_BASE_URL", ""),
                "resolved_model": resolved_model or "",
            },
        )
        # endregion
        finalize_root_runtime_status(
            root,
            team_id=bundle.team_spec.team_id,
            entry_agent_id=bundle.entry_agent_id,
            model=effective_model,
            session_id=session_id,
            session_db_path=str(getattr(session, "db_path", "")) or None,
            intake_file=str(intake_path) if intake_path else None,
            prompt=launch_prompt,
            error=str(_friendly_runtime_error(exc)),
        )
        raise _friendly_runtime_error(exc) from exc
    finalize_root_runtime_status(
        root,
        team_id=bundle.team_spec.team_id,
        entry_agent_id=bundle.entry_agent_id,
        model=effective_model,
        session_id=session_id,
        session_db_path=str(getattr(session, "db_path", "")) or None,
        intake_file=str(intake_path) if intake_path else None,
        prompt=launch_prompt,
        final_output=_final_output_text(result),
    )
    return LiveRunSummary(
        scope="root",
        team_id=bundle.team_spec.team_id,
        entry_agent_id=bundle.entry_agent_id,
        model=effective_model,
        session_id=session_id,
        session_db_path=str(getattr(session, "db_path", "")) or None,
        final_output=_final_output_text(result),
        prompt=launch_prompt,
        intake_file=str(intake_path) if intake_path else None,
    )


def run_subproject_commander(
    root: Path,
    run_id: str,
    prompt: str | None = None,
    model: str | None = None,
    session_id: str | None = None,
    max_turns: int | None = None,
    auto_install: bool | None = None,
) -> LiveRunSummary:
    root = root.resolve()
    ensure_openai_api_key(root)
    resolved_model = _normalize_model_name(model or _env_value(root, "ASM_OPENAI_MODEL", None))
    if os.environ.get("ASM_OPENROUTER_TEST_MODE", "").strip().lower() in {"1", "true", "yes", "on"}:
        resolved_model = None
    resolved_max_turns = int(_env_value(root, "ASM_ROOT_MAX_TURNS", "12")) if max_turns is None else max_turns
    resolved_auto_install = (
        (_env_value(root, "ASM_AUTO_INSTALL", "1") != "0") if auto_install is None else auto_install
    )
    ensure_agents_sdk_available(auto_install=resolved_auto_install)
    package = load_handoff_package(root, run_id)
    project_name = package.routing_decision.target_name
    agents_module = import_module("agents")
    _configure_agents_sdk_transport(agents_module)
    run_config = None
    if os.environ.get("ASM_OPENROUTER_TEST_MODE", "").strip().lower() in {"1", "true", "yes", "on"}:
        try:
            from agents.models.multi_provider import MultiProvider
            from agents.run_config import RunConfig

            run_config = RunConfig(
                model_provider=MultiProvider(
                    openai_api_key=os.environ.get("OPENAI_API_KEY"),
                    openai_base_url=os.environ.get("OPENAI_BASE_URL"),
                    openai_prefix_mode="model_id",
                    unknown_prefix_mode="model_id",
                )
            )
        except Exception as exc:  # pragma: no cover
            _debug_log(
                run_id="pre-fix",
                hypothesis_id="H5-H6",
                location="workspace_orchestrator/live_runtime.py:run_subproject_commander:run_config_error",
                message="Failed to configure MultiProvider for OpenRouter test",
                data={"error_type": exc.__class__.__name__, "error_message": str(exc)[:200]},
            )
    entry_agent_id = f"subproject.{project_name}.commander"
    bundle = instantiate_agents_sdk_bundle(
        build_subproject_runtime_spec(root, project_name, run_id=run_id),
        entry_agent_id=entry_agent_id,
        model=resolved_model,
        expansion_depth=2,
        extra_tools_by_agent_id=_build_subproject_extra_tools_by_agent_id(root, run_id, agents_module),
    )
    session_name = session_id or f"{project_name}-{run_id}"
    runner = getattr(agents_module, "Runner")
    session = _build_session(agents_module, root, session_name, SUBPROJECT_SESSION_DB)
    launch_prompt = build_subproject_launch_prompt(root, run_id, prompt=prompt)
    try:
        result = runner.run_sync(
            bundle.entry_agent,
            launch_prompt,
            session=session,
            max_turns=resolved_max_turns,
            run_config=run_config,
        )
    except Exception as exc:  # pragma: no cover - exercised through fake runtime tests
        raise _friendly_runtime_error(exc) from exc

    result_path = root / ".agent_workspace" / "runs" / run_id / "subproject_result.json"
    if not result_path.exists():
        fallback = DelegationResult(
            handoff_id=package.handoff_id,
            produced_by=package.target_agent_id,
            status="completed",
            summary=_final_output_text(result) or "Subproject run finished without an explicit result tool call.",
        )
        write_json(result_path, fallback.to_dict())

    return LiveRunSummary(
        scope="subproject",
        team_id=bundle.team_spec.team_id,
        entry_agent_id=bundle.entry_agent_id,
        model=resolved_model or bundle.team_spec.get_agent(bundle.entry_agent_id).preferred_model,
        session_id=session_name,
        session_db_path=str(getattr(session, "db_path", "")) or None,
        final_output=_final_output_text(result),
        prompt=launch_prompt,
        intake_file=str(package.task_request.intake_file) if package.task_request.intake_file else None,
        run_id=run_id,
        project_name=project_name,
    )
