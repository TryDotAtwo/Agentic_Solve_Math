from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SubprojectInfo:
    name: str
    path: Path
    role: str
    has_readme: bool
    has_agents: bool
    has_main: bool
    isolated: bool = True

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["path"] = str(self.path)
        return data


@dataclass(frozen=True)
class IntakeBrief:
    source_file: Path
    competition_links: list[str] = field(default_factory=list)
    notebook_links: list[str] = field(default_factory=list)
    discussion_links: list[str] = field(default_factory=list)
    paper_links: list[str] = field(default_factory=list)
    repo_links: list[str] = field(default_factory=list)
    other_links: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["source_file"] = str(self.source_file)
        return data


@dataclass(frozen=True)
class WorkspaceSnapshot:
    root: Path
    rules_dir: Path
    intake_dir: Path
    subprojects: list[SubprojectInfo]

    def to_dict(self) -> dict[str, object]:
        return {
            "root": str(self.root),
            "rules_dir": str(self.rules_dir),
            "intake_dir": str(self.intake_dir),
            "subprojects": [item.to_dict() for item in self.subprojects],
        }
