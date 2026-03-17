from __future__ import annotations

import json
import re
from pathlib import Path

from .runs import ensure_run_dir, read_json, utc_now_iso, write_json


LOG_SYNC_FILENAME = "log_sync_state.json"


def _logs_dir(root: Path) -> Path:
    return root / "rules" / "logs"


def _ensure_log_file(path: Path, title: str) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {title}\n", encoding="utf-8")


def _append_markdown(path: Path, content: str) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    separator = "\n\n" if current and not current.endswith("\n\n") else ""
    path.write_text(f"{current}{separator}{content.rstrip()}\n", encoding="utf-8")


def _sync_state_path(root: Path, run_id: str) -> Path:
    return ensure_run_dir(root, run_id) / LOG_SYNC_FILENAME


def _load_synced_events(root: Path, run_id: str) -> set[str]:
    path = _sync_state_path(root, run_id)
    if not path.exists():
        return set()
    data = read_json(path)
    return set(data.get("events", ()))


def _save_synced_events(root: Path, run_id: str, events: set[str]) -> None:
    write_json(_sync_state_path(root, run_id), {"events": sorted(events)})


def _next_interaction_number(path: Path) -> int:
    if not path.exists():
        return 1
    text = path.read_text(encoding="utf-8")
    matches = [int(item) for item in re.findall(r"## \d{4}-\d{2}-\d{2} \| Interaction (\d+)", text)]
    return (max(matches) + 1) if matches else 1


def _journal_entry(run_payload: dict[str, object], event_key: str) -> str:
    handoff = dict(run_payload["handoff"])
    trace = dict(run_payload["trace"])
    result = run_payload["result"]
    run_id = str(run_payload["run_id"])
    objective = str(dict(handoff["task_request"])["objective"])
    target = str(handoff["target_agent_id"])
    requester = str(handoff["requester_agent_id"])
    project_name = str(dict(handoff["routing_decision"])["target_name"])

    lines = [
        f"## {utc_now_iso()[:10]} | Automated run sync | {run_id} | {event_key}",
        "",
        "### Context",
        "",
        f"- Project: `{project_name}`",
        f"- Target agent: `{target}`",
        f"- Requester: `{requester}`",
        f"- Objective: {objective}",
        "",
        "### Trace snapshot",
        "",
        f"- Status: `{trace['status']}`",
        f"- Events: {', '.join(trace['events']) if trace['events'] else '-'}",
        f"- Artifacts: {', '.join(trace['artifacts']) if trace['artifacts'] else '-'}",
    ]
    execution = run_payload.get("execution")
    if execution:
        execution = dict(execution)
        lines.extend(
            [
                "",
                "### Execution snapshot",
                "",
                f"- Mode: `{execution['mode']}`",
                f"- Status: `{execution['status']}`",
                f"- Command: `{' '.join(execution['command'])}`",
            ]
        )
        if execution.get("exit_code") is not None:
            lines.append(f"- Exit code: `{execution['exit_code']}`")
    if result:
        result = dict(result)
        lines.extend(
            [
                "",
                "### Result snapshot",
                "",
                f"- Produced by: `{result['produced_by']}`",
                f"- Status: `{result['status']}`",
                f"- Summary: {result['summary']}",
            ]
        )
    return "\n".join(lines)


def _interaction_entry(run_payload: dict[str, object], event_key: str, interaction_number: int) -> str:
    handoff = dict(run_payload["handoff"])
    trace = dict(run_payload["trace"])
    result = run_payload["result"]
    run_id = str(run_payload["run_id"])
    project_name = str(dict(handoff["routing_decision"])["target_name"])

    lines = [
        f"## {utc_now_iso()[:10]} | Interaction {interaction_number} - Automated run sync for {run_id} | {event_key}",
        "",
        "### Participants",
        "",
        "- Root orchestrator",
        f"- Target runtime: `{project_name}/main.py`",
        f"- Target agent: `{handoff['target_agent_id']}`",
        "",
        "### Context",
        "",
        f"- Root synchronized the current run lifecycle state for `{run_id}`.",
        f"- Current trace status: `{trace['status']}`.",
        "",
        "### Messages / decisions",
        "",
        f"- Event key: `{event_key}`",
        f"- Known artifacts: {', '.join(trace['artifacts']) if trace['artifacts'] else '-'}",
    ]
    execution = run_payload.get("execution")
    if execution:
        execution = dict(execution)
        lines.append(f"- Execution mode/status: `{execution['mode']}` / `{execution['status']}`")
    if result:
        result = dict(result)
        lines.append(f"- Result summary: {result['summary']}")
    lines.extend(
        [
            "",
            "### Outcomes",
            "",
            f"- Root logs updated for `{run_id}`.",
            f"- Trace remains canonical in `.agent_workspace/runs/{run_id}/trace.json`.",
        ]
    )
    return "\n".join(lines)


def sync_run_logs(root: Path, run_id: str, category: str) -> bool:
    root = root.resolve()
    from .delegation import describe_run
    from .execution import load_execution_record

    payload = describe_run(root, run_id)
    execution = load_execution_record(root, run_id)
    if execution is not None:
        payload["execution"] = execution.to_dict()

    status_source = payload["result"] if category == "result" else payload.get("execution")
    if not status_source:
        return False

    event_key = f"{category}:{status_source['status']}"
    synced = _load_synced_events(root, run_id)
    if event_key in synced:
        return False

    logs_dir = _logs_dir(root)
    journal_path = logs_dir / "RESEARCH_JOURNAL.md"
    interactions_path = logs_dir / "AGENT_INTERACTIONS_LOG.md"
    _ensure_log_file(journal_path, "Research Journal")
    _ensure_log_file(interactions_path, "Agent Interactions Log")

    _append_markdown(journal_path, _journal_entry(payload, event_key))
    interaction_number = _next_interaction_number(interactions_path)
    _append_markdown(interactions_path, _interaction_entry(payload, event_key, interaction_number))

    synced.add(event_key)
    _save_synced_events(root, run_id, synced)
    return True
