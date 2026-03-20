from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from importlib import import_module
from importlib.metadata import PackageNotFoundError, version
from importlib.util import find_spec
from pathlib import Path

from .delegation import load_handoff_package
from .model_policy import select_model_for_agent
from .organization import AgentManifest, OrganizationModel, build_root_organization, build_subproject_organization


DEFAULT_OPENAI_MODEL = "gpt-5-mini"


@dataclass(frozen=True)
class AgentsSDKAvailability:
    package_name: str
    available: bool
    version: str | None = None
    reason: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimeMetadata:
    scope: str
    root_path: str
    project_name: str
    run_id: str | None = None
    handoff_id: str | None = None
    requester_agent_id: str | None = None
    target_agent_id: str | None = None
    objective: str | None = None
    intake_file: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimeAgentSpec:
    agent_id: str
    display_name: str
    scope: str
    department_key: str
    rank: str
    shared_service: bool
    handoff_description: str
    instructions: str
    preferred_model: str
    model_rationale: str
    private_profile_root: str
    memory_path: str
    instructions_path: str
    rules_path: str
    reports_path: str
    allowed_tools: tuple[str, ...] = field(default_factory=tuple)
    read_roots: tuple[str, ...] = field(default_factory=tuple)
    write_roots: tuple[str, ...] = field(default_factory=tuple)
    hidden_roots: tuple[str, ...] = field(default_factory=tuple)
    handoff_target_ids: tuple[str, ...] = field(default_factory=tuple)
    tool_target_ids: tuple[str, ...] = field(default_factory=tuple)
    mutable_rule_roots: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimeTeamSpec:
    team_id: str
    scope: str
    manager_agent_id: str
    organization_name: str
    metadata: RuntimeMetadata
    agents_sdk: AgentsSDKAvailability
    orchestration_pattern: str
    agents: tuple[RuntimeAgentSpec, ...]

    def get_agent(self, agent_id: str) -> RuntimeAgentSpec:
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        raise KeyError(f"Unknown runtime agent id: {agent_id}")

    def to_dict(self) -> dict[str, object]:
        return {
            "team_id": self.team_id,
            "scope": self.scope,
            "manager_agent_id": self.manager_agent_id,
            "organization_name": self.organization_name,
            "metadata": self.metadata.to_dict(),
            "agents_sdk": self.agents_sdk.to_dict(),
            "orchestration_pattern": self.orchestration_pattern,
            "agent_count": len(self.agents),
            "agents": [agent.to_dict() for agent in self.agents],
        }


@dataclass(frozen=True)
class AgentsSDKBundle:
    team_spec: RuntimeTeamSpec
    entry_agent_id: str
    entry_agent: object
    sdk_agents_by_id: dict[str, object]
    materialized_agent_ids: tuple[str, ...]


def detect_agents_sdk() -> AgentsSDKAvailability:
    if find_spec("agents") is None:
        return AgentsSDKAvailability(
            package_name="agents",
            available=False,
            reason="module_not_found",
        )

    try:
        package_version = version("openai-agents")
    except PackageNotFoundError:
        package_version = None

    return AgentsSDKAvailability(
        package_name="agents",
        available=True,
        version=package_version,
        reason="ok",
    )


def _build_runtime_metadata(
    organization: OrganizationModel,
    run_id: str | None = None,
) -> RuntimeMetadata:
    if not run_id:
        return RuntimeMetadata(
            scope=organization.scope,
            root_path=str(organization.root),
            project_name=organization.name,
        )

    package = load_handoff_package(organization.root, run_id)
    return RuntimeMetadata(
        scope=organization.scope,
        root_path=str(organization.root),
        project_name=organization.name,
        run_id=package.run_id,
        handoff_id=package.handoff_id,
        requester_agent_id=package.requester_agent_id,
        target_agent_id=package.target_agent_id,
        objective=package.task_request.objective,
        intake_file=str(package.task_request.intake_file) if package.task_request.intake_file else None,
    )


