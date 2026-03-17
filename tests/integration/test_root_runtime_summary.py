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
    (project_dir / "main.py").write_text("print('fixture')\n", encoding="utf-8")
    (tmp_path / "kaggle_intake" / "sample.md").write_text(
        """# Intake

- https://www.kaggle.com/competitions/example-comp
""",
        encoding="utf-8",
    )
    return tmp_path


def test_root_cli_runtime_summary_reports_run_metadata(tmp_path: Path, monkeypatch, capsys) -> None:
    root = _prepare_root(tmp_path)
    monkeypatch.setattr(cli, "_workspace_root", lambda: root)

    cli.main(
        [
            "build-handoff",
            "--project",
            "CayleyPy_TestHarness",
            "--objective",
            "Investigate fixture project",
            "--json",
        ]
    )
    run_id = json.loads(capsys.readouterr().out)["run_id"]

    exit_code = cli.main(["runtime-summary", "--run-id", run_id, "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["manager_agent_id"] == "root.orchestrator"
    assert payload["metadata"]["run_id"] == run_id
    assert payload["metadata"]["target_agent_id"] == "subproject.CayleyPy_TestHarness.commander"

    exit_code = cli.main(["sdk-status", "--json"])
    sdk_payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert sdk_payload["package_name"] == "agents"
    assert "available" in sdk_payload
