from __future__ import annotations

from pathlib import Path

from .models import SubprojectInfo, WorkspaceSnapshot


ROOT_EXCLUDE_DIRS = {
    ".cursor",
    ".git",
    "__pycache__",
    "kaggle_intake",
    "rules",
    "tests",
    "workspace_orchestrator",
}


def infer_role(name: str) -> str:
    if name == "Math_Hypothese_AutoCheck_Witch_Agents":
        return "math-research"
    if name == "CayleyPy_Pancake":
        return "engineering-reference"
    if name.startswith("CayleyPy_"):
        return "kaggle-subproject"
    return "generic-subproject"


def discover_subprojects(root: Path) -> list[SubprojectInfo]:
    subprojects: list[SubprojectInfo] = []
    for path in sorted(root.iterdir(), key=lambda item: item.name.lower()):
        if not path.is_dir():
            continue
        if (
            path.name in ROOT_EXCLUDE_DIRS
            or path.name.startswith(".")
            or path.name.startswith("pytest-cache-files-")
        ):
            continue

        has_readme = (path / "README.md").exists()
        has_agents = (path / "AGENTS.md").exists()
        has_main = (path / "main.py").exists()

        if not (has_readme or has_agents or has_main or path.name.startswith("CayleyPy_")):
            continue

        subprojects.append(
            SubprojectInfo(
                name=path.name,
                path=path,
                role=infer_role(path.name),
                has_readme=has_readme,
                has_agents=has_agents,
                has_main=has_main,
                isolated=True,
            )
        )
    return subprojects


def build_snapshot(root: Path) -> WorkspaceSnapshot:
    return WorkspaceSnapshot(
        root=root,
        rules_dir=root / "rules",
        intake_dir=root / "kaggle_intake",
        subprojects=discover_subprojects(root),
    )
