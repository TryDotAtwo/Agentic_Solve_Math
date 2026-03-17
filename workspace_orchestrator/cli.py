from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .acl import can_call_agent
from .communications import callable_targets
from .contracts import DelegationResult
from .delegation import describe_run, load_handoff_package, record_delegation_result
from .execution import execute_run
from .handoff import (
    build_handoff_for_subproject,
    build_task_request_from_intake,
    default_research_plan,
    materialize_handoff_package,
)
from .intake import find_latest_intake_file, parse_intake_file
from .openai_runtime import build_root_runtime_spec, build_subproject_runtime_spec, detect_agents_sdk
from .organization import ROOT_EXECUTIVE_ID, build_root_organization, build_subproject_organization
from .visibility import can_read_path, can_write_path
from .workspace import build_snapshot


def _workspace_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _build_org(project: str | None):
    root = _workspace_root()
    if project:
        return build_subproject_organization(root, project)
    return build_root_organization(root)


def _infer_project_name(agent_id: str) -> str | None:
    if agent_id == ROOT_EXECUTIVE_ID or agent_id.startswith("root."):
        return None
    if agent_id.startswith("subproject."):
        parts = agent_id.split(".")
        if len(parts) < 3:
            raise SystemExit(f"Invalid subproject agent id: {agent_id}")
        return parts[1]
    raise SystemExit(f"Unknown agent id namespace: {agent_id}")


def _load_agent_manifest(agent_id: str):
    project = _infer_project_name(agent_id)
    return _build_org(project).get_agent(agent_id)


def _print_overview() -> int:
    root = _workspace_root()
    snapshot = build_snapshot(root)

    print("Agentic Solve Math - root meta-orchestrator")
    print(f"root: {snapshot.root}")
    print(f"rules: {snapshot.rules_dir}")
    print(f"intake: {snapshot.intake_dir}")
    print("")
    print("isolated subprojects:")
    for project in snapshot.subprojects:
        flags = []
        if project.has_agents:
            flags.append("AGENTS")
        if project.has_readme:
            flags.append("README")
        if project.has_main:
            flags.append("main.py")
        flag_text = ", ".join(flags) if flags else "no markers"
        print(f"- {project.name} [{project.role}] ({flag_text})")
    return 0


def _print_subprojects(as_json: bool) -> int:
    snapshot = build_snapshot(_workspace_root())
    if as_json:
        print(json.dumps([item.to_dict() for item in snapshot.subprojects], ensure_ascii=False, indent=2))
        return 0

    for project in snapshot.subprojects:
        print(f"{project.name}\t{project.role}\tisolated={project.isolated}\tmain={project.has_main}")
    return 0


def _print_intake(path: Path, as_json: bool) -> int:
    brief = parse_intake_file(path)
    if as_json:
        print(json.dumps(brief.to_dict(), ensure_ascii=False, indent=2))
        return 0

    print(f"intake: {brief.source_file}")
    print("")
    print("competition links:")
    for item in brief.competition_links:
        print(f"- {item}")
    print("notebooks:")
    for item in brief.notebook_links:
        print(f"- {item}")
    print("discussions:")
    for item in brief.discussion_links:
        print(f"- {item}")
    print("papers:")
    for item in brief.paper_links:
        print(f"- {item}")
    print("repositories:")
    for item in brief.repo_links:
        print(f"- {item}")
    print("priorities:")
    for item in brief.priorities:
        print(f"- {item}")
    print("notes:")
    for item in brief.notes:
        print(f"- {item}")
    return 0


def _resolve_intake_path(path_str: str | None) -> Path:
    if path_str:
        return Path(path_str)
    return find_latest_intake_file(_workspace_root() / "kaggle_intake")


def _delegate(project_name: str, passthrough: list[str]) -> int:
    root = _workspace_root()
    main_path = root / project_name / "main.py"
    if not main_path.exists():
        raise SystemExit(f"Subproject main.py not found: {main_path}")

    cmd = [sys.executable, str(main_path), *passthrough]
    print("Delegating to subproject:", " ".join(cmd))
    completed = subprocess.run(cmd)
    return completed.returncode


