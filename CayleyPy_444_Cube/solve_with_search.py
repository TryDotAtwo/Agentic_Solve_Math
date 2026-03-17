from __future__ import annotations

"""
Generate submission using state-aware beam search.

Reads test.csv (initial_state_id, initial_state), runs
`search.solver_beam.solve_batch_two_stage` which applies real cube moves from
`puzzle_info.json`, and writes the `path` column.
"""

from pathlib import Path
import time

import pandas as pd

from CayleyPy_444_Cube.cube_engine import apply_path, is_solved, parse_state
from CayleyPy_444_Cube.search.moves import string_to_moves
from CayleyPy_444_Cube.search.solver_beam import BeamConfig, solve_batch


def generate_search_submission(
    test_path: Path | str = "data/test.csv",
    output_path: Path | str = "submission_search.csv",
) -> Path:
    start_time = time.time()
    test_path = Path(test_path).resolve()
    print(f"[solve_with_search] Loading test file from {test_path} ...")
    if not test_path.exists():
        raise SystemExit(
            f"Expected test file not found: {test_path}\n"
            "Place the official competition data/test.csv (or a subset) in the CayleyPy_444_Cube/data directory."
        )

    df_test = pd.read_csv(test_path)
    if "initial_state_id" not in df_test.columns:
        raise SystemExit(f"Test file {test_path} must contain an 'initial_state_id' column.")
    if "initial_state" not in df_test.columns:
        raise SystemExit(
            f"Test file {test_path} must contain an 'initial_state' column with cube encodings, as in the official data/test.csv file."
        )

    states = df_test["initial_state"].astype(str).tolist()
    n = len(states)
    fast_cfg = BeamConfig(max_depth=25, beam_width=256, branching_factor=24)
    print(
        "[solve_with_search] Solving "
        f"{n} instances with single-stage beam search "
        f"(depth={fast_cfg.max_depth}, beam={fast_cfg.beam_width}) ..."
    )
    solutions = solve_batch(states, config=fast_cfg, use_retries=True)
    print(f"[solve_with_search] Done. Generated {len(solutions)} solutions.")

    df_sub = pd.DataFrame(
        {
            "initial_state_id": df_test["initial_state_id"],
            "path": solutions,
        }
    )
    # Ensure no NaN (Kaggle validation rejects null); empty "" allowed for solved cubes
    df_sub["path"] = df_sub["path"].fillna("f0.-f0").astype(str).replace("nan", "f0.-f0")

    # Quick summary: how many solutions actually solve the cube under our engine.
    solved = 0
    for s_repr, path_str in zip(states, df_sub["path"].tolist()):
        moves = string_to_moves(path_str)
        final_state = apply_path(parse_state(s_repr), moves)
        if is_solved(final_state):
            solved += 1

    output_path = Path(output_path).resolve()
    df_sub.to_csv(output_path, index=False)
    elapsed = time.time() - start_time
    print(f"[solve_with_search] Search-based submission written to {output_path}")
    print(
        f"[solve_with_search] Solved {solved}/{n} instances under local engine; "
        f"total solve time: {elapsed:0.1f} seconds"
    )
    return output_path


def main() -> None:
    generate_search_submission()


if __name__ == "__main__":
    main()

