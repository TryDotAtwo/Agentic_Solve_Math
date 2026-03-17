from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

from .workspace import discover_subprojects


ROOT_EXECUTIVE_ID = "root.orchestrator"


@dataclass(frozen=True)
class AgentManifest:
    agent_id: str
    display_name: str
    scope: str
    department_key: str
    rank: str
    read_roots: tuple[Path, ...]
    write_roots: tuple[Path, ...]
    hidden_roots: tuple[Path, ...]
    callable_agents: tuple[str, ...] = field(default_factory=tuple)
    shared_service_agents: tuple[str, ...] = field(default_factory=tuple)
    allowed_tools: tuple[str, ...] = field(default_factory=tuple)
    mutable_rule_roots: tuple[Path, ...] = field(default_factory=tuple)
    shared_service: bool = False

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        for key in ("read_roots", "write_roots", "hidden_roots", "mutable_rule_roots"):
            data[key] = [str(item) for item in getattr(self, key)]
        return data


@dataclass(frozen=True)
class DepartmentManifest:
    key: str
    name: str
    scope: str
    path: Path
    head_agent_id: str
    staff_agent_ids: tuple[str, ...]
    shared_service_agent_ids: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["path"] = str(self.path)
        return data


@dataclass(frozen=True)
class OrganizationModel:
    name: str
    scope: str
    root: Path
    departments: tuple[DepartmentManifest, ...]
    agents: tuple[AgentManifest, ...]

    @property
    def agent_count(self) -> int:
        return len(self.agents)

    def get_agent(self, agent_id: str) -> AgentManifest:
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        raise KeyError(f"Unknown agent id: {agent_id}")

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "scope": self.scope,
            "root": str(self.root),
            "agent_count": self.agent_count,
            "departments": [item.to_dict() for item in self.departments],
            "agents": [item.to_dict() for item in self.agents],
        }


ROOT_DEPARTMENTS: tuple[dict[str, object], ...] = (
    {
        "key": "01_intake_and_orchestration",
        "name": "Intake and Orchestration",
        "staff": (
            ("intake_analyst", "Intake Analyst", False),
            ("context_packager", "Context Packager", False),
        ),
        "allowed_tools": ("read_intake", "build_handoff"),
        "extra_reads": ("kaggle_intake",),
        "extra_writes": (),
    },
    {
        "key": "02_research_intelligence",
        "name": "Research Intelligence",
        "staff": (
            ("global_searcher", "Global Searcher", True),
            ("paper_scout", "Paper Scout", True),
        ),
        "allowed_tools": ("web_search", "paper_search", "source_classification"),
        "extra_reads": ("kaggle_intake", "rules/registry"),
        "extra_writes": (),
    },
    {
        "key": "03_architecture_and_capability",
        "name": "Architecture and Capability",
        "staff": (
            ("capability_designer", "Capability Designer", False),
            ("rule_engineer", "Rule Engineer", False),
        ),
        "allowed_tools": ("architecture_edit", "manifest_design"),
        "extra_reads": ("workspace_orchestrator", "rules/organization", "rules/architecture"),
        "extra_writes": ("rules/architecture",),
    },
    {
        "key": "04_tooling_and_mcp_ops",
        "name": "Tooling and MCP Ops",
        "staff": (
            ("tool_integrator", "Tool Integrator", False),
            ("access_operator", "Access Operator", False),
        ),
        "allowed_tools": ("tool_registry", "mcp_policy", "connector_review"),
        "extra_reads": ("workspace_orchestrator", "rules/architecture"),
        "extra_writes": (),
    },
    {
        "key": "05_cross_project_analysis",
        "name": "Cross-project Analysis",
        "staff": (
            ("benchmark_analyst", "Benchmark Analyst", False),
            ("pattern_synthesizer", "Pattern Synthesizer", False),
        ),
        "allowed_tools": ("benchmark_analysis", "summary_synthesis"),
        "extra_reads": ("rules/registry", "rules/logs"),
        "extra_writes": ("rules/registry",),
    },
    {
        "key": "06_editorial_and_history",
        "name": "Editorial and History",
        "staff": (
            ("history_scribe", "History Scribe", True),
            ("article_drafter", "Article Drafter", False),
        ),
        "allowed_tools": ("history_log", "article_draft"),
        "extra_reads": ("rules/logs", "rules/architecture"),
        "extra_writes": ("rules/logs",),
    },
    {
        "key": "07_audit_and_compliance",
        "name": "Audit and Compliance",
        "staff": (
            ("access_auditor", "Access Auditor", False),
            ("result_verifier", "Result Verifier", False),
        ),
        "allowed_tools": ("audit", "compliance_review"),
        "extra_reads": ("rules", "workspace_orchestrator"),
        "extra_writes": (),
    },
    {
        "key": "08_organization_evolution",
        "name": "Organization Evolution",
        "staff": (
            ("workforce_designer", "Workforce Designer", False),
            ("training_curator", "Training Curator", False),
        ),
        "allowed_tools": ("organization_design", "training_design"),
        "extra_reads": ("rules/organization", "rules/architecture"),
        "extra_writes": ("rules/organization",),
    },
)


