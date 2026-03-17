from __future__ import annotations

"""
Minimal baseline script for CayleyPy-444-Cube.

Purpose:
- load the official test CSV (assumed path: `test.csv` in this subproject root);
- generate a trivially valid submission with:
  - `id` copied from the test file;
  - `solution` = empty string for every row (\"no moves\");
- save it as `submission.csv` in the project root;
- run the local schema validation from `CayleyPy_444_Cube.submission`.

This script does NOT attempt to solve the cubes. It only provides a
pipeline check for:
- data loading;
- submission.csv generation;
- local validation;
- subsequent autosubmit (if the user decides to call it).
"""

from pathlib import Path

import pandas as pd

from CayleyPy_444_Cube.submission import load_submission_csv, validate_submission_schema


def generate_dummy_submission(
    test_path: Path | str = "data/test.csv",
    output_path: Path | str = "submission.csv",
) -> Path:
    """
    Create a dummy submission file with the correct schema.

    - Reads `test_path` as CSV and expects an `initial_state_id` column.
    - Produces `output_path` with columns:
      - `initial_state_id` (copied from test);
      - `path` (empty string for every row).
    - Runs the local validation on the resulting DataFrame.
    """
    test_path = Path(test_path).resolve()
    if not test_path.exists():
        raise SystemExit(
            f"Expected test file not found: {test_path}\n"
            "Place the official competition data/test.csv (or a subset) in the CayleyPy_444_Cube/data directory."
        )

    df_test = pd.read_csv(test_path)
    if "initial_state_id" not in df_test.columns:
        raise SystemExit(
            f"Test file {test_path} must contain an 'initial_state_id' column to build a submission."
        )

    df_sub = pd.DataFrame(
        {
            "initial_state_id": df_test["initial_state_id"],
            # Empty path: purely for schema correctness; does not solve the cubes.
            "path": ["" for _ in range(len(df_test))],
        }
    )

    output_path = Path(output_path).resolve()
    df_sub.to_csv(output_path, index=False)

    # Run local validation using the same code as autosubmit.
    df_loaded = load_submission_csv(output_path)
    validate_submission_schema(df_loaded)

    print(f"Dummy submission written to {output_path}")
    return output_path


def main() -> None:
    """CLI entry: generate a dummy submission from `data/test.csv`."""
    generate_dummy_submission()


if __name__ == "__main__":
    main()

