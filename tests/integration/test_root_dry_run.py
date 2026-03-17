import json
from pathlib import Path

from workspace_orchestrator import cli


def _prepare_root(tmp_path: Path) -> Path:
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    logs_dir = rules_dir / "logs"
    logs_dir.mkdir()
    (logs_dir / "RESEARCH_JOURNAL.md").write_text("# Research Journal\n", encoding="utf-8")
    (logs_dir / "AGENT_INTERACTIONS_LOG.md").write_text("# Agent Interactions Log\n", encoding="utf-8")
    (logs_dir / "USER_PROMPTS_LOG.md").write_text("# User Prompts Log\n", encoding="utf-8")
    intake_dir = tmp_path / "kaggle_intake"
    intake_dir.mkdir()
    (tmp_path / "workspace_orchestrator").mkdir()
    project_dir = tmp_path / "CayleyPy_TestHarness"
    project_dir.mkdir()
    (project_dir / "main.py").write_text(
        """
from __future__ import annotations
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--root-handoff", required=True)
parser.add_argument("--root-run-dir", required=True)
args = parser.parse_args()

handoff = json.loads(Path(args.root_handoff).read_text(encoding="utf-8"))
run_dir = Path(args.root_run_dir)
(run_dir / "subproject_result.json").write_text(
    json.dumps(
        {
            "handoff_id": handoff["handoff_id"],
            "produced_by": handoff["target_agent_id"],
            "status": "completed",
            "summary": "Integration flow completed.",
            "canonical_paths": ["CayleyPy_TestHarness/docs/final.md"],
            "escalations": [],
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)
print("integration-ok")
""",
        encoding="utf-8",
    )
    (intake_dir / "sample.md").write_text(
        """# Intake

- https://www.kaggle.com/competitions/example-comp
""",
        encoding="utf-8",
    )
    return tmp_path


def test_root_cli_executes_fixture_subproject_end_to_end(tmp_path: Path, monkeypatch, capsys) -> None:
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
    build_payload = json.loads(capsys.readouterr().out)
    run_id = build_payload["run_id"]

    exit_code = cli.main(["execute-run", run_id, "--json"])
    execute_payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert execute_payload["status"] == "succeeded"

    exit_code = cli.main(["show-run", run_id, "--json"])
    show_payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert show_payload["trace"]["status"] == "completed"
    assert show_payload["result"]["summary"] == "Integration flow completed."
    journal = (root / "rules" / "logs" / "RESEARCH_JOURNAL.md").read_text(encoding="utf-8")
    interactions = (root / "rules" / "logs" / "AGENT_INTERACTIONS_LOG.md").read_text(encoding="utf-8")
    assert run_id in journal
    assert run_id in interactions