SUBPROJECT_DEPARTMENTS: tuple[dict[str, object], ...] = (
    {
        "key": "01_source_intelligence",
        "name": "Source Intelligence",
        "staff": (
            ("web_researcher", "Web Researcher", True),
            ("paper_researcher", "Paper Researcher", True),
            ("baseline_scout", "Baseline Scout", False),
        ),
        "allowed_tools": ("web_search", "paper_search", "baseline_scan"),
    },
    {
        "key": "02_problem_analysis",
        "name": "Problem Analysis",
        "staff": (
            ("hypothesis_analyst", "Hypothesis Analyst", False),
            ("formal_analyst", "Formal Analyst", False),
            ("failure_analyst", "Failure Analyst", False),
        ),
        "allowed_tools": ("math_analysis", "hypothesis_tracking"),
    },
    {
        "key": "03_data_and_parsing",
        "name": "Data and Parsing",
        "staff": (
            ("dataset_parser", "Dataset Parser", False),
            ("schema_validator", "Schema Validator", False),
            ("artifact_indexer", "Artifact Indexer", False),
        ),
        "allowed_tools": ("dataset_parse", "schema_validation"),
    },
    {
        "key": "04_experimentation",
        "name": "Experimentation",
        "staff": (
            ("experiment_planner", "Experiment Planner", False),
            ("runner_operator", "Runner Operator", False),
            ("benchmark_recorder", "Benchmark Recorder", False),
        ),
        "allowed_tools": ("experiment_plan", "experiment_run"),
    },
    {
        "key": "05_solver_engineering",
        "name": "Solver Engineering",
        "staff": (
            ("search_engineer", "Search Engineer", False),
            ("model_engineer", "Model Engineer", False),
            ("pipeline_integrator", "Pipeline Integrator", False),
        ),
        "allowed_tools": ("solver_edit", "pipeline_edit"),
    },
    {
        "key": "06_evaluation_and_submission",
        "name": "Evaluation and Submission",
        "staff": (
            ("metric_analyst", "Metric Analyst", False),
            ("submission_operator", "Submission Operator", False),
            ("leaderboard_monitor", "Leaderboard Monitor", False),
        ),
        "allowed_tools": ("metric_eval", "submission_prepare"),
    },
    {
        "key": "07_editorial_and_history",
        "name": "Editorial and History",
        "staff": (
            ("local_historian", "Local Historian", True),
            ("report_drafter", "Report Drafter", False),
            ("evidence_curator", "Evidence Curator", False),
        ),
        "allowed_tools": ("history_log", "report_write"),
    },
    {
        "key": "08_audit_and_validation",
        "name": "Audit and Validation",
        "staff": (
            ("rule_auditor", "Rule Auditor", False),
            ("result_validator", "Result Validator", False),
            ("access_checker", "Access Checker", False),
        ),
        "allowed_tools": ("audit", "validation"),
    },
)


def _workspace_runtime_root(root: Path) -> Path:
    return root / ".agent_workspace"


def _root_hidden_roots(root: Path) -> tuple[Path, ...]:
    hidden = [project.path for project in discover_subprojects(root)]
    return tuple(sorted(hidden, key=str))


def _subproject_hidden_roots(root: Path, subproject_name: str) -> tuple[Path, ...]:
    hidden: list[Path] = [root / "rules", root / "kaggle_intake", root / "workspace_orchestrator"]
    hidden.extend(
        project.path for project in discover_subprojects(root) if project.name != subproject_name
    )
    return tuple(sorted(hidden, key=str))


