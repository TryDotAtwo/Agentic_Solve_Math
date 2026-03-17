"""
Neural-network and hybrid (NN + search) components for CayleyPy-444-Cube.

This package only provides high-level scaffolding at this stage:

- a canonical place to define:
  - how cube states are tensorized for NN input;
  - which targets are predicted (next-move policy, value / distance estimate, or both);
  - simple model architectures suitable for experimentation;
  - data loading utilities for training / evaluation.
- a clear interface layer between:
  - `search` (purely algorithmic solvers);
  - NN components used as heuristics / policies inside search.

The actual training code and heavy ML dependencies (PyTorch, JAX, etc.) are
intentionally not included yet; they should be added when a concrete training
environment and dataset are available.
"""

