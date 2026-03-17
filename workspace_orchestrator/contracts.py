from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class TaskRequest:
    task_id: str
    task_type: str
    source: str
    objective: str
    requested_by: str
    intake_file: Path | None = None
    competition_links: tuple[str, ...] = field(default_factory=tuple)
    priorities: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["intake_file"] = str(self.intake_file) if self.intake_file else None
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TaskRequest":
        return cls(
            task_id=str(data["task_id"]),
            task_type=str(data["task_type"]),
            source=str(data["source"]),
            objective=str(data["objective"]),
            requested_by=str(data["requested_by"]),
            intake_file=Path(data["intake_file"]) if data.get("intake_file") else None,
            competition_links=tuple(data.get("competition_links", ())),
            priorities=tuple(data.get("priorities", ())),
            notes=tuple(data.get("notes", ())),
        )


@dataclass(frozen=True)
class RoutingDecision:
    target_kind: str
    target_name: str
    target_agent_id: str
    reason: str
    requires_approval: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RoutingDecision":
        return cls(
            target_kind=str(data["target_kind"]),
            target_name=str(data["target_name"]),
            target_agent_id=str(data["target_agent_id"]),
            reason=str(data["reason"]),
            requires_approval=bool(data.get("requires_approval", False)),
        )


@dataclass(frozen=True)
class ResearchPlan:
    plan_id: str
    research_questions: tuple[str, ...] = field(default_factory=tuple)
    deliverables: tuple[str, ...] = field(default_factory=tuple)
    evidence_requirements: tuple[str, ...] = field(default_factory=tuple)
    stop_conditions: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ResearchPlan":
        return cls(
            plan_id=str(data["plan_id"]),
            research_questions=tuple(data.get("research_questions", ())),
            deliverables=tuple(data.get("deliverables", ())),
            evidence_requirements=tuple(data.get("evidence_requirements", ())),
            stop_conditions=tuple(data.get("stop_conditions", ())),
        )


@dataclass(frozen=True)
class EscalationRequest:
    request_id: str
    requested_by: str
    summary: str
    reason: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "EscalationRequest":
        return cls(
            request_id=str(data["request_id"]),
            requested_by=str(data["requested_by"]),
            summary=str(data["summary"]),
            reason=str(data["reason"]),
        )


@dataclass(frozen=True)
class ChangeRequest:
    request_id: str
    requested_by: str
    scope: str
    target: str
    summary: str
    justification: str
    proposed_changes: tuple[str, ...] = field(default_factory=tuple)
    status: str = "proposed"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ChangeRequest":
        return cls(
            request_id=str(data["request_id"]),
            requested_by=str(data["requested_by"]),
            scope=str(data["scope"]),
            target=str(data["target"]),
            summary=str(data["summary"]),
            justification=str(data["justification"]),
            proposed_changes=tuple(data.get("proposed_changes", ())),
            status=str(data.get("status", "proposed")),
        )


