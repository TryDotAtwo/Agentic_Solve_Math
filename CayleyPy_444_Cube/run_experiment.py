from __future__ import annotations

"""
Entry point for running local experiments with different solver configurations.

Current focus:
- provide a simple CLI that can:
  - run the dummy baseline (empty solutions);
  - run the search-based solver scaffold;
  - write out submission-like CSV files for comparison;
  - (optionally) prepare inputs for external evaluation.

This script does not talk to Kaggle directly; autosubmit remains in
`submission/autosubmit.py`.
"""

from pathlib import Path
import argparse

if __package__ in (None, ""):
    # Running as a script: adjust sys.path to allow package-style imports.
    import sys
    from pathlib import Path as _Path

    project_root = _Path(__file__).resolve().parent
    sys.path.insert(0, str(project_root.parent))
    from CayleyPy_444_Cube.generate_dummy_submission import (  # type: ignore[import]
        generate_dummy_submission,
    )
    from CayleyPy_444_Cube.solve_with_search import (  # type: ignore[import]
        generate_search_submission,
    )
else:
    # Imported as part of the CayleyPy_444_Cube package.
    from .generate_dummy_submission import generate_dummy_submission  # type: ignore[import]
    from .solve_with_search import generate_search_submission  # type: ignore[import]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run local experiments for CayleyPy-444-Cube solvers."
    )
    parser.add_argument(
        "--mode",
        choices=["dummy", "search"],
        default="dummy",
        help="Which solver configuration to run (default: dummy).",
    )
    parser.add_argument(
        "--test-path",
        default="data/test.csv",
        help="Path to competition test.csv (default: data/test.csv in project).",
    )
    parser.add_argument(
        "--output-path",
        default=None,
        help="Where to write the submission-like CSV (default depends on mode).",
    )

    args = parser.parse_args(argv)

    test_path = Path(args.test_path)

    if args.mode == "dummy":
        output = args.output_path or "submission_dummy.csv"
        generate_dummy_submission(test_path=test_path, output_path=output)
    elif args.mode == "search":
        output = args.output_path or "submission_search.csv"
        generate_search_submission(test_path=test_path, output_path=output)
    else:
        raise SystemExit(f"Unknown mode: {args.mode}")


if __name__ == "__main__":
    main()

