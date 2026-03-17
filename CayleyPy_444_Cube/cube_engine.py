"""
Cube engine for CayleyPy-444-Cube: apply moves from puzzle_info.json to states.

Treats data/puzzle_info.json as the single source of truth. States are length-96
vectors; applying a generator permutes indices according to the JSON definition.
"""

from __future__ import annotations

from typing import List

from CayleyPy_444_Cube.puzzle_info import CENTRAL_STATE, GENERATORS


def parse_state(s: str) -> List[int]:
    """Parse a state string (e.g. from test.csv initial_state) into a list of 96 ints."""
    s = s.strip().strip('"')
    if not s:
        return list(CENTRAL_STATE)
    parts = s.replace(" ", "").split(",")
    return [int(p) for p in parts if p]


def state_to_str(state: List[int]) -> str:
    """Serialize state to the format expected in CSV."""
    return ",".join(str(x) for x in state)


def apply_move(state: List[int], generator_name: str) -> List[int]:
    """
    Apply a single generator to state. Returns a new state (permutation of indices).
    generator_name must be a key in GENERATORS (e.g. "f0", "-f1", "r2").
    """
    perm = GENERATORS.get(generator_name)
    if perm is None:
        raise ValueError(f"Unknown generator: {generator_name}")
    n = len(state)
    return [state[perm[i]] for i in range(n)]


def apply_path(state: List[int], path_tokens: List[str]) -> List[int]:
    """Apply a sequence of generators to state. path_tokens is a list of generator names."""
    current = list(state)
    for token in path_tokens:
        current = apply_move(current, token)
    return current


def is_solved(state: List[int]) -> bool:
    """Return True iff state equals CENTRAL_STATE (solved cube)."""
    if len(state) != len(CENTRAL_STATE):
        return False
    return all(a == b for a, b in zip(state, CENTRAL_STATE))


def hamming_to_solved(state: List[int]) -> int:
    """Number of positions differing from CENTRAL_STATE. Used as a simple heuristic."""
    if len(state) != len(CENTRAL_STATE):
        return 96
    return sum(1 for a, b in zip(state, CENTRAL_STATE) if a != b)
