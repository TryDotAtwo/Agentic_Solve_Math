import json
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
    project_dir = tmp_path / "CayleyPy_TestHarness"
    project_dir.mkdir()
    (project_dir / "README.md").write_text("# Fixture project\n", encoding="utf-8")
    (tmp_path / ".env").write_text("OPENAI_API_KEY=sk-test-key\n", encoding="utf-8")
    return tmp_path


def test_dashboard_command_can_emit_snapshot_json(tmp_path: Path, monkeypatch, capsys) -> None:
    root = _prepare_root(tmp_path)
    monkeypatch.setattr(cli, "_workspace_root", lambda: root)

    exit_code = cli.main(["dashboard", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["stats"]["subprojects_total"] == 1
    assert payload["root_team"]["agent_count"] == 25
