"""Tests for verifiers."""
import pytest
from src.verifiers import verify_sat_solution, verify_3sat_solution, verify_subset_sum_solution


class TestSATVerifier:
    """Test SAT solution verifier."""
    
    def test_valid_solution(self):
        """Test that a valid solution is accepted."""
        clauses = [[1, 2], [-1, 2]]  # (x1 OR x2) AND (NOT x1 OR x2)
        assignment = {1: False, 2: True}  # x2 = True satisfies both
        
        assert verify_sat_solution(clauses, assignment) is True
    
    def test_invalid_solution(self):
        """Test that an invalid solution is rejected."""
        clauses = [[1, 2], [-1, -2]]  # (x1 OR x2) AND (NOT x1 OR NOT x2)
        assignment = {1: True, 2: True}  # Second clause fails
        
        assert verify_sat_solution(clauses, assignment) is False


class TestSubsetSumVerifier:
    """Test Subset Sum verifier."""
    
    def test_valid_subset(self):
        """Test that a valid subset is accepted."""
        numbers = [3, 7, 1, 8, 4]
        target = 12
        subset = [8, 4]
        
        assert verify_subset_sum_solution(numbers, target, subset) is True
    
    def test_invalid_sum(self):
        """Test that wrong sum is rejected."""
        numbers = [3, 7, 1, 8, 4]
        target = 12
        subset = [3, 7]  # Sum is 10, not 12
        
        assert verify_subset_sum_solution(numbers, target, subset) is False
    
    def test_invalid_element(self):
        """Test that element not in original set is rejected."""
        numbers = [3, 7, 1, 8, 4]
        target = 12
        subset = [5, 7]  # 5 not in numbers
        
        assert verify_subset_sum_solution(numbers, target, subset) is False
