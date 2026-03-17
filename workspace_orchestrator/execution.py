from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from .contracts import DelegationResult, ExecutionRecord
from .delegation import append_run_trace, load_handoff_package, record_delegation_result
from .root_logs import sync_run_logs
from .runs import ensure_run_dir, read_json, utc_now_iso, write_json
from .runtime_registry import ExecutionProfile, get_execution_profile


EXECUTION_RECORD_FILENAME = "execution_record.json"
STDOUT_FILENAME = "execution_stdout.txt"
STDERR_FILENAME = "execution_stderr.txt"
INCOMING_RESULT_FILENAME = "subproject_result.json"


def _run_dir(root: Path, run_id: str) -> Path:
    return root / ".agent_workspace" / "runs" / run_id


def load_execution_record(root: Path, run_id: str) -> ExecutionRecord | None:
    path = _run_dir(root, run_id) / EXECUTION_RECORD_FILENAME
    if not path.exists():
        return None
    return ExecutionRecord.from_dict(read_json(path))


def _project_name_from_package(root: Path, run_id: str) -> str:
    package = load_handoff_package(root, run_id)
    return package.routing_decision.target_name


def build_execution_command(
    root: Path,
    run_id: str,
    passthrough: tuple[str, ...] = (),
    python_executable: str | None = None,
) -> tuple[list[str], ExecutionProfile, str]:
    root = root.resolve()
    project_name = _project_name_from_package(root, run_id)
    profile = get_execution_profile(project_name)
    main_path = root / project_name / "main.py"
    if not main_path.exists():
        raise FileNotFoundError(f"Subproject main.py not found for run {run_id}: {main_path}")

    run_dir = ensure_run_dir(root, run_id)
    command = [python_executable or sys.executable, str(main_path)]
    if profile.mode == "protocol_v1":
        command.extend(
            [
                "--root-handoff",
                str(run_dir / "handoff.json"),
                "--root-run-dir",
                str(run_dir),
            ]
        )
    elif profile.mode != "legacy":
        raise ValueError(f"Unsupported execution mode {profile.mode!r} for project {project_name}")

    command.extend(profile.default_args)
    command.extend(passthrough)
    return command, profile, project_name


def _write_execution_record(root: Path, run_id: str, record: ExecutionRecord) -> Path:
    path = _run_dir(root, run_id) / EXECUTION_RECORD_FILENAME
    write_json(path, record.to_dict())
    return path


def execute_run(
    root: Path,
    run_id: str,
    passthrough: tuple[str, ...] = (),
    timeout_seconds: float | None = None,
    python_executable: str | None = None,
    dry_run: bool = False,
) -> ExecutionRecord:
    root = root.resolve()
    package = load_handoff_package(root, run_id)
    run_dir = ensure_run_dir(root, run_id)
    command, profile, project_name = build_execution_command(
        root,
        run_id,
        passthrough=passthrough,
        python_executable=python_executable,
    )
    stdout_path = run_dir / STDOUT_FILENAME
    stderr_path = run_dir / STDERR_FILENAME
    started_at = utc_now_iso()

    if dry_run:
        record = ExecutionRecord(
            run_id=run_id,
            handoff_id=package.handoff_id,
            project_name=project_name,
            mode=profile.mode,
            command=tuple(command),
            status="dry_run",
            started_at=started_at,
            finished_at=started_at,
            notes=profile.notes,
        )
        _write_execution_record(root, run_id, record)
        append_run_trace(
            root,
            run_id,
            status="dry_run",
            append_artifacts=(EXECUTION_RECORD_FILENAME,),
            append_events=("execution_dry_run",),
        )
        sync_run_logs(root, run_id, "execution")
        return record

    append_run_trace(root, run_id, status="running", append_events=("execution_started",))

    exit_code: int | None = None
    status = "succeeded"
    env = os.environ.copy()
    env["ASM_ROOT_RUN_ID"] = run_id
    env["ASM_ROOT_RUN_DIR"] = str(run_dir)
    env["ASM_ROOT_HANDOFF"] = str(run_dir / "handoff.json")
    env["ASM_EXECUTION_MODE"] = profile.mode

    try:
        with stdout_path.open("w", encoding="utf-8") as stdout_handle, stderr_path.open(
            "w", encoding="utf-8"
        ) as stderr_handle:
            completed = subprocess.run(
                command,
                cwd=root / project_name,
                env=env,
                stdout=stdout_handle,
                stderr=stderr_handle,
                text=True,
                timeout=timeout_seconds,
            )
        exit_code = completed.returncode
        if exit_code != 0:
            status = "failed"
    except subprocess.TimeoutExpired:
        status = "timed_out"

    finished_at = utc_now_iso()
    record = ExecutionRecord(
        run_id=run_id,
        handoff_id=package.handoff_id,
        project_name=project_name,
        mode=profile.mode,
        command=tuple(command),
        status=status,
        started_at=started_at,
        finished_at=finished_at,
        exit_code=exit_code,
        stdout_artifact=STDOUT_FILENAME,
        stderr_artifact=STDERR_FILENAME,
        notes=profile.notes,
    )
    _write_execution_record(root, run_id, record)

    if status == "succeeded":
        append_run_trace(
            root,
            run_id,
            status="awaiting_result",
            append_artifacts=(EXECUTION_RECORD_FILENAME, STDOUT_FILENAME, STDERR_FILENAME),
            append_events=("execution_succeeded",),
        )
        sync_run_logs(root, run_id, "execution")
        incoming_result_path = run_dir / INCOMING_RESULT_FILENAME
        if incoming_result_path.exists():
            append_run_trace(
                root,
                run_id,
                append_artifacts=(INCOMING_RESULT_FILENAME,),
                append_events=("incoming_result_detected",),
            )
            incoming = DelegationResult.from_dict(read_json(incoming_result_path))
            record_delegation_result(root, run_id, incoming)
    else:
        failure_event = "execution_timed_out" if status == "timed_out" else f"execution_failed:{exit_code}"
        append_run_trace(
            root,
            run_id,
            status="execution_failed",
            append_artifacts=(EXECUTION_RECORD_FILENAME, STDOUT_FILENAME, STDERR_FILENAME),
            append_events=(failure_event,),
        )
        sync_run_logs(root, run_id, "execution")

    return record
