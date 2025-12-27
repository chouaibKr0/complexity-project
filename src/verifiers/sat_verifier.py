"""
SAT Solution Verifier.

Verifies that a given assignment satisfies a SAT formula.
Verification runs in polynomial time O(n * m) where n = variables, m = clauses.

This demonstrates that SAT is in NP: solutions can be verified efficiently.
"""
from typing import Any


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
    
    TODO: Implement verification logic
    """
    # TODO: Implement SAT verification
    # For each clause:
    #   - Check if at least one literal is satisfied
    #   - A positive literal i is satisfied if assignment[i] = True
    #   - A negative literal -i is satisfied if assignment[i] = False
    # Return True only if ALL clauses are satisfied
    
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
    
    TODO: Implement this helper
    """
    # Get the variable index (absolute value of literal)
    var = abs(literal)
    
    # Get the variable's truth value from assignment
    var_value = assignment.get(var, False)
    
    # Positive literal: return var value directly
    # Negative literal: return negation of var value
    if literal > 0:
        return var_value
    else:
        return not var_value


def evaluate_clause(clause: list[int], assignment: dict[int, bool]) -> bool:
    """
    Evaluate a single clause (disjunction of literals).
    
    TODO: Implement this helper
    """
    # A clause is a disjunction (OR) of literals
    # It's satisfied if AT LEAST ONE literal is True
    for literal in clause:
        if evaluate_literal(literal, assignment):
            # Found a true literal -> clause is satisfied
            return True
    
    # No literal was true -> clause is unsatisfied
    return False
