"""
3-SAT Solution Verifier.

Verifies that a given assignment satisfies a 3-SAT formula.
Same as SAT verifier but also checks that each clause has exactly 3 literals.
"""
from typing import Any

from src.utils.errors import ValidationError
from src.utils.validation import validate_sat_instance
from .sat_verifier import verify_sat_solution



def verify_3sat_solution(clauses: list[list[int]], assignment: dict[int, bool]) -> bool:
    """
    Verify that an assignment satisfies a 3-SAT formula.
    
    Args:
        clauses: 3-CNF formula (each clause has exactly 3 literals).
        assignment: Variable assignment {var_id: True/False}.
    
    Returns:
        True if valid 3-SAT and assignment satisfies all clauses.
    
    TODO: Implement verification logic
    """
    
    # 1. First verify this is actually 3-SAT (each clause has exactly 3 literals) 2. Normalize variables to 1..n 3. Evaluate CNF under assignment
    clauses, num_literals = _validate_and_normalize_3sat(clauses)
    if clauses == [] or num_literals == 0:
        return False
    A = [assignment.get(i + 1, False) for i in range(num_literals)]
    # 3. Evaluate CNF under assignment
    return _eval_cnf(clauses, A)

    


def _validate_and_normalize_3sat(clauses: list[list[int]]) -> tuple[list[list[int]], int]:
    """
    Validate and normalize a 3-SAT instance (each clause has exactly 3 literals).
    Returns:
        Tuple of (normalized_clauses, num_variables) where variables are 1 to num_num_variables. 
    """
    # Validate: each clause is a list of exactly 3 ints

    for i, clause in enumerate(clauses):
        if not isinstance(clause, list):
            return [], 0
        if len(clause) != 3:
            return [], 0
        for l in clause:
            if not isinstance(l, int):
                return [], 0

    # Find all variable indices (abs(literal))
    var_set = set(abs(l) for clause in clauses for l in clause)
    var_list = sorted(var_set)
    var_map = {v: i+1 for i, v in enumerate(var_list)}  # map old var to 1..n

    # Normalize: replace each literal l with sign(l) * new_var_index
    normalized = []
    for clause in clauses:
        norm_clause = []
        for l in clause:
            v = abs(l)
            sign = 1 if l > 0 else -1
            norm_clause.append(sign * var_map[v])
        normalized.append(norm_clause)

    num_variables = len(var_list)
    return normalized, num_variables

    
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
        if _eval_literal(l, A) == True:
            return True
    return False

def _eval_literal(l: int, A: list[bool]) -> bool:
    """
    Evaluate a single literal l under assignment A.
    Args:
        l: Literal (positive or negative integer).
        A: Assignment list where A[i] is the value of variable (i+1).
    Returns:
        True if l is satisfied under A, False otherwise.
    """
    var_index = abs(l) - 1  # Convert to 0-based index
    if l > 0:
        return A[var_index]  # Positive literal
    else:
        return not A[var_index]  # Negative literal
