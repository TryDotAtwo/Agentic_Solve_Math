from __future__ import annotations

import asyncio
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
from .openai_runtime import build_root_runtime_spec, build_subproject_runtime_spec, detect_agents_sdk, instantiate_agents_sdk_bundle
from .organization import build_root_organization, build_subproject_organization
from .provider_config import (
    activate_provider_runtime,
    env_value,
    load_runtime_config,
)
from .runtime_events import append_runtime_event, load_runtime_events
from .runtime_state import begin_root_runtime_status, finalize_root_runtime_status, update_root_runtime_status
from .runs import utc_now_iso, write_json
from .visibility import can_read_path
from .workspace import build_snapshot


ROOT_SESSION_DB = "root_sessions.sqlite"
SUBPROJECT_SESSION_DB = "subproject_sessions.sqlite"
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
    provider_id: str
    provider_route: str
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


class _RuntimeEventRecorder:
    def __init__(
        self,
        root: Path,
        *,
        scope: str,
        session_id: str,
        team_id: str,
        project_name: str | None = None,
        run_id: str | None = None,
    ) -> None:
        self.root = root
        self.scope = scope
        self.session_id = session_id
        self.team_id = team_id
        self.project_name = project_name
        self.run_id = run_id

    def record(
        self,
        *,
        event_type: str,
        title: str,
        summary: str,
        agent_id: str | None = None,
        agent_name: str | None = None,
        department_key: str | None = None,
        target_agent_id: str | None = None,
        target_agent_name: str | None = None,
        tool_name: str | None = None,
        transcript: str | None = None,
        phase: str | None = None,
        details: dict[str, object] | None = None,
        update_status: bool = True,
    ) -> None:
        event = append_runtime_event(
            self.root,
            event_type=event_type,
            title=title,
            summary=summary,
            scope=self.scope,
            session_id=self.session_id,
            team_id=self.team_id,
            run_id=self.run_id,
            project_name=self.project_name,
            agent_id=agent_id,
            agent_name=agent_name,
            department_key=department_key,
            target_agent_id=target_agent_id,
            target_agent_name=target_agent_name,
            tool_name=tool_name,
            transcript=transcript,
            phase=phase,
            details=details,
        )
        if update_status:
            update_root_runtime_status(
                self.root,
                active_scope=self.scope,
                active_team_id=self.team_id,
                active_project_name=self.project_name,
                active_run_id=self.run_id,
                active_agent_id=target_agent_id or agent_id,
                active_agent_name=target_agent_name or agent_name,
                active_department_key=department_key,
                current_phase=phase,
                last_event_type=event.event_type,
                last_event_summary=event.summary,
                last_event_at=event.created_at,
                event_count=len(load_runtime_events(self.root, limit=5000)),
            )


def _agent_name(agent: object) -> str:
    return str(getattr(agent, "name", getattr(agent, "display_name", "")) or "")


def _agent_id(agent: object) -> str:
    return str(getattr(agent, "agent_id", getattr(agent, "id", _agent_name(agent))) or "")


def _agent_department_key(agent: object) -> str | None:
    return str(getattr(agent, "department_key")) if getattr(agent, "department_key", None) is not None else None


def _safe_tool_name(tool: object) -> str:
    return str(
        getattr(tool, "name", None)
        or getattr(tool, "__name__", None)
        or getattr(tool.__class__, "__name__", "tool")
    )


def _tool_target_agent_id(tool_name: str) -> str | None:
    if not tool_name.startswith("call_"):
        return None
    compact = tool_name[len("call_") :]
    if not compact:
        return None
    return compact.replace("_", ".")


def _compact_text(value: object, limit: int = 260) -> str:
    if value is None:
        return ""
    text = " ".join(str(value).split())
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3]}..."


def _extract_message_text(raw_item: object) -> str:
    content = getattr(raw_item, "content", None)
    if content is None and hasattr(raw_item, "model_dump"):
        payload = raw_item.model_dump(exclude_unset=True)
        content = payload.get("content")
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                if isinstance(item.get("text"), str):
                    parts.append(item["text"])
                elif isinstance(item.get("content"), str):
                    parts.append(item["content"])
                elif isinstance(item.get("summary"), str):
                    parts.append(item["summary"])
            elif isinstance(getattr(item, "text", None), str):
                parts.append(getattr(item, "text"))
        return _compact_text(" ".join(part for part in parts if part))
    return _compact_text(content)


