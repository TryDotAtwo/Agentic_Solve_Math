from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .agent_profiles import collect_department_milestones, ensure_root_agent_profiles, profile_excerpt
from .delegation import describe_run
from .execution import load_execution_record
from .intake import find_latest_intake_file, parse_intake_file
from .openai_runtime import build_root_runtime_spec, detect_agents_sdk
from .organization import ROOT_EXECUTIVE_ID, build_root_organization
from .runtime_state import load_root_runtime_status
from .workspace import build_snapshot


ACTIVE_RUN_STATUSES = {"prepared", "running", "awaiting_result"}
COMPLETED_RUN_STATUSES = {"completed", "succeeded", "dry_run"}
FAILED_RUN_STATUSES = {"failed", "execution_failed", "timed_out", "escalated"}


@dataclass(frozen=True)
class DashboardSnapshot:
    generated_at: str
    stats: dict[str, object]
    bootstrap: dict[str, object]
    sdk: dict[str, object]
    runtime_status: dict[str, object] | None
    workspace: dict[str, object]
    latest_intake: dict[str, object] | None
    root_team: dict[str, object]
    subprojects: list[dict[str, object]]
    graph: dict[str, object]
    agents: list[dict[str, object]]
    milestones: list[dict[str, object]]
    runs: list[dict[str, object]]
    logs: dict[str, list[dict[str, object]]]
    sessions: list[dict[str, object]]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def _iso_from_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _run_updated_at(run_dir: Path) -> str:
    latest = max(path.stat().st_mtime for path in run_dir.iterdir())
    return _iso_from_timestamp(latest)


def _current_run_status(payload: dict[str, object]) -> str:
    result = payload.get("result")
    if result:
        return str(result["status"])
    execution = payload.get("execution")
    if execution:
        return str(execution["status"])
    return str(dict(payload["trace"])["status"])


def _progress_percent(status: str) -> int:
    mapping = {
        "prepared": 18,
        "running": 42,
        "awaiting_result": 76,
        "completed": 100,
        "succeeded": 100,
        "dry_run": 100,
        "failed": 100,
        "execution_failed": 100,
        "timed_out": 100,
        "escalated": 100,
    }
    return mapping.get(status, 0)


def load_dashboard_run_detail(root: Path, run_id: str) -> dict[str, object]:
    payload = describe_run(root, run_id)
    execution = load_execution_record(root, run_id)
    if execution is not None:
        payload["execution"] = execution.to_dict()
    run_dir = Path(payload["run_dir"])
    payload["updated_at"] = _run_updated_at(run_dir)
    payload["current_status"] = _current_run_status(payload)
    return payload


def _load_recent_runs(root: Path, limit: int) -> list[dict[str, object]]:
    runs_dir = root / ".agent_workspace" / "runs"
    if not runs_dir.exists():
        return []

    run_dirs = sorted(
        (path for path in runs_dir.iterdir() if path.is_dir() and path.name.startswith("run-")),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    runs: list[dict[str, object]] = []
    for run_dir in run_dirs[:limit]:
        detail = load_dashboard_run_detail(root, run_dir.name)
        handoff = dict(detail["handoff"])
        task_request = dict(handoff["task_request"])
        trace = dict(detail["trace"])
        result = dict(detail["result"]) if detail["result"] else None
        execution = dict(detail["execution"]) if detail.get("execution") else None
        current_status = str(detail["current_status"])
        runs.append(
            {
                "run_id": detail["run_id"],
                "handoff_id": handoff["handoff_id"],
                "project_name": dict(handoff["routing_decision"])["target_name"],
                "objective": task_request["objective"],
                "requester_agent_id": handoff["requester_agent_id"],
                "target_agent_id": handoff["target_agent_id"],
                "created_at": handoff["created_at"],
                "updated_at": detail["updated_at"],
                "trace_status": trace["status"],
                "execution_status": execution["status"] if execution else None,
                "result_status": result["status"] if result else None,
                "current_status": current_status,
                "progress_percent": _progress_percent(current_status),
                "artifact_count": len(trace["artifacts"]),
                "event_count": len(trace["events"]),
                "last_event": trace["events"][-1] if trace["events"] else None,
                "summary": result["summary"] if result else None,
                "artifacts": list(trace["artifacts"]),
            }
        )
    return runs


def _parse_markdown_sections(path: Path, limit: int) -> list[dict[str, object]]:
    if not path.exists():
        return []

    sections: list[dict[str, object]] = []
    title: str | None = None
    body_lines: list[str] = []

    def flush() -> None:
        nonlocal title, body_lines
        if title is None:
            return
        body = "\n".join(body_lines).strip()
        excerpt = " ".join(line.strip() for line in body.splitlines() if line.strip())
        sections.append(
            {
                "title": title,
                "excerpt": excerpt[:280] + ("..." if len(excerpt) > 280 else ""),
                "source": str(path),
            }
        )
        title = None
        body_lines = []

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("## "):
            flush()
            title = raw_line[3:].strip()
            continue
        if title is not None:
            body_lines.append(raw_line)
    flush()
    sections.reverse()
    return sections[:limit]


def _latest_intake(root: Path) -> dict[str, object] | None:
    intake_dir = root / "kaggle_intake"
    if not intake_dir.exists():
        return None
    try:
        path = find_latest_intake_file(intake_dir)
    except FileNotFoundError:
        return None
    return parse_intake_file(path).to_dict()


def _bootstrap_summary(root: Path) -> dict[str, object]:
    env_path = root / ".env"
    values = _parse_env_file(env_path)
    api_key = values.get("OPENAI_API_KEY")
    google_key = values.get("GOOGLE_API_KEY")
    gemini_key = values.get("GEMINI_API_KEY")
    base_url = values.get("OPENAI_BASE_URL", "")
    provider_route = "openai"
    if google_key or gemini_key or (api_key and api_key.startswith("AIza")) or "generativelanguage.googleapis.com" in base_url:
        provider_route = "google_openai_compatible"
    return {
        "configured": bool(api_key or google_key or gemini_key),
        "env_file_present": env_path.exists(),
        "provider_route": provider_route,
        "model_override": values.get("ASM_OPENAI_MODEL"),
    }


def _root_team_summary(root: Path) -> dict[str, object]:
    org = build_root_organization(root)
    runtime = build_root_runtime_spec(root)
    runtime_by_id = {agent.agent_id: agent for agent in runtime.agents}
    model_counts: dict[str, int] = {}
    for agent in runtime.agents:
        model_counts[agent.preferred_model] = model_counts.get(agent.preferred_model, 0) + 1

    departments = []
    for department in org.departments:
        head = runtime_by_id[department.head_agent_id]
        departments.append(
            {
                "key": department.key,
                "name": department.name,
                "path": str(department.path),
                "head_agent_id": department.head_agent_id,
                "head_display_name": head.display_name,
                "head_model": head.preferred_model,
                "staff_count": len(department.staff_agent_ids),
                "shared_service_count": len(department.shared_service_agent_ids),
                "staff_agent_ids": list(department.staff_agent_ids),
                "shared_service_agent_ids": list(department.shared_service_agent_ids),
            }
        )

    manager = runtime.get_agent(runtime.manager_agent_id)
    shared_services = [
        {
            "agent_id": agent.agent_id,
            "display_name": agent.display_name,
            "department_key": agent.department_key,
            "preferred_model": agent.preferred_model,
        }
        for agent in runtime.agents
        if agent.shared_service
    ]
    return {
        "organization_name": org.name,
        "team_id": runtime.team_id,
        "agent_count": org.agent_count,
        "department_count": len(org.departments),
        "manager": {
            "agent_id": manager.agent_id,
            "display_name": manager.display_name,
            "preferred_model": manager.preferred_model,
            "model_rationale": manager.model_rationale,
        },
        "model_counts": model_counts,
        "departments": departments,
        "shared_services": shared_services,
    }


def _agent_rank_order(rank: str) -> int:
    return {"executive": 0, "head": 1, "staff": 2}.get(rank, 99)


def _root_graph_and_dossiers(root: Path) -> tuple[dict[str, object], list[dict[str, object]]]:
    org = build_root_organization(root)
    runtime = build_root_runtime_spec(root)
    profiles = ensure_root_agent_profiles(root)
    runtime_by_id = {agent.agent_id: agent for agent in runtime.agents}
    by_id = {agent.agent_id: agent for agent in org.agents}

    nodes: list[dict[str, object]] = []
    dossiers: list[dict[str, object]] = []
    edges: list[dict[str, object]] = []
    call_edges: list[dict[str, object]] = []

    for manifest in sorted(org.agents, key=lambda item: (_agent_rank_order(item.rank), item.department_key, item.agent_id)):
        runtime_agent = runtime_by_id[manifest.agent_id]
        profile = profiles[manifest.agent_id]
        nodes.append(
            {
                "id": manifest.agent_id,
                "label": manifest.display_name,
                "department_key": manifest.department_key,
                "rank": manifest.rank,
                "shared_service": manifest.shared_service,
                "model": runtime_agent.preferred_model,
                "callable_count": len(manifest.callable_agents),
            }
        )
        dossiers.append(
            {
                "agent_id": manifest.agent_id,
                "display_name": manifest.display_name,
                "department_key": manifest.department_key,
                "rank": manifest.rank,
                "scope": manifest.scope,
                "shared_service": manifest.shared_service,
                "preferred_model": runtime_agent.preferred_model,
                "model_rationale": runtime_agent.model_rationale,
                "allowed_tools": list(manifest.allowed_tools),
                "callable_agents": list(manifest.callable_agents),
                "shared_service_agents": list(manifest.shared_service_agents),
                "read_roots": [str(item) for item in manifest.read_roots],
                "write_roots": [str(item) for item in manifest.write_roots],
                "memory_path": str(profile.memory_file),
                "instructions_path": str(profile.instructions_file),
                "rules_path": str(profile.rules_file),
                "reports_path": str(profile.reports_file),
                "memory_excerpt": profile_excerpt(profile.memory_file),
                "instructions_excerpt": profile_excerpt(profile.instructions_file),
                "rules_excerpt": profile_excerpt(profile.rules_file),
                "reports_excerpt": profile_excerpt(profile.reports_file),
            }
        )

    for department in org.departments:
        edges.append(
            {
                "source": ROOT_EXECUTIVE_ID,
                "target": department.head_agent_id,
                "kind": "executive_to_head",
            }
        )
        for staff_agent_id in department.staff_agent_ids:
            edges.append(
                {
                    "source": department.head_agent_id,
                    "target": staff_agent_id,
                    "kind": "head_to_staff",
                }
            )
        for shared_agent_id in department.shared_service_agent_ids:
            if shared_agent_id in department.staff_agent_ids:
                edges.append(
                    {
                        "source": department.head_agent_id,
                        "target": shared_agent_id,
                        "kind": "head_to_shared_service",
                    }
                )

    for manifest in org.agents:
        for target_id in manifest.callable_agents:
            if target_id not in by_id:
                continue
            call_edges.append(
                {
                    "source": manifest.agent_id,
                    "target": target_id,
                    "kind": "callable_link",
                }
            )

    return (
        {
            "nodes": nodes,
            "edges": edges,
            "call_edges": call_edges,
        },
        dossiers,
    )


def _session_files(root: Path) -> list[dict[str, object]]:
    sessions_dir = root / ".agent_workspace" / "sessions"
    if not sessions_dir.exists():
        return []
    files = []
    for path in sorted(sessions_dir.glob("*.sqlite")):
        stat = path.stat()
        files.append(
            {
                "name": path.name,
                "path": str(path),
                "size_bytes": stat.st_size,
                "modified_at": _iso_from_timestamp(stat.st_mtime),
            }
        )
    return files


def build_dashboard_snapshot(root: Path, run_limit: int = 12, log_limit: int = 8) -> DashboardSnapshot:
    root = root.resolve()
    snapshot = build_snapshot(root)
    runs = _load_recent_runs(root, limit=run_limit)
    graph, agents = _root_graph_and_dossiers(root)
    statuses = [item["current_status"] for item in runs]
    runtime_status = load_root_runtime_status(root)
    sessions = _session_files(root)
    return DashboardSnapshot(
        generated_at=_iso_from_timestamp(datetime.now(tz=timezone.utc).timestamp()),
        stats={
            "subprojects_total": len(snapshot.subprojects),
            "runs_total": len(runs),
            "runs_active": sum(status in ACTIVE_RUN_STATUSES for status in statuses),
            "runs_completed": sum(status in COMPLETED_RUN_STATUSES for status in statuses),
            "runs_failed": sum(status in FAILED_RUN_STATUSES for status in statuses),
            "sessions_total": len(sessions),
            "root_agents": 25,
        },
        bootstrap=_bootstrap_summary(root),
        sdk=detect_agents_sdk().to_dict(),
        runtime_status=runtime_status.to_dict() if runtime_status else None,
        workspace=snapshot.to_dict(),
        latest_intake=_latest_intake(root),
        root_team=_root_team_summary(root),
        subprojects=[item.to_dict() for item in snapshot.subprojects],
        graph=graph,
        agents=agents,
        milestones=collect_department_milestones(root, limit=log_limit),
        runs=runs,
        logs={
            "research_journal": _parse_markdown_sections(root / "rules" / "logs" / "RESEARCH_JOURNAL.md", log_limit),
            "agent_interactions": _parse_markdown_sections(
                root / "rules" / "logs" / "AGENT_INTERACTIONS_LOG.md",
                log_limit,
            ),
            "user_prompts": _parse_markdown_sections(root / "rules" / "logs" / "USER_PROMPTS_LOG.md", log_limit),
        },
        sessions=sessions,
    )
