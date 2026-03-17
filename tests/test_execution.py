import json
from pathlib import Path

from workspace_orchestrator.delegation import load_delegation_result, load_run_trace
from workspace_orchestrator.execution import execute_run
from workspace_orchestrator.handoff import (
    build_handoff_for_subproject,
    build_task_request_from_intake,
    default_research_plan,
    materialize_handoff_package,
)
from workspace_orchestrator.intake import parse_intake_file


def _prepare_root(tmp_path: Path, project_name: str, main_body: str) -> Path:
    (tmp_path / "rules").mkdir()
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


def test_execute_run_protocol_mode_auto_ingests_result(tmp_path: Path) -> None:
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
print("fixture-protocol-ok")
""",
    )
    run_id = _materialize_run(root, "CayleyPy_TestHarness")

    record = execute_run(root, run_id)
    trace = load_run_trace(root, run_id)
    result = load_delegation_result(root, run_id)

    assert record.status == "succeeded"
    assert trace.status == "completed"
    assert result is not None
    assert result.summary == "Fixture protocol execution completed."
    assert (root / ".agent_workspace" / "runs" / run_id / "execution_stdout.txt").exists()


def test_execute_run_legacy_mode_waits_for_manual_result(tmp_path: Path) -> None:
    root = _prepare_root(
        tmp_path,
        "CayleyPy_444_Cube",
        """
from __future__ import annotations
print("legacy-ok")
""",
    )
    run_id = _materialize_run(root, "CayleyPy_444_Cube")

    record = execute_run(root, run_id)
    trace = load_run_trace(root, run_id)

    assert record.mode == "legacy"
    assert record.status == "succeeded"
    assert trace.status == "awaiting_result"
    assert load_delegation_result(root, run_id) is None


def test_execute_run_records_failure_for_nonzero_exit(tmp_path: Path) -> None:
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

    record = execute_run(root, run_id)
    trace = load_run_trace(root, run_id)

    assert record.status == "failed"
    assert record.exit_code == 5
    assert trace.status == "execution_failed"


def test_execute_run_records_timeout(tmp_path: Path) -> None:
    root = _prepare_root(
        tmp_path,
        "CayleyPy_TestHarness",
        """
from __future__ import annotations
import argparse
import time
parser = argparse.ArgumentParser()
parser.add_argument("--root-handoff", required=True)
parser.add_argument("--root-run-dir", required=True)
parser.parse_args()
time.sleep(1.0)
""",
    )
    run_id = _materialize_run(root, "CayleyPy_TestHarness")

    record = execute_run(root, run_id, timeout_seconds=0.1)
    trace = load_run_trace(root, run_id)

    assert record.status == "timed_out"
    assert trace.status == "execution_failed"
