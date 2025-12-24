"""Reductions package - Polynomial-time reductions between NP-complete problems."""
from .sat_to_3sat import reduce_sat_to_3sat
from .three_sat_to_subset_sum import reduce_3sat_to_subset_sum

__all__ = [
    "reduce_sat_to_3sat",
    "reduce_3sat_to_subset_sum",
]
