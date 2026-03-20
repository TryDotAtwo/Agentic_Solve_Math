from __future__ import annotations

import hashlib
import os
from dataclasses import asdict, dataclass


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
) -> AgentModelPolicy:
    # Test mode: OpenRouter "free" routing assigns a deterministic (per-agent) model
    # from a configured allow-list. This allows a smoke test that exercises
    # heterogeneous models across the whole org/team.
    #
    # Env:
    # - ASM_OPENROUTER_TEST_MODE=1
    # - ASM_OPENROUTER_FREE_MODELS (optional, comma-separated)
    openrouter_test_mode = os.environ.get("ASM_OPENROUTER_TEST_MODE", "")
    if openrouter_test_mode.strip().lower() in {"1", "true", "yes", "on"}:
        free_models_raw = os.environ.get("ASM_OPENROUTER_FREE_MODELS", "").strip()
        if free_models_raw:
            free_models = [m.strip() for m in free_models_raw.split(",") if m.strip()]
        else:
            # Curated subset from https://openrouter.ai/models?q=free
            free_models = [
                "stepfun/step-3.5-flash:free",
                "nvidia/nemotron-3-super-120b-a12b:free",
                "arcee-ai/trinity-large-preview:free",
                "z-ai/glm-4.5-air:free",
                "nvidia/nemotron-3-nano-30b-a3b:free",
                "arcee-ai/trinity-mini:free",
                "nvidia/nemotron-nano-12b-v2-vl:free",
                "nvidia/nemotron-nano-9b-v2:free",
                "qwen/qwen3-coder:free",
                "qwen/qwen3-next-80b-a3b-instruct:free",
                "meta-llama/llama-3.3-70b-instruct:free",
                "openai/gpt-oss-120b:free",
            ]

        digest = hashlib.md5(agent_id.encode("utf-8")).hexdigest()
        idx = int(digest, 16) % max(1, len(free_models))
        chosen = free_models[idx]
        return AgentModelPolicy(
            model=chosen,
            rationale="OpenRouter free-test per-agent deterministic model assignment.",
        )

    lowered = agent_id.lower()
    strong_general = "gpt-5.2"
    strong_coding = "gpt-5.2-codex"
    economical_general = "gpt-5-mini"

    if agent_id == "root.orchestrator":
        return AgentModelPolicy(
            model=strong_general,
            rationale="Root orchestration benefits from strong reasoning tier.",
        )
    if lowered.endswith(".commander"):
        return AgentModelPolicy(
            model=strong_general,
            rationale="Subproject commanders need high-level planning, delegation and synthesis.",
        )
    if "search_engineer" in lowered or "model_engineer" in lowered or "pipeline_integrator" in lowered:
        return AgentModelPolicy(
            model=strong_coding,
            rationale="Solver engineering roles benefit from strong coding tier.",
        )
    if "capability_designer" in lowered or "rule_engineer" in lowered or "tool_integrator" in lowered:
        return AgentModelPolicy(
            model=strong_coding,
            rationale="Architecture and tooling roles are code-heavy and fit the strongest coding-optimized model.",
        )
    if "history" in lowered or "historian" in lowered or "article_drafter" in lowered or "report_drafter" in lowered:
        return AgentModelPolicy(
            model=economical_general,
            rationale="Documentation and historical synthesis need quality but should stay cost-efficient.",
        )
    if "auditor" in lowered or "validator" in lowered or "verifier" in lowered:
        return AgentModelPolicy(
            model=strong_general,
            rationale="Audit and validation roles need strong reasoning for high-confidence checks.",
        )
    if shared_service and ("search" in lowered or "paper" in lowered):
        return AgentModelPolicy(
            model=strong_general,
            rationale="Shared research services need strong synthesis across search results and evidence.",
        )
    if rank == "head":
        return AgentModelPolicy(
            model=strong_general,
            rationale="Department heads coordinate, review and escalate, so they need a strong manager model.",
        )
    if any(token in lowered for token in ("parser", "indexer", "monitor", "recorder", "packager")):
        return AgentModelPolicy(
            model=economical_general,
            rationale="Structured parsing and monitoring are important but usually narrower than strategic roles.",
        )
    if any(token in lowered for token in ("researcher", "analyst", "scout", "planner")):
        return AgentModelPolicy(
            model=strong_general,
            rationale="Research and analysis roles benefit from stronger reasoning and evidence synthesis.",
        )
    if scope == "root":
        return AgentModelPolicy(
            model=economical_general,
            rationale="Default root staff policy favors a cost-efficient strong general model.",
        )
    return AgentModelPolicy(
        model=economical_general,
        rationale="Default subproject staff policy favors a cost-efficient strong general model.",
    )
