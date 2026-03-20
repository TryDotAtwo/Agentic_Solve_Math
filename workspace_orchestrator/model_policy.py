from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass

from .provider_config import ResolvedProviderRuntime


@dataclass(frozen=True)
class AgentModelPolicy:
    model: str
    rationale: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def select_model_for_agent(
    agent_id: str,
    scope: str,
    department_key: str,
    rank: str,
    shared_service: bool,
    provider_runtime: ResolvedProviderRuntime | None = None,
) -> AgentModelPolicy:
    runtime = provider_runtime
    if runtime and runtime.model_strategy == "free_pool" and runtime.free_model_ids:
        digest = hashlib.md5(agent_id.encode("utf-8")).hexdigest()
        idx = int(digest, 16) % max(1, len(runtime.free_model_ids))
        chosen = runtime.free_model_ids[idx]
        return AgentModelPolicy(
            model=chosen,
            rationale=(
                f"{runtime.route_label} assigns a deterministic per-agent model from "
                f"the active free pool ({runtime.free_model_source})."
            ),
        )

    lowered = agent_id.lower()
    role_models = runtime.role_models if runtime is not None else None
    manager_model = role_models.manager if role_models else "gpt-5.2"
    research_model = role_models.research if role_models else "gpt-5.2"
    coding_model = role_models.coding if role_models else "gpt-5.2-codex"
    audit_model = role_models.audit if role_models else "gpt-5.2"
    history_model = role_models.history if role_models else "gpt-5-mini"
    support_model = role_models.support if role_models else "gpt-5-mini"

    if agent_id == "root.orchestrator":
        return AgentModelPolicy(
            model=manager_model,
            rationale="Root orchestration benefits from the strongest manager/reasoning tier for the active provider.",
        )
    if lowered.endswith(".commander"):
        return AgentModelPolicy(
            model=manager_model,
            rationale="Subproject commanders need high-level planning, delegation and synthesis.",
        )
    if "search_engineer" in lowered or "model_engineer" in lowered or "pipeline_integrator" in lowered:
        return AgentModelPolicy(
            model=coding_model,
            rationale="Solver engineering roles benefit from the coding-focused tier for the active provider.",
        )
    if "capability_designer" in lowered or "rule_engineer" in lowered or "tool_integrator" in lowered:
        return AgentModelPolicy(
            model=coding_model,
            rationale="Architecture and tooling roles are code-heavy and fit the coding-optimized tier.",
        )
    if "history" in lowered or "historian" in lowered or "article_drafter" in lowered or "report_drafter" in lowered:
        return AgentModelPolicy(
            model=history_model,
            rationale="Documentation and historical synthesis follow the provider's history/editorial tier.",
        )
    if "auditor" in lowered or "validator" in lowered or "verifier" in lowered:
        return AgentModelPolicy(
            model=audit_model,
            rationale="Audit and validation roles need strong reasoning for high-confidence checks.",
        )
    if shared_service and ("search" in lowered or "paper" in lowered):
        return AgentModelPolicy(
            model=research_model,
            rationale="Shared research services need strong synthesis across search results and evidence.",
        )
    if rank == "head":
        return AgentModelPolicy(
            model=manager_model,
            rationale="Department heads coordinate, review and escalate, so they use the manager tier.",
        )
    if any(token in lowered for token in ("parser", "indexer", "monitor", "recorder", "packager")):
        return AgentModelPolicy(
            model=support_model,
            rationale="Structured parsing and monitoring use the support tier for the active provider.",
        )
    if any(token in lowered for token in ("researcher", "analyst", "scout", "planner")):
        return AgentModelPolicy(
            model=research_model,
            rationale="Research and analysis roles benefit from stronger reasoning and evidence synthesis.",
        )
    if scope == "root":
        return AgentModelPolicy(
            model=support_model,
            rationale="Default root staff policy uses the support tier for the active provider.",
        )
    return AgentModelPolicy(
        model=support_model,
        rationale="Default subproject staff policy uses the support tier for the active provider.",
    )
