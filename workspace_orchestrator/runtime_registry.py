from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExecutionProfile:
    project_name: str
    mode: str
    default_args: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)


def get_execution_profile(project_name: str) -> ExecutionProfile:
    if project_name == "CayleyPy_444_Cube":
        return ExecutionProfile(
            project_name=project_name,
            mode="legacy",
            default_args=("--no-submit",),
            notes=(
                "Project-local main.py is not yet root-handoff aware.",
                "Default launch is safety-biased and disables Kaggle submit.",
            ),
        )
    return ExecutionProfile(
        project_name=project_name,
        mode="protocol_v1",
        notes=("Launch via root-handoff protocol flags.",),
    )
