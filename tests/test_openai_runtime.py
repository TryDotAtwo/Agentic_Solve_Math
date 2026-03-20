import sys
import types
from pathlib import Path

from workspace_orchestrator.handoff import (
    build_handoff_for_subproject,
    build_task_request_from_intake,
    default_research_plan,
    materialize_handoff_package,
)
from workspace_orchestrator.intake import parse_intake_file
from workspace_orchestrator.openai_runtime import (
    build_root_runtime_spec,
    build_subproject_runtime_spec,
    detect_agents_sdk,
    instantiate_agents_sdk_bundle,
)


def _prepare_root(tmp_path: Path, project_name: str = "CayleyPy_TestHarness") -> Path:
    (tmp_path / "rules").mkdir()
    (tmp_path / "kaggle_intake").mkdir()
    (tmp_path / "workspace_orchestrator").mkdir()
    project_dir = tmp_path / project_name
    project_dir.mkdir()
    (project_dir / "main.py").write_text("print('fixture')\n", encoding="utf-8")
    (tmp_path / "kaggle_intake" / "sample.md").write_text(
        """# Intake

- https://www.kaggle.com/competitions/example-comp
""",
        encoding="utf-8",
    )
    return tmp_path


def _materialize_run(root: Path, project_name: str = "CayleyPy_TestHarness") -> str:
    brief = parse_intake_file(root / "kaggle_intake" / "sample.md")
    request = build_task_request_from_intake(
        brief,
        objective="Investigate the fixture competition",
        task_id="task-001",
        requested_by="root.02_research_intelligence.head",
    )
    plan = default_research_plan(
        objective="Investigate the fixture competition",
        plan_id="plan-001",
        research_questions=("What should the team research first?",),
    )
    package = build_handoff_for_subproject(
        root,
        project_name=project_name,
        task_request=request,
        research_plan=plan,
        requester_agent_id="root.02_research_intelligence.head",
        run_id="run-001",
        handoff_id="handoff-001",
    )
    materialize_handoff_package(root, package)
    return package.run_id


def test_detect_agents_sdk_reports_missing(monkeypatch) -> None:
    monkeypatch.setattr("workspace_orchestrator.openai_runtime.find_spec", lambda name: None)

    availability = detect_agents_sdk()

    assert availability.available is False
    assert availability.package_name == "agents"
    assert availability.reason == "module_not_found"


def test_build_root_runtime_spec_propagates_run_metadata(tmp_path: Path) -> None:
    root = _prepare_root(tmp_path)
    run_id = _materialize_run(root)

    team = build_root_runtime_spec(root, run_id=run_id)
    orchestrator = team.get_agent("root.orchestrator")
    research_head = team.get_agent("root.02_research_intelligence.head")
    history_scribe = team.get_agent("root.06_editorial_and_history.history_scribe")

    assert team.manager_agent_id == "root.orchestrator"
    assert team.metadata.run_id == run_id
    assert team.metadata.handoff_id == "handoff-001"
    assert team.metadata.objective == "Investigate the fixture competition"
    assert team.metadata.target_agent_id == "subproject.CayleyPy_TestHarness.commander"
    assert orchestrator.preferred_model == "gpt-5.2"
    assert "root.01_intake_and_orchestration.head" in orchestrator.handoff_target_ids
    assert research_head.preferred_model == "gpt-5.2"
    assert history_scribe.preferred_model == "gpt-5-mini"
    assert research_head.tool_target_ids == (
        "root.02_research_intelligence.global_searcher",
        "root.02_research_intelligence.paper_scout",
        "root.06_editorial_and_history.history_scribe",
    )


def test_build_subproject_runtime_spec_marks_local_shared_services(tmp_path: Path) -> None:
    root = _prepare_root(tmp_path)
    run_id = _materialize_run(root)

    team = build_subproject_runtime_spec(root, "CayleyPy_TestHarness", run_id=run_id)
    commander = team.get_agent("subproject.CayleyPy_TestHarness.commander")
    editorial_head = team.get_agent("subproject.CayleyPy_TestHarness.07_editorial_and_history.head")
    search_engineer = team.get_agent("subproject.CayleyPy_TestHarness.05_solver_engineering.search_engineer")

    assert team.manager_agent_id == "subproject.CayleyPy_TestHarness.commander"
    assert team.metadata.run_id == run_id
    assert commander.preferred_model == "gpt-5.2"
    assert search_engineer.preferred_model == "gpt-5.2-codex"
    assert "subproject.CayleyPy_TestHarness.01_source_intelligence.head" in commander.handoff_target_ids
    assert (
        "subproject.CayleyPy_TestHarness.07_editorial_and_history.local_historian"
        in editorial_head.tool_target_ids
    )


def test_instantiate_agents_sdk_bundle_uses_fake_sdk(tmp_path: Path, monkeypatch) -> None:
    root = _prepare_root(tmp_path)
    team = build_root_runtime_spec(root)

    class FakeAgent:
        def __init__(self, **kwargs):
            self.kwargs = dict(kwargs)
            self.name = kwargs["name"]
            self.instructions = kwargs["instructions"]
            self.model = kwargs.get("model")
            self.tools = list(kwargs.get("tools", []))
            self.handoffs = list(kwargs.get("handoffs", []))
            self.handoff_description = kwargs.get("handoff_description")

        def as_tool(self, tool_name: str, tool_description: str):
            return {
                "tool_name": tool_name,
                "tool_description": tool_description,
                "agent_name": self.name,
            }

    fake_module = types.SimpleNamespace(Agent=FakeAgent)
    monkeypatch.setattr("workspace_orchestrator.openai_runtime.find_spec", lambda name: object())
    monkeypatch.setitem(sys.modules, "agents", fake_module)

    bundle = instantiate_agents_sdk_bundle(
        team,
        entry_agent_id="root.02_research_intelligence.head",
        model=None,
        expansion_depth=1,
    )

    entry_agent = bundle.entry_agent
    assert isinstance(entry_agent, FakeAgent)
    assert entry_agent.model == "gpt-5.2"
    assert len(entry_agent.tools) == 3
    assert entry_agent.tools[0]["tool_name"] == "call_root_02_research_intelligence_global_searcher"
    assert bundle.materialized_agent_ids == ("root.02_research_intelligence.head",)