def _extract_tool_output_text(item: object) -> str:
    if getattr(item, "output", None) is not None:
        return _compact_text(getattr(item, "output"))
    raw_item = getattr(item, "raw_item", None)
    if raw_item is not None and hasattr(raw_item, "model_dump"):
        payload = raw_item.model_dump(exclude_unset=True)
        return _compact_text(payload.get("output"))
    if isinstance(raw_item, dict):
        return _compact_text(raw_item.get("output"))
    return ""


def _record_stream_event(recorder: _RuntimeEventRecorder, event: object) -> None:
    event_type = getattr(event, "type", "")
    if event_type == "agent_updated_stream_event":
        agent = getattr(event, "new_agent", None)
        recorder.record(
            event_type="agent_started",
            title="Agent activated",
            summary=f"{_agent_name(agent) or _agent_id(agent)} is now active.",
            agent_id=_agent_id(agent),
            agent_name=_agent_name(agent),
            department_key=_agent_department_key(agent),
            phase="agent_active",
        )
        return

    if event_type != "run_item_stream_event":
        return

    name = str(getattr(event, "name", ""))
    item = getattr(event, "item", None)
    agent = getattr(item, "agent", None)
    agent_id = _agent_id(agent)
    agent_name = _agent_name(agent)
    department_key = _agent_department_key(agent)

    if name == "message_output_created":
        transcript = _extract_message_text(getattr(item, "raw_item", None))
        recorder.record(
            event_type="agent_message",
            title="Agent message",
            summary=transcript or f"{agent_name or agent_id} produced a message.",
            agent_id=agent_id,
            agent_name=agent_name,
            department_key=department_key,
            transcript=transcript or None,
            phase="agent_message",
        )
        return

    if name in {"handoff_requested", "handoff_occured"}:
        source_agent = getattr(item, "source_agent", None) or agent
        target_agent = getattr(item, "target_agent", None)
        recorder.record(
            event_type="handoff",
            title="Agent handoff",
            summary=(
                f"{_agent_name(source_agent) or _agent_id(source_agent)} -> "
                f"{_agent_name(target_agent) or _agent_id(target_agent)}"
            ),
            agent_id=_agent_id(source_agent),
            agent_name=_agent_name(source_agent),
            department_key=_agent_department_key(source_agent),
            target_agent_id=_agent_id(target_agent),
            target_agent_name=_agent_name(target_agent),
            phase="handoff",
        )
        return

    if name in {"tool_called", "tool_search_called"}:
        raw_item = getattr(item, "raw_item", None)
        tool_name = ""
        if isinstance(raw_item, dict):
            tool_name = str(raw_item.get("name") or raw_item.get("tool_name") or "")
        else:
            tool_name = str(getattr(raw_item, "name", "") or getattr(item, "title", "") or getattr(item, "description", ""))
        tool_name = tool_name or _safe_tool_name(item)
        target_id = _tool_target_agent_id(tool_name)
        recorder.record(
            event_type="tool_called",
            title="Tool called",
            summary=f"{agent_name or agent_id} called {tool_name}.",
            agent_id=agent_id,
            agent_name=agent_name,
            department_key=department_key,
            target_agent_id=target_id,
            tool_name=tool_name,
            phase="tool_running",
        )
        return

    if name in {"tool_output", "tool_search_output_created"}:
        transcript = _extract_tool_output_text(item)
        recorder.record(
            event_type="tool_output",
            title="Tool output",
            summary=transcript or f"{agent_name or agent_id} received tool output.",
            agent_id=agent_id,
            agent_name=agent_name,
            department_key=department_key,
            transcript=transcript or None,
            phase="tool_output",
        )


