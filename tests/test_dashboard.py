import json
from pathlib import Path

from workspace_orchestrator.agent_profiles import append_department_milestone
from workspace_orchestrator.contracts import DelegationResult, ExecutionRecord
from workspace_orchestrator.dashboard import build_dashboard_snapshot, load_dashboard_run_detail
from workspace_orchestrator.delegation import append_run_trace, record_delegation_result
from workspace_orchestrator.handoff import (
    build_handoff_for_subproject,
    build_task_request_from_intake,
    default_research_plan,
    materialize_handoff_package,
)
from workspace_orchestrator.intake import parse_intake_file
from workspace_orchestrator.runs import ensure_run_dir, write_json


def _prepare_root(tmp_path: Path) -> Path:
    (tmp_path / "rules").mkdir()
    logs_dir = tmp_path / "rules" / "logs"
    logs_dir.mkdir()
    (logs_dir / "RESEARCH_JOURNAL.md").write_text(
        """# Research Journal

## 2026-03-20 | Session: Dashboard work

Root dashboard planning entry.

## 2026-03-19 | Session: Earlier note

Previous research note.
""",
        encoding="utf-8",
    )
    (logs_dir / "AGENT_INTERACTIONS_LOG.md").write_text(
        """# Agent Interactions Log

## 2026-03-20 | Interaction 1 - Dashboard sync

Recent interaction entry.
""",
        encoding="utf-8",
    )
    (logs_dir / "USER_PROMPTS_LOG.md").write_text(
        """# User Prompts Log

## 2026-03-20 | Prompt 022 | Russian

Please build a browser dashboard.
""",
        encoding="utf-8",
    )
    (tmp_path / "kaggle_intake").mkdir()
    (tmp_path / "workspace_orchestrator").mkdir()
    project_dir = tmp_path / "CayleyPy_TestHarness"
    project_dir.mkdir()
    (project_dir / "main.py").write_text("print('fixture')\n", encoding="utf-8")
    (project_dir / "README.md").write_text("# Fixture project\n", encoding="utf-8")
    (tmp_path / "kaggle_intake" / "sample.md").write_text(
        """# Intake

- https://www.kaggle.com/competitions/example-comp
- https://arxiv.org/abs/1234.5678
""",
        encoding="utf-8",
    )
    (tmp_path / ".env").write_text(
        "\n".join(
            (
                "OPENAI_API_KEY=AIza-test-key",
                "ASM_OPENAI_MODEL=gemini-2.5-flash",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    sessions_dir = tmp_path / ".agent_workspace" / "sessions"
    sessions_dir.mkdir(parents=True)
    (sessions_dir / "root_sessions.sqlite").write_text("", encoding="utf-8")
    return tmp_path


def _materialize_run(root: Path, run_id: str, objective: str) -> str:
    brief = parse_intake_file(root / "kaggle_intake" / "sample.md")
    request = build_task_request_from_intake(
        brief,
        objective=objective,
        task_id=f"task-{run_id}",
        requested_by="root.02_research_intelligence.head",
    )
    plan = default_research_plan(
        objective=objective,
        plan_id=f"plan-{run_id}",
        research_questions=("What should the team research first?",),
    )
    package = build_handoff_for_subproject(
        root,
        project_name="CayleyPy_TestHarness",
        task_request=request,
        research_plan=plan,
        requester_agent_id="root.02_research_intelligence.head",
        run_id=run_id,
        handoff_id=f"handoff-{run_id}",
    )
    materialize_handoff_package(root, package)
    return package.run_id


def test_build_dashboard_snapshot_summarizes_bootstrap_runs_and_logs(tmp_path: Path) -> None:
    root = _prepare_root(tmp_path)
    active_run_id = _materialize_run(root, "run-active", "Investigate active fixture")
    completed_run_id = _materialize_run(root, "run-completed", "Investigate completed fixture")

    append_run_trace(root, active_run_id, status="running", append_events=("execution_started",))

    completed_execution = ExecutionRecord(
        run_id=completed_run_id,
        handoff_id=f"handoff-{completed_run_id}",
        project_name="CayleyPy_TestHarness",
        mode="protocol_v1",
        command=("python", "main.py"),
        status="succeeded",
        started_at="2026-03-20T08:00:00Z",
        finished_at="2026-03-20T08:05:00Z",
        exit_code=0,
        stdout_artifact="execution_stdout.txt",
        stderr_artifact="execution_stderr.txt",
        notes=("fixture execution",),
    )
    write_json(
        ensure_run_dir(root, completed_run_id) / "execution_record.json",
        completed_execution.to_dict(),
    )
    result = DelegationResult(
        handoff_id=f"handoff-{completed_run_id}",
        produced_by="subproject.CayleyPy_TestHarness.commander",
        status="completed",
        summary="Fixture research finished.",
        canonical_paths=("CayleyPy_TestHarness/docs/final.md",),
    )
    record_delegation_result(root, completed_run_id, result)
    append_department_milestone(
        root,
        "root.06_editorial_and_history.head",
        title="Prepared article milestone draft",
        summary="High-level narrative for the current phase is ready.",
        next_actions=("Align evidence excerpts",),
    )

    snapshot = build_dashboard_snapshot(root, run_limit=10, log_limit=5).to_dict()

    assert snapshot["bootstrap"]["configured"] is True
    assert snapshot["bootstrap"]["provider_route"] == "google_openai_compatible"
    assert snapshot["stats"]["subprojects_total"] == 1
    assert snapshot["stats"]["runs_total"] == 2
    assert snapshot["stats"]["runs_active"] == 1
    assert snapshot["stats"]["runs_completed"] == 1
    assert snapshot["root_team"]["agent_count"] == 25
    assert snapshot["root_team"]["department_count"] == 8
    assert snapshot["root_team"]["manager"]["agent_id"] == "root.orchestrator"
    assert snapshot["runs"][0]["run_id"] == completed_run_id
    assert snapshot["runs"][0]["result_status"] == "completed"
    assert snapshot["runs"][1]["run_id"] == active_run_id
    assert snapshot["runs"][1]["trace_status"] == "running"
    assert any(node["id"] == "root.orchestrator" for node in snapshot["graph"]["nodes"])
    assert snapshot["graph"]["edges"]
    assert snapshot["milestones"][0]["title"] == "Prepared article milestone draft"
    assert snapshot["agents"][0]["memory_path"].endswith("memory.md")
    assert snapshot["logs"]["research_journal"][0]["title"].startswith("2026-03-20")
    assert snapshot["logs"]["agent_interactions"][0]["title"].startswith("2026-03-20")
    assert snapshot["logs"]["user_prompts"][0]["title"].startswith("2026-03-20")


def test_load_dashboard_run_detail_returns_canonical_run_payload(tmp_path: Path) -> None:
    root = _prepare_root(tmp_path)
    run_id = _materialize_run(root, "run-detail", "Inspect a single run")
    append_run_trace(root, run_id, status="awaiting_result", append_events=("execution_succeeded",))

    detail = load_dashboard_run_detail(root, run_id)

    assert detail["run_id"] == run_id
    assert detail["trace"]["status"] == "awaiting_result"
    assert detail["handoff"]["routing_decision"]["target_name"] == "CayleyPy_TestHarness"
    assert "handoff.json" in detail["files"]