def _resolve_roots(root: Path, items: tuple[str, ...]) -> tuple[Path, ...]:
    return tuple(root / item for item in items)


def _root_dept_workspace(root: Path, department_key: str) -> Path:
    return _workspace_runtime_root(root) / "root" / department_key


def _subproject_dept_workspace(root: Path, subproject_name: str, department_key: str) -> Path:
    return root / subproject_name / ".agent_workspace" / department_key


def _root_department_rules(root: Path, department_key: str) -> Path:
    return root / "rules" / "organization" / "root_departments" / department_key


def _subproject_department_rules(root: Path, subproject_name: str, department_key: str) -> Path:
    return root / subproject_name / ".agent_workspace" / "rules" / department_key


def _shared_service_ids(department_key: str, staff: tuple[tuple[str, str, bool], ...], prefix: str) -> tuple[str, ...]:
    shared = []
    for slug, _, is_shared in staff:
        if is_shared:
            shared.append(f"{prefix}.{department_key}.{slug}")
    return tuple(shared)


def build_root_organization(root: Path) -> OrganizationModel:
    root = root.resolve()
    hidden_roots = _root_hidden_roots(root)

    departments: list[DepartmentManifest] = []
    agents: list[AgentManifest] = [
        AgentManifest(
            agent_id=ROOT_EXECUTIVE_ID,
            display_name="Root Orchestrator",
            scope="root",
            department_key="root_command",
            rank="executive",
            read_roots=(
                root / "rules",
                root / "kaggle_intake",
                root / "workspace_orchestrator",
                _workspace_runtime_root(root),
            ),
            write_roots=(root / "rules", root / "workspace_orchestrator", _workspace_runtime_root(root)),
            hidden_roots=(),
            allowed_tools=("orchestrate", "delegate", "log_update"),
        )
    ]

    for spec in ROOT_DEPARTMENTS:
        key = str(spec["key"])
        name = str(spec["name"])
        dept_path = root / "rules" / "organization" / "root_departments" / key
        head_id = f"root.{key}.head"
        shared_ids = _shared_service_ids(key, spec["staff"], "root")
        staff_ids = tuple(f"root.{key}.{slug}" for slug, _, _ in spec["staff"])
        departments.append(
            DepartmentManifest(
                key=key,
                name=name,
                scope="root",
                path=dept_path,
                head_agent_id=head_id,
                staff_agent_ids=staff_ids,
                shared_service_agent_ids=shared_ids,
            )
        )

        read_roots = (
            root / "rules",
            _root_dept_workspace(root, key),
            *_resolve_roots(root, tuple(spec["extra_reads"])),
        )
        write_roots = (
            _root_dept_workspace(root, key),
            *_resolve_roots(root, tuple(spec["extra_writes"])),
        )

        agents.append(
            AgentManifest(
                agent_id=head_id,
                display_name=f"Head of {name}",
                scope="root",
                department_key=key,
                rank="head",
                read_roots=tuple(dict.fromkeys(read_roots)),
                write_roots=tuple(dict.fromkeys(write_roots)),
                hidden_roots=hidden_roots,
                allowed_tools=tuple(spec["allowed_tools"]),
                mutable_rule_roots=(_root_department_rules(root, key),),
            )
        )
        for slug, display_name, is_shared in spec["staff"]:
            agents.append(
                AgentManifest(
                    agent_id=f"root.{key}.{slug}",
                    display_name=display_name,
                    scope="root",
                    department_key=key,
                    rank="staff",
                    read_roots=tuple(dict.fromkeys(read_roots)),
                    write_roots=tuple(dict.fromkeys(write_roots)),
                    hidden_roots=hidden_roots,
                    allowed_tools=tuple(spec["allowed_tools"]),
                    shared_service=is_shared,
                )
            )

    agents = _attach_call_graph(tuple(agents), tuple(departments), ROOT_EXECUTIVE_ID)
    return OrganizationModel(
        name="root",
        scope="root",
        root=root,
        departments=tuple(departments),
        agents=tuple(agents),
    )


