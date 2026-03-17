from pathlib import Path

from workspace_orchestrator.organization import build_root_organization, build_subproject_organization
from workspace_orchestrator.visibility import can_read_path, can_write_path


def _prepare_root(tmp_path: Path) -> None:
    (tmp_path / "rules" / "logs").mkdir(parents=True)
    (tmp_path / "rules" / "organization").mkdir(parents=True)
    (tmp_path / "kaggle_intake").mkdir()
    (tmp_path / "workspace_orchestrator").mkdir()
    (tmp_path / "CayleyPy_444_Cube" / "docs").mkdir(parents=True)
    (tmp_path / ".agent_workspace" / "root" / "06_editorial_and_history").mkdir(parents=True)
    (tmp_path / "CayleyPy_444_Cube" / ".agent_workspace" / "01_source_intelligence").mkdir(parents=True)


def test_root_staff_cannot_read_subproject_internal_paths(tmp_path: Path) -> None:
    _prepare_root(tmp_path)
    org = build_root_organization(tmp_path)
    article_drafter = org.get_agent("root.06_editorial_and_history.article_drafter")

    assert can_read_path(article_drafter, tmp_path / "rules" / "logs" / "RESEARCH_JOURNAL.md") is True
    assert can_read_path(article_drafter, tmp_path / "CayleyPy_444_Cube" / "docs" / "local_note.md") is False


def test_subproject_staff_can_read_subproject_but_not_root_rules(tmp_path: Path) -> None:
    _prepare_root(tmp_path)
    org = build_subproject_organization(tmp_path, "CayleyPy_444_Cube")
    researcher = org.get_agent("subproject.CayleyPy_444_Cube.01_source_intelligence.web_researcher")

    assert can_read_path(researcher, tmp_path / "CayleyPy_444_Cube" / "docs" / "report.md") is True
    assert can_read_path(researcher, tmp_path / "rules" / "organization" / "README.md") is False


def test_write_scope_is_limited_to_allowed_roots(tmp_path: Path) -> None:
    _prepare_root(tmp_path)
    root_org = build_root_organization(tmp_path)
    sub_org = build_subproject_organization(tmp_path, "CayleyPy_444_Cube")

    history = root_org.get_agent("root.06_editorial_and_history.history_scribe")
    researcher = sub_org.get_agent("subproject.CayleyPy_444_Cube.01_source_intelligence.web_researcher")

    assert can_write_path(history, tmp_path / "rules" / "logs" / "session.md") is True
    assert can_write_path(history, tmp_path / "workspace_orchestrator" / "cli.py") is False
    assert (
        can_write_path(
            researcher,
            tmp_path / "CayleyPy_444_Cube" / ".agent_workspace" / "01_source_intelligence" / "scan.json",
        )
        is True
    )
    assert can_write_path(researcher, tmp_path / "rules" / "logs" / "session.md") is False