def _build_run_hooks(agents_module, recorder: _RuntimeEventRecorder):
    base_cls = getattr(agents_module, "RunHooksBase", None)
    if base_cls is None:
        return None

    class ObservabilityHooks(base_cls):
        async def on_agent_start(self, context, agent) -> None:  # noqa: ANN001
            recorder.record(
                event_type="agent_started",
                title="Agent started",
                summary=f"{_agent_name(agent) or _agent_id(agent)} started work.",
                agent_id=_agent_id(agent),
                agent_name=_agent_name(agent),
                department_key=_agent_department_key(agent),
                phase="agent_started",
            )

        async def on_handoff(self, context, from_agent, to_agent) -> None:  # noqa: ANN001
            recorder.record(
                event_type="handoff",
                title="Handoff",
                summary=f"{_agent_name(from_agent) or _agent_id(from_agent)} -> {_agent_name(to_agent) or _agent_id(to_agent)}",
                agent_id=_agent_id(from_agent),
                agent_name=_agent_name(from_agent),
                department_key=_agent_department_key(from_agent),
                target_agent_id=_agent_id(to_agent),
                target_agent_name=_agent_name(to_agent),
                phase="handoff",
            )

        async def on_tool_start(self, context, agent, tool) -> None:  # noqa: ANN001
            tool_name = _safe_tool_name(tool)
            recorder.record(
                event_type="tool_called",
                title="Tool start",
                summary=f"{_agent_name(agent) or _agent_id(agent)} called {tool_name}.",
                agent_id=_agent_id(agent),
                agent_name=_agent_name(agent),
                department_key=_agent_department_key(agent),
                target_agent_id=_tool_target_agent_id(tool_name),
                tool_name=tool_name,
                phase="tool_running",
            )

        async def on_tool_end(self, context, agent, tool, result) -> None:  # noqa: ANN001
            recorder.record(
                event_type="tool_output",
                title="Tool finished",
                summary=_compact_text(result) or f"{_safe_tool_name(tool)} finished.",
                agent_id=_agent_id(agent),
                agent_name=_agent_name(agent),
                department_key=_agent_department_key(agent),
                tool_name=_safe_tool_name(tool),
                transcript=_compact_text(result) or None,
                phase="tool_output",
            )

        async def on_llm_end(self, context, agent, response) -> None:  # noqa: ANN001
            transcript = _extract_message_text(response)
            if not transcript:
                return
            recorder.record(
                event_type="agent_message",
                title="LLM response",
                summary=transcript,
                agent_id=_agent_id(agent),
                agent_name=_agent_name(agent),
                department_key=_agent_department_key(agent),
                transcript=transcript,
                phase="agent_message",
            )

        async def on_agent_end(self, context, agent, output) -> None:  # noqa: ANN001
            recorder.record(
                event_type="agent_completed",
                title="Agent completed",
                summary=_compact_text(output) or f"{_agent_name(agent) or _agent_id(agent)} completed.",
                agent_id=_agent_id(agent),
                agent_name=_agent_name(agent),
                department_key=_agent_department_key(agent),
                transcript=_compact_text(output) or None,
                phase="agent_completed",
            )

    return ObservabilityHooks()


async def _run_streamed_workflow(
    runner: object,
    *,
    entry_agent: object,
    launch_prompt: str,
    session: object,
    max_turns: int,
    run_config: object,
    hooks: object | None,
    recorder: _RuntimeEventRecorder,
):
    result = runner.run_streamed(
        entry_agent,
        launch_prompt,
        session=session,
        max_turns=max_turns,
        run_config=run_config,
        hooks=hooks,
    )
    async for event in result.stream_events():
        _record_stream_event(recorder, event)
    return result


def _run_workflow_with_observability(
    runner: object,
    *,
    entry_agent: object,
    launch_prompt: str,
    session: object,
    max_turns: int,
    run_config: object,
    hooks: object | None,
    recorder: _RuntimeEventRecorder,
):
    if hasattr(runner, "run_streamed"):
        return asyncio.run(
            _run_streamed_workflow(
                runner,
                entry_agent=entry_agent,
                launch_prompt=launch_prompt,
                session=session,
                max_turns=max_turns,
                run_config=run_config,
                hooks=hooks,
                recorder=recorder,
            )
        )
    return runner.run_sync(
        entry_agent,
        launch_prompt,
        session=session,
        max_turns=max_turns,
        run_config=run_config,
        hooks=hooks,
    )


def _launch_config(root: Path):
    return load_runtime_config(root).launch


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


