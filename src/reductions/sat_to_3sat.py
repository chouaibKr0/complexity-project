"""
SAT to 3-SAT Reduction.

This module implements the polynomial-time reduction from SAT to 3-SAT.
This proves that 3-SAT is NP-hard (since SAT is NP-complete).

Reduction technique:
- Clauses with 1 literal: (a) -> (a ∨ y ∨ z) ∧ (a ∨ y ∨ ¬z) ∧ (a ∨ ¬y ∨ z) ∧ (a ∨ ¬y ∨ ¬z)
- Clauses with 2 literals: (a ∨ b) -> (a ∨ b ∨ y) ∧ (a ∨ b ∨ ¬y)
- Clauses with 3 literals: Keep as is
- Clauses with k>3 literals: (a ∨ b ∨ c ∨ d ∨ ...) -> 
    (a ∨ b ∨ y1) ∧ (¬y1 ∨ c ∨ y2) ∧ (¬y2 ∨ d ∨ y3) ∧ ... (chain with auxiliary variables)

"""
from dataclasses import dataclass


@dataclass 
class ReductionResult:
    """Result of a reduction."""
    original_variables: int
    original_clauses: int
    reduced_variables: int  
    reduced_clauses: int
    reduced_instance: list[list[int]]
    auxiliary_var_start: int  # First auxiliary variable ID


def reduce_sat_to_3sat(clauses: list[list[int]], num_variables: int = None) -> ReductionResult:
    """
    Reduce a SAT instance to an equisatisfiable 3-SAT instance.
    
    This is a polynomial-time reduction.
    
    Args:
        clauses: SAT instance in CNF form.
        num_variables: Number of variables (auto-detected if None).
    
    Returns:
        ReductionResult with the 3-SAT instance.
    
    Complexity: O(sum of clause lengths) - polynomial time
    
   
    """
    if num_variables is None:
        num_variables = max(abs(lit) for clause in clauses for lit in clause) if clauses else 0

    reduced_clauses: list[list[int]] = []

    aux_var_counter = num_variables + 1
    auxiliary_var_start = aux_var_counter

    for clause in clauses:
        size = len(clause)

        if size == 1:
            a = clause[0]
            y = aux_var_counter
            z = aux_var_counter + 1
            aux_var_counter += 2

            reduced_clauses.extend(
                transform_clause_size_1(a, y, z)
            )

        elif size == 2:
            a, b = clause
            y = aux_var_counter
            aux_var_counter += 1

            reduced_clauses.extend(
                transform_clause_size_2(a, b, y)
            )

        elif size == 3:
            reduced_clauses.append(clause.copy())

        else:  # size > 3
            reduced = transform_clause_size_large(clause, aux_var_counter)
            reduced_clauses.extend(reduced)
            aux_var_counter += size - 3

    return ReductionResult(
        original_variables=num_variables,
        original_clauses=len(clauses),
        reduced_variables=aux_var_counter - 1,
        reduced_clauses=len(reduced_clauses),
        reduced_instance=reduced_clauses,
        auxiliary_var_start=auxiliary_var_start
    )


def transform_clause_size_1(literal: int, aux_var_1: int, aux_var_2: int) -> list[list[int]]:
    """
    Transform a 1-literal clause to 3-SAT clauses.
    """
    return [
        [literal,  aux_var_1,  aux_var_2],
        [literal,  aux_var_1, -aux_var_2],
        [literal, -aux_var_1,  aux_var_2],
        [literal, -aux_var_1, -aux_var_2],
    ]


def transform_clause_size_2(lit1: int, lit2: int, aux_var: int) -> list[list[int]]:
    """
    Transform a 2-literal clause to 3-SAT clauses.
    """
    return [
        [lit1, lit2,  aux_var],
        [lit1, lit2, -aux_var],
    ]


def transform_clause_size_large(literals: list[int], aux_var_start: int) -> list[list[int]]:
    """
    Transform a clause with >3 literals to 3-SAT clauses.
    """
    clauses: list[list[int]] = []

    # First clause
    clauses.append([literals[0], literals[1], aux_var_start])

    current_aux = aux_var_start

    # Chain middle clauses
    for i in range(2, len(literals) - 2):
        next_aux = current_aux + 1
        clauses.append([-current_aux, literals[i], next_aux])
        current_aux = next_aux

    # Last clause
    clauses.append([-current_aux, literals[-2], literals[-1]])

    return clauses