from __future__ import annotations

"""
Project-local orchestrator for the CayleyPy-444-Cube competition.

High-level pipeline:
- (optionally) download competition data via Kaggle CLI into `data/`;
- generate a submission CSV using the best-known solver configuration
  in this subproject (`run_best.py`);
- validate and submit the file via `submission.autosubmit`.
"""

from pathlib import Path
import argparse
import os
import subprocess

import pandas as pd

if __package__ in (None, ""):
    # Running as a script: adjust sys.path to allow package-style imports.
    import sys
    from pathlib import Path as _Path

    project_root_for_imports = _Path(__file__).resolve().parent
    sys.path.insert(0, str(project_root_for_imports.parent))
    from CayleyPy_444_Cube.run_best import main as run_best_main  # type: ignore[import]
    from CayleyPy_444_Cube.submission.autosubmit import submit_file  # type: ignore[import]
    from CayleyPy_444_Cube.puzzle_info import CENTRAL_STATE  # type: ignore[import]
    from CayleyPy_444_Cube.cube_engine import parse_state, apply_path  # type: ignore[import]
    from CayleyPy_444_Cube.search.moves import string_to_moves  # type: ignore[import]
else:
    # Imported as part of the CayleyPy_444_Cube package.
    from .run_best import main as run_best_main  # type: ignore[import]
    from .submission.autosubmit import submit_file  # type: ignore[import]
    from .puzzle_info import CENTRAL_STATE  # type: ignore[import]
    from .cube_engine import parse_state, apply_path  # type: ignore[import]
    from .search.moves import string_to_moves  # type: ignore[import]


def _run_cmd(cmd: list[str]) -> None:
    """Run a subprocess command, streaming output, and fail on non-zero exit."""
    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise SystemExit(f"Command failed with exit code {proc.returncode}: {' '.join(cmd)}")


def _ensure_kaggle_env(project_root: Path) -> None:
    """If ~/.kaggle lacks kaggle.json but project has it, set KAGGLE_CONFIG_DIR."""
    home_kaggle = Path.home() / ".kaggle" / "kaggle.json"
    if home_kaggle.exists():
        return
    for name in ("kaggle.json", "kaggle (1).json", "kaggle(1).json"):
        p = project_root / name
        if p.exists():
            os.environ["KAGGLE_CONFIG_DIR"] = str(project_root)
            return


def _fix_submission_with_sample(submission_path: Path, data_dir: Path) -> None:
    """
    Ensure all paths in submission_best.csv are valid according to the puzzle
    spec. For any invalid path, fall back to the official sample_submission
    path for that instance.
    """
    if not submission_path.exists():
        return

    df_sub = pd.read_csv(submission_path)
    df_test = pd.read_csv(data_dir / "test.csv")
    df_sample = pd.read_csv(data_dir / "sample_submission.csv")

    merged = (
        df_sub.merge(df_test, on="initial_state_id", how="left")
        .merge(df_sample, on="initial_state_id", how="left", suffixes=("", "_sample"))
    )

    central = CENTRAL_STATE

    def _is_valid_row(row: pd.Series) -> bool:
        path_str = str(row.get("path", ""))
        if not path_str or path_str.lower() == "nan":
            return False
        moves = string_to_moves(path_str)
        final_state = apply_path(list(central), moves)
        init_state = parse_state(str(row["initial_state"]))
        return final_state == init_state

    mask_invalid = ~merged.apply(_is_valid_row, axis=1)
    n_invalid = int(mask_invalid.sum())
    if n_invalid > 0:
        merged.loc[mask_invalid, "path"] = merged.loc[mask_invalid, "path_sample"]
        fixed = merged[["initial_state_id", "path"]]
        fixed.to_csv(submission_path, index=False)
        print(f"[main] Fixed {n_invalid} invalid paths using sample_submission.csv")
    else:
        print("[main] All paths passed local central->initial_state check; no fixes applied.")


