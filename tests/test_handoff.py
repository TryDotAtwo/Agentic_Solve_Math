from pathlib import Path

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


def test_build_handoff_uses_target_manifest_permissions(tmp_path: Path) -> None:
    root = _prepare_root(tmp_path)
    intake_file = root / "kaggle_intake" / "sample.md"
    intake_file.write_text(
        """# Intake

- https://www.kaggle.com/competitions/example-comp
- https://arxiv.org/abs/1234.5678
""",
        encoding="utf-8",
    )

    brief = parse_intake_file(intake_file)
    request = build_task_request_from_intake(
        brief,
        objective="Investigate the competition",
        task_id="task-001",
        requested_by="root.01_intake_and_orchestration.head",
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
        requester_agent_id="root.01_intake_and_orchestration.head",
        run_id="run-001",
        handoff_id="handoff-001",
    )

    assert package.target_agent_id == "subproject.CayleyPy_444_Cube.commander"
    assert any("CayleyPy_444_Cube" in item for item in package.target_read_roots)
    assert "local_orchestrate" in package.allowed_tools


def test_materialize_handoff_package_writes_root_owned_run_dir(tmp_path: Path) -> None:
    root = _prepare_root(tmp_path)
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
        requested_by="root.01_intake_and_orchestration.head",
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
        requester_agent_id="root.01_intake_and_orchestration.head",
        run_id="run-001",
        handoff_id="handoff-001",
    )

    run_dir = materialize_handoff_package(root, package)

    assert run_dir == root / ".agent_workspace" / "runs" / "run-001"
    assert (run_dir / "handoff.json").exists()
    assert (run_dir / "task_request.json").exists()
    assert (run_dir / "trace.json").exists()
    assert not (root / "CayleyPy_444_Cube" / ".agent_workspace" / "runs" / "run-001").exists()
