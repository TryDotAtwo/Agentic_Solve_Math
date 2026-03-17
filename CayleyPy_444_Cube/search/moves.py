from __future__ import annotations

"""
Canonical move set for the 4x4x4 cube (abstract level).

This module does NOT implement the actual cube state transitions; it only
defines a consistent set of move tokens and basic helpers for working with
move sequences. A future integration with a concrete 4x4x4 engine should:

- interpret these tokens as specific face / slice turns;
- provide functions to apply them to internal state objects.
"""

from typing import Iterable, List

from CayleyPy_444_Cube.puzzle_info import GENERATOR_NAMES

# For now we use a single flat move alphabet that matches the Kaggle
# `generators` keys and sample_submission `path` encoding.
ALL_MOVES: tuple[str, ...] = GENERATOR_NAMES


def moves_to_string(moves: Iterable[str]) -> str:
    """
    Join a sequence of move tokens into a single solution string, using the
    `.` separator expected by the competition (`path` column).
    """
    return ".".join(moves)


def string_to_moves(s: str) -> List[str]:
    """Split a solution string into move tokens (very lightweight parsing)."""
    s = s.strip()
    if not s:
        return []
    return [token for token in s.split(".") if token]

