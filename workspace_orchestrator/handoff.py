from __future__ import annotations

from pathlib import Path

from .contracts import HandoffPackage, ResearchPlan, RoutingDecision, RunTrace, TaskRequest
from .intake import IntakeBrief
from .organization import build_subproject_organization
from .runs import create_run_id, ensure_run_dir, utc_now_iso, write_json


def build_task_request_from_intake(
    brief: IntakeBrief,
    objective: str,
    task_id: str | None = None,
    requested_by: str = "root.orchestrator",
    source: str = "intake_file",
    task_type: str = "kaggle_research",
) -> TaskRequest:
    return TaskRequest(
        task_id=task_id or create_run_id("task"),
        task_type=task_type,
        source=source,
        objective=objective,
        requested_by=requested_by,
        intake_file=brief.source_file,
        competition_links=tuple(brief.competition_links),
        priorities=tuple(brief.priorities),
        notes=tuple(brief.notes),
    )


def default_research_plan(
    objective: str,
    plan_id: str | None = None,
    research_questions: tuple[str, ...] = (),
) -> ResearchPlan:
    questions = research_questions or (objective,)
    return ResearchPlan(
        plan_id=plan_id or create_run_id("plan"),
        research_questions=questions,
        deliverables=("research_summary", "handoff_package"),
        evidence_requirements=("official_competition_materials", "paper_and_repo_scan"),
        stop_conditions=("escalate_on_policy_boundary", "escalate_on_missing_context"),
    )


def build_handoff_for_subproject(
    root: Path,
    project_name: str,
    task_request: TaskRequest,
    research_plan: ResearchPlan,
    requester_agent_id: str,
    run_id: str | None = None,
    handoff_id: str | None = None,
) -> HandoffPackage:
    org = build_subproject_organization(root, project_name)
    target = org.get_agent(f"subproject.{project_name}.commander")
    decision = RoutingDecision(
        target_kind="existing_subproject",
        target_name=project_name,
        target_agent_id=target.agent_id,
        reason="Explicit subproject handoff",
    )
    return HandoffPackage(
        handoff_id=handoff_id or create_run_id("handoff"),
        run_id=run_id or create_run_id("run"),
        created_at=utc_now_iso(),
        requester_agent_id=requester_agent_id,
        target_agent_id=target.agent_id,
        task_request=task_request,
        routing_decision=decision,
        research_plan=research_plan,
        target_read_roots=tuple(str(item) for item in target.read_roots),
        target_write_roots=tuple(str(item) for item in target.write_roots),
        allowed_tools=target.allowed_tools,
        callable_agents=target.callable_agents,
        shared_service_agents=target.shared_service_agents,
    )


def materialize_handoff_package(root: Path, package: HandoffPackage) -> Path:
    run_dir = ensure_run_dir(root, package.run_id)
    write_json(run_dir / "handoff.json", package.to_dict())
    write_json(run_dir / "task_request.json", package.task_request.to_dict())
    write_json(run_dir / "routing_decision.json", package.routing_decision.to_dict())
    write_json(run_dir / "research_plan.json", package.research_plan.to_dict())
    trace = RunTrace(
        run_id=package.run_id,
        handoff_id=package.handoff_id,
        status="prepared",
        target_agent_id=package.target_agent_id,
        artifacts=("handoff.json", "task_request.json", "routing_decision.json", "research_plan.json"),
        events=("prepared",),
    )
    write_json(run_dir / "trace.json", trace.to_dict())
    return run_dir
