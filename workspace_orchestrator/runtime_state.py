from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .runs import read_json, utc_now_iso, write_json


ROOT_RUNTIME_STATUS_FILENAME = "root_runtime_status.json"


@dataclass(frozen=True)
class RootRuntimeStatus:
    status: str
    team_id: str
    entry_agent_id: str
    model: str
    session_id: str
    started_at: str
    updated_at: str
    session_db_path: str | None = None
    finished_at: str | None = None
    intake_file: str | None = None
    prompt_excerpt: str | None = None
    final_output_excerpt: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RootRuntimeStatus":
        return cls(
            status=str(data["status"]),
            team_id=str(data["team_id"]),
            entry_agent_id=str(data["entry_agent_id"]),
            model=str(data["model"]),
            session_id=str(data["session_id"]),
            started_at=str(data["started_at"]),
            updated_at=str(data["updated_at"]),
            session_db_path=str(data["session_db_path"]) if data.get("session_db_path") is not None else None,
            finished_at=str(data["finished_at"]) if data.get("finished_at") is not None else None,
            intake_file=str(data["intake_file"]) if data.get("intake_file") is not None else None,
            prompt_excerpt=str(data["prompt_excerpt"]) if data.get("prompt_excerpt") is not None else None,
            final_output_excerpt=(
                str(data["final_output_excerpt"]) if data.get("final_output_excerpt") is not None else None
            ),
            error=str(data["error"]) if data.get("error") is not None else None,
        )


def _runtime_dir(root: Path) -> Path:
    path = root / ".agent_workspace" / "runtime"
    path.mkdir(parents=True, exist_ok=True)
    return path


def root_runtime_status_path(root: Path) -> Path:
    return _runtime_dir(root) / ROOT_RUNTIME_STATUS_FILENAME


def load_root_runtime_status(root: Path) -> RootRuntimeStatus | None:
    path = root_runtime_status_path(root)
    if not path.exists():
        return None
    return RootRuntimeStatus.from_dict(read_json(path))


def _excerpt(text: str | None, limit: int = 600) -> str | None:
    if text is None:
        return None
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 3]}..."


def begin_root_runtime_status(
    root: Path,
    *,
    team_id: str,
    entry_agent_id: str,
    model: str,
    session_id: str,
    intake_file: str | None,
    prompt: str | None,
) -> RootRuntimeStatus:
    now = utc_now_iso()
    status = RootRuntimeStatus(
        status="running",
        team_id=team_id,
        entry_agent_id=entry_agent_id,
        model=model,
        session_id=session_id,
        started_at=now,
        updated_at=now,
        intake_file=intake_file,
        prompt_excerpt=_excerpt(prompt),
    )
    write_json(root_runtime_status_path(root), status.to_dict())
    return status


def finalize_root_runtime_status(
    root: Path,
    *,
    team_id: str,
    entry_agent_id: str,
    model: str,
    session_id: str,
    session_db_path: str | None,
    intake_file: str | None,
    prompt: str | None,
    final_output: str | None = None,
    error: str | None = None,
) -> RootRuntimeStatus:
    current = load_root_runtime_status(root)
    started_at = current.started_at if current is not None else utc_now_iso()
    now = utc_now_iso()
    status = RootRuntimeStatus(
        status="failed" if error else "succeeded",
        team_id=team_id,
        entry_agent_id=entry_agent_id,
        model=model,
        session_id=session_id,
        started_at=started_at,
        updated_at=now,
        session_db_path=session_db_path,
        finished_at=now,
        intake_file=intake_file,
        prompt_excerpt=_excerpt(prompt),
        final_output_excerpt=_excerpt(final_output),
        error=_excerpt(error),
    )
    write_json(root_runtime_status_path(root), status.to_dict())
    return status