def _print_org_summary(project: str | None, as_json: bool) -> int:
    org = _build_org(project)
    if as_json:
        print(json.dumps(org.to_dict(), ensure_ascii=False, indent=2))
        return 0

    print(f"organization: {org.name}")
    print(f"scope: {org.scope}")
    print(f"agents: {org.agent_count}")
    print("departments:")
    for department in org.departments:
        shared = ", ".join(department.shared_service_agent_ids) if department.shared_service_agent_ids else "-"
        print(
            f"- {department.key}\thead={department.head_agent_id}\tstaff={len(department.staff_agent_ids)}\tshared={shared}"
        )
    return 0


def _print_agents(project: str | None, as_json: bool) -> int:
    org = _build_org(project)
    if as_json:
        print(json.dumps([agent.to_dict() for agent in org.agents], ensure_ascii=False, indent=2))
        return 0

    for agent in org.agents:
        print(
            f"{agent.agent_id}\t{agent.rank}\tdepartment={agent.department_key}\tshared={agent.shared_service}"
        )
    return 0


def _print_agent_manifest(agent_id: str, as_json: bool) -> int:
    manifest = _load_agent_manifest(agent_id)
    if as_json:
        print(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2))
        return 0

    print(f"agent: {manifest.agent_id}")
    print(f"display: {manifest.display_name}")
    print(f"scope: {manifest.scope}")
    print(f"department: {manifest.department_key}")
    print(f"rank: {manifest.rank}")
    print(f"shared_service: {manifest.shared_service}")
    print("read_roots:")
    for item in manifest.read_roots:
        print(f"- {item}")
    print("write_roots:")
    for item in manifest.write_roots:
        print(f"- {item}")
    print("hidden_roots:")
    for item in manifest.hidden_roots:
        print(f"- {item}")
    print("callable_agents:")
    for item in manifest.callable_agents:
        print(f"- {item}")
    return 0


def _print_callable_targets(agent_id: str, as_json: bool) -> int:
    project = _infer_project_name(agent_id)
    org = _build_org(project)
    targets = callable_targets(org, agent_id)
    if as_json:
        print(json.dumps(list(targets), ensure_ascii=False, indent=2))
        return 0

    for item in targets:
        print(item)
    return 0


