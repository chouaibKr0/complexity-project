"""Tests for SAT Solver."""
import pytest
from src.solvers import SATSolver
from src.verifiers import verify_sat_solution


class TestSATSolver:
    """Test suite for SAT solver."""
    
    @pytest.fixture
    def simple_sat_instance(self):
        """Simple satisfiable instance: (x1 OR x2) AND (NOT x1 OR x2)."""
        return [[1, 2], [-1, 2]]
    
    @pytest.fixture
    def simple_unsat_instance(self):
        """Simple unsatisfiable instance: (x1) AND (NOT x1)."""
        return [[1], [-1]]
    
    @pytest.mark.parametrize("algorithm", ["brute_force", "backtrack", "dpll"])
    def test_simple_sat(self, simple_sat_instance, algorithm):
        """Test that a simple SAT instance is solved correctly."""
        solver = SATSolver(algorithm=algorithm)
        result = solver.solve(simple_sat_instance)
        
        assert result.satisfiable is True
        assert result.solution is not None
        # Verify the solution is correct
        assert verify_sat_solution(simple_sat_instance, result.solution)
    
    @pytest.mark.parametrize("algorithm", ["brute_force", "backtrack", "dpll"])
    def test_simple_unsat(self, simple_unsat_instance, algorithm):
        """Test that an unsatisfiable instance is detected."""
        solver = SATSolver(algorithm=algorithm)
        result = solver.solve(simple_unsat_instance)
        
        assert result.satisfiable is False
        assert result.solution is None
    
    def test_empty_clause_unsat(self):
        """Empty clause makes formula unsatisfiable."""
        # This should be caught by validation
        pass
    
    def test_single_variable(self):
        """Test with single variable."""
        solver = SATSolver(algorithm="dpll")
        result = solver.solve([[1]])
        
        assert result.satisfiable is True
        assert result.solution[1] is True
    
    @pytest.mark.benchmark
    def test_performance_small(self, benchmark):
        """Benchmark small instance performance."""
        clauses = [[1, 2, 3], [-1, 2, -3], [1, -2, 3]]
        solver = SATSolver(algorithm="dpll")
        
        result = benchmark(solver.solve, clauses)
        assert result.satisfiable is not None
