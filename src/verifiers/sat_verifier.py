"""
SAT Solution Verifier.

Verifies that a given assignment satisfies a SAT formula.
Verification runs in polynomial time O(n * m) where n = variables, m = clauses.

This demonstrates that SAT is in NP: solutions can be verified efficiently.
"""
from typing import Any
from src.solvers.base import SolverResult
from src.utils.errors import ValidationError

def verify_sat_solver_result(clauses: list[list[int]], result: SolverResult) -> bool|None:
    """
    Verify the result from a SAT solver.
    Args:
        clauses: CNF formula 
        result: SolverResult from the SAT solver.
    Returns:
        True if the solver result is correct, False otherwise.
    """
    if not isinstance(result, SolverResult):
        raise ValidationError("Result must be a SolverResult instance.")
    solution = {}
    if result.satisfiable is None:
        # Verifier cannot determine unsatisfiability
        return None
        try:
            solution: dict[int, bool] = result.solution
        except Exception:
            raise ValidationError("Solution must be a dictionary of variable assignments to verify.")
    return verify_sat_solution(clauses, solution) == result.satisfiable


def verify_sat_solution(clauses: list[list[int]], assignment: dict[int, bool]) -> bool:
    """
    Verify that an assignment satisfies a SAT formula.
    
    This is the polynomial-time certificate verifier for SAT.
    
    Args:
        clauses: CNF formula as list of clauses.
        assignment: Variable assignment {var_id: True/False}.
    
    Returns:
        True if assignment satisfies all clauses.
    
    Complexity: O(total_literals) - polynomial time
    
    """

    
    # Check each clause - ALL must be satisfied
    for clause in clauses:
        if not evaluate_clause(clause, assignment):
            # Found an unsatisfied clause -> formula is not satisfied
            return False
    
    # All clauses satisfied
    return True


def evaluate_literal(literal: int, assignment: dict[int, bool]) -> bool:
    """
    Evaluate a single literal under an assignment.

    """
    # Get the variable index (absolute value of literal)
    var = abs(literal)
    
    # Get the variable's truth value from assignment
    var_value = assignment.get(var, False)
    # The return of false when the variable is not assigned, will not pose a problem in evaluation(same holds for true). Since the absence of a variable in a correct assignment implies the satisfiability holds for both values.
    
    # Positive literal: return var value directly
    # Negative literal: return negation of var value
    if literal > 0:
        return var_value
    else:
        return not var_value


def evaluate_clause(clause: list[int], assignment: dict[int, bool]) -> bool:
    """
    Evaluate a single clause (disjunction of literals).

    """
    # A clause is a disjunction (OR) of literals
    # It's satisfied if AT LEAST ONE literal is True
    for literal in clause:
        if evaluate_literal(literal, assignment):
            # The return of false when the variable is not assigned, will not pose a problem in evaluation(same holds for true). Since the absence of a variable in a correct assignment implies the satisfiability holds for both values.
            # Found a true literal => clause is satisfied
            return True
    
    # No literal was true -> clause is unsatisfied
    return False
