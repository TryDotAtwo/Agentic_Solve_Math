from pathlib import Path

from workspace_orchestrator.contracts import (
    ChangeRequest,
    ExecutionRecord,
    HandoffPackage,
    ResearchPlan,
    RoutingDecision,
    RunTrace,
    TaskRequest,
)


def test_task_request_and_handoff_package_round_trip() -> None:
    request = TaskRequest(
        task_id="task-001",
        task_type="kaggle_research",
        source="chat",
        objective="Study and route the intake",
        requested_by="root.orchestrator",
        intake_file=Path("kaggle_intake/sample.md"),
        competition_links=("https://www.kaggle.com/competitions/example",),
        priorities=("build baseline",),
        notes=("pay attention to structure",),
    )
    routing = RoutingDecision(
        target_kind="existing_subproject",
        target_name="CayleyPy_444_Cube",
        target_agent_id="subproject.CayleyPy_444_Cube.commander",
        reason="Matched explicit project",
    )
    plan = ResearchPlan(
        plan_id="plan-001",
        research_questions=("What is the best baseline?",),
        deliverables=("brief", "handoff"),
        evidence_requirements=("official files",),
        stop_conditions=("need user approval",),
    )
    change = ChangeRequest(
        request_id="chg-001",
        requested_by="subproject.CayleyPy_444_Cube.commander",
        scope="root_policy",
        target="department_graph",
        summary="Need an extra submission role",
        justification="Submission workload increased",
        proposed_changes=("add one role",),
    )
    package = HandoffPackage(
        handoff_id="handoff-001",
        run_id="run-001",
        created_at="2026-03-17T12:00:00Z",
        requester_agent_id="root.01_intake_and_orchestration.head",
        target_agent_id="subproject.CayleyPy_444_Cube.commander",
        task_request=request,
        routing_decision=routing,
        research_plan=plan,
        target_read_roots=("D:/Agentic_Solve_Math/CayleyPy_444_Cube",),
        target_write_roots=("D:/Agentic_Solve_Math/CayleyPy_444_Cube/.agent_workspace",),
        allowed_tools=("web_search",),
        callable_agents=("subproject.CayleyPy_444_Cube.01_source_intelligence.head",),
        shared_service_agents=("subproject.CayleyPy_444_Cube.07_editorial_and_history.local_historian",),
        change_requests=(change,),
    )
    trace = RunTrace(
        run_id="run-001",
        handoff_id="handoff-001",
        status="prepared",
        target_agent_id="subproject.CayleyPy_444_Cube.commander",
        artifacts=("handoff.json",),
        events=("prepared",),
    )

    rebuilt = HandoffPackage.from_dict(package.to_dict())
    rebuilt_trace = RunTrace.from_dict(trace.to_dict())

    assert rebuilt.handoff_id == "handoff-001"
    assert rebuilt.task_request.task_id == "task-001"
    assert rebuilt.routing_decision.target_name == "CayleyPy_444_Cube"
    assert rebuilt.change_requests[0].scope == "root_policy"
    assert rebuilt_trace.events == ("prepared",)


def test_execution_record_round_trip() -> None:
    record = ExecutionRecord(
        run_id="run-001",
        handoff_id="handoff-001",
        project_name="CayleyPy_444_Cube",
        mode="legacy",
        command=("python", "main.py", "--no-submit"),
        status="succeeded",
        started_at="2026-03-17T12:00:00Z",
        finished_at="2026-03-17T12:00:01Z",
        exit_code=0,
        stdout_artifact="execution_stdout.txt",
        stderr_artifact="execution_stderr.txt",
        notes=("legacy launcher",),
    )

    rebuilt = ExecutionRecord.from_dict(record.to_dict())

    assert rebuilt.run_id == "run-001"
    assert rebuilt.command[-1] == "--no-submit"
    assert rebuilt.exit_code == 0
