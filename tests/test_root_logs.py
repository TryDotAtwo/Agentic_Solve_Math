from pathlib import Path

from workspace_orchestrator.execution import execute_run
from workspace_orchestrator.handoff import (
    build_handoff_for_subproject,
    build_task_request_from_intake,
    default_research_plan,
    materialize_handoff_package,
)
from workspace_orchestrator.intake import parse_intake_file
from workspace_orchestrator.root_logs import sync_run_logs


def _prepare_root(tmp_path: Path, project_name: str, main_body: str) -> Path:
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
    project_dir = tmp_path / project_name
    project_dir.mkdir()
    (project_dir / "main.py").write_text(main_body, encoding="utf-8")
    (intake_dir / "sample.md").write_text(
        """# Intake

- https://www.kaggle.com/competitions/example-comp
""",
        encoding="utf-8",
    )
    return tmp_path


def _materialize_run(root: Path, project_name: str) -> str:
    brief = parse_intake_file(root / "kaggle_intake" / "sample.md")
    request = build_task_request_from_intake(
        brief,
        objective="Investigate the competition",
        task_id="task-001",
        requested_by="root.02_research_intelligence.head",
    )
    plan = default_research_plan(
        objective="Investigate the competition",
        plan_id="plan-001",
        research_questions=("What should the team study first?",),
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


def test_protocol_execution_auto_updates_root_logs(tmp_path: Path) -> None:
    root = _prepare_root(
        tmp_path,
        "CayleyPy_TestHarness",
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
            "summary": "Fixture protocol execution completed.",
            "canonical_paths": ["CayleyPy_TestHarness/docs/summary.md"],
            "escalations": [],
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)
""",
    )
    run_id = _materialize_run(root, "CayleyPy_TestHarness")

    execute_run(root, run_id)

    journal = (root / "rules" / "logs" / "RESEARCH_JOURNAL.md").read_text(encoding="utf-8")
    interactions = (root / "rules" / "logs" / "AGENT_INTERACTIONS_LOG.md").read_text(encoding="utf-8")

    assert "run-001 | execution:succeeded" in journal
    assert "run-001 | result:completed" in journal
    assert "Fixture protocol execution completed." in journal
    assert "run-001 | execution:succeeded" in interactions
    assert "run-001 | result:completed" in interactions


def test_root_log_sync_is_idempotent_for_same_event(tmp_path: Path) -> None:
    root = _prepare_root(
        tmp_path,
        "CayleyPy_TestHarness",
        """
from __future__ import annotations
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--root-handoff", required=True)
parser.add_argument("--root-run-dir", required=True)
parser.parse_args()
""",
    )
    run_id = _materialize_run(root, "CayleyPy_TestHarness")

    execute_run(root, run_id)
    sync_run_logs(root, run_id, "execution")
    sync_run_logs(root, run_id, "execution")

    journal = (root / "rules" / "logs" / "RESEARCH_JOURNAL.md").read_text(encoding="utf-8")
    assert journal.count("run-001 | execution:succeeded") == 1


def test_failed_execution_updates_root_logs_without_result_entry(tmp_path: Path) -> None:
    root = _prepare_root(
        tmp_path,
        "CayleyPy_TestHarness",
        """
from __future__ import annotations
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--root-handoff", required=True)
parser.add_argument("--root-run-dir", required=True)
parser.parse_args()
raise SystemExit(5)
""",
    )
    run_id = _materialize_run(root, "CayleyPy_TestHarness")

    execute_run(root, run_id)

    journal = (root / "rules" / "logs" / "RESEARCH_JOURNAL.md").read_text(encoding="utf-8")
    assert "run-001 | execution:failed" in journal
    assert "result:" not in journal