@dataclass(frozen=True)
class HandoffPackage:
    handoff_id: str
    run_id: str
    created_at: str
    requester_agent_id: str
    target_agent_id: str
    task_request: TaskRequest
    routing_decision: RoutingDecision
    research_plan: ResearchPlan
    target_read_roots: tuple[str, ...] = field(default_factory=tuple)
    target_write_roots: tuple[str, ...] = field(default_factory=tuple)
    allowed_tools: tuple[str, ...] = field(default_factory=tuple)
    callable_agents: tuple[str, ...] = field(default_factory=tuple)
    shared_service_agents: tuple[str, ...] = field(default_factory=tuple)
    change_requests: tuple[ChangeRequest, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "handoff_id": self.handoff_id,
            "run_id": self.run_id,
            "created_at": self.created_at,
            "requester_agent_id": self.requester_agent_id,
            "target_agent_id": self.target_agent_id,
            "task_request": self.task_request.to_dict(),
            "routing_decision": self.routing_decision.to_dict(),
            "research_plan": self.research_plan.to_dict(),
            "target_read_roots": list(self.target_read_roots),
            "target_write_roots": list(self.target_write_roots),
            "allowed_tools": list(self.allowed_tools),
            "callable_agents": list(self.callable_agents),
            "shared_service_agents": list(self.shared_service_agents),
            "change_requests": [item.to_dict() for item in self.change_requests],
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HandoffPackage":
        return cls(
            handoff_id=str(data["handoff_id"]),
            run_id=str(data["run_id"]),
            created_at=str(data["created_at"]),
            requester_agent_id=str(data["requester_agent_id"]),
            target_agent_id=str(data["target_agent_id"]),
            task_request=TaskRequest.from_dict(dict(data["task_request"])),
            routing_decision=RoutingDecision.from_dict(dict(data["routing_decision"])),
            research_plan=ResearchPlan.from_dict(dict(data["research_plan"])),
            target_read_roots=tuple(data.get("target_read_roots", ())),
            target_write_roots=tuple(data.get("target_write_roots", ())),
            allowed_tools=tuple(data.get("allowed_tools", ())),
            callable_agents=tuple(data.get("callable_agents", ())),
            shared_service_agents=tuple(data.get("shared_service_agents", ())),
            change_requests=tuple(ChangeRequest.from_dict(dict(item)) for item in data.get("change_requests", ())),
        )


@dataclass(frozen=True)
class DelegationResult:
    handoff_id: str
    produced_by: str
    status: str
    summary: str
    canonical_paths: tuple[str, ...] = field(default_factory=tuple)
    escalations: tuple[EscalationRequest, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "handoff_id": self.handoff_id,
            "produced_by": self.produced_by,
            "status": self.status,
            "summary": self.summary,
            "canonical_paths": list(self.canonical_paths),
            "escalations": [item.to_dict() for item in self.escalations],
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "DelegationResult":
        return cls(
            handoff_id=str(data["handoff_id"]),
            produced_by=str(data["produced_by"]),
            status=str(data["status"]),
            summary=str(data["summary"]),
            canonical_paths=tuple(data.get("canonical_paths", ())),
            escalations=tuple(EscalationRequest.from_dict(dict(item)) for item in data.get("escalations", ())),
        )


@dataclass(frozen=True)
class ExecutionRecord:
    run_id: str
    handoff_id: str
    project_name: str
    mode: str
    command: tuple[str, ...] = field(default_factory=tuple)
    status: str = "pending"
    started_at: str = ""
    finished_at: str | None = None
    exit_code: int | None = None
    stdout_artifact: str | None = None
    stderr_artifact: str | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "handoff_id": self.handoff_id,
            "project_name": self.project_name,
            "mode": self.mode,
            "command": list(self.command),
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "exit_code": self.exit_code,
            "stdout_artifact": self.stdout_artifact,
            "stderr_artifact": self.stderr_artifact,
            "notes": list(self.notes),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ExecutionRecord":
        return cls(
            run_id=str(data["run_id"]),
            handoff_id=str(data["handoff_id"]),
            project_name=str(data["project_name"]),
            mode=str(data["mode"]),
            command=tuple(data.get("command", ())),
            status=str(data.get("status", "pending")),
            started_at=str(data.get("started_at", "")),
            finished_at=str(data["finished_at"]) if data.get("finished_at") is not None else None,
            exit_code=int(data["exit_code"]) if data.get("exit_code") is not None else None,
            stdout_artifact=str(data["stdout_artifact"]) if data.get("stdout_artifact") is not None else None,
            stderr_artifact=str(data["stderr_artifact"]) if data.get("stderr_artifact") is not None else None,
            notes=tuple(data.get("notes", ())),
        )


@dataclass(frozen=True)
class RunTrace:
    run_id: str
    handoff_id: str
    status: str
    target_agent_id: str
    artifacts: tuple[str, ...] = field(default_factory=tuple)
    events: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RunTrace":
        return cls(
            run_id=str(data["run_id"]),
            handoff_id=str(data["handoff_id"]),
            status=str(data["status"]),
            target_agent_id=str(data["target_agent_id"]),
            artifacts=tuple(data.get("artifacts", ())),
            events=tuple(data.get("events", ())),
        )
