from __future__ import annotations

"""
Input / target schema definitions for NN components.

This module focuses on *shapes* and *interfaces*, not on concrete tensor
implementations. Once a specific ML framework is chosen, the same ideas can
be mapped to framework-specific types (e.g. torch.Tensor).
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class StateTensorSpec:
    """
    Specification of how a single cube state is represented for NN input.

    Fields:
    - channels: number of feature channels (e.g. colors, piece types, phases);
    - height, width: spatial dimensions if using 2D layouts;
    - extra: optional dict for additional metadata (e.g. phase flags).
    """

    channels: int
    height: int
    width: int
    extra: Dict[str, Any] | None = None


@dataclass
class TargetSpec:
    """
    Specification of the prediction targets for the NN.

    Examples:
    - policy over moves (size = number of move tokens in search.moves.ALL_MOVES);
    - scalar value (estimated distance-to-go or quality score).
    """

    policy_size: int
    has_value_head: bool = True


def default_state_tensor_spec() -> StateTensorSpec:
    """
    Return a placeholder state-tensor spec for initial experiments.

    ASSUMPTION:
    - we will eventually map a 4x4x4 cube to a 2D layout with a fixed number
      of channels (e.g. one-hot colors / piece types).
    """
    return StateTensorSpec(
        channels=24,  # placeholder; to be refined once encoding is fixed
        height=8,
        width=8,
        extra={"note": "ASSUMPTION; update once real encoding is known"},
    )


def default_target_spec(num_moves: int) -> TargetSpec:
    """Return a default target spec with a policy over `num_moves` and a value head."""
    return TargetSpec(policy_size=num_moves, has_value_head=True)

