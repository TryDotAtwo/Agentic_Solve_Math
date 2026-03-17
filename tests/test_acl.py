from pathlib import Path

from workspace_orchestrator.acl import can_call_agent
from workspace_orchestrator.organization import build_root_organization, build_subproject_organization


def _prepare_root(tmp_path: Path) -> None:
    (tmp_path / "rules").mkdir()
    (tmp_path / "kaggle_intake").mkdir()
    (tmp_path / "workspace_orchestrator").mkdir()
    (tmp_path / "CayleyPy_444_Cube").mkdir()


def test_root_orchestrator_can_call_heads_but_not_staff(tmp_path: Path) -> None:
    _prepare_root(tmp_path)
    org = build_root_organization(tmp_path)

    orchestrator = org.get_agent("root.orchestrator")
    head = org.get_agent("root.01_intake_and_orchestration.head")
    staff = org.get_agent("root.02_research_intelligence.global_searcher")

    assert can_call_agent(orchestrator, head) is True
    assert can_call_agent(orchestrator, staff) is False


def test_staff_can_call_shared_service_but_not_other_department_staff(tmp_path: Path) -> None:
    _prepare_root(tmp_path)
    org = build_root_organization(tmp_path)

    caller = org.get_agent("root.03_architecture_and_capability.rule_engineer")
    shared = org.get_agent("root.02_research_intelligence.global_searcher")
    foreign_staff = org.get_agent("root.05_cross_project_analysis.pattern_synthesizer")

    assert can_call_agent(caller, shared) is True
    assert can_call_agent(caller, foreign_staff) is False


def test_subproject_staff_cannot_call_root_agents(tmp_path: Path) -> None:
    _prepare_root(tmp_path)
    root_org = build_root_organization(tmp_path)
    sub_org = build_subproject_organization(tmp_path, "CayleyPy_444_Cube")

    caller = sub_org.get_agent("subproject.CayleyPy_444_Cube.05_solver_engineering.search_engineer")
    callee = root_org.get_agent("root.orchestrator")

    assert can_call_agent(caller, callee) is False
