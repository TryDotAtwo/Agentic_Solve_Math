import hashlib

from workspace_orchestrator.model_policy import select_model_for_agent
from workspace_orchestrator.provider_config import ResolvedProviderRuntime, RoleModelMatrix


def _expected_model(agent_id: str, free_models: list[str]) -> str:
    digest = hashlib.md5(agent_id.encode("utf-8")).hexdigest()
    idx = int(digest, 16) % max(1, len(free_models))
    return free_models[idx]


def test_openrouter_free_pool_assigns_deterministic_per_agent_models() -> None:
    free_models = ["m1", "m2", "m3", "m4"]
    runtime = ResolvedProviderRuntime(
        provider_id="openrouter",
        route_label="openrouter",
        api_key="or-test",
        base_url="https://openrouter.ai/api/v1",
        config_path="runtime_config.toml",
        model_strategy="free_pool",
        default_model=None,
        role_models=RoleModelMatrix(
            manager="openrouter/auto",
            research="openrouter/auto",
            coding="openrouter/auto",
            audit="openrouter/auto",
            history="openrouter/auto",
            support="openrouter/auto",
        ),
        free_model_ids=tuple(free_models),
        free_model_source="unit_test",
    )

    a1 = "root.orchestrator"
    a2 = "subproject.CayleyPy_444_Cube.05_solver_engineering.search_engineer"

    p1 = select_model_for_agent(
        agent_id=a1,
        scope="root",
        department_key="executive",
        rank="executive",
        shared_service=False,
        provider_runtime=runtime,
    )
    p2 = select_model_for_agent(
        agent_id=a2,
        scope="subproject",
        department_key="05_solver_engineering",
        rank="staff",
        shared_service=False,
        provider_runtime=runtime,
    )

    assert p1.model == _expected_model(a1, free_models)
    assert p2.model == _expected_model(a2, free_models)
