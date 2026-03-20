from pathlib import Path

from workspace_orchestrator.agent_profiles import append_department_milestone, ensure_root_agent_profiles


def _prepare_root(tmp_path: Path) -> Path:
    (tmp_path / "rules").mkdir()
    (tmp_path / "kaggle_intake").mkdir()
    (tmp_path / "workspace_orchestrator").mkdir()
    (tmp_path / "CayleyPy_444_Cube").mkdir()
    return tmp_path


def test_ensure_root_agent_profiles_materializes_memory_instruction_rule_files(tmp_path: Path) -> None:
    root = _prepare_root(tmp_path)

    profiles = ensure_root_agent_profiles(root)
    profile = profiles["root.03_architecture_and_capability.rule_engineer"]

    assert profile.memory_file.exists()
    assert profile.instructions_file.exists()
    assert profile.rules_file.exists()
    assert profile.reports_file.exists()
    assert "Rule Engineer" in profile.instructions_file.read_text(encoding="utf-8")
    assert "Hierarchy" in profile.rules_file.read_text(encoding="utf-8")


def test_append_department_milestone_writes_head_report_section(tmp_path: Path) -> None:
    root = _prepare_root(tmp_path)
    profiles = ensure_root_agent_profiles(root)

    report_path = append_department_milestone(
        root,
        "root.02_research_intelligence.head",
        title="Collected baseline evidence",
        summary="Initial source scan and paper triage are complete.",
        next_actions=("Escalate best sources to orchestrator", "Prepare handoff brief"),
    )

    text = report_path.read_text(encoding="utf-8")
    assert report_path == profiles["root.02_research_intelligence.head"].reports_file
    assert "Collected baseline evidence" in text
    assert "Prepare handoff brief" in text
