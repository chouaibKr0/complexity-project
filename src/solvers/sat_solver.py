"""
SAT Solver Implementation.

This module implements solvers for the Boolean Satisfiability Problem (SAT).
SAT is NP-complete: given a Boolean formula in CNF, determine if there exists
an assignment that makes the formula true.

Algorithms to implement:
1. Brute Force - Try all 2^n assignments
2. Backtracking - Basic backtracking with pruning
3. DPLL - Davis-Putnam-Logemann-Loveland algorithm

"""

import time
from typing import Any
import numpy as np

from .base import BaseSolver, SolverResult
from ..utils.validation import validate_sat_instance, normalize_sat
from ..utils.timer import Timer


class SATSolver(BaseSolver):
    """
    Solver for SAT (Boolean Satisfiability Problem).
    
    Input: CNF formula as list of clauses
           Each clause is a list of literals (positive or negative integers)
           Example: [[1, -2], [2, 3], [-1, -3]] represents
                    (x1 OR NOT x2) AND (x2 OR x3) AND (NOT x1 OR NOT x3)
    
    Output: SolverResult with:
            - satisfiable: bool
            - solution: dict mapping variable -> bool, or None if UNSAT
    """
    
    def __init__(self, algorithm: str = "dpll"):
        """
        Initialize SAT solver.
        
        Args:
            algorithm: One of "brute_force", "backtrack", "dpll"
        """
        super().__init__(name=f"SAT-{algorithm}")
        self.algorithm = algorithm
    
    def solve(self, clauses: list[list[int]], num_variables: int | None = None) -> SolverResult:
        """
        Solve the SAT instance.
        
        Args:
            clauses: List of clauses in CNF form.
            num_variables: Number of variables (auto-detected if None).
        
        Returns:
            SolverResult with satisfiability and assignment.
        """

        # Validate and normalize input (variables become 1, 2, ..., n)
        validate_sat_instance(clauses, num_variables)
        clauses, num_variables, var_mapping = normalize_sat(clauses)
        
        self.stats["calls"] += 1
        nodes = 0
        
        with Timer("sat_solve") as timer:
            if self.algorithm == "brute_force":
                sat, assignment, nodes = self._brute_force(clauses, num_variables)
            elif self.algorithm == "backtrack":
                sat, assignment, nodes = self._backtrack(clauses, num_variables)
            elif self.algorithm == "dpll":
                sat, assignment, nodes = self._dpll(clauses, num_variables)
            else:
                raise ValueError(f"Unknown algorithm: {self.algorithm}")
        
        self.stats["total_time"] += timer.elapsed
        self.stats["nodes_explored"] += nodes
        
        return SolverResult(
            satisfiable=sat,
            solution=assignment,
            time_seconds=timer.elapsed,
            nodes_explored=nodes,
            algorithm=self.algorithm
        )
    
    def _brute_force(self, clauses: list[list[int]], n: int) -> tuple[bool, dict | None, int]:
        """
        Brute force: enumerate all 2^n assignments.
        
        - Generate all possible truth assignments
        - Check each assignment against all clauses
        - Return first satisfying assignment found
        
        Returns:
            (is_satisfiable, assignment_dict, nodes_explored)
        """
        nodes = 0
        
        # Try all 2^n possible assignments (from 0 to 2^n - 1)
        for i in range(2 ** n):
            nodes += 1
            
            # Build assignment: bit j of i gives truth value for variable j+1
            # Example: i=5 (binary 101) with n=3 -> {1: True, 2: False, 3: True}
            assignment = {}
            for var in range(1, n + 1):
                # Check if bit (var-1) is set in i
                assignment[var] = bool((i >> (var - 1)) & 1)
            
            # Check if this assignment satisfies all clauses
            if self._evaluate_formula(clauses, assignment):
                return True, assignment, nodes
        
        # No satisfying assignment found
        return False, None, nodes
    
    def _backtrack(self, clauses: list[list[int]], n: int) -> tuple[bool, dict | None, int]:
        """
        Backtracking with early termination.

        - Assign variables one by one
        - Prune when a clause becomes unsatisfiable
        - Backtrack when stuck
        
        Returns:
            (is_satisfiable, assignment_dict, nodes_explored)
        """
        self._nodes = 0  # Counter for nodes explored
        
        def backtrack_helper(assignment: dict[int, bool], var: int) -> dict[int, bool] | None:
            """
            Recursive backtracking helper.
            
            Args:
                assignment: Current partial assignment
                var: Next variable to assign (1 to n)
            
            Returns:
                Complete satisfying assignment or None
            """
            self._nodes += 1
            
            # Check if any clause is already unsatisfied (early termination/pruning)
            result = self._evaluate_formula(clauses, assignment)
            if result is False:
                # Some clause is definitely unsatisfied -> prune this branch
                return None
            
            # If all variables assigned and formula is satisfied
            if var > n:
                return assignment if result else None
            
            # Try assigning True to variable var
            assignment[var] = True
            solution = backtrack_helper(assignment.copy(), var + 1)
            if solution is not None:
                return solution
            
            # Try assigning False to variable var (backtrack)
            assignment[var] = False
            solution = backtrack_helper(assignment.copy(), var + 1)
            if solution is not None:
                return solution
            
            # Neither value works -> backtrack
            return None
        
        result = backtrack_helper({}, 1)
        return (True, result, self._nodes) if result else (False, None, self._nodes)
    
    def _dpll(self, clauses: list[list[int]], n: int) -> tuple[bool, dict | None, int]:
        """
        DPLL algorithm with unit propagation and pure literal elimination.
        
        Key steps:
        1. Unit propagation: if a clause has one literal, it must be true
        2. Pure literal elimination: if a variable appears with one polarity, set it
        3. Branching: choose a variable and try both values
        
        Returns:
            (is_satisfiable, assignment_dict, nodes_explored)
        """

        self._nodes = 0
        
        def dpll_helper(clauses: list[list[int]], assignment: dict[int, bool]) -> dict[int, bool] | None:
            """
            Recursive DPLL helper.
            
            Args:
                clauses: Current (possibly simplified) set of clauses
                assignment: Current partial assignment
            
            Returns:
                Complete satisfying assignment or None
            """
            self._nodes += 1
            
            # Step 1: Unit propagation - repeat until no more unit clauses
            clauses, assignment, conflict = self._unit_propagate(clauses, assignment)
            if conflict:
                return None  # Conflict detected during propagation
            
            # Step 2: Pure literal elimination
            pure_literals = self._find_pure_literals(clauses, assignment)
            for var, value in pure_literals.items():
                assignment[var] = value
                # Remove clauses satisfied by pure literal
                clauses = [c for c in clauses if not self._clause_satisfied(c, assignment)]
            
            # Base case: all clauses satisfied (empty clause list)
            if not clauses:
                # Fill in any unassigned variables (can be anything)
                for var in range(1, n + 1):
                    if var not in assignment:
                        assignment[var] = True
                return assignment
            
            # Base case: empty clause found (unsatisfiable)
            if any(len(c) == 0 for c in clauses):
                return None
            
            # Step 3: Branching - choose an unassigned variable
            # Find first unassigned variable
            unassigned = None
            for var in range(1, n + 1):
                if var not in assignment:
                    unassigned = var
                    break
            
            if unassigned is None:
                # All variables assigned but clauses remain -> check satisfiability
                return assignment if self._evaluate_formula(clauses, assignment) else None
            
            # Try True first
            new_assignment = assignment.copy()
            new_assignment[unassigned] = True
            # Simplify clauses with new assignment
            simplified = self._simplify_clauses(clauses, unassigned, True)
            result = dpll_helper(simplified, new_assignment)
            if result is not None:
                return result
            
            # Try False
            new_assignment = assignment.copy()
            new_assignment[unassigned] = False
            # Simplify clauses with new assignment
            simplified = self._simplify_clauses(clauses, unassigned, False)
            result = dpll_helper(simplified, new_assignment)
            return result
        
        result = dpll_helper(clauses, {})
        return (True, result, self._nodes) if result else (False, None, self._nodes)
    
    # Helper methods you might want to use
    
    def _evaluate_clause(self, clause: list[int], assignment: dict[int, bool]) -> bool | None:
        """
        Evaluate a clause under a partial assignment.
        
        Returns:
            True if satisfied, False if unsatisfied, None if undetermined
        """
        has_unassigned = False
        
        for literal in clause:
            var = abs(literal)
            
            if var not in assignment:
                # Variable not yet assigned
                has_unassigned = True
                continue
            
            # Get the literal's value: positive literal = var value, negative = NOT var value
            value = assignment[var] if literal > 0 else not assignment[var]
            
            if value:
                # Clause is satisfied (at least one True literal)
                return True
        
        # If we have unassigned variables, clause is undetermined
        # Otherwise, all literals are False -> clause unsatisfied
        return None if has_unassigned else False
    
    def _evaluate_formula(self, clauses: list[list[int]], assignment: dict[int, bool]) -> bool | None:
        """
        Evaluate entire formula under assignment.
        
        Returns:
            True if all clauses satisfied, False if any unsatisfied, None if undetermined
        """
        all_satisfied = True
        
        for clause in clauses:
            result = self._evaluate_clause(clause, assignment)
            
            if result is False:
                # One clause is definitely unsatisfied -> formula is UNSAT
                return False
            elif result is None:
                # Undetermined clause -> can't conclude formula is satisfied yet
                all_satisfied = False
        
        # All clauses satisfied or some undetermined
        return True if all_satisfied else None
    
    def _unit_propagate(self, clauses: list[list[int]], assignment: dict[int, bool]) -> tuple[list[list[int]], dict[int, bool], bool]:
        """
        Apply unit propagation.
        
        Returns:
            (simplified_clauses, updated_assignment, is_conflict)
        """

        assignment = assignment.copy()
        clauses = [c[:] for c in clauses]  # Deep copy clauses
        
        changed = True
        while changed:
            changed = False
            
            for clause in clauses:
                # Remove assigned literals from clause
                unassigned = []
                satisfied = False
                
                for literal in clause:
                    var = abs(literal)
                    if var in assignment:
                        # Check if this literal satisfies the clause
                        value = assignment[var] if literal > 0 else not assignment[var]
                        if value:
                            satisfied = True
                            break
                        # Literal is False, don't add to unassigned
                    else:
                        unassigned.append(literal)
                
                if satisfied:
                    continue
                
                if len(unassigned) == 0:
                    # All literals are False -> conflict
                    return clauses, assignment, True
                
                if len(unassigned) == 1:
                    # Unit clause: the single literal must be True
                    literal = unassigned[0]
                    var = abs(literal)
                    value = literal > 0  # True if positive, False if negative
                    assignment[var] = value
                    changed = True
            
            # Simplify clauses by removing satisfied clauses
            clauses = [c for c in clauses if not self._clause_satisfied(c, assignment)]
        
        return clauses, assignment, False
    
    def _find_pure_literals(self, clauses: list[list[int]], assignment: dict[int, bool]) -> dict[int, bool]:
        """Find all pure literals (appear with only one polarity)."""
        positive = set()  # Variables appearing positively
        negative = set()  # Variables appearing negatively
        
        for clause in clauses:
            for literal in clause:
                var = abs(literal)
                if var not in assignment:  # Only consider unassigned variables
                    if literal > 0:
                        positive.add(var)
                    else:
                        negative.add(var)
        
        pure = {}
        # Variables that appear only positively -> set to True
        for var in positive - negative:
            pure[var] = True
        # Variables that appear only negatively -> set to False
        for var in negative - positive:
            pure[var] = False
        
        return pure
    
    def _clause_satisfied(self, clause: list[int], assignment: dict[int, bool]) -> bool:
        """Check if a clause is satisfied by the current assignment."""
        for literal in clause:
            var = abs(literal)
            if var in assignment:
                value = assignment[var] if literal > 0 else not assignment[var]
                if value:
                    return True
        return False
    
    def _simplify_clauses(self, clauses: list[list[int]], var: int, value: bool) -> list[list[int]]:
        """
        Simplify clauses after assigning var=value.
        
        - Remove clauses satisfied by this assignment
        - Remove false literals from remaining clauses
        """
        simplified = []
        
        for clause in clauses:
            new_clause = []
            satisfied = False
            
            for literal in clause:
                lit_var = abs(literal)
                
                if lit_var == var:
                    # This literal involves the assigned variable
                    lit_value = value if literal > 0 else not value
                    if lit_value:
                        # Clause is satisfied
                        satisfied = True
                        break
                    # Literal is False, skip it (don't add to new_clause)
                else:
                    new_clause.append(literal)
            
            if not satisfied:
                simplified.append(new_clause)
        
        return simplified
