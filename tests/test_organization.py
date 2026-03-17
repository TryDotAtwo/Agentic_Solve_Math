from pathlib import Path

from workspace_orchestrator.organization import build_root_organization, build_subproject_organization


def _prepare_root(tmp_path: Path) -> None:
    (tmp_path / "rules").mkdir()
    (tmp_path / "kaggle_intake").mkdir()
    (tmp_path / "workspace_orchestrator").mkdir()
    (tmp_path / "CayleyPy_444_Cube").mkdir()


def test_build_root_organization_has_expected_scale_and_shared_services(tmp_path: Path) -> None:
    _prepare_root(tmp_path)

    org = build_root_organization(tmp_path)

    assert org.agent_count == 25
    assert len(org.departments) == 8
    assert org.get_agent("root.orchestrator").rank == "executive"
    assert org.get_agent("root.02_research_intelligence.global_searcher").shared_service is True
    assert org.get_agent("root.06_editorial_and_history.history_scribe").shared_service is True
    assert org.get_agent("root.03_architecture_and_capability.head").mutable_rule_roots


def test_build_subproject_organization_has_expected_scale_and_commander(tmp_path: Path) -> None:
    _prepare_root(tmp_path)

    org = build_subproject_organization(tmp_path, "CayleyPy_444_Cube")

    assert org.agent_count == 33
    assert len(org.departments) == 8
    assert org.get_agent("subproject.CayleyPy_444_Cube.commander").rank == "executive"
    assert (
        org.get_agent("subproject.CayleyPy_444_Cube.07_editorial_and_history.local_historian").shared_service
        is True
    )
