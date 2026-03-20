import hashlib

from workspace_orchestrator.model_policy import select_model_for_agent


def _expected_model(agent_id: str, free_models: list[str]) -> str:
    digest = hashlib.md5(agent_id.encode("utf-8")).hexdigest()
    idx = int(digest, 16) % max(1, len(free_models))
    return free_models[idx]


def test_openrouter_test_mode_assigns_deterministic_per_agent_models(monkeypatch) -> None:
    free_models = ["m1", "m2", "m3", "m4"]
    monkeypatch.setenv("ASM_OPENROUTER_TEST_MODE", "1")
    monkeypatch.setenv("ASM_OPENROUTER_FREE_MODELS", ",".join(free_models))

    a1 = "root.orchestrator"
    a2 = "subproject.CayleyPy_444_Cube.05_solver_engineering.search_engineer"

    p1 = select_model_for_agent(
        agent_id=a1,
        scope="root",
        department_key="executive",
        rank="executive",
        shared_service=False,
    )
    p2 = select_model_for_agent(
        agent_id=a2,
        scope="subproject",
        department_key="05_solver_engineering",
        rank="staff",
        shared_service=False,
    )

    assert p1.model == _expected_model(a1, free_models)
    assert p2.model == _expected_model(a2, free_models)

