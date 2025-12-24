"""Tests for 3-SAT Solver."""
import pytest
from src.solvers import ThreeSATSolver
from src.verifiers import verify_3sat_solution


class TestThreeSATSolver:
    """Test suite for 3-SAT solver."""
    
    @pytest.fixture
    def simple_3sat_instance(self):
        """Simple 3-SAT instance."""
        return [[1, 2, 3], [-1, 2, -3], [1, -2, 3]]
    
    @pytest.mark.parametrize("algorithm", ["brute_force", "backtrack", "dpll"])
    def test_simple_3sat(self, simple_3sat_instance, algorithm):
        """Test simple 3-SAT solving."""
        solver = ThreeSATSolver(algorithm=algorithm)
        result = solver.solve(simple_3sat_instance)
        
        if result.satisfiable:
            assert verify_3sat_solution(simple_3sat_instance, result.solution)
    
    def test_invalid_clause_size(self):
        """Test that non-3-SAT instance is rejected."""
        from src.utils.errors import ValidationError
        
        solver = ThreeSATSolver()
        invalid_instance = [[1, 2], [1, 2, 3]]  # First clause has only 2 literals
        
        with pytest.raises(ValidationError):
            solver.solve(invalid_instance)
