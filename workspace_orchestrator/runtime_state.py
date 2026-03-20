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
    provider_id: str | None = None
    provider_route: str | None = None
    session_db_path: str | None = None
    finished_at: str | None = None
    intake_file: str | None = None
    prompt_excerpt: str | None = None
    final_output_excerpt: str | None = None
    error: str | None = None
    active_scope: str | None = None
    active_team_id: str | None = None
    active_project_name: str | None = None
    active_run_id: str | None = None
    active_agent_id: str | None = None
    active_agent_name: str | None = None
    active_department_key: str | None = None
    current_phase: str | None = None
    last_event_type: str | None = None
    last_event_summary: str | None = None
    last_event_at: str | None = None
    event_count: int = 0

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
            provider_id=str(data["provider_id"]) if data.get("provider_id") is not None else None,
            provider_route=str(data["provider_route"]) if data.get("provider_route") is not None else None,
            session_db_path=str(data["session_db_path"]) if data.get("session_db_path") is not None else None,
            finished_at=str(data["finished_at"]) if data.get("finished_at") is not None else None,
            intake_file=str(data["intake_file"]) if data.get("intake_file") is not None else None,
            prompt_excerpt=str(data["prompt_excerpt"]) if data.get("prompt_excerpt") is not None else None,
            final_output_excerpt=(
                str(data["final_output_excerpt"]) if data.get("final_output_excerpt") is not None else None
            ),
            error=str(data["error"]) if data.get("error") is not None else None,
            active_scope=str(data["active_scope"]) if data.get("active_scope") is not None else None,
            active_team_id=str(data["active_team_id"]) if data.get("active_team_id") is not None else None,
            active_project_name=(
                str(data["active_project_name"]) if data.get("active_project_name") is not None else None
            ),
            active_run_id=str(data["active_run_id"]) if data.get("active_run_id") is not None else None,
            active_agent_id=str(data["active_agent_id"]) if data.get("active_agent_id") is not None else None,
            active_agent_name=str(data["active_agent_name"]) if data.get("active_agent_name") is not None else None,
            active_department_key=(
                str(data["active_department_key"]) if data.get("active_department_key") is not None else None
            ),
            current_phase=str(data["current_phase"]) if data.get("current_phase") is not None else None,
            last_event_type=str(data["last_event_type"]) if data.get("last_event_type") is not None else None,
            last_event_summary=(
                str(data["last_event_summary"]) if data.get("last_event_summary") is not None else None
            ),
            last_event_at=str(data["last_event_at"]) if data.get("last_event_at") is not None else None,
            event_count=int(data.get("event_count", 0) or 0),
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
    provider_id: str | None = None,
    provider_route: str | None = None,
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
        provider_id=provider_id,
        provider_route=provider_route,
        intake_file=intake_file,
        prompt_excerpt=_excerpt(prompt),
        active_scope="root",
        active_team_id=team_id,
        active_agent_id=entry_agent_id,
        current_phase="root_launch",
    )
    write_json(root_runtime_status_path(root), status.to_dict())
    return status


def update_root_runtime_status(
    root: Path,
    *,
    status: str | None = None,
    model: str | None = None,
    session_db_path: str | None = None,
    finished_at: str | None = None,
    intake_file: str | None = None,
    prompt: str | None = None,
    final_output: str | None = None,
    error: str | None = None,
    active_scope: str | None = None,
    active_team_id: str | None = None,
    active_project_name: str | None = None,
    active_run_id: str | None = None,
    active_agent_id: str | None = None,
    active_agent_name: str | None = None,
    active_department_key: str | None = None,
    current_phase: str | None = None,
    last_event_type: str | None = None,
    last_event_summary: str | None = None,
    last_event_at: str | None = None,
    event_count: int | None = None,
) -> RootRuntimeStatus | None:
    current = load_root_runtime_status(root)
    if current is None:
        return None

    updated = RootRuntimeStatus(
        status=status or current.status,
        team_id=current.team_id,
        entry_agent_id=current.entry_agent_id,
        model=model or current.model,
        session_id=current.session_id,
        started_at=current.started_at,
        updated_at=utc_now_iso(),
        provider_id=current.provider_id,
        provider_route=current.provider_route,
        session_db_path=session_db_path if session_db_path is not None else current.session_db_path,
        finished_at=finished_at if finished_at is not None else current.finished_at,
        intake_file=intake_file if intake_file is not None else current.intake_file,
        prompt_excerpt=_excerpt(prompt) if prompt is not None else current.prompt_excerpt,
        final_output_excerpt=(
            _excerpt(final_output) if final_output is not None else current.final_output_excerpt
        ),
        error=_excerpt(error) if error is not None else current.error,
        active_scope=active_scope if active_scope is not None else current.active_scope,
        active_team_id=active_team_id if active_team_id is not None else current.active_team_id,
        active_project_name=(
            active_project_name if active_project_name is not None else current.active_project_name
        ),
        active_run_id=active_run_id if active_run_id is not None else current.active_run_id,
        active_agent_id=active_agent_id if active_agent_id is not None else current.active_agent_id,
        active_agent_name=active_agent_name if active_agent_name is not None else current.active_agent_name,
        active_department_key=(
            active_department_key if active_department_key is not None else current.active_department_key
        ),
        current_phase=current_phase if current_phase is not None else current.current_phase,
        last_event_type=last_event_type if last_event_type is not None else current.last_event_type,
        last_event_summary=(
            last_event_summary if last_event_summary is not None else current.last_event_summary
        ),
        last_event_at=last_event_at if last_event_at is not None else current.last_event_at,
        event_count=event_count if event_count is not None else current.event_count,
    )
    write_json(root_runtime_status_path(root), updated.to_dict())
    return updated


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
    provider_id: str | None = None,
    provider_route: str | None = None,
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
        provider_id=provider_id if provider_id is not None else (current.provider_id if current else None),
        provider_route=(
            provider_route if provider_route is not None else (current.provider_route if current else None)
        ),
        session_db_path=session_db_path,
        finished_at=now,
        intake_file=intake_file,
        prompt_excerpt=_excerpt(prompt),
        final_output_excerpt=_excerpt(final_output),
        error=_excerpt(error),
        active_scope=current.active_scope if current is not None else "root",
        active_team_id=current.active_team_id if current is not None else team_id,
        active_project_name=current.active_project_name if current is not None else None,
        active_run_id=current.active_run_id if current is not None else None,
        active_agent_id=current.active_agent_id if current is not None else entry_agent_id,
        active_agent_name=current.active_agent_name if current is not None else None,
        active_department_key=current.active_department_key if current is not None else None,
        current_phase="failed" if error else "completed",
        last_event_type=current.last_event_type if current is not None else None,
        last_event_summary=current.last_event_summary if current is not None else None,
        last_event_at=current.last_event_at if current is not None else now,
        event_count=current.event_count if current is not None else 0,
    )
    write_json(root_runtime_status_path(root), status.to_dict())
    return status
