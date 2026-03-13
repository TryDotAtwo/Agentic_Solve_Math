from __future__ import annotations

"""
Minimal autosubmit helper for the CayleyPy-444-Cube Kaggle competition.

Responsibilities:
- load a submission CSV;
- validate its schema (id, solution);
- submit via Kaggle CLI (if available) or HTTP fallback;
- log attempts and responses to a local log file.

ASSUMPTION:
- The competition slug is "cayleypy-444-cube". Update DEFAULT_KAGGLE_COMPETITION
  once the actual slug is confirmed.
"""

import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_KAGGLE_COMPETITION = "cayleypy-444-cube"  # TODO: confirm actual slug
LOG_FILE = Path(__file__).resolve().parent.parent / "autosubmit.log"


def _log_event(event: str, **data: Any) -> None:
    """Append a single JSON line describing an autosubmit event."""
    payload = {
        "timestamp": time.time(),
        "event": event,
        **data,
    }
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        # Logging must never crash the main flow.
        pass


def load_submission_csv(path: Path) -> pd.DataFrame:
    """Load a submission CSV as a DataFrame, with basic error handling."""
    path = path.resolve()
    if not path.exists():
        raise SystemExit(f"Submission file not found: {path}")
    try:
        df = pd.read_csv(path)
    except Exception as exc:  # pragma: no cover - defensive
        raise SystemExit(f"Failed to read CSV {path}: {exc}") from exc
    _log_event("load_submission_csv_ok", file=str(path), n_rows=len(df), columns=list(df.columns))
    return df


def validate_submission_schema(df: pd.DataFrame) -> None:
    """
    Validate that the DataFrame matches the expected submission schema.

    Expected minimal columns:
    - id (integer-like, unique)
    - solution (string-like)

    Raises ValueError on problems.
    """
    missing = [c for c in ("id", "solution") if c not in df.columns]
    if missing:
        _log_event("schema_validation_failed", reason="missing_columns", missing=missing)
        raise ValueError(f"Submission is missing required columns: {missing}")

    if df["id"].isnull().any():
        _log_event("schema_validation_failed", reason="null_ids")
        raise ValueError("Submission contains null values in 'id' column.")

    if df["id"].duplicated().any():
        _log_event("schema_validation_failed", reason="duplicate_ids")
        raise ValueError("Submission has duplicated 'id' values.")

    # Basic integer-like check: try to cast to int without changing the values.
    try:
        ids_as_int = df["id"].astype("int64")
    except Exception:
        _log_event("schema_validation_failed", reason="id_not_integer_like")
        raise ValueError("Column 'id' must be integer-like.")
    if (ids_as_int.astype(str) != df["id"].astype(str)).any():
        # Very conservative check; if this fires, better to fix DataFrame upstream.
        _log_event("schema_validation_failed", reason="id_cast_mismatch")
        raise ValueError("Column 'id' cannot be safely interpreted as integer ids.")

    if df["solution"].isnull().any():
        _log_event("schema_validation_failed", reason="null_solutions")
        raise ValueError("Submission contains null values in 'solution' column.")

    # Light sanity check: enforce string dtype for solution.
    try:
        df["solution"].astype(str)
    except Exception:
        _log_event("schema_validation_failed", reason="solution_not_string_like")
        raise ValueError("Column 'solution' must be coercible to string.")

    _log_event(
        "schema_validation_ok",
        n_rows=len(df),
        columns=list(df.columns),
    )


def _resolve_competition_slug(competition: str | None) -> str:
    """Resolve competition slug from CLI arg, env var, or default."""
    if competition:
        return competition
    env_slug = os.environ.get("KAGGLE_COMPETITION")
    if env_slug:
        return env_slug
    return DEFAULT_KAGGLE_COMPETITION


def _find_kaggle_config_dirs(project_root: Path) -> list[Path]:
    """Return candidate directories where kaggle.json may live."""
    dirs: list[Path] = []
    if os.environ.get("KAGGLE_CONFIG_DIR"):
        dirs.append(Path(os.environ["KAGGLE_CONFIG_DIR"]))
    dirs.append(project_root)
    dirs.append(Path.home() / ".kaggle")
    return dirs


def _kaggle_submit_http(file_path: Path, competition: str, message: str, config_dirs: list[Path]) -> None:
    """Fallback: submit using Kaggle HTTP API directly (legacy API, may be deprecated)."""
    try:
        import requests  # type: ignore[import]
    except ImportError as exc:
        raise SystemExit("HTTP submission requires the 'requests' package: pip install requests") from exc

    kaggle_json_path: Path | None = None
    for d in config_dirs:
        p = d / "kaggle.json"
        if p.exists():
            kaggle_json_path = p
            break

    if kaggle_json_path is None:
        _log_event("kaggle_http_no_kaggle_json", config_dirs=[str(d) for d in config_dirs])
        raise SystemExit(
            "Could not find kaggle.json. Place it either in this project root or in ~/.kaggle/.\n"
            "Download from Kaggle: Settings → API → Create New Token."
        )

    with kaggle_json_path.open(encoding="utf-8") as f:
        creds = json.load(f)
    username = creds.get("username") or creds.get("username_")
    key = creds.get("key") or creds.get("key_")
    if not username or not key:
        raise SystemExit("kaggle.json must contain 'username' and 'key' fields.")

    auth = base64.b64encode(f"{username}:{key}".encode("utf-8")).decode("utf-8")
    url = f"https://www.kaggle.com/api/v1/competitions/submit/{competition}"

    with file_path.open("rb") as f:
        files = {"submission": (file_path.name, f, "text/csv")}
        data = {"description": (None, message or file_path.name)}
        resp = requests.post(
            url,
            files=files,
            data=data,
            headers={"Authorization": f"Basic {auth}"},
            timeout=120,
        )

    _log_event(
        "kaggle_http_response",
        status_code=resp.status_code,
        text_preview=(resp.text or "")[:300],
    )

    if resp.status_code == 200:
        print("Submission sent via Kaggle HTTP API. Check the competition page for results.")
        return
    if resp.status_code == 404:
        raise SystemExit(
            "Kaggle returned 404 for the legacy HTTP API.\n"
            "Fix and use the official Kaggle CLI instead (pip install 'kaggle>=1.5.0,<1.8.0')."
        )
    raise SystemExit(f"Kaggle HTTP API returned {resp.status_code}: {resp.text[:500]}")