def _build_root_orchestrator_tools(
    root: Path,
    agents_module,
    recorder: _RuntimeEventRecorder | None = None,
) -> list[object]:
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
        if recorder is not None:
            recorder.record(
                event_type="handoff_package_created",
                title="Handoff prepared",
                summary=f"Prepared {package.run_id} for {project_name}.",
                agent_id="root.orchestrator",
                agent_name="Root Orchestrator",
                target_agent_id=package.target_agent_id,
                target_agent_name=package.target_agent_id,
                phase="handoff_prepared",
                details={
                    "run_id": package.run_id,
                    "handoff_id": package.handoff_id,
                },
            )
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

        package = load_handoff_package(root, run_id)
        if recorder is not None:
            recorder.record(
                event_type="subproject_launch_requested",
                title="Subproject team launch",
                summary=f"Launching {package.routing_decision.target_name} for {run_id}.",
                agent_id="root.orchestrator",
                agent_name="Root Orchestrator",
                target_agent_id=package.target_agent_id,
                target_agent_name=package.target_agent_id,
                phase="subproject_launch",
                details={"run_id": run_id},
            )
        result = run_subproject_commander(
            root,
            run_id,
            max_turns=max_turns,
            auto_install=False,
            session_id=f"{package.routing_decision.target_name}-{run_id}",
        )
        return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)

    functions = (
        build_handoff,
        show_run,
        run_subproject_team,
    )
    return reader_tools + [_decorate_tool(agents_module, func) for func in functions]


def _build_root_history_tools(
    root: Path,
    agents_module,
    agent_id: str,
    recorder: _RuntimeEventRecorder | None = None,
) -> list[object]:
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
        if recorder is not None:
            recorder.record(
                event_type="research_note_recorded",
                title="Root research note",
                summary=title,
                agent_id=agent_id,
                agent_name="History Scribe",
                phase="documentation",
            )
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


