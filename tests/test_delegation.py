from pathlib import Path

from workspace_orchestrator.contracts import DelegationResult
from workspace_orchestrator.delegation import (
    describe_run,
    load_delegation_result,
    load_run_trace,
    record_delegation_result,
)
from workspace_orchestrator.handoff import (
    build_handoff_for_subproject,
    build_task_request_from_intake,
    default_research_plan,
    materialize_handoff_package,
)
from workspace_orchestrator.intake import parse_intake_file


def _prepare_root(tmp_path: Path) -> Path:
    (tmp_path / "rules").mkdir()
    (tmp_path / "kaggle_intake").mkdir()
    (tmp_path / "workspace_orchestrator").mkdir()
    (tmp_path / "CayleyPy_444_Cube").mkdir()
    return tmp_path


def _materialized_run(root: Path) -> tuple[str, str]:
    intake_file = root / "kaggle_intake" / "sample.md"
    intake_file.write_text(
        """# Intake

- https://www.kaggle.com/competitions/example-comp
""",
        encoding="utf-8",
    )
    brief = parse_intake_file(intake_file)
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
        project_name="CayleyPy_444_Cube",
        task_request=request,
        research_plan=plan,
        requester_agent_id="root.02_research_intelligence.head",
        run_id="run-001",
        handoff_id="handoff-001",
    )
    materialize_handoff_package(root, package)
    return package.run_id, package.handoff_id


def test_record_delegation_result_updates_trace_and_result_file(tmp_path: Path) -> None:
    root = _prepare_root(tmp_path)
    run_id, handoff_id = _materialized_run(root)

    result = DelegationResult(
        handoff_id=handoff_id,
        produced_by="subproject.CayleyPy_444_Cube.commander",
        status="completed",
        summary="Initial research package prepared.",
        canonical_paths=("CayleyPy_444_Cube/docs/research_summary.md",),
    )

    result_path = record_delegation_result(root, run_id, result)

    assert result_path == root / ".agent_workspace" / "runs" / run_id / "delegation_result.json"
    saved = load_delegation_result(root, run_id)
    trace = load_run_trace(root, run_id)
    assert saved is not None
    assert saved.summary == "Initial research package prepared."
    assert trace.status == "completed"
    assert "delegation_result.json" in trace.artifacts
    assert trace.events[-1] == "result_recorded:completed"


def test_describe_run_returns_handoff_trace_and_result(tmp_path: Path) -> None:
    root = _prepare_root(tmp_path)
    run_id, handoff_id = _materialized_run(root)
    record_delegation_result(
        root,
        run_id,
        DelegationResult(
            handoff_id=handoff_id,
            produced_by="subproject.CayleyPy_444_Cube.commander",
            status="completed",
            summary="Package ready for review.",
            canonical_paths=("CayleyPy_444_Cube/docs/research_summary.md",),
        ),
    )

    description = describe_run(root, run_id)

    assert description["run_id"] == "run-001"
    assert description["trace"]["status"] == "completed"
    assert description["handoff"]["target_agent_id"] == "subproject.CayleyPy_444_Cube.commander"
    assert description["result"]["summary"] == "Package ready for review."


def test_record_delegation_result_rejects_mismatched_handoff_id(tmp_path: Path) -> None:
    root = _prepare_root(tmp_path)
    run_id, _ = _materialized_run(root)

    try:
        record_delegation_result(
            root,
            run_id,
            DelegationResult(
                handoff_id="handoff-other",
                produced_by="subproject.CayleyPy_444_Cube.commander",
                status="completed",
                summary="Invalid result.",
            ),
        )
    except ValueError as exc:
        assert "handoff id mismatch" in str(exc).lower()
    else:
        raise AssertionError("Expected mismatched handoff id to raise ValueError")