def _instruction_text(manifest: AgentManifest, metadata: RuntimeMetadata) -> str:
    base_instructions = _load_optional_text(manifest.instructions_file)
    base_rules = _load_optional_text(manifest.rules_file)
    return " ".join(
        (
            f"You are {manifest.display_name} ({manifest.agent_id}).",
            f"Scope: {manifest.scope}. Department: {manifest.department_key}. Rank: {manifest.rank}.",
            f"Private profile root: {manifest.private_profile_root}.",
            f"Memory file: {manifest.memory_file}. Reports file: {manifest.reports_file}.",
            f"Readable roots: {', '.join(str(item) for item in manifest.read_roots) or '-'}.",
            f"Writable roots: {', '.join(str(item) for item in manifest.write_roots) or '-'}.",
            f"Hidden roots: {', '.join(str(item) for item in manifest.hidden_roots) or '-'}.",
            f"Allowed internal tool classes: {', '.join(manifest.allowed_tools) or '-'}.",
            (
                f"Callable agent ids: {', '.join(manifest.callable_agents) or '-'}; "
                f"shared service agent ids: {', '.join(manifest.shared_service_agents) or '-'}."
            ),
            (
                f"Run metadata: run_id={metadata.run_id or '-'}, handoff_id={metadata.handoff_id or '-'}, "
                f"objective={metadata.objective or '-'}, target_agent_id={metadata.target_agent_id or '-'}."
            ),
            (
                "Honor ACL and visibility boundaries, do not access hidden roots, "
                "and escalate policy or architecture changes instead of bypassing hierarchy."
            ),
            f"Base instructions file content: {base_instructions or '-'}",
            f"Base rules file content: {base_rules or '-'}",
        )
    )


