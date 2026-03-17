from __future__ import annotations

"""
Lightweight accessors for the Kaggle-provided 4x4x4 puzzle specification.

This module treats `data/puzzle_info.json` as the single source of truth for:

- the canonical solved (central) state vector;
- the available move generators and their permutation actions;
- the order and names of those generators, which define the move alphabet and
  the encoding used in submission `path` strings.
"""

from pathlib import Path
from typing import Dict, List, Tuple
import json

_PUZZLE_INFO_PATH = Path(__file__).resolve().parent / "data" / "puzzle_info.json"

with _PUZZLE_INFO_PATH.open("r", encoding="utf-8") as f:
    _raw = json.load(f)

# Public, typed views of the underlying JSON structure.

CENTRAL_STATE: List[int] = list(_raw["central_state"])

GENERATORS: Dict[str, Tuple[int, ...]] = {
    name: tuple(perm) for name, perm in _raw["generators"].items()
}

# The move alphabet, in the exact order provided by the JSON.
GENERATOR_NAMES: Tuple[str, ...] = tuple(_raw["generators"].keys())

