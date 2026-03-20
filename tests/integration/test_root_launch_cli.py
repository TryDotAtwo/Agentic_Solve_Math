import json
import sys
import types
from pathlib import Path

from workspace_orchestrator import cli


def _prepare_root(tmp_path: Path) -> Path:
    (tmp_path / "rules").mkdir()
    logs_dir = tmp_path / "rules" / "logs"
    logs_dir.mkdir()
    (logs_dir / "RESEARCH_JOURNAL.md").write_text("# Research Journal\n", encoding="utf-8")
    (logs_dir / "AGENT_INTERACTIONS_LOG.md").write_text("# Agent Interactions Log\n", encoding="utf-8")
    (logs_dir / "USER_PROMPTS_LOG.md").write_text("# User Prompts Log\n", encoding="utf-8")
    (tmp_path / "kaggle_intake").mkdir()
    (tmp_path / "workspace_orchestrator").mkdir()
    (tmp_path / "CayleyPy_TestHarness").mkdir()
    (tmp_path / "CayleyPy_TestHarness" / "README.md").write_text("# Fixture project\n", encoding="utf-8")
    (tmp_path / "kaggle_intake" / "sample.md").write_text(
        """# Intake

- https://www.kaggle.com/competitions/example-comp
""",
        encoding="utf-8",
    )
    (tmp_path / ".env").write_text("OPENAI_API_KEY=sk-test-key\n", encoding="utf-8")
    return tmp_path


def _install_fake_agents_sdk(monkeypatch) -> None:
    class FakeAgent:
        def __init__(self, **kwargs):
            self.name = kwargs["name"]
            self.tools = list(kwargs.get("tools", []))
            self.handoffs = list(kwargs.get("handoffs", []))

        def as_tool(self, tool_name: str, tool_description: str):
            def _tool(*args, **kwargs):
                return {
                    "tool_name": tool_name,
                    "tool_description": tool_description,
                    "args": args,
                    "kwargs": kwargs,
                }

            _tool.__name__ = tool_name
            return _tool

    class FakeRunner:
        @staticmethod
        def run_sync(agent, input, session=None, max_turns=None, run_config=None, **_kwargs):
            return types.SimpleNamespace(final_output="Root CLI launch completed.")

    class FakeSQLiteSession:
        def __init__(self, session_id: str, db_path: str | None = None):
            self.session_id = session_id
            self.db_path = db_path

    def function_tool(func=None, **_kwargs):
        if func is None:
            return lambda inner: inner
        return func

    fake_module = types.SimpleNamespace(
        Agent=FakeAgent,
        Runner=FakeRunner,
        SQLiteSession=FakeSQLiteSession,
        WebSearchTool=type("FakeWebSearchTool", (), {}),
        function_tool=function_tool,
    )
    monkeypatch.setattr("workspace_orchestrator.openai_runtime.find_spec", lambda name: object())
    monkeypatch.setitem(sys.modules, "agents", fake_module)


class _FakeDashboardHandle:
    def __init__(self, url: str = "http://127.0.0.1:8765") -> None:
        self.url = url
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_launch_root_command_runs_live_runtime(tmp_path: Path, monkeypatch, capsys) -> None:
    root = _prepare_root(tmp_path)
    _install_fake_agents_sdk(monkeypatch)
    monkeypatch.setattr(cli, "_workspace_root", lambda: root)

    exit_code = cli.main(["launch-root", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["entry_agent_id"] == "root.orchestrator"
    assert payload["final_output"] == "Root CLI launch completed."


def test_cli_no_args_auto_launches_root_when_bootstrap_is_present(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    root = _prepare_root(tmp_path)
    _install_fake_agents_sdk(monkeypatch)
    dashboard_handle = _FakeDashboardHandle()
    opened_urls: list[str] = []
    monkeypatch.setattr(cli, "_workspace_root", lambda: root)
    monkeypatch.setattr(cli, "start_dashboard_server", lambda *args, **kwargs: dashboard_handle)
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: opened_urls.append(url))

    exit_code = cli.main([])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert dashboard_handle.closed is True
    assert opened_urls == ["http://127.0.0.1:8765"]
    assert "Agentic Solve Math - operator session" in output
    assert "dashboard_url: http://127.0.0.1:8765" in output
    assert "entry_agent: root.orchestrator" in output
    assert "final_output: Root CLI launch completed." in output


def test_cli_no_args_closes_dashboard_on_keyboard_interrupt(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    root = _prepare_root(tmp_path)
    dashboard_handle = _FakeDashboardHandle()

    monkeypatch.setattr(cli, "_workspace_root", lambda: root)
    monkeypatch.setattr(cli, "start_dashboard_server", lambda *args, **kwargs: dashboard_handle)
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: True)
    monkeypatch.setattr(cli, "_launch_root", lambda *args, **kwargs: (_ for _ in ()).throw(KeyboardInterrupt()))

    exit_code = cli.main([])
    output = capsys.readouterr().out

    assert exit_code == 130
    assert dashboard_handle.closed is True
    assert "operator_session_status: interrupted" in output


def test_launch_root_command_reports_friendly_runtime_errors(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    root = _prepare_root(tmp_path)

    class FakeRateLimitError(Exception):
        pass

    class FakeAgent:
        def __init__(self, **kwargs):
            self.name = kwargs["name"]
            self.tools = list(kwargs.get("tools", []))
            self.handoffs = list(kwargs.get("handoffs", []))

        def as_tool(self, tool_name: str, tool_description: str):
            def _tool(*args, **kwargs):
                return None

            _tool.__name__ = tool_name
            return _tool

    class FakeRunner:
        @staticmethod
        def run_sync(agent, input, session=None, max_turns=None, run_config=None, **_kwargs):
            raise FakeRateLimitError("insufficient_quota")

    class FakeSQLiteSession:
        def __init__(self, session_id: str, db_path: str | None = None):
            self.session_id = session_id
            self.db_path = db_path

    def function_tool(func=None, **_kwargs):
        if func is None:
            return lambda inner: inner
        return func

    fake_module = types.SimpleNamespace(
        Agent=FakeAgent,
        Runner=FakeRunner,
        SQLiteSession=FakeSQLiteSession,
        WebSearchTool=type("FakeWebSearchTool", (), {}),
        function_tool=function_tool,
    )
    monkeypatch.setattr("workspace_orchestrator.openai_runtime.find_spec", lambda name: object())
    monkeypatch.setitem(sys.modules, "agents", fake_module)
    monkeypatch.setattr(cli, "_workspace_root", lambda: root)

    exit_code = cli.main(["launch-root", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["status"] == "error"
    assert "quota" in payload["error"].lower()
