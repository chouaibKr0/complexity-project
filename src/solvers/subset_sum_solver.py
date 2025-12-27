"""
Subset Sum Solver Implementation.

Given a set of integers S and a target T, determine if there exists
a subset of S that sums to exactly T.

Subset Sum is NP-complete.

Algorithms to implement:
1. Brute Force - Try all 2^n subsets
2. Backtracking - With pruning
3. Dynamic Programming - O(n*T) pseudo-polynomial time

TODO: Implement the solving algorithms
"""
import time
from typing import Any
import numpy as np

from .base import BaseSolver, SolverResult
from ..utils.validation import validate_subset_sum_instance
from ..utils.timer import Timer


class SubsetSumSolver(BaseSolver):
    """
    Solver for Subset Sum Problem.
    
    Input: 
        - numbers: list of positive integers
        - target: target sum
    
    Output: SolverResult with:
        - satisfiable: True if subset exists
        - solution: list of numbers in the subset, or None
    """
    
    def __init__(self, algorithm: str = "dynamic"):
        """
        Initialize Subset Sum solver.
        
        Args:
            algorithm: One of "brute_force", "backtrack", "dynamic"
        """
        super().__init__(name=f"SubsetSum-{algorithm}")
        self.algorithm = algorithm
    
    def solve(self, numbers: list[int], target: int) -> SolverResult:
        """
        Solve the Subset Sum instance.
        
        Args:
            numbers: List of positive integers.
            target: Target sum to achieve.
        
        Returns:
            SolverResult with satisfiability and subset.
        """
        # Validate input
        validate_subset_sum_instance(numbers, target)
        
        self.stats["calls"] += 1
        nodes = 0
        
        with Timer("subset_sum_solve") as timer:
            if self.algorithm == "brute_force":
                sat, subset, nodes = self._brute_force(numbers, target)
            elif self.algorithm == "backtrack":
                sat, subset, nodes = self._backtrack(numbers, target)
            elif self.algorithm == "dynamic":
                sat, subset, nodes = self._dynamic_programming(numbers, target)
            else:
                raise ValueError(f"Unknown algorithm: {self.algorithm}")
        
        self.stats["total_time"] += timer.elapsed
        self.stats["nodes_explored"] += nodes
        
        return SolverResult(
            satisfiable=sat,
            solution=subset,
            time_seconds=timer.elapsed,
            nodes_explored=nodes,
            algorithm=self.algorithm
        )
    
    def _brute_force(self, numbers: list[int], target: int) -> tuple[bool, list | None, int]:
        """
        Brute force: enumerate all 2^n subsets using bit masking.
        
        Time Complexity: O(2^n * n)
        Space Complexity: O(n)
        
        For each of the 2^n subsets:
        - Use bitmask to determine which elements to include
        - Calculate sum and check if it equals target
        
        Returns:
            (found_subset, subset_list, nodes_explored)
        """
        n = len(numbers)
        nodes = 0
        
        # Try all 2^n subsets
        for mask in range(1 << n):  # 2^n subsets
            nodes += 1
            subset = []
            current_sum = 0
            
            # Check each bit in the mask
            for i in range(n):
                if mask & (1 << i):  # If i-th bit is set
                    subset.append(numbers[i])
                    current_sum += numbers[i]
            
            # Check if this subset sums to target
            if current_sum == target:
                return True, subset, nodes
        
        return False, None, nodes
        raise NotImplementedError("Brute force Subset Sum solver not implemented")
    
    def _backtrack(self, numbers: list[int], target: int) -> tuple[bool, list | None, int]:
        """
        Backtracking with pruning.
        
        Time Complexity: O(2^n) worst case, but typically much better
        Space Complexity: O(n) for recursion stack
        
        Pruning strategies:
        1. If current sum > target, prune (assuming all positive)
        2. If current sum + remaining sum < target, prune
        3. Early termination when solution found
        
        Returns:
            (found_subset, subset_list, nodes_explored)
        """
        nodes = [0]  # Use list to allow modification in nested function
        n = len(numbers)
        
        # Calculate prefix sums for pruning
        remaining_sum = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            remaining_sum[i] = remaining_sum[i + 1] + numbers[i]
        
        def backtrack_helper(index: int, current_sum: int, current_subset: list[int]) -> tuple[bool, list | None]:
            """
            Recursive backtracking helper.
            
            Args:
                index: Current position in numbers array
                current_sum: Sum of numbers selected so far
                current_subset: List of numbers selected so far
            
            Returns:
                (found, subset) tuple
            """
            nodes[0] += 1
            
            # Base case: found solution
            if current_sum == target:
                return True, current_subset.copy()
            
            # Base case: reached end or impossible to reach target
            if index >= n:
                return False, None
            
            # Pruning 1: current sum exceeds target (assuming positive numbers)
            if current_sum > target:
                return False, None
            
            # Pruning 2: even with all remaining numbers, can't reach target
            if current_sum + remaining_sum[index] < target:
                return False, None
            
            # Try including current number
            current_subset.append(numbers[index])
            found, subset = backtrack_helper(index + 1, current_sum + numbers[index], current_subset)
            if found:
                return True, subset
            current_subset.pop()  # Backtrack
            
            # Try not including current number
            found, subset = backtrack_helper(index + 1, current_sum, current_subset)
            if found:
                return True, subset
            
            return False, None
        
        found, subset = backtrack_helper(0, 0, [])
        return found, subset, nodes[0]
        raise NotImplementedError("Backtracking Subset Sum solver not implemented")
    
    def _dynamic_programming(self, numbers: list[int], target: int) -> tuple[bool, list | None, int]:
        """
        Dynamic programming approach.
        
        Time Complexity: O(n * target)
        Space Complexity: O(n * target) or O(target) with space optimization
        
        DP Table: dp[i][j] = True if we can achieve sum j using first i numbers
        
        Recurrence:
        dp[i][j] = dp[i-1][j] OR (dp[i-1][j-numbers[i-1]] if j >= numbers[i-1])
        
        Note: This is pseudo-polynomial (polynomial in numeric value of target)
        
        Returns:
            (found_subset, subset_list, nodes_explored)
        """
        n = len(numbers)
        nodes = 0
        
        # Handle edge cases
        if target < 0:
            return False, None, 0
        if target == 0:
            return True, [], 0
        
        # Create DP table: dp[i][j] = can we make sum j using first i numbers
        dp = np.zeros((n + 1, target + 1), dtype=bool)
        
        # Base case: sum of 0 is always achievable (empty subset)
        for i in range(n + 1):
            dp[i][0] = True
        
        # Fill DP table
        for i in range(1, n + 1):
            for j in range(target + 1):
                nodes += 1
                
                # Option 1: don't include numbers[i-1]
                dp[i][j] = dp[i - 1][j]
                
                # Option 2: include numbers[i-1] (if possible)
                if j >= numbers[i - 1]:
                    dp[i][j] = dp[i][j] or dp[i - 1][j - numbers[i - 1]]
        
        # Check if target is achievable
        if not dp[n][target]:
            return False, None, nodes
        
        # Reconstruct the subset
        subset = self._reconstruct_subset(dp, numbers, target)
        return True, subset, nodes
        raise NotImplementedError("Dynamic programming Subset Sum solver not implemented")
    
    # Helper methods
    
    def _reconstruct_subset(self, dp: np.ndarray, numbers: list[int], target: int) -> list[int]:
        """
        Reconstruct the subset from the DP table by backtracking.
        
        Args:
            dp: Filled DP table
            numbers: Original list of numbers
            target: Target sum
        
        Returns:
            List of numbers that sum to target
        """
        subset = []
        i = len(numbers)
        j = target
        
        # Backtrack through DP table
        while i > 0 and j > 0:
            # If dp[i][j] is True but dp[i-1][j] is False,
            # then numbers[i-1] must be included
            if not dp[i - 1][j]:
                subset.append(numbers[i - 1])
                j -= numbers[i - 1]
            i -= 1
        
        return subset
        pass