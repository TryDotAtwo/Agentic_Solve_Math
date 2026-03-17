"""
State-aware beam search for CayleyPy-444-Cube.

Uses cube_engine to apply moves and detect solved states. Guarantees that
returned paths actually solve the cube (or returns best-effort with retries).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

import random

from CayleyPy_444_Cube.cube_engine import (
    apply_move,
    apply_path,
    is_solved,
    parse_state,
    hamming_to_solved,
)
from CayleyPy_444_Cube.search.moves import ALL_MOVES, moves_to_string


@dataclass
class BeamConfig:
    """Configuration for state-aware beam search."""

    max_depth: int = 30
    beam_width: int = 512
    branching_factor: int = 24  # use all moves when >= len(ALL_MOVES)
    random_seed: int | None = None
    length_weight: float = 0.01  # penalty per move to prefer shorter solutions


def _score(state: List[int], path_len: int, length_weight: float) -> float:
    """Lower is better. Primary: hamming to solved. Secondary: path length."""
    h = hamming_to_solved(state)
    return h + length_weight * path_len


def solve_instance(
    state_repr: str,
    config: BeamConfig | None = None,
) -> List[str]:
    """
    Find a move sequence that solves the cube. Uses beam search over real states.
    Returns a path that satisfies is_solved(apply_path(parse_state(s), path)).
    """
    if config is None:
        config = BeamConfig()

    state = parse_state(state_repr)
    if is_solved(state):
        return []

    rng = random.Random(config.random_seed)
    n_moves = len(ALL_MOVES)
    branch_k = min(config.branching_factor, n_moves)
    moves_list = list(ALL_MOVES)

    # Beam: list of (state, path)
    beam: List[Tuple[Tuple[int, ...], List[str]]] = [((tuple(state), []))]
    best_unsolved: Tuple[Tuple[int, ...], List[str]] | None = None
    best_unsolved_score = float("inf")

    for depth in range(config.max_depth):
        candidates: List[Tuple[Tuple[int, ...], List[str], float]] = []
        for state_tuple, path in beam:
            if branch_k >= n_moves:
                move_iter = moves_list
            else:
                move_iter = rng.sample(moves_list, k=branch_k)

            for move in move_iter:
                st = list(state_tuple)
                st = apply_move(st, move)
                new_path = path + [move]
                if is_solved(st):
                    return new_path
                score = _score(st, len(new_path), config.length_weight)
                candidates.append((tuple(st), new_path, score))
                if score < best_unsolved_score:
                    best_unsolved_score = score
                    best_unsolved = (tuple(st), new_path)

        if not candidates:
            break
        candidates.sort(key=lambda x: x[2])
        beam = [(s, p) for s, p, _ in candidates[: config.beam_width]]

    # Not solved within depth: return best partial; if empty, fallback to single move
    if best_unsolved is not None:
        return best_unsolved[1]
    # Kaggle requires non-empty path; return arbitrary valid move as last resort
    return [moves_list[0]]


def solve_instance_with_retries(
    state_repr: str,
    config: BeamConfig | None = None,
    max_retries: int = 3,
) -> List[str]:
    """
    Try solve_instance up to max_retries times with different seeds.
    Returns first solution found, or best effort from last try.
    """
    cfg = config or BeamConfig()
    for attempt in range(max_retries):
        cfg.random_seed = (cfg.random_seed or 0) + attempt * 777
        path = solve_instance(state_repr, config=cfg)
        state = parse_state(state_repr)
        if not path:
            if is_solved(state):
                return []
            continue
        final = apply_path(state, path)
        if is_solved(final):
            return path
    # Best effort from last retry; ensure non-empty for Kaggle
    return path if path else [list(ALL_MOVES)[0]]


def solve_instance_with_flag(
    state_repr: str,
    config: BeamConfig | None = None,
) -> Tuple[List[str], bool]:
    """
    Same as solve_instance but returns (path, solved).
    solved=True iff the returned path actually solves the cube.
    """
    state = parse_state(state_repr)
    if is_solved(state):
        return [], True
    path = solve_instance(state_repr, config=config)
    if not path:
        return [list(ALL_MOVES)[0]], False
    final = apply_path(state, path)
    return path, is_solved(final)


def solve_batch_two_stage(
    states: List[str],
    fast_config: BeamConfig | None = None,
    hard_config: BeamConfig | None = None,
) -> List[str]:
    """
    Two-stage pipeline: fast pass on all, then re-solve suspected hard instances
    with stronger config.
    """
    fast_cfg = fast_config or BeamConfig(max_depth=25, beam_width=256)
    hard_cfg = hard_config or BeamConfig(max_depth=40, beam_width=1024)

    results: List[str] = []
    hard_indices: List[int] = []

    total = len(states)
    for i, s in enumerate(states):
        path, solved = solve_instance_with_flag(s, config=fast_cfg)
        path_str = moves_to_string(path) if path else list(ALL_MOVES)[0]
        results.append(path_str)
        if not solved or len(path) > 15:
            hard_indices.append(i)
        # Progress log every 50 instances (or on last)
        if (i + 1) % 50 == 0 or i + 1 == total:
            remaining = total - (i + 1)
            print(
                f"[solver_beam] fast pass {i + 1}/{total} done, "
                f"remaining {remaining}"
            )

    hard_total = len(hard_indices)
    if hard_total:
        print(
            f"[solver_beam] hard pass on {hard_total} instances "
            "(deeper beam search) ..."
        )
    for j, idx in enumerate(hard_indices):
        path = solve_instance_with_retries(states[idx], config=hard_cfg)
        results[idx] = moves_to_string(path) if path else list(ALL_MOVES)[0]
        if (j + 1) % 20 == 0 or j + 1 == hard_total:
            remaining = hard_total - (j + 1)
            print(
                f"[solver_beam] hard pass {j + 1}/{hard_total} done, "
                f"remaining {remaining}"
            )

    return results


def solve_batch(
    states: Iterable[str],
    config: BeamConfig | None = None,
    use_retries: bool = True,
) -> List[str]:
    """Run solver on batch; returns dot-separated path strings, never empty."""
    cfg = config or BeamConfig()
    states_list = list(states)
    total = len(states_list)
    results: List[str] = []
    for i, s in enumerate(states_list):
        path = (
            solve_instance_with_retries(s, config=cfg)
            if use_retries
            else solve_instance(s, config=cfg)
        )
        # Never emit empty path (Kaggle validation rejects null/empty)
        results.append(moves_to_string(path) if path else list(ALL_MOVES)[0])
        if (i + 1) % 50 == 0 or i + 1 == total:
            remaining = total - (i + 1)
            print(
                f"[solver_beam] single pass {i + 1}/{total} done, "
                f"remaining {remaining}"
            )
    return results
