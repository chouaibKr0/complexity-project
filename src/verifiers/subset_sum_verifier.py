"""
Subset Sum Solution Verifier.

Verifies that a given subset sums to the target.
Verification runs in polynomial time O(n).

This demonstrates that Subset Sum is in NP.
"""
from typing import Any


def verify_subset_sum_solution(numbers: list[int], target: int, subset: list[int]) -> bool:
    """
    Verify that a subset sums to the target.
    
    This is the polynomial-time certificate verifier for Subset Sum.
    
    Args:
        numbers: Original set of numbers.
        target: Target sum.
        subset: Proposed subset that should sum to target.
    
    Returns:
        True if subset is valid and sums to target.
    
    Complexity: O(n) - polynomial time
    
    """

    # Guard against invalid subset
    if subset is None:
        return False
    
    # Build a frequency map of the original numbers
    counts = {}
    for x in numbers:
        counts[x] = counts.get(x, 0) + 1

    # Verify all elements of subset come from numbers
    total = 0
    for x in subset:
        if x not in counts or counts[x] == 0:
            return False
        counts[x] -= 1
        total += x

    # Verify sum equals target
    return total == target