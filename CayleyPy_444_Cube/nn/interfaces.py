from __future__ import annotations

"""
High-level interfaces between NN components and search-based solvers.

The key idea:
- search operates on abstract state strings and move tokens;
- NN components provide:
  - policy logits / probabilities over moves;
  - value estimates (distance-to-go or solution quality);
- a thin adapter turns NN outputs into heuristic scores compatible with
  `search.solver_random_beam`.
"""

from dataclasses import dataclass
from typing import Protocol, Sequence

from CayleyPy_444_Cube.search.moves import ALL_MOVES


class PolicyValueModel(Protocol):
    """
    Abstract interface for a policy+value model.

    A concrete implementation could be a PyTorch / JAX / TF model; we only
    require this minimal protocol for integration with search.
    """

    def predict(self, state_repr: str) -> tuple[Sequence[float], float]:
        """
        Given a single state representation, return:
        - policy logits or scores over `ALL_MOVES` (same order);
        - scalar value estimate (e.g. negative distance-to-go; higher is better).
        """


@dataclass
class NNGuidedHeuristic:
    """
    Adapter that turns a PolicyValueModel into a heuristic function compatible
    with `search.solver_random_beam`.
    """

    model: PolicyValueModel
    length_penalty_weight: float = 0.1
    value_weight: float = 1.0

    def __call__(self, state_repr: str, moves_so_far: Sequence[str]) -> float:
        """
        Combine NN value estimate with a simple length penalty.

        Lower scores are considered better by the search code, so we negate
        the value estimate (assuming higher value is better) and add a small
        penalty for longer sequences.
        """
        # NN prediction is independent of the current prefix by default; a more
        # advanced integration could re-simulate the state after moves_so_far.
        policy_scores, value_est = self.model.predict(state_repr)
        _ = policy_scores  # placeholder: not yet used directly by beam search

        length_penalty = self.length_penalty_weight * len(moves_so_far)
        # We treat `value_est` as \"goodness\"; to turn it into a cost-like score
        # we negate it.
        return float(length_penalty - self.value_weight * value_est)


def num_moves() -> int:
    """Utility returning the current size of the move alphabet."""
    return len(ALL_MOVES)

