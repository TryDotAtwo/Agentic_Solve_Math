import json
import os
import sqlite3
import sys
import types
from pathlib import Path

from workspace_orchestrator.handoff import (
    build_handoff_for_subproject,
    build_task_request_from_intake,
    default_research_plan,
    materialize_handoff_package,
)
from workspace_orchestrator.intake import parse_intake_file
from workspace_orchestrator.live_runtime import (
    _build_root_extra_tools_by_agent_id,
    _build_subproject_extra_tools_by_agent_id,
    LiveRuntimeError,
    run_root_orchestrator,
    run_subproject_commander,
)
from workspace_orchestrator.provider_config import (
    DEFAULT_OPENROUTER_FREE_MODELS,
    activate_provider_runtime,
    resolve_provider_runtime,
)


def _prepare_root(tmp_path: Path, project_name: str = "CayleyPy_TestHarness") -> Path:
    (tmp_path / "rules").mkdir()
    logs_dir = tmp_path / "rules" / "logs"
    logs_dir.mkdir()
    (logs_dir / "RESEARCH_JOURNAL.md").write_text("# Research Journal\n", encoding="utf-8")
    (logs_dir / "AGENT_INTERACTIONS_LOG.md").write_text("# Agent Interactions Log\n", encoding="utf-8")
    (logs_dir / "USER_PROMPTS_LOG.md").write_text("# User Prompts Log\n", encoding="utf-8")
    (tmp_path / "kaggle_intake").mkdir()
    (tmp_path / "workspace_orchestrator").mkdir()
    project_dir = tmp_path / project_name
    project_dir.mkdir()
    (project_dir / "main.py").write_text("print('fixture')\n", encoding="utf-8")
    (project_dir / "README.md").write_text("# Fixture project\n", encoding="utf-8")
    (tmp_path / "kaggle_intake" / "sample.md").write_text(
        """# Intake

- https://www.kaggle.com/competitions/example-comp
- https://arxiv.org/abs/1234.5678
""",
        encoding="utf-8",
    )
    return tmp_path


def _materialize_run(root: Path, project_name: str = "CayleyPy_TestHarness") -> str:
    brief = parse_intake_file(root / "kaggle_intake" / "sample.md")
    request = build_task_request_from_intake(
        brief,
        objective="Investigate the fixture competition",
        task_id="task-001",
        requested_by="root.02_research_intelligence.head",
    )
    plan = default_research_plan(
        objective="Investigate the fixture competition",
        plan_id="plan-001",
        research_questions=("What should the team research first?",),
    )
    package = build_handoff_for_subproject(
        root,
        project_name=project_name,
        task_request=request,
        research_plan=plan,
        requester_agent_id="root.02_research_intelligence.head",
        run_id="run-001",
        handoff_id="handoff-001",
    )
    materialize_handoff_package(root, package)
    return package.run_id