def _build_agent_profile_tools(
    root: Path,
    agents_module,
    agent_id: str,
    rank: str,
    recorder: _RuntimeEventRecorder | None = None,
) -> list[object]:
    def append_private_memory_note(title: str, body: str, tags: list[str] | None = None) -> str:
        """Append a private durable memory note for the current agent."""

        path = append_private_memory_entry(
            root,
            agent_id,
            title=title,
            body=body,
            tags=tuple(tags or ()),
        )
        if recorder is not None:
            recorder.record(
                event_type="memory_note_recorded",
                title="Private memory updated",
                summary=title,
                agent_id=agent_id,
                agent_name=agent_id,
                phase="memory_write",
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
            if recorder is not None:
                recorder.record(
                    event_type="milestone_recorded",
                    title=title,
                    summary=summary,
                    agent_id=agent_id,
                    agent_name=agent_id,
                    phase="milestone",
                    transcript=summary,
                    details={"next_actions": list(next_actions or ())},
                )
            return json.dumps({"reports_path": str(path), "agent_id": agent_id}, ensure_ascii=False, indent=2)

        functions.append(record_department_milestone)

    return [_decorate_tool(agents_module, func) for func in functions]


def _build_subproject_commander_tools(
    root: Path,
    run_id: str,
    agents_module,
    agent_id: str,
    recorder: _RuntimeEventRecorder | None = None,
) -> list[object]:
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
        if recorder is not None:
            recorder.record(
                event_type="subproject_result_recorded",
                title="Subproject result recorded",
                summary=summary,
                agent_id=agent_id,
                agent_name=agent_id,
                phase="subproject_result",
                transcript=summary,
                details={"status": status, "canonical_paths": list(canonical_paths or ())},
            )
        return json.dumps({"result_path": str(result_path), "status": status}, ensure_ascii=False, indent=2)

    functions = (
        record_subproject_result,
    )
    return reader_tools + [_decorate_tool(agents_module, func) for func in functions]


def _build_subproject_history_tools(
    root: Path,
    run_id: str,
    agents_module,
    agent_id: str,
    recorder: _RuntimeEventRecorder | None = None,
) -> list[object]:
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
        if recorder is not None:
            recorder.record(
                event_type="subproject_note_recorded",
                title="Subproject historian note",
                summary=title,
                agent_id=agent_id,
                agent_name=agent_id,
                phase="documentation",
            )
        return json.dumps({"notes_path": str(notes_path), "title": title}, ensure_ascii=False, indent=2)

    functions = (
        append_subproject_note,
    )
    return reader_tools + [_decorate_tool(agents_module, func) for func in functions]


def _build_root_extra_tools_by_agent_id(
    root: Path,
    agents_module,
    recorder: _RuntimeEventRecorder | None = None,
) -> dict[str, list[object]]:
    org = build_root_organization(root)
    web_search_cls = getattr(agents_module, "WebSearchTool", None)
    mapping: dict[str, list[object]] = {
        manifest.agent_id: _build_agent_profile_tools(
            root,
            agents_module,
            manifest.agent_id,
            manifest.rank,
            recorder=recorder,
        )
        for manifest in org.agents
    }
    mapping["root.orchestrator"] = [
        *mapping.get("root.orchestrator", ()),
        *_build_root_orchestrator_tools(root, agents_module, recorder=recorder),
    ]
    for manifest in org.agents:
        extras = list(mapping.get(manifest.agent_id, ()))
        if web_search_cls is not None and any(
            tool_name in {"web_search", "paper_search", "source_classification"} for tool_name in manifest.allowed_tools
        ):
            extras.append(web_search_cls())
        if manifest.agent_id == "root.06_editorial_and_history.history_scribe":
            extras.extend(_build_root_history_tools(root, agents_module, manifest.agent_id, recorder=recorder))
        if extras:
            mapping[manifest.agent_id] = extras
    return mapping


def _build_subproject_extra_tools_by_agent_id(
    root: Path,
    run_id: str,
    agents_module,
    recorder: _RuntimeEventRecorder | None = None,
) -> dict[str, list[object]]:
    package = load_handoff_package(root, run_id)
    project_name = package.routing_decision.target_name
    org = build_subproject_organization(root, project_name)
    entry_agent_id = f"subproject.{project_name}.commander"
    web_search_cls = getattr(agents_module, "WebSearchTool", None)
    mapping: dict[str, list[object]] = {
        manifest.agent_id: _build_agent_profile_tools(
            root,
            agents_module,
            manifest.agent_id,
            manifest.rank,
            recorder=recorder,
        )
        for manifest in org.agents
    }
    mapping[entry_agent_id] = [
        *mapping.get(entry_agent_id, ()),
        *_build_subproject_commander_tools(root, run_id, agents_module, entry_agent_id, recorder=recorder),
    ]
    for manifest in org.agents:
        extras = list(mapping.get(manifest.agent_id, ()))
        if web_search_cls is not None and any(
            tool_name in {"web_search", "paper_search", "baseline_scan"} for tool_name in manifest.allowed_tools
        ):
            extras.append(web_search_cls())
        if manifest.agent_id.endswith(".local_historian"):
            extras.extend(
                _build_subproject_history_tools(
                    root,
                    run_id,
                    agents_module,
                    manifest.agent_id,
                    recorder=recorder,
                )
            )
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


def _configure_agents_sdk_transport(agents_module, provider_runtime) -> None:
    if provider_runtime.default_openai_api is None and not provider_runtime.disable_tracing:
        return
    set_default_openai_api = getattr(agents_module, "set_default_openai_api", None)
    if provider_runtime.default_openai_api and callable(set_default_openai_api):
        set_default_openai_api(provider_runtime.default_openai_api)
    set_tracing_disabled = getattr(agents_module, "set_tracing_disabled", None)
    if provider_runtime.disable_tracing and callable(set_tracing_disabled):
        set_tracing_disabled(True)
    _debug_log(
        run_id="provider",
        hypothesis_id="transport",
        location="workspace_orchestrator/live_runtime.py:_configure_agents_sdk_transport",
        message="Configured provider transport for Agents SDK runtime",
        data={
            "provider_id": provider_runtime.provider_id,
            "provider_route": provider_runtime.route_label,
            "default_openai_api": provider_runtime.default_openai_api or "",
            "disable_tracing": provider_runtime.disable_tracing,
            "openai_base_url": os.environ.get("OPENAI_BASE_URL", ""),
        },
    )


def _build_run_config_for_provider(agents_module, provider_runtime):
    if provider_runtime.provider_id != "openrouter" or not provider_runtime.use_multi_provider:
        return None
    try:
        from agents.models.multi_provider import MultiProvider
        from agents.run_config import RunConfig

        return RunConfig(
            model_provider=MultiProvider(
                openai_api_key=os.environ.get("OPENAI_API_KEY"),
                openai_base_url=os.environ.get("OPENAI_BASE_URL"),
                openai_prefix_mode=provider_runtime.openai_prefix_mode,
                unknown_prefix_mode=provider_runtime.unknown_prefix_mode,
            )
        )
    except Exception as exc:  # pragma: no cover
        _debug_log(
            run_id="provider",
            hypothesis_id="run_config",
            location="workspace_orchestrator/live_runtime.py:_build_run_config_for_provider",
            message="Failed to configure provider-specific RunConfig",
            data={
                "provider_id": provider_runtime.provider_id,
                "provider_route": provider_runtime.route_label,
                "error_type": exc.__class__.__name__,
                "error_message": str(exc)[:200],
            },
        )
        return None


def run_root_orchestrator(
    root: Path,
    prompt: str | None = None,
    intake_file: str | Path | None = None,
    model: str | None = None,
    session_id: str = "root-main",
    max_turns: int | None = None,
    auto_install: bool | None = None,
    provider: str | None = None,
) -> LiveRunSummary:
    root = root.resolve()
    try:
        launch_config = _launch_config(root)
        resolved_max_turns = (
            int(env_value(root, "ASM_ROOT_MAX_TURNS", str(launch_config.max_turns)))
            if max_turns is None
            else max_turns
        )
        resolved_auto_install = (
            (env_value(root, "ASM_AUTO_INSTALL", "1" if launch_config.auto_install else "0") != "0")
            if auto_install is None
            else auto_install
        )
        with activate_provider_runtime(root, provider_override=provider) as provider_session:
            provider_runtime = provider_session.runtime
            resolved_model = _normalize_model_name(
                model or env_value(root, "ASM_OPENAI_MODEL", provider_runtime.default_model)
            )
            if provider_runtime.model_strategy == "free_pool":
                resolved_model = None
            _debug_log(
                run_id="provider",
                hypothesis_id="root_launch",
                location="workspace_orchestrator/live_runtime.py:run_root_orchestrator",
                message="Resolved runtime config",
                data={
                    "provider_id": provider_runtime.provider_id,
                    "provider_route": provider_runtime.route_label,
                    "resolved_model": resolved_model or "",
                    "openai_base_url": os.environ.get("OPENAI_BASE_URL", ""),
                    "free_model_source": provider_runtime.free_model_source,
                    "free_pool_size": len(provider_runtime.free_model_ids),
                },
            )
            ensure_agents_sdk_available(auto_install=resolved_auto_install)
            agents_module = import_module("agents")
            _configure_agents_sdk_transport(agents_module, provider_runtime)
            run_config = _build_run_config_for_provider(agents_module, provider_runtime)
            base_team_spec = build_root_runtime_spec(root, provider_runtime=provider_runtime)
            recorder = _RuntimeEventRecorder(
                root,
                scope="root",
                session_id=session_id,
                team_id=base_team_spec.team_id,
            )
            extra_tools = _build_root_extra_tools_by_agent_id(root, agents_module, recorder=recorder)
            bundle = instantiate_agents_sdk_bundle(
                base_team_spec,
                entry_agent_id="root.orchestrator",
                model=resolved_model,
                expansion_depth=2,
                extra_tools_by_agent_id=extra_tools,
            )
            runner = getattr(agents_module, "Runner")
            session = _build_session(agents_module, root, session_id, ROOT_SESSION_DB)
            launch_prompt = build_root_launch_prompt(root, prompt=prompt, intake_file=intake_file)
            effective_model = resolved_model or bundle.team_spec.get_agent(bundle.entry_agent_id).preferred_model
            intake_path = _latest_intake_path(root, intake_file)
            hooks = None if hasattr(runner, "run_streamed") else _build_run_hooks(agents_module, recorder)
            begin_root_runtime_status(
                root,
                team_id=bundle.team_spec.team_id,
                entry_agent_id=bundle.entry_agent_id,
                model=effective_model,
                session_id=session_id,
                intake_file=str(intake_path) if intake_path else None,
                prompt=launch_prompt,
                provider_id=provider_runtime.provider_id,
                provider_route=provider_runtime.route_label,
            )
            recorder.record(
                event_type="root_session_started",
                title="Root session started",
                summary="Root orchestration runtime is now live.",
                agent_id=bundle.entry_agent_id,
                agent_name=bundle.team_spec.get_agent(bundle.entry_agent_id).display_name,
                phase="root_launch",
            )
            try:
                result = _run_workflow_with_observability(
                    runner,
                    entry_agent=bundle.entry_agent,
                    launch_prompt=launch_prompt,
                    session=session,
                    max_turns=resolved_max_turns,
                    run_config=run_config,
                    hooks=hooks,
                    recorder=recorder,
                )
            except Exception as exc:  # pragma: no cover - exercised through fake runtime tests
                friendly = _friendly_runtime_error(exc)
                recorder.record(
                    event_type="runtime_failed",
                    title="Root session failed",
                    summary=str(friendly),
                    agent_id=bundle.entry_agent_id,
                    agent_name=bundle.team_spec.get_agent(bundle.entry_agent_id).display_name,
                    phase="failed",
                )
                finalize_root_runtime_status(
                    root,
                    team_id=bundle.team_spec.team_id,
                    entry_agent_id=bundle.entry_agent_id,
                    model=effective_model,
                    session_id=session_id,
                    session_db_path=str(getattr(session, "db_path", "")) or None,
                    intake_file=str(intake_path) if intake_path else None,
                    prompt=launch_prompt,
                    provider_id=provider_runtime.provider_id,
                    provider_route=provider_runtime.route_label,
                    error=str(friendly),
                )
                raise friendly from exc
            recorder.record(
                event_type="root_session_completed",
                title="Root session completed",
                summary=_final_output_text(result) or "Root orchestration finished without explicit final output.",
                agent_id=bundle.entry_agent_id,
                agent_name=bundle.team_spec.get_agent(bundle.entry_agent_id).display_name,
                phase="completed",
                transcript=_final_output_text(result) or None,
            )
            finalize_root_runtime_status(
                root,
                team_id=bundle.team_spec.team_id,
                entry_agent_id=bundle.entry_agent_id,
                model=effective_model,
                session_id=session_id,
                session_db_path=str(getattr(session, "db_path", "")) or None,
                intake_file=str(intake_path) if intake_path else None,
                prompt=launch_prompt,
                provider_id=provider_runtime.provider_id,
                provider_route=provider_runtime.route_label,
                final_output=_final_output_text(result),
            )
            return LiveRunSummary(
                scope="root",
                team_id=bundle.team_spec.team_id,
                entry_agent_id=bundle.entry_agent_id,
                model=effective_model,
                provider_id=provider_runtime.provider_id,
                provider_route=provider_runtime.route_label,
                session_id=session_id,
                session_db_path=str(getattr(session, "db_path", "")) or None,
                final_output=_final_output_text(result),
                prompt=launch_prompt,
                intake_file=str(intake_path) if intake_path else None,
            )
    except LiveRuntimeError:
        raise
    except RuntimeError as exc:
        raise LiveRuntimeError(str(exc)) from exc


def run_subproject_commander(
    root: Path,
    run_id: str,
    prompt: str | None = None,
    model: str | None = None,
    session_id: str | None = None,
    max_turns: int | None = None,
    auto_install: bool | None = None,
    provider: str | None = None,
) -> LiveRunSummary:
    root = root.resolve()
    try:
        launch_config = _launch_config(root)
        resolved_max_turns = (
            int(env_value(root, "ASM_ROOT_MAX_TURNS", str(launch_config.max_turns)))
            if max_turns is None
            else max_turns
        )
        resolved_auto_install = (
            (env_value(root, "ASM_AUTO_INSTALL", "1" if launch_config.auto_install else "0") != "0")
            if auto_install is None
            else auto_install
        )
        package = load_handoff_package(root, run_id)
        project_name = package.routing_decision.target_name
        with activate_provider_runtime(root, provider_override=provider) as provider_session:
            provider_runtime = provider_session.runtime
            resolved_model = _normalize_model_name(
                model or env_value(root, "ASM_OPENAI_MODEL", provider_runtime.default_model)
            )
            if provider_runtime.model_strategy == "free_pool":
                resolved_model = None
            ensure_agents_sdk_available(auto_install=resolved_auto_install)
            agents_module = import_module("agents")
            _configure_agents_sdk_transport(agents_module, provider_runtime)
            run_config = _build_run_config_for_provider(agents_module, provider_runtime)
            entry_agent_id = f"subproject.{project_name}.commander"
            team_spec = build_subproject_runtime_spec(root, project_name, run_id=run_id, provider_runtime=provider_runtime)
            session_name = session_id or f"{project_name}-{run_id}"
            recorder = _RuntimeEventRecorder(
                root,
                scope="subproject",
                session_id=session_name,
                team_id=team_spec.team_id,
                project_name=project_name,
                run_id=run_id,
            )
            extra_tools = _build_subproject_extra_tools_by_agent_id(root, run_id, agents_module, recorder=recorder)
            bundle = instantiate_agents_sdk_bundle(
                team_spec,
                entry_agent_id=entry_agent_id,
                model=resolved_model,
                expansion_depth=2,
                extra_tools_by_agent_id=extra_tools,
            )
            runner = getattr(agents_module, "Runner")
            session = _build_session(agents_module, root, session_name, SUBPROJECT_SESSION_DB)
            launch_prompt = build_subproject_launch_prompt(root, run_id, prompt=prompt)
            hooks = None if hasattr(runner, "run_streamed") else _build_run_hooks(agents_module, recorder)
            update_root_runtime_status(
                root,
                active_scope="subproject",
                active_team_id=bundle.team_spec.team_id,
                active_project_name=project_name,
                active_run_id=run_id,
                active_agent_id=entry_agent_id,
                active_agent_name=bundle.team_spec.get_agent(entry_agent_id).display_name,
                current_phase="subproject_launch",
            )
            recorder.record(
                event_type="subproject_session_started",
                title="Subproject session started",
                summary=f"{project_name} commander is now active.",
                agent_id=entry_agent_id,
                agent_name=bundle.team_spec.get_agent(entry_agent_id).display_name,
                phase="subproject_launch",
            )
            try:
                result = _run_workflow_with_observability(
                    runner,
                    entry_agent=bundle.entry_agent,
                    launch_prompt=launch_prompt,
                    session=session,
                    max_turns=resolved_max_turns,
                    run_config=run_config,
                    hooks=hooks,
                    recorder=recorder,
                )
            except Exception as exc:  # pragma: no cover - exercised through fake runtime tests
                recorder.record(
                    event_type="subproject_session_failed",
                    title="Subproject session failed",
                    summary=str(_friendly_runtime_error(exc)),
                    agent_id=entry_agent_id,
                    agent_name=bundle.team_spec.get_agent(entry_agent_id).display_name,
                    phase="failed",
                )
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
            recorder.record(
                event_type="subproject_session_completed",
                title="Subproject session completed",
                summary=_final_output_text(result) or f"{project_name} completed.",
                agent_id=entry_agent_id,
                agent_name=bundle.team_spec.get_agent(entry_agent_id).display_name,
                phase="completed",
                transcript=_final_output_text(result) or None,
            )

            return LiveRunSummary(
                scope="subproject",
                team_id=bundle.team_spec.team_id,
                entry_agent_id=bundle.entry_agent_id,
                model=resolved_model or bundle.team_spec.get_agent(bundle.entry_agent_id).preferred_model,
                provider_id=provider_runtime.provider_id,
                provider_route=provider_runtime.route_label,
                session_id=session_name,
                session_db_path=str(getattr(session, "db_path", "")) or None,
                final_output=_final_output_text(result),
                prompt=launch_prompt,
                intake_file=str(package.task_request.intake_file) if package.task_request.intake_file else None,
                run_id=run_id,
                project_name=project_name,
            )
    except LiveRuntimeError:
        raise
    except RuntimeError as exc:
        raise LiveRuntimeError(str(exc)) from exc
