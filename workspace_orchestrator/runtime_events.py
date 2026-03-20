from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from uuid import uuid4

from .runs import utc_now_iso


ROOT_RUNTIME_EVENTS_FILENAME = "root_runtime_events.jsonl"

_DIALOGUE_EVENT_TYPES = frozenset(
    {
        "agent_started",
        "agent_message",
        "handoff",
        "tool_called",
        "tool_output",
        "milestone_recorded",
        "subproject_result_recorded",
    }
)


@dataclass(frozen=True)
class RuntimeEvent:
    event_id: str
    created_at: str
    event_type: str
    title: str
    summary: str
    scope: str
    session_id: str
    team_id: str | None = None
    run_id: str | None = None
    project_name: str | None = None
    agent_id: str | None = None
    agent_name: str | None = None
    department_key: str | None = None
    target_agent_id: str | None = None
    target_agent_name: str | None = None
    tool_name: str | None = None
    transcript: str | None = None
    phase: str | None = None
    details: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "RuntimeEvent":
        details = payload.get("details")
        return cls(
            event_id=str(payload["event_id"]),
            created_at=str(payload["created_at"]),
            event_type=str(payload["event_type"]),
            title=str(payload["title"]),
            summary=str(payload["summary"]),
            scope=str(payload["scope"]),
            session_id=str(payload.get("session_id") or "unknown"),
            team_id=str(payload["team_id"]) if payload.get("team_id") is not None else None,
            run_id=str(payload["run_id"]) if payload.get("run_id") is not None else None,
            project_name=str(payload["project_name"]) if payload.get("project_name") is not None else None,
            agent_id=str(payload["agent_id"]) if payload.get("agent_id") is not None else None,
            agent_name=str(payload["agent_name"]) if payload.get("agent_name") is not None else None,
            department_key=str(payload["department_key"]) if payload.get("department_key") is not None else None,
            target_agent_id=(
                str(payload["target_agent_id"]) if payload.get("target_agent_id") is not None else None
            ),
            target_agent_name=(
                str(payload["target_agent_name"]) if payload.get("target_agent_name") is not None else None
            ),
            tool_name=str(payload["tool_name"]) if payload.get("tool_name") is not None else None,
            transcript=str(payload["transcript"]) if payload.get("transcript") is not None else None,
            phase=str(payload["phase"]) if payload.get("phase") is not None else None,
            details=dict(details) if isinstance(details, dict) else {},
        )


def runtime_events_path(root: Path) -> Path:
    runtime_dir = root / ".agent_workspace" / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    return runtime_dir / ROOT_RUNTIME_EVENTS_FILENAME


def append_runtime_event(
    root: Path,
    *,
    event_type: str,
    title: str,
    summary: str,
    scope: str,
    session_id: str,
    team_id: str | None = None,
    run_id: str | None = None,
    project_name: str | None = None,
    agent_id: str | None = None,
    agent_name: str | None = None,
    department_key: str | None = None,
    target_agent_id: str | None = None,
    target_agent_name: str | None = None,
    tool_name: str | None = None,
    transcript: str | None = None,
    phase: str | None = None,
    details: dict[str, object] | None = None,
) -> RuntimeEvent:
    event = RuntimeEvent(
        event_id=f"evt-{uuid4().hex[:12]}",
        created_at=utc_now_iso(),
        event_type=event_type,
        title=title,
        summary=summary,
        scope=scope,
        session_id=session_id,
        team_id=team_id,
        run_id=run_id,
        project_name=project_name,
        agent_id=agent_id,
        agent_name=agent_name,
        department_key=department_key,
        target_agent_id=target_agent_id,
        target_agent_name=target_agent_name,
        tool_name=tool_name,
        transcript=transcript,
        phase=phase,
        details=dict(details or {}),
    )
    path = runtime_events_path(root)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
    return event


def load_runtime_events(root: Path, limit: int = 60) -> list[RuntimeEvent]:
    path = runtime_events_path(root)
    if not path.exists():
        return []

    events: list[RuntimeEvent] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            events.append(RuntimeEvent.from_dict(payload))
    return events[-limit:]


def build_dialogue_feed(root: Path, limit: int = 30) -> list[dict[str, object]]:
    dialogue_events = [
        event
        for event in load_runtime_events(root, limit=max(limit * 3, 60))
        if event.event_type in _DIALOGUE_EVENT_TYPES
    ]
    dialogue_events = dialogue_events[-limit:]
    return [event.to_dict() for event in reversed(dialogue_events)]
