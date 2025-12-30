"""Input validation utilities."""
from typing import Any
from .errors import ValidationError


def normalize_sat(clauses: list[list[int]]) -> tuple[list[list[int]], int, dict[int, int]]:
    """
    Normalize clauses so variables are consecutively numbered from 1 to n.
    
    Args:
        clauses: List of clauses with potentially non-consecutive variable numbers.
    
    Returns:
        Tuple of (normalized_clauses, num_variables, var_mapping)
        - normalized_clauses: Clauses with variables renumbered 1 to n
        - num_variables: Number of distinct variables (n)
        - var_mapping: Dict mapping original var -> new var (for debugging/reverse mapping)
    """
    # Collect all variables and sort them
    all_vars = sorted(set(abs(lit) for clause in clauses for lit in clause))
    num_variables = len(all_vars)
    
    # Create mapping: original_var -> new_var (1, 2, 3, ...)
    var_mapping = {old_var: new_var for new_var, old_var in enumerate(all_vars, start=1)}
    
    # Normalize clauses
    normalized_clauses = []
    for clause in clauses:
        normalized_clause = []
        for lit in clause:
            sign = 1 if lit > 0 else -1
            new_var = var_mapping[abs(lit)]
            normalized_clause.append(sign * new_var)
        normalized_clauses.append(normalized_clause)
    
    return normalized_clauses, num_variables, var_mapping


def validate_sat_instance(clauses: list[list[int]], num_variables: int |None = None) -> bool:
    """
    Validate a SAT instance in CNF form.
    
    Args:
        clauses: List of clauses, where each clause is a list of literals.
                 Positive int = positive literal, negative int = negated literal.
        num_variables: Expected number of variables (optional).
    
    Returns:
        True if the instance is valid.
    
    Raises:
        ValidationError: If the instance is invalid.
    """
    if not isinstance(clauses, list):
        raise ValidationError("Clauses must be a list")
    
    if len(clauses) == 0:
        raise ValidationError("Empty clause set")
    
    all_vars = set()
    for i, clause in enumerate(clauses):
        if not isinstance(clause, list):
            raise ValidationError(f"Clause {i} must be a list")
        if len(clause) == 0:
            raise ValidationError(f"Clause {i} is empty (unsatisfiable)")
        
        for literal in clause:
            if not isinstance(literal, int) or literal == 0:
                raise ValidationError(f"Invalid literal {literal} in clause {i}")
            all_vars.add(abs(literal))
    
    if num_variables is not None and len(all_vars) != num_variables:
        raise ValidationError(f"Expected {num_variables} variables, found {len(all_vars)}")
    

    
    return True


def validate_3sat_instance(clauses: list[list[int]]) -> bool: 
    """
    Validate and  a 3-SAT instance (each clause has exactly 3 literals).
    
    Returns:
        True if valid 3-SAT instance.
    
    Raises:
        ValidationError: If any clause doesn't have exactly 3 literals.
    """
    for i, clause in enumerate(clauses):
        if not isinstance(clause, list):
            raise ValidationError(f"Clause {i} must be a list")
        if len(clause) != 3:
            raise ValidationError(f"Clause {i} has {len(clause)} literals, expected 3")
    
    return validate_sat_instance(clauses)


def validate_subset_sum_instance(numbers: list[int], target: int) -> bool:
    """
    Validate a Subset Sum instance.
    
    Args:
        numbers: List of positive integers.
        target: Target sum (positive integer).
    
    Raises:
        ValidationError: If the instance is invalid.
    """
    if not isinstance(numbers, list):
        raise ValidationError("Numbers must be a list")
    
    if len(numbers) == 0:
        raise ValidationError("Empty number set")
    
    for i, num in enumerate(numbers):
        if not isinstance(num, int):
            raise ValidationError(f"Element {i} is not an integer")
        if num < 0:
            raise ValidationError(f"Element {i} is negative: {num}")
    
    if not isinstance(target, int) or target < 0:
        raise ValidationError(f"Target must be a non-negative integer, got {target}")
    
    return True


def validate_assignment(assignment: dict[int, bool], num_variables: int) -> bool:
    """Validate a variable assignment."""
    if not isinstance(assignment, dict):
        raise ValidationError("Assignment must be a dictionary")
    
    for var, val in assignment.items():
        if not isinstance(var, int) or var < 1:
            raise ValidationError(f"Invalid variable: {var}")
        if not isinstance(val, bool):
            raise ValidationError(f"Invalid value for variable {var}: {val}")
    
    return True