def _check_call(caller_id: str, callee_id: str) -> int:
    caller = _load_agent_manifest(caller_id)
    callee = _load_agent_manifest(callee_id)
    allowed = can_call_agent(caller, callee)
    print(
        json.dumps(
            {
                "caller": caller_id,
                "callee": callee_id,
                "allowed": allowed,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if allowed else 1


def _check_path(agent_id: str, path: Path, mode: str) -> int:
    manifest = _load_agent_manifest(agent_id)
    allowed = can_read_path(manifest, path) if mode == "read" else can_write_path(manifest, path)
    print(
        json.dumps(
            {
                "agent": agent_id,
                "path": str(path),
                "mode": mode,
                "allowed": allowed,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if allowed else 1


def _build_handoff(
    project_name: str,
    objective: str,
    intake_file: str | None,
    requester_agent_id: str,
    research_questions: list[str],
    as_json: bool,
) -> int:
    root = _workspace_root()
    intake_path = _resolve_intake_path(intake_file)
    brief = parse_intake_file(intake_path)
    task_request = build_task_request_from_intake(
        brief,
        objective=objective,
        requested_by=requester_agent_id,
    )
    research_plan = default_research_plan(
        objective=objective,
        research_questions=tuple(research_questions),
    )
    package = build_handoff_for_subproject(
        root,
        project_name=project_name,
        task_request=task_request,
        research_plan=research_plan,
        requester_agent_id=requester_agent_id,
    )
    run_dir = materialize_handoff_package(root, package)
    payload = {
        "run_id": package.run_id,
        "handoff_id": package.handoff_id,
        "run_dir": str(run_dir),
        "target_agent_id": package.target_agent_id,
        "requester_agent_id": package.requester_agent_id,
        "intake_file": str(intake_path),
        "objective": objective,
    }

    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"run: {package.run_id}")
    print(f"handoff: {package.handoff_id}")
    print(f"requester: {package.requester_agent_id}")
    print(f"target: {package.target_agent_id}")
    print(f"intake: {intake_path}")
    print(f"objective: {objective}")
    print(f"run_dir: {run_dir}")
    return 0


def _print_run(run_id: str, as_json: bool) -> int:
    payload = describe_run(_workspace_root(), run_id)
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    handoff = payload["handoff"]
    trace = payload["trace"]
    result = payload["result"]
    print(f"run: {payload['run_id']}")
    print(f"dir: {payload['run_dir']}")
    print(f"status: {trace['status']}")
    print(f"target: {handoff['target_agent_id']}")
    print(f"requester: {handoff['requester_agent_id']}")
    print(f"objective: {handoff['task_request']['objective']}")
    print(f"intake: {handoff['task_request']['intake_file']}")
    if result:
        print(f"result_status: {result['status']}")
        print(f"result_summary: {result['summary']}")
    else:
        print("result_status: pending")
    print("files:")
    for item in payload["files"]:
        print(f"- {item}")
    return 0


def _record_result(
    run_id: str,
    produced_by: str,
    status: str,
    summary: str,
    canonical_paths: list[str],
    as_json: bool,
) -> int:
    root = _workspace_root()
    package = load_handoff_package(root, run_id)
    result = DelegationResult(
        handoff_id=package.handoff_id,
        produced_by=produced_by,
        status=status,
        summary=summary,
        canonical_paths=tuple(canonical_paths),
    )
    result_path = record_delegation_result(root, run_id, result)
    payload = {
        "run_id": run_id,
        "handoff_id": package.handoff_id,
        "status": status,
        "produced_by": produced_by,
        "result_path": str(result_path),
    }

    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"run: {run_id}")
    print(f"handoff: {package.handoff_id}")
    print(f"status: {status}")
    print(f"produced_by: {produced_by}")
    print(f"result_path: {result_path}")
    return 0


def _execute_run(
    run_id: str,
    timeout_seconds: float | None,
    dry_run: bool,
    passthrough: list[str],
    as_json: bool,
) -> int:
    record = execute_run(
        _workspace_root(),
        run_id,
        passthrough=tuple(passthrough),
        timeout_seconds=timeout_seconds,
        dry_run=dry_run,
    )
    payload = record.to_dict()
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"run: {record.run_id}")
        print(f"project: {record.project_name}")
        print(f"mode: {record.mode}")
        print(f"status: {record.status}")
        print(f"command: {' '.join(record.command)}")
        if record.exit_code is not None:
            print(f"exit_code: {record.exit_code}")
    return 0 if record.status in {"succeeded", "dry_run"} else 1


def _print_sdk_status(as_json: bool) -> int:
    payload = detect_agents_sdk().to_dict()
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"package: {payload['package_name']}")
    print(f"available: {payload['available']}")
    print(f"version: {payload['version'] or '-'}")
    print(f"reason: {payload['reason']}")
    return 0


def _print_runtime_summary(project: str | None, run_id: str | None, as_json: bool) -> int:
    root = _workspace_root()
    if project:
        payload = build_subproject_runtime_spec(root, project, run_id=run_id).to_dict()
    else:
        payload = build_root_runtime_spec(root, run_id=run_id).to_dict()

    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"team: {payload['team_id']}")
    print(f"scope: {payload['scope']}")
    print(f"manager: {payload['manager_agent_id']}")
    print(f"orchestration_pattern: {payload['orchestration_pattern']}")
    print(f"agents_sdk_available: {payload['agents_sdk']['available']}")
    print(f"run_id: {payload['metadata']['run_id'] or '-'}")
    print(f"handoff_id: {payload['metadata']['handoff_id'] or '-'}")
    print(f"objective: {payload['metadata']['objective'] or '-'}")
    print(f"agent_count: {payload['agent_count']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args_list = list(sys.argv[1:] if argv is None else argv)

    # Legacy convenience: `python main.py --no-submit` should still reach C4.
    if args_list and args_list[0].startswith("-"):
        return _delegate("CayleyPy_444_Cube", args_list)

    parser = argparse.ArgumentParser(
        description="Root launcher for the Agentic Solve Math meta-orchestrator."
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("overview", help="Show root-level overview and discovered subprojects.")

    p = sub.add_parser("list-subprojects", help="List isolated subprojects known to the root.")
    p.add_argument("--json", action="store_true", help="Print JSON instead of plain text.")

    p = sub.add_parser("parse-intake", help="Parse a Kaggle intake markdown file.")
    p.add_argument("file", nargs="?", default=None, help="Path to intake markdown file.")
    p.add_argument("--json", action="store_true", help="Print JSON instead of plain text.")

    p = sub.add_parser("delegate", help="Delegate execution into a subproject main.py.")
    p.add_argument("subproject", help="Subproject folder name, for example CayleyPy_444_Cube.")
    p.add_argument("args", nargs=argparse.REMAINDER, help="Arguments forwarded to the subproject.")

    p = sub.add_parser("run-c4", help="Convenience wrapper around CayleyPy_444_Cube/main.py.")
    p.add_argument("args", nargs=argparse.REMAINDER, help="Arguments forwarded to the C4 subproject.")

    p = sub.add_parser("org-summary", help="Show the configured root or subproject organization.")
    p.add_argument("--project", default=None, help="Subproject name. Omit for root organization.")
    p.add_argument("--json", action="store_true", help="Print JSON instead of plain text.")

    p = sub.add_parser("list-agents", help="List configured agents for root or a subproject.")
    p.add_argument("--project", default=None, help="Subproject name. Omit for root organization.")
    p.add_argument("--json", action="store_true", help="Print JSON instead of plain text.")

    p = sub.add_parser("agent-manifest", help="Print a manifest for a configured agent.")
    p.add_argument("agent_id", help="Agent id like root.orchestrator or subproject.CayleyPy_444_Cube.commander")
    p.add_argument("--json", action="store_true", help="Print JSON instead of plain text.")

    p = sub.add_parser("callable-targets", help="Show which agents a configured agent may call.")
    p.add_argument("agent_id", help="Agent id like root.orchestrator or subproject.CayleyPy_444_Cube.commander")
    p.add_argument("--json", action="store_true", help="Print JSON instead of plain text.")

    p = sub.add_parser("can-call", help="Check whether one agent may call another.")
    p.add_argument("caller_id", help="Caller agent id.")
    p.add_argument("callee_id", help="Callee agent id.")

    p = sub.add_parser("check-path", help="Check whether an agent may read or write a path.")
    p.add_argument("agent_id", help="Agent id.")
    p.add_argument("path", help="Path to check.")
    p.add_argument("--mode", choices=("read", "write"), default="read", help="Permission mode.")

    p = sub.add_parser("build-handoff", help="Prepare a root-owned handoff package for a subproject.")
    p.add_argument("--project", required=True, help="Subproject folder name, for example CayleyPy_444_Cube.")
    p.add_argument("--objective", required=True, help="Research objective for the target subproject team.")
    p.add_argument("--intake-file", default=None, help="Explicit intake markdown file. Defaults to the latest one.")
    p.add_argument(
        "--requester",
        default="root.02_research_intelligence.head",
        help="Root agent id responsible for the handoff.",
    )
    p.add_argument(
        "--research-question",
        action="append",
        default=[],
        help="Explicit research question for the handoff plan. May be repeated.",
    )
    p.add_argument("--json", action="store_true", help="Print JSON instead of plain text.")

    p = sub.add_parser("show-run", help="Inspect a prepared root-owned run directory.")
    p.add_argument("run_id", help="Run id like run-123456789abc.")
    p.add_argument("--json", action="store_true", help="Print JSON instead of plain text.")

    p = sub.add_parser("record-result", help="Record a delegation result for a prepared run.")
    p.add_argument("run_id", help="Run id like run-123456789abc.")
    p.add_argument("--produced-by", required=True, help="Agent id that produced the result.")
    p.add_argument("--status", required=True, help="Result status, for example completed or escalated.")
    p.add_argument("--summary", required=True, help="Short human-readable summary.")
    p.add_argument(
        "--canonical-path",
        action="append",
        default=[],
        help="Canonical artifact path produced by the delegated team. May be repeated.",
    )
    p.add_argument("--json", action="store_true", help="Print JSON instead of plain text.")

    p = sub.add_parser("execute-run", help="Launch the delegated local runtime for a prepared run.")
    p.add_argument("run_id", help="Run id like run-123456789abc.")
    p.add_argument(
        "--timeout-seconds",
        type=float,
        default=None,
        help="Optional subprocess timeout in seconds.",
    )
    p.add_argument("--dry-run", action="store_true", help="Only materialize the planned execution record.")
    p.add_argument(
        "--arg",
        action="append",
        default=[],
        help="Passthrough argument forwarded to the delegated local runtime. May be repeated.",
    )
    p.add_argument("--json", action="store_true", help="Print JSON instead of plain text.")

    p = sub.add_parser("sdk-status", help="Inspect local OpenAI Agents SDK availability.")
    p.add_argument("--json", action="store_true", help="Print JSON instead of plain text.")

    p = sub.add_parser("runtime-summary", help="Show the OpenAI runtime team spec for root or a subproject.")
    p.add_argument("--project", default=None, help="Subproject name. Omit for root runtime.")
    p.add_argument("--run-id", default=None, help="Optional prepared run id for contextual metadata.")
    p.add_argument("--json", action="store_true", help="Print JSON instead of plain text.")

    parsed = parser.parse_args(args_list)

    if parsed.command in (None, "overview"):
        return _print_overview()
    if parsed.command == "list-subprojects":
        return _print_subprojects(parsed.json)
    if parsed.command == "parse-intake":
        target = Path(parsed.file) if parsed.file else find_latest_intake_file(_workspace_root() / "kaggle_intake")
        return _print_intake(target, parsed.json)
    if parsed.command == "delegate":
        passthrough = parsed.args[1:] if parsed.args and parsed.args[0] == "--" else parsed.args
        return _delegate(parsed.subproject, passthrough)
    if parsed.command == "run-c4":
        passthrough = parsed.args[1:] if parsed.args and parsed.args[0] == "--" else parsed.args
        return _delegate("CayleyPy_444_Cube", passthrough)
    if parsed.command == "org-summary":
        return _print_org_summary(parsed.project, parsed.json)
    if parsed.command == "list-agents":
        return _print_agents(parsed.project, parsed.json)
    if parsed.command == "agent-manifest":
        return _print_agent_manifest(parsed.agent_id, parsed.json)
    if parsed.command == "callable-targets":
        return _print_callable_targets(parsed.agent_id, parsed.json)
    if parsed.command == "can-call":
        return _check_call(parsed.caller_id, parsed.callee_id)
    if parsed.command == "check-path":
        return _check_path(parsed.agent_id, Path(parsed.path), parsed.mode)
    if parsed.command == "build-handoff":
        return _build_handoff(
            parsed.project,
            parsed.objective,
            parsed.intake_file,
            parsed.requester,
            parsed.research_question,
            parsed.json,
        )
    if parsed.command == "show-run":
        return _print_run(parsed.run_id, parsed.json)
    if parsed.command == "record-result":
        return _record_result(
            parsed.run_id,
            parsed.produced_by,
            parsed.status,
            parsed.summary,
            parsed.canonical_path,
            parsed.json,
        )
    if parsed.command == "execute-run":
        return _execute_run(
            parsed.run_id,
            parsed.timeout_seconds,
            parsed.dry_run,
            parsed.arg,
            parsed.json,
        )
    if parsed.command == "sdk-status":
        return _print_sdk_status(parsed.json)
    if parsed.command == "runtime-summary":
        return _print_runtime_summary(parsed.project, parsed.run_id, parsed.json)

    raise SystemExit(f"Unknown command: {parsed.command}")