def _do_kaggle_submit(file_path: Path, competition: str, message: str) -> None:
    """Submit a file using Kaggle CLI, with HTTP fallback on specific errors."""
    import shutil

    project_root = Path(__file__).resolve().parent.parent
    config_dirs = _find_kaggle_config_dirs(project_root)

    kaggle_exe = shutil.which("kaggle")
    if not kaggle_exe and os.name == "nt":
        scripts = Path(sys.executable).resolve().parent / "Scripts" / "kaggle.exe"
        if scripts.exists():
            kaggle_exe = str(scripts)

    if kaggle_exe:
        cmd = [
            kaggle_exe,
            "competitions",
            "submit",
            "-c",
            competition,
            "-f",
            str(file_path),
            "-m",
            message or file_path.name,
        ]
    else:
        cmd = [
            sys.executable,
            "-m",
            "kaggle",
            "competitions",
            "submit",
            "-c",
            competition,
            "-f",
            str(file_path),
            "-m",
            message or file_path.name,
        ]

    env = os.environ.copy()
    if (project_root / "kaggle.json").exists():
        env["KAGGLE_CONFIG_DIR"] = str(project_root)

    print("Submitting to Kaggle:", " ".join(cmd))
    try:
        proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, cmd, proc.stdout, proc.stderr)
        _log_event("kaggle_cli_submit_ok", file=str(file_path), competition=competition)
        print("Submission sent via Kaggle CLI. Check the competition page for results.")
    except FileNotFoundError:
        _log_event("kaggle_cli_not_found", file=str(file_path), competition=competition)
        raise SystemExit(
            "Kaggle CLI not found. Install it via: pip install kaggle\n"
            "Then configure your API token (kaggle.json) as described in Kaggle docs."
        )
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr or exc.stdout or ""
        if isinstance(stderr, bytes):  # pragma: no cover - defensive
            stderr = stderr.decode("utf-8", errors="replace")
        _log_event(
            "kaggle_cli_submit_failed",
            file=str(file_path),
            competition=competition,
            stderr_preview=stderr[:300],
        )
        if "kagglesdk" in stderr or "get_access_token_from_env" in stderr:
            print("Kaggle CLI failed with kagglesdk-related error, attempting HTTP fallback…")
            _kaggle_submit_http(file_path, competition, message, config_dirs)
            return
        raise SystemExit(f"Kaggle CLI submission failed: {exc}\n{stderr}")


def submit_file(file_path: str | Path, competition: str | None = None, message: str | None = None) -> None:
    """
    High-level entry point: validate a submission CSV and submit it to Kaggle.

    Steps:
    - resolve and check file path;
    - load CSV and validate schema (id, solution);
    - resolve competition slug (arg → env → default);
    - submit via Kaggle CLI with HTTP fallback.
    """
    path = Path(file_path).resolve()
    if not path.exists():
        raise SystemExit(f"Submission file not found: {path}")

    df = load_submission_csv(path)
    validate_submission_schema(df)

    comp_slug = _resolve_competition_slug(competition)
    if not comp_slug:
        raise SystemExit(
            "No competition slug specified. Provide --competition, set KAGGLE_COMPETITION, "
            "or adjust DEFAULT_KAGGLE_COMPETITION in submission/autosubmit.py."
        )

    _log_event(
        "submit_file",
        file=str(path),
        competition=comp_slug,
        message=message or "",
        n_rows=len(df),
    )
    _do_kaggle_submit(path, comp_slug, message or f"submit {path.name}")


def _parse_args(argv: list[str]) -> Any:
    import argparse

    parser = argparse.ArgumentParser(
        description="Autosubmit helper for CayleyPy-444-Cube (validate & submit submission.csv)."
    )
    parser.add_argument(
        "--file",
        default="submission.csv",
        help="Path to submission CSV (default: submission.csv).",
    )
    parser.add_argument(
        "--competition",
        "-c",
        default=None,
        help="Kaggle competition slug (overrides KAGGLE_COMPETITION and default).",
    )
    parser.add_argument(
        "--message",
        "-m",
        default="",
        help="Submission description shown on Kaggle (default: empty).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Entry point for `python -m CayleyPy_444_Cube.submission.autosubmit`."""
    if argv is None:
        argv = sys.argv[1:]
    args = _parse_args(argv)
    submit_file(
        file_path=args.file,
        competition=args.competition,
        message=args.message,
    )


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()

