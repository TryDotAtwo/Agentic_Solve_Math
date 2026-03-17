from __future__ import annotations

from pathlib import Path

from .contracts import DelegationResult, HandoffPackage, RunTrace
from .root_logs import sync_run_logs
from .runs import ensure_run_dir, read_json, write_json


def _run_dir(root: Path, run_id: str) -> Path:
    return root / ".agent_workspace" / "runs" / run_id


def load_handoff_package(root: Path, run_id: str) -> HandoffPackage:
    run_dir = _run_dir(root, run_id)
    return HandoffPackage.from_dict(read_json(run_dir / "handoff.json"))


def load_run_trace(root: Path, run_id: str) -> RunTrace:
    run_dir = _run_dir(root, run_id)
    return RunTrace.from_dict(read_json(run_dir / "trace.json"))


def append_run_trace(
    root: Path,
    run_id: str,
    status: str | None = None,
    append_artifacts: tuple[str, ...] = (),
    append_events: tuple[str, ...] = (),
) -> RunTrace:
    trace = load_run_trace(root, run_id)
    artifacts = tuple(dict.fromkeys((*trace.artifacts, *append_artifacts)))
    events = (*trace.events, *append_events)
    updated = RunTrace(
        run_id=trace.run_id,
        handoff_id=trace.handoff_id,
        status=status or trace.status,
        target_agent_id=trace.target_agent_id,
        artifacts=artifacts,
        events=events,
    )
    write_json(_run_dir(root, run_id) / "trace.json", updated.to_dict())
    return updated


def load_delegation_result(root: Path, run_id: str) -> DelegationResult | None:
    run_dir = _run_dir(root, run_id)
    result_path = run_dir / "delegation_result.json"
    if not result_path.exists():
        return None
    return DelegationResult.from_dict(read_json(result_path))


def record_delegation_result(root: Path, run_id: str, result: DelegationResult) -> Path:
    package = load_handoff_package(root, run_id)
    if package.handoff_id != result.handoff_id:
        raise ValueError(
            f"Handoff id mismatch for run {run_id}: expected {package.handoff_id}, got {result.handoff_id}"
        )

    run_dir = ensure_run_dir(root, run_id)
    result_path = run_dir / "delegation_result.json"
    write_json(result_path, result.to_dict())
    append_run_trace(
        root,
        run_id,
        status=result.status,
        append_artifacts=("delegation_result.json",),
        append_events=(f"result_recorded:{result.status}",),
    )
    sync_run_logs(root, run_id, "result")
    return result_path


def describe_run(root: Path, run_id: str) -> dict[str, object]:
    package = load_handoff_package(root, run_id)
    trace = load_run_trace(root, run_id)
    result = load_delegation_result(root, run_id)
    run_dir = _run_dir(root, run_id)
    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "handoff": package.to_dict(),
        "trace": trace.to_dict(),
        "result": result.to_dict() if result else None,
        "files": sorted(path.name for path in run_dir.iterdir()),
    }
