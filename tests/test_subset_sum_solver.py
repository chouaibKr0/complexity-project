"""Tests for Subset Sum Solver."""
import pytest
from src.solvers import SubsetSumSolver
from src.verifiers import verify_subset_sum_solution


class TestSubsetSumSolver:
    """Test suite for Subset Sum solver."""
    
    @pytest.fixture
    def simple_instance(self):
        """Simple instance with solution."""
        return [3, 7, 1, 8, 4], 12  # Solution: [8, 4] or [3, 1, 8]
    
    @pytest.fixture
    def no_solution_instance(self):
        """Instance with no solution."""
        return [2, 4, 6, 8], 3  # All even, target is odd
    
    @pytest.mark.parametrize("algorithm", ["brute_force", "backtrack", "dynamic"])
    def test_simple_solution(self, simple_instance, algorithm):
        """Test finding a solution."""
        numbers, target = simple_instance
        solver = SubsetSumSolver(algorithm=algorithm)
        result = solver.solve(numbers, target)
        
        assert result.satisfiable is True
        assert result.solution is not None
        assert verify_subset_sum_solution(numbers, target, result.solution)
    
    @pytest.mark.parametrize("algorithm", ["brute_force", "backtrack", "dynamic"])
    def test_no_solution(self, no_solution_instance, algorithm):
        """Test detecting no solution."""
        numbers, target = no_solution_instance
        solver = SubsetSumSolver(algorithm=algorithm)
        result = solver.solve(numbers, target)
        
        assert result.satisfiable is False
    
    def test_empty_subset(self):
        """Target 0 should always have empty subset solution."""
        solver = SubsetSumSolver()
        result = solver.solve([1, 2, 3], 0)
        
        assert result.satisfiable is True
        assert result.solution == []
    
    def test_single_element(self):
        """Test with single element."""
        solver = SubsetSumSolver()
        result = solver.solve([5], 5)
        
        assert result.satisfiable is True
        assert result.solution == [5]
