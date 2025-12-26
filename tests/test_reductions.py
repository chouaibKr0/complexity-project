"""Tests for reductions."""
import pytest
from src.reductions import reduce_sat_to_3sat, reduce_3sat_to_subset_sum, reduce_sat_to_subset_sum
from src.solvers import SATSolver, ThreeSATSolver, SubsetSumSolver


class TestSATTo3SAT:
    """Test SAT to 3-SAT reduction."""
    
    def test_single_literal_clause(self):
        """Test reduction of single-literal clause."""
        clauses = [[1]]  # Just (x1)
        result = reduce_sat_to_3sat(clauses, 1)
        
        # All clauses in result should have exactly 3 literals
        for clause in result.reduced_instance:
            assert len(clause) == 3
    
    def test_two_literal_clause(self):
        """Test reduction of two-literal clause."""
        clauses = [[1, 2]]  # (x1 OR x2)
        result = reduce_sat_to_3sat(clauses, 2)
        
        for clause in result.reduced_instance:
            assert len(clause) == 3
    
    def test_three_literal_unchanged(self):
        """3-literal clause should remain unchanged."""
        clauses = [[1, 2, 3]]
        result = reduce_sat_to_3sat(clauses, 3)
        
        assert [1, 2, 3] in result.reduced_instance or \
               any(set(c) == {1, 2, 3} for c in result.reduced_instance)
    
    def test_preserves_satisfiability(self):
        """Reduction should preserve satisfiability."""
        # Satisfiable SAT instance
        sat_clauses = [[1, 2], [-1, 2], [1, -2]]
        
        sat_solver = SATSolver(algorithm="dpll")
        sat_result = sat_solver.solve(sat_clauses)
        
        # Reduce to 3-SAT
        reduction = reduce_sat_to_3sat(sat_clauses)
        
        three_sat_solver = ThreeSATSolver(algorithm="dpll")
        three_sat_result = three_sat_solver.solve(reduction.reduced_instance)
        
        # Both should have same satisfiability
        assert sat_result.satisfiable == three_sat_result.satisfiable


class TestThreeSATToSubsetSum:
    """Test 3-SAT to Subset Sum reduction."""
    
    def test_simple_reduction(self):
        """Test basic 3-SAT to Subset Sum reduction."""
        clauses = [[1, 2, 3], [-1, -2, 3]]
        result = reduce_3sat_to_subset_sum(clauses, 3)
        
        assert len(result.numbers) > 0
        assert result.target > 0
    
    def test_preserves_satisfiability(self):
        """Reduction should preserve satisfiability."""
        # Satisfiable 3-SAT
        clauses = [[1, 2, 3], [-1, 2, -3], [1, -2, 3]]
        
        three_sat_solver = ThreeSATSolver()
        three_sat_result = three_sat_solver.solve(clauses)
        
        reduction = reduce_3sat_to_subset_sum(clauses, 3)
        
        ss_solver = SubsetSumSolver()
        ss_result = ss_solver.solve(reduction.numbers, reduction.target)
        
        assert three_sat_result.satisfiable == ss_result.satisfiable

class TestSATToSubsetSum:
    """Test SAT to Subset Sum reduction."""
    
    def test_simple_reduction(self):
        """Test basic SAT to Subset Sum reduction."""
        clauses = [[1, 2, 3], [-1, -2, 3]]
        result = reduce_sat_to_subset_sum(clauses, 3)
        
        assert len(result.numbers) > 0
        assert result.target > 0
    
    def test_preserves_satisfiability(self):
        """Reduction should preserve satisfiability."""
        # Satisfiable SAT
        clauses = [[1, 2, 3], [-1, 2, -3], [1, -2, 3]]
        
        sat_solver = SATSolver()
        sat_result = sat_solver.solve(clauses)
        
        reduction = reduce_sat_to_subset_sum(clauses, 3)
        
        ss_solver = SubsetSumSolver()
        ss_result = ss_solver.solve(reduction.numbers, reduction.target)
        
        assert sat_result.satisfiable == ss_result.satisfiable