def _install_fake_agents_sdk(monkeypatch):
    class FakeWebSearchTool:
        pass

    class FakeAgent:
        def __init__(self, **kwargs):
            self.kwargs = dict(kwargs)
            self.name = kwargs["name"]
            self.instructions = kwargs.get("instructions", "")
            self.model = kwargs.get("model")
            self.tools = list(kwargs.get("tools", []))
            self.handoffs = list(kwargs.get("handoffs", []))

        def as_tool(self, tool_name: str, tool_description: str):
            def _tool(*args, **kwargs):
                return {
                    "tool_name": tool_name,
                    "tool_description": tool_description,
                    "agent_name": self.name,
                    "args": args,
                    "kwargs": kwargs,
                }

            _tool.__name__ = tool_name
            return _tool

    class FakeSQLiteSession:
        def __init__(self, session_id: str, db_path: str | None = None):
            self.session_id = session_id
            self.db_path = db_path

    class FakeRunner:
        last_call = None

        @staticmethod
        def run_sync(agent, input, session=None, max_turns=None, run_config=None, **_kwargs):
            FakeRunner.last_call = {
                "agent": agent,
                "input": input,
                "session": session,
                "max_turns": max_turns,
                "run_config": run_config,
            }
            if agent.name == "Subproject Commander":
                for tool in agent.tools:
                    if getattr(tool, "__name__", "") == "record_subproject_result":
                        tool(
                            status="completed",
                            summary="Subproject fixture completed.",
                            canonical_paths=["CayleyPy_TestHarness/docs/final.md"],
                        )
                        break
                return types.SimpleNamespace(final_output="Subproject fixture completed.")
            return types.SimpleNamespace(final_output="Root fixture completed.")

    def function_tool(func=None, **_kwargs):
        if func is None:
            return lambda inner: inner
        return func

    fake_module = types.SimpleNamespace(
        Agent=FakeAgent,
        Runner=FakeRunner,
        SQLiteSession=FakeSQLiteSession,
        WebSearchTool=FakeWebSearchTool,
        function_tool=function_tool,
    )
    monkeypatch.setattr("workspace_orchestrator.openai_runtime.find_spec", lambda name: object())
    monkeypatch.setitem(sys.modules, "agents", fake_module)
    return FakeRunner


