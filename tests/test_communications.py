from pathlib import Path

from workspace_orchestrator.communications import callable_targets
from workspace_orchestrator.organization import build_root_organization


def _prepare_root(tmp_path: Path) -> None:
    (tmp_path / "rules").mkdir()
    (tmp_path / "kaggle_intake").mkdir()
    (tmp_path / "workspace_orchestrator").mkdir()


def test_callable_targets_include_own_head_and_shared_services(tmp_path: Path) -> None:
    _prepare_root(tmp_path)
    org = build_root_organization(tmp_path)

    targets = callable_targets(org, "root.03_architecture_and_capability.rule_engineer")

    assert "root.03_architecture_and_capability.head" in targets
    assert "root.02_research_intelligence.global_searcher" in targets
    assert "root.02_research_intelligence.paper_scout" in targets
    assert "root.05_cross_project_analysis.pattern_synthesizer" not in targets
