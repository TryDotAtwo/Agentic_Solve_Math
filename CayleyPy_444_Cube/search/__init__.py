"""
Search-based solvers and heuristics for CayleyPy-444-Cube.

This package currently contains:

- `moves` – canonical move set and utilities for working with move sequences;
- `solver_random_beam` – a simple beam-search style solver skeleton that
  operates on abstract states and move sequences.

The concrete cube state representation and exact move semantics are left
deliberately abstract for now, because the official competition encoding
and baseline implementations are not yet available in this repository.
The intent is that:

- engineering work can plug in a real 4x4x4 engine behind the same interfaces;
- mathematical work (see docs/03_STATE_AND_GROUP_STRUCTURE.md and
  docs/04_POTENTIAL_HYPOTHESES.md) can inform better heuristics and
  state features over time.
"""