def test_resolve_provider_runtime_reads_root_env_file(tmp_path: Path, monkeypatch) -> None:
    root = _prepare_root(tmp_path)
    (root / ".env").write_text("OPENAI_API_KEY=sk-test-key\n", encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    runtime = resolve_provider_runtime(root)

    assert runtime.provider_id == "openai"
    assert runtime.api_key == "sk-test-key"
    assert runtime.route_label == "openai"


def test_resolve_provider_runtime_sets_google_route_for_google_style_openai_key(
    tmp_path: Path, monkeypatch
) -> None:
    root = _prepare_root(tmp_path)
    (root / ".env").write_text("OPENAI_API_KEY=AIzaSy-test-google-key\n", encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    runtime = resolve_provider_runtime(root)

    assert runtime.api_key == "AIzaSy-test-google-key"
    assert runtime.base_url == "https://generativelanguage.googleapis.com/v1beta/openai/"
    assert runtime.route_label == "google_openai_compatible"


def test_resolve_provider_runtime_accepts_google_api_key(tmp_path: Path, monkeypatch) -> None:
    root = _prepare_root(tmp_path)
    (root / ".env").write_text("GOOGLE_API_KEY=goog-test-key\n", encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    runtime = resolve_provider_runtime(root)

    assert runtime.api_key == "goog-test-key"
    assert runtime.base_url == "https://generativelanguage.googleapis.com/v1beta/openai/"
    assert runtime.route_label == "google_openai_compatible"


def test_activate_provider_runtime_restores_environment_after_close(tmp_path: Path, monkeypatch) -> None:
    root = _prepare_root(tmp_path)
    (root / ".env").write_text("OPENAI_API_KEY=sk-test-key\n", encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_BASE_URL", "https://old.example/v1")

    with activate_provider_runtime(root) as session:
        assert session.runtime.provider_id == "openai"
        assert os.environ["OPENAI_API_KEY"] == "sk-test-key"
        assert "OPENAI_BASE_URL" not in os.environ

    assert "OPENAI_API_KEY" not in os.environ
    assert os.environ["OPENAI_BASE_URL"] == "https://old.example/v1"


def test_run_root_orchestrator_uses_fake_sdk_and_persistent_session(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.delenv("ASM_OPENAI_MODEL", raising=False)
    root = _prepare_root(tmp_path)
    (root / ".env").write_text("OPENAI_API_KEY=sk-test-key\n", encoding="utf-8")
    fake_runner = _install_fake_agents_sdk(monkeypatch)

    summary = run_root_orchestrator(
        root,
        prompt="Start the root orchestration cycle.",
        session_id="root-session",
        auto_install=False,
    )

    assert summary.final_output == "Root fixture completed."
    assert summary.session_id == "root-session"
    assert summary.session_db_path == str(root / ".agent_workspace" / "sessions" / "root_sessions.sqlite")
    assert summary.entry_agent_id == "root.orchestrator"
    assert summary.model == "gpt-5.2"
    assert summary.provider_id == "openai"
    assert summary.provider_route == "openai"
    status_payload = json.loads(
        (root / ".agent_workspace" / "runtime" / "root_runtime_status.json").read_text(encoding="utf-8")
    )
    assert status_payload["status"] == "succeeded"
    assert status_payload["session_id"] == "root-session"
    assert status_payload["provider_id"] == "openai"
    assert status_payload["event_count"] >= 2
    assert fake_runner.last_call["session"].db_path == str(
        root / ".agent_workspace" / "sessions" / "root_sessions.sqlite"
    )
    runtime_events = (root / ".agent_workspace" / "runtime" / "root_runtime_events.jsonl").read_text(encoding="utf-8")
    assert "root_session_started" in runtime_events
    assert "root_session_completed" in runtime_events
    tool_names = {getattr(tool, "__name__", tool.__class__.__name__) for tool in fake_runner.last_call["agent"].tools}
    assert "parse_latest_intake" in tool_names
    assert "build_handoff" in tool_names


def test_run_subproject_commander_writes_subproject_result(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("ASM_OPENAI_MODEL", raising=False)
    root = _prepare_root(tmp_path)
    (root / ".env").write_text("OPENAI_API_KEY=sk-test-key\n", encoding="utf-8")
    _install_fake_agents_sdk(monkeypatch)
    run_id = _materialize_run(root)

    summary = run_subproject_commander(
        root,
        run_id,
        session_id="subproject-session",
        auto_install=False,
    )

    result_path = root / ".agent_workspace" / "runs" / run_id / "subproject_result.json"
    payload = json.loads(result_path.read_text(encoding="utf-8"))

    assert summary.final_output == "Subproject fixture completed."
    assert summary.run_id == run_id
    assert summary.session_db_path == str(root / ".agent_workspace" / "sessions" / "subproject_sessions.sqlite")
    assert summary.model == "gpt-5.2"
    assert summary.provider_id == "openai"
    assert payload["status"] == "completed"
    assert payload["summary"] == "Subproject fixture completed."
    runtime_events = (root / ".agent_workspace" / "runtime" / "root_runtime_events.jsonl").read_text(encoding="utf-8")
    assert "subproject_session_started" in runtime_events
    assert "subproject_result_recorded" in runtime_events


def test_history_agents_receive_acl_bounded_operational_tools(tmp_path: Path, monkeypatch) -> None:
    root = _prepare_root(tmp_path)
    _install_fake_agents_sdk(monkeypatch)
    fake_agents = sys.modules["agents"]
    run_id = _materialize_run(root)

    root_mapping = _build_root_extra_tools_by_agent_id(root, fake_agents)
    root_history_tools = {
        getattr(tool, "__name__", tool.__class__.__name__)
        for tool in root_mapping["root.06_editorial_and_history.history_scribe"]
    }
    assert "append_root_research_note" in root_history_tools
    assert "build_handoff" not in root_history_tools
    assert "run_subproject_team" not in root_history_tools

    sub_mapping = _build_subproject_extra_tools_by_agent_id(root, run_id, fake_agents)
    historian_tools = {
        getattr(tool, "__name__", tool.__class__.__name__)
        for tool in sub_mapping["subproject.CayleyPy_TestHarness.07_editorial_and_history.local_historian"]
    }
    assert "append_subproject_note" in historian_tools
    assert "record_subproject_result" not in historian_tools


def test_department_heads_receive_milestone_reporting_tool(tmp_path: Path, monkeypatch) -> None:
    root = _prepare_root(tmp_path)
    _install_fake_agents_sdk(monkeypatch)
    fake_agents = sys.modules["agents"]

    root_mapping = _build_root_extra_tools_by_agent_id(root, fake_agents)
    head_tools = {
        getattr(tool, "__name__", tool.__class__.__name__)
        for tool in root_mapping["root.02_research_intelligence.head"]
    }

    assert "record_department_milestone" in head_tools


def test_run_root_orchestrator_falls_back_to_temp_session_db_on_sqlite_io_error(
    tmp_path: Path, monkeypatch
) -> None:
    root = _prepare_root(tmp_path)
    (root / ".env").write_text("OPENAI_API_KEY=sk-test-key\n", encoding="utf-8")
    _install_fake_agents_sdk(monkeypatch)

    class FlakySQLiteSession:
        attempts = 0

        def __init__(self, session_id: str, db_path: str | None = None):
            FlakySQLiteSession.attempts += 1
            if FlakySQLiteSession.attempts == 1:
                raise sqlite3.OperationalError("disk I/O error")
            self.session_id = session_id
            self.db_path = db_path

    sys.modules["agents"].SQLiteSession = FlakySQLiteSession

    summary = run_root_orchestrator(
        root,
        prompt="Start the root orchestration cycle.",
        session_id="root-session",
        auto_install=False,
    )

    assert summary.final_output == "Root fixture completed."
    assert summary.session_db_path is not None
    assert "Agentic_Solve_Math" in summary.session_db_path
    assert summary.session_db_path.endswith("root_sessions.sqlite")
    assert summary.session_db_path != str(root / ".agent_workspace" / "sessions" / "root_sessions.sqlite")


def test_run_root_orchestrator_wraps_quota_errors_with_friendly_message(
    tmp_path: Path, monkeypatch
) -> None:
    root = _prepare_root(tmp_path)
    (root / ".env").write_text("OPENAI_API_KEY=sk-test-key\n", encoding="utf-8")
    _install_fake_agents_sdk(monkeypatch)

    class FakeRateLimitError(Exception):
        pass

    class RaisingRunner:
        @staticmethod
        def run_sync(agent, input, session=None, max_turns=None, run_config=None, **_kwargs):
            raise FakeRateLimitError("insufficient_quota")

    sys.modules["agents"].Runner = RaisingRunner

    try:
        run_root_orchestrator(
            root,
            prompt="Start the root orchestration cycle.",
            session_id="root-session",
            auto_install=False,
        )
    except LiveRuntimeError as exc:
        assert "quota" in str(exc).lower()
    else:
        raise AssertionError("Expected a friendly LiveRuntimeError for quota failures.")


def test_run_root_orchestrator_uses_curated_openrouter_intersection_for_free_pool(
    tmp_path: Path, monkeypatch
) -> None:
    root = _prepare_root(tmp_path)
    (root / ".env").write_text("OPENROUTER_API_KEY=or-test-key\n", encoding="utf-8")
    (root / "runtime_config.toml").write_text(
        """[bootstrap]
active_provider = "openrouter"
""",
        encoding="utf-8",
    )
    _install_fake_agents_sdk(monkeypatch)
    monkeypatch.setattr(
        "workspace_orchestrator.provider_config.discover_openrouter_free_models",
        lambda url, timeout=10.0: tuple(reversed(DEFAULT_OPENROUTER_FREE_MODELS))
        + ("external/provider-only:free",),
    )

    summary = run_root_orchestrator(
        root,
        prompt="Start the root orchestration cycle.",
        session_id="root-openrouter-session",
        auto_install=False,
        provider="openrouter",
    )

    assert summary.final_output == "Root fixture completed."
    assert summary.provider_id == "openrouter"
    assert summary.provider_route == "openrouter"
    assert summary.model == "meta-llama/llama-3.3-70b-instruct:free"
    status_payload = json.loads(
        (root / ".agent_workspace" / "runtime" / "root_runtime_status.json").read_text(encoding="utf-8")
    )
    assert status_payload["provider_id"] == "openrouter"
    assert status_payload["model"] == "meta-llama/llama-3.3-70b-instruct:free"
