from pathlib import Path

from workspace_orchestrator.workspace import build_snapshot


def test_build_snapshot_discovers_isolated_subprojects(tmp_path: Path) -> None:
    (tmp_path / "rules").mkdir()
    (tmp_path / "kaggle_intake").mkdir()

    pancake = tmp_path / "CayleyPy_Pancake"
    pancake.mkdir()
    (pancake / "README.md").write_text("# Pancake", encoding="utf-8")
    (pancake / "main.py").write_text("print('ok')", encoding="utf-8")

    math = tmp_path / "Math_Hypothese_AutoCheck_Witch_Agents"
    math.mkdir()
    (math / "AGENTS.md").write_text("# Agents", encoding="utf-8")

    snapshot = build_snapshot(tmp_path)
    names = [item.name for item in snapshot.subprojects]

    assert "CayleyPy_Pancake" in names
    assert "Math_Hypothese_AutoCheck_Witch_Agents" in names