def _load_optional_text(path: Path) -> str:
    if not path.exists():
        return ""
    return " ".join(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _handoff_target_ids(manifest: AgentManifest) -> tuple[str, ...]:
    shared = set(manifest.shared_service_agents)
    return tuple(agent_id for agent_id in manifest.callable_agents if agent_id not in shared)


def _tool_target_ids(manifest: AgentManifest) -> tuple[str, ...]:
    shared = set(manifest.shared_service_agents)
    return tuple(agent_id for agent_id in manifest.callable_agents if agent_id in shared)


def _build_team_spec(
    organization: OrganizationModel,
    manager_agent_id: str,
    orchestration_pattern: str,
    run_id: str | None = None,
) -> RuntimeTeamSpec:
    metadata = _build_runtime_metadata(organization, run_id=run_id)
    agents = tuple(
        _runtime_agent_spec(manifest, metadata)
        for manifest in organization.agents
    )
    return RuntimeTeamSpec(
        team_id=f"{organization.scope}:{organization.name}",
        scope=organization.scope,
        manager_agent_id=manager_agent_id,
        organization_name=organization.name,
        metadata=metadata,
        agents_sdk=detect_agents_sdk(),
        orchestration_pattern=orchestration_pattern,
        agents=agents,
    )


def _runtime_agent_spec(manifest: AgentManifest, metadata: RuntimeMetadata) -> RuntimeAgentSpec:
    policy = select_model_for_agent(
        agent_id=manifest.agent_id,
        scope=manifest.scope,
        department_key=manifest.department_key,
        rank=manifest.rank,
        shared_service=manifest.shared_service,
    )
    return RuntimeAgentSpec(
        agent_id=manifest.agent_id,
        display_name=manifest.display_name,
        scope=manifest.scope,
        department_key=manifest.department_key,
        rank=manifest.rank,
        shared_service=manifest.shared_service,
        handoff_description=f"{manifest.display_name} handles {manifest.department_key} responsibilities.",
        instructions=_instruction_text(manifest, metadata),
        preferred_model=policy.model,
        model_rationale=policy.rationale,
        private_profile_root=str(manifest.private_profile_root),
        memory_path=str(manifest.memory_file),
        instructions_path=str(manifest.instructions_file),
        rules_path=str(manifest.rules_file),
        reports_path=str(manifest.reports_file),
        allowed_tools=manifest.allowed_tools,
        read_roots=tuple(str(item) for item in manifest.read_roots),
        write_roots=tuple(str(item) for item in manifest.write_roots),
        hidden_roots=tuple(str(item) for item in manifest.hidden_roots),
        handoff_target_ids=_handoff_target_ids(manifest),
        tool_target_ids=_tool_target_ids(manifest),
        mutable_rule_roots=tuple(str(item) for item in manifest.mutable_rule_roots),
    )


def build_root_runtime_spec(root: Path, run_id: str | None = None) -> RuntimeTeamSpec:
    return _build_team_spec(
        build_root_organization(root),
        manager_agent_id="root.orchestrator",
        orchestration_pattern="handoffs_plus_shared_tools",
        run_id=run_id,
    )


def build_subproject_runtime_spec(root: Path, project_name: str, run_id: str | None = None) -> RuntimeTeamSpec:
    if run_id:
        package = load_handoff_package(root, run_id)
        expected = f"subproject.{project_name}.commander"
        if package.target_agent_id != expected:
            raise ValueError(f"Run {run_id} targets {package.target_agent_id}, not {expected}")
    return _build_team_spec(
        build_subproject_organization(root, project_name),
        manager_agent_id=f"subproject.{project_name}.commander",
        orchestration_pattern="local_handoffs_plus_shared_tools",
        run_id=run_id,
    )


def _tool_name(agent_id: str) -> str:
    return f"call_{agent_id.replace('.', '_')}"


def _sdk_agent_name(display_name: str) -> str:
    sanitized = display_name.replace("-", " ")
    sanitized = re.sub(r"[^A-Za-z0-9_ ]+", "", sanitized)
    sanitized = re.sub(r"\s+", " ", sanitized).strip()
    return sanitized or "Agent"


def _load_agents_module():
    availability = detect_agents_sdk()
    if not availability.available:
        raise RuntimeError("OpenAI Agents SDK is not available in this environment.")
    return import_module("agents")


def instantiate_agents_sdk_bundle(
    team_spec: RuntimeTeamSpec,
    entry_agent_id: str | None = None,
    model: str | None = None,
    expansion_depth: int = 1,
    extra_tools_by_agent_id: dict[str, list[object]] | None = None,
) -> AgentsSDKBundle:
    agents_module = _load_agents_module()
    agent_cls = getattr(agents_module, "Agent")
    entry_id = entry_agent_id or team_spec.manager_agent_id
    by_id = {agent.agent_id: agent for agent in team_spec.agents}
    cache: dict[tuple[str, int], object] = {}
    support_agents: dict[str, object] = {}
    extra_tools_by_agent_id = extra_tools_by_agent_id or {}

    def build(agent_id: str, depth: int) -> object:
        key = (agent_id, depth)
        if key in cache:
            return cache[key]

        spec = by_id[agent_id]
        tools = []
        handoffs = []
        if depth > 0:
            for target_id in spec.tool_target_ids:
                if target_id not in by_id:
                    continue
                target = build(target_id, depth - 1)
                support_agents[target_id] = target
                tools.append(
                    target.as_tool(
                        tool_name=_tool_name(target_id),
                        tool_description=f"Direct shared-service call into {target_id}.",
                    )
                )
            for target_id in spec.handoff_target_ids:
                if target_id not in by_id:
                    continue
                target = build(target_id, depth - 1)
                support_agents[target_id] = target
                handoffs.append(target)
        tools.extend(extra_tools_by_agent_id.get(agent_id, ()))

        kwargs = {
            "name": _sdk_agent_name(spec.display_name),
            "instructions": spec.instructions,
            "model": model or spec.preferred_model or DEFAULT_OPENAI_MODEL,
        }
        if spec.handoff_description:
            kwargs["handoff_description"] = spec.handoff_description
        if tools:
            kwargs["tools"] = tools
        if handoffs:
            kwargs["handoffs"] = handoffs
        agent = agent_cls(**kwargs)
        cache[key] = agent
        return agent

    entry_agent = build(entry_id, expansion_depth)
    return AgentsSDKBundle(
        team_spec=team_spec,
        entry_agent_id=entry_id,
        entry_agent=entry_agent,
        sdk_agents_by_id={entry_id: entry_agent, **support_agents},
        materialized_agent_ids=(entry_id,),
    )
