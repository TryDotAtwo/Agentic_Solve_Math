from workspace_orchestrator.model_policy import select_model_for_agent


def test_model_policy_uses_strong_general_model_for_root_orchestrator() -> None:
    policy = select_model_for_agent(
        agent_id="root.orchestrator",
        scope="root",
        department_key="executive",
        rank="executive",
        shared_service=False,
    )

    assert policy.model == "gpt-5.2"


def test_model_policy_uses_coding_model_for_solver_engineers() -> None:
    policy = select_model_for_agent(
        agent_id="subproject.CayleyPy_444_Cube.05_solver_engineering.search_engineer",
        scope="subproject",
        department_key="05_solver_engineering",
        rank="staff",
        shared_service=False,
    )

    assert policy.model == "gpt-5.2-codex"


def test_model_policy_uses_economical_model_for_history_roles() -> None:
    policy = select_model_for_agent(
        agent_id="root.06_editorial_and_history.history_scribe",
        scope="root",
        department_key="06_editorial_and_history",
        rank="staff",
        shared_service=True,
    )

    assert policy.model == "gpt-5-mini"
