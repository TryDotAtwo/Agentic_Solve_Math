from __future__ import annotations

"""
Thin wrapper to generate a \"best known\" submission for CayleyPy-444-Cube.

At this stage, \"best\" simply means:
- use the search-based solver scaffold (`solve_with_search.generate_search_submission`);
- rely on its current default configuration.

As the project evolves, this script should be updated to point to the
strongest validated configuration (including NN-guided search, ensembles, etc.).
"""

from pathlib import Path

if __package__ in (None, ""):
    # Running as a script: adjust sys.path to allow package-style imports.
    import sys
    from pathlib import Path as _Path

    project_root = _Path(__file__).resolve().parent
    sys.path.insert(0, str(project_root.parent))
    from CayleyPy_444_Cube.solve_with_search import generate_search_submission  # type: ignore[import]
else:
    # Imported as part of the CayleyPy_444_Cube package.
    from .solve_with_search import generate_search_submission  # type: ignore[import]


def main() -> None:
    # Resolve paths relative to this file's directory so that the script
    # works regardless of the current working directory.
    project_root = Path(__file__).resolve().parent
    test_path = project_root / "data" / "test.csv"
    output_path = project_root / "submission_best.csv"
    generate_search_submission(test_path=test_path, output_path=output_path)


if __name__ == "__main__":
    main()