def build_subproject_organization(root: Path, subproject_name: str) -> OrganizationModel:
    root = root.resolve()
    hidden_roots = _subproject_hidden_roots(root, subproject_name)
    subproject_path = root / subproject_name

    departments: list[DepartmentManifest] = []
    commander_id = f"subproject.{subproject_name}.commander"
    agents: list[AgentManifest] = [
        AgentManifest(
            agent_id=commander_id,
            display_name="Subproject Commander",
            scope="subproject",
            department_key="00_project_command",
            rank="executive",
            read_roots=(subproject_path, subproject_path / ".agent_workspace"),
            write_roots=(subproject_path / ".agent_workspace",),
            hidden_roots=hidden_roots,
            callable_agents=(ROOT_EXECUTIVE_ID,),
            allowed_tools=("local_orchestrate", "local_delegate"),
        )
    ]

    for spec in SUBPROJECT_DEPARTMENTS:
        key = str(spec["key"])
        name = str(spec["name"])
        dept_path = root / "rules" / "organization" / "subproject_template_departments" / key
        head_id = f"subproject.{subproject_name}.{key}.head"
        staff_ids = tuple(f"subproject.{subproject_name}.{key}.{slug}" for slug, _, _ in spec["staff"])
        shared_ids = tuple(
            agent_id
            for agent_id, (_, _, is_shared) in zip(staff_ids, spec["staff"])
            if is_shared
        )
        departments.append(
            DepartmentManifest(
                key=key,
                name=name,
                scope="subproject",
                path=dept_path,
                head_agent_id=head_id,
                staff_agent_ids=staff_ids,
                shared_service_agent_ids=shared_ids,
            )
        )
        read_roots = (subproject_path, _subproject_dept_workspace(root, subproject_name, key))
        write_roots = (_subproject_dept_workspace(root, subproject_name, key),)

        agents.append(
            AgentManifest(
                agent_id=head_id,
                display_name=f"Head of {name}",
                scope="subproject",
                department_key=key,
                rank="head",
                read_roots=read_roots,
                write_roots=write_roots,
                hidden_roots=hidden_roots,
                allowed_tools=tuple(spec["allowed_tools"]),
                mutable_rule_roots=(_subproject_department_rules(root, subproject_name, key),),
            )
        )
        for slug, display_name, is_shared in spec["staff"]:
            extra_write_roots = list(write_roots)
            if key == "07_editorial_and_history":
                extra_write_roots.append(subproject_path / "docs")
            agents.append(
                AgentManifest(
                    agent_id=f"subproject.{subproject_name}.{key}.{slug}",
                    display_name=display_name,
                    scope="subproject",
                    department_key=key,
                    rank="staff",
                    read_roots=read_roots,
                    write_roots=tuple(extra_write_roots),
                    hidden_roots=hidden_roots,
                    allowed_tools=tuple(spec["allowed_tools"]),
                    shared_service=is_shared,
                )
            )

    agents = _attach_call_graph(tuple(agents), tuple(departments), commander_id)
    return OrganizationModel(
        name=subproject_name,
        scope="subproject",
        root=root,
        departments=tuple(departments),
        agents=tuple(agents),
    )


def _attach_call_graph(
    agents: tuple[AgentManifest, ...],
    departments: tuple[DepartmentManifest, ...],
    executive_id: str,
) -> list[AgentManifest]:
    by_id = {agent.agent_id: agent for agent in agents}
    heads = [dept.head_agent_id for dept in departments]
    shared_services = [agent.agent_id for agent in agents if agent.shared_service]
    updated: list[AgentManifest] = []

    for agent in agents:
        allowed: list[str] = list(agent.callable_agents)
        if agent.rank == "executive":
            allowed.extend(heads)
        elif agent.rank == "head":
            dept = next(item for item in departments if item.key == agent.department_key)
            allowed.append(executive_id)
            allowed.extend(heads)
            allowed.extend(dept.staff_agent_ids)
            allowed.extend(shared_services)
        else:
            dept = next(item for item in departments if item.key == agent.department_key)
            allowed.append(dept.head_agent_id)
            allowed.extend(item for item in dept.staff_agent_ids if item != agent.agent_id)
            allowed.extend(shared_services)

        deduped = tuple(item for item in dict.fromkeys(allowed) if item in by_id or item == ROOT_EXECUTIVE_ID)
        updated.append(
            replace(
                agent,
                callable_agents=deduped,
                shared_service_agents=tuple(item for item in shared_services if item != agent.agent_id),
            )
        )

    return updated