def download_c4_data(data_dir: Path, project_root: Path) -> None:
    """
    Download CayleyPy-444-Cube data via Kaggle CLI into `data_dir`.

    Requires:
    - installed `kaggle` CLI;
    - configured API credentials (kaggle.json in project root or ~/.kaggle).
    """
    _ensure_kaggle_env(project_root)
    data_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "kaggle",
        "competitions",
        "download",
        "-c",
        "cayley-py-444-cube",
        "-p",
        str(data_dir),
    ]
    try:
        _run_cmd(cmd)
    except SystemExit as exc:
        test_path = data_dir / "test.csv"
        # If Kaggle credentials are missing but the user already placed data
        # manually, allow the pipeline to continue.
        if test_path.exists():
            print(
                "Warning: Kaggle download failed, but data/test.csv exists already; "
                "continuing without downloading."
            )
            return
        # Otherwise, re-raise the original failure.
        raise exc


def generate_c4_submission_best(data_dir: Path, project_root: Path) -> Path:
    """
    Generate a submission for CayleyPy-444-Cube using the project's best-known solver.

    Currently:
    - assumes that `data/test.csv` is present under the project root;
    - calls `run_best.main()` to produce `submission_best.csv`.
    """
    test_path = data_dir / "test.csv"
    if not test_path.exists():
        raise SystemExit(
            f"Expected test file not found: {test_path}\n"
            "Run with --download-data first, or download manually from Kaggle."
        )

    run_best_main()
    submission_path = project_root / "submission_best.csv"
    if not submission_path.exists():
        raise SystemExit(f"Expected submission file not found after run_best: {submission_path}")
    return submission_path


def autosubmit_c4(submission_path: Path, message: str) -> None:
    """
    Validate and submit a CayleyPy-444-Cube submission via the subproject's autosubmit module.
    """
    submit_file(file_path=submission_path, competition=None, message=message)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Orchestrator for CayleyPy-444-Cube: download data, solve, submit."
    )
    parser.add_argument(
        "--no-download-data",
        action="store_true",
        help="Skip Kaggle data download step (assume data already present).",
    )
    parser.add_argument(
        "--no-submit",
        action="store_true",
        help="Do not autosubmit to Kaggle, only generate the submission file.",
    )
    parser.add_argument(
        "--reuse-submission",
        action="store_true",
        help=(
            "Reuse existing submission_best.csv (if present) and skip solving. "
            "Useful to just submit an already generated CSV."
        ),
    )
    parser.add_argument(
        "--message",
        default="C4 submission from CayleyPy_444_Cube/main.py",
        help="Submission description for Kaggle.",
    )

    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parent
    data_dir = project_root / "data"

    if not args.no_download_data:
        print("[main] Downloading CayleyPy-444-Cube data via Kaggle CLI ...")
        download_c4_data(data_dir, project_root)
    else:
        print("[main] Skipping data download (user requested --no-download-data).")

    if args.reuse_submission:
        submission_path = project_root / "submission_best.csv"
        if not submission_path.exists():
            raise SystemExit(
                f"--reuse-submission requested, but file not found: {submission_path}"
            )
        print(f"[main] Reusing existing submission file at {submission_path}")
    else:
        print("[main] Generating submission_best.csv via run_best.py ...")
        submission_path = generate_c4_submission_best(data_dir, project_root)
        print(f"[main] Generated submission at {submission_path}")

    # Before submitting, fix any invalid paths using sample_submission.csv.
    print("[main] Running local validity check and fixes on submission_best.csv ...")
    _fix_submission_with_sample(submission_path, data_dir)

    if not args.no_submit:
        print("[main] Submitting to Kaggle via submission.autosubmit ...")
        autosubmit_c4(submission_path, args.message)
        print("[main] Submission step completed.")
    else:
        print("[main] Skipping autosubmit (user requested --no-submit).")


if __name__ == "__main__":
    main()

