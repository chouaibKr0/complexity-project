"""
3-SAT Solution Verifier.

Verifies that a given assignment satisfies a 3-SAT formula.
Same as SAT verifier but also checks that each clause has exactly 3 literals.
"""
from typing import Any
from src.solvers.base import SolverResult
from src.utils.errors import ValidationError
from src.utils.validation import validate_sat_instance, normalize_sat
from .sat_verifier import verify_sat_solution


def verify_3sat_solver_result(clauses: list[list[int]], result: SolverResult) -> bool|None:
    """
    Verify the result from a 3-SAT solver.
    Args:
        clauses: 3-CNF formula (each clause has exactly 3 literals).
        result: SolverResult from the 3-SAT solver.
    Returns:
        True if the solver result is correct, False otherwise.
    """
    if not isinstance(result, SolverResult):
        raise ValidationError("Result must be a SolverResult instance.")
    if result.satisfiable is None:
        # Verifier cannot determine unsatisfiability
        return None
    return verify_3sat_solution(clauses, result.solution) == result.satisfiable

def verify_3sat_solution(clauses: list[list[int]], assignment: Any) -> bool:
    """
    Verify that an assignment satisfies a 3-SAT formula.
    
    Args:
        clauses: 3-CNF formula (each clause has exactly 3 literals).
        assignment: Variable assignment {var_id: True/False}.
    
    Returns:
        True if valid 3-SAT and assignment satisfies all clauses.
    

    """
    
    validate_sat_instance(clauses)
    clauses, num_literals, var_mapping = normalize_sat(clauses)
    if assignment is not None:
        A = sat_solution_to_assignment(assignment) 
    else:
        raise ValidationError("Validation impossible with no assignment provided.")
    if len(A) > num_literals:
        raise ValidationError("Assignment length does not match number of literals.")
        # If solver returns partial model (e.g., DPLL), fill missing vars arbitrarily
    for v in range(1, num_literals + 1):
        assignment.setdefault(v, False)

    # Evaluate CNF correctly (handles negative literals)
    for C in clauses:
        ok_clause = False
        for l in C:
            v = abs(l)
            val = assignment[v]
            lit_true = val if l > 0 else (not val)
            if lit_true:
                ok_clause = True
                break
        if not ok_clause:
            return False
    return True

    

def sat_solution_to_assignment(solution: Any) -> list[bool]:
    """
    Convert a SAT solver solution to a list of variable assignments.
    
    Args:
        solution: Solver solution (dict {var_id: True/False}).
    
    Returns:
        List of integers where positive means True and negative means False.
    """
    if isinstance(solution, list) and all(isinstance(x, bool) for x in solution):
        return solution

    if not isinstance(solution, dict):
        raise ValidationError("Solution must be a dictionary or a list.")
    
    assignment = []
    for var_id, value in solution.items():
        if value:
            assignment.append(var_id)
        else:
            assignment.append(-var_id)
    return assignment


    
def _eval_cnf(F: list[list[int]], A: list[bool]) -> bool:
    """
    Evaluate CNF formula F under assignment A.
    Args:
        F: CNF formula (list of clauses).
        A: Assignment list where A[i] is the value of variable (i+1).
    Returns:
        True if F is satisfied under A, False otherwise.
    """
    for C in F:
        if _eval_clause(C, A) == False:
            return False
    return True

def _eval_clause(C: list[int], A: list[bool]) -> bool:
    """
    Evaluate a single clause C under assignment A.
    Args:
        C: Clause (list of literals).
        A: Assignment list where A[i] is the value of variable (i+1).
    Returns:        
        True if C is satisfied under A, False otherwise.    
    """
    for l in C:
            if len(A) > abs(l) - 1  and A[abs(l) - 1] == True:
                return True
    return False

