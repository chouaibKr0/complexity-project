"""
SAT to Subset Sum Reduction.

This module implements the polynomial-time reduction from SAT to Subset Sum.
This proves that Subset Sum is NP-hard.


Reference: Standard textbook reduction (e.g., Sipser's "Introduction to the 
Theory of Computation" or Cormen et al. "Introduction to Algorithms")


"""
from dataclasses import dataclass


@dataclass
class SubsetSumReduction:
    """Result of SAT to Subset Sum reduction."""
    numbers: list[int]
    target: int
    # Mapping information for solution translation
    variable_positive_indices: dict[int, int]  # var -> index in numbers for positive
    variable_negative_indices: dict[int, int]  # var -> index in numbers for negative
    slack_indices: list[int]  # indices of slack variables


def reduce_sat_to_subset_sum(clauses: list[list[int]], num_variables: int = None) -> SubsetSumReduction:
    """
    Reduce a SAT instance to a Subset Sum instance.
    
    
    """
    if num_variables is None:
        num_variables = max(abs(lit) for clause in clauses for lit in clause) if clauses else 0
    
    num_clauses = len(clauses)
    
    # Base for digit encoding (large enough to avoid carry)
    B = 10

    numbers: list[int] = []

    var_pos_idx: dict[int, int] = {}
    var_neg_idx: dict[int, int] = {}
    slack_indices: list[int] = []

    # Helper: build a number from digit positions
    def build_number(digits: dict[int, int]) -> int:
        value = 0
        for pos, digit in digits.items():
            value += digit * (B ** pos)
        return value

    # 1. Variable numbers
    
    for i in range(1, num_variables + 1):
        pos_digits = {i - 1: 1}
        neg_digits = {i - 1: 1}

        for j, clause in enumerate(clauses):
            if i in clause:
                pos_digits[num_variables + j] = 1
            if -i in clause:
                neg_digits[num_variables + j] = 1

        pos_number = build_number(pos_digits)
        neg_number = build_number(neg_digits)

        var_pos_idx[i] = len(numbers)
        numbers.append(pos_number)

        var_neg_idx[i] = len(numbers)
        numbers.append(neg_number)

    # 2. Slack numbers (per clause)
   
    for j, clause in enumerate(clauses):
        clause_size = len(clause)

        # Need (clause_size - 1) slack variables
        for _ in range(clause_size - 1):
            digits = {num_variables + j: 1}
            slack_indices.append(len(numbers))
            numbers.append(build_number(digits))

    
    # 3. Target number
    target_digits = {}

    # Variable positions → exactly 1
    for i in range(num_variables):
        target_digits[i] = 1

    # Clause positions → clause size
    for j, clause in enumerate(clauses):
        target_digits[num_variables + j] = len(clause)

    target = build_number(target_digits)

    return SubsetSumReduction(
        numbers=numbers,
        target=target,
        variable_positive_indices=var_pos_idx,
        variable_negative_indices=var_neg_idx,
        slack_indices=slack_indices
    )

def translate_subset_to_assignment(
    subset: list[int], 
    reduction: SubsetSumReduction,
    num_variables: int
) -> dict[int, bool]:
    """
    Translate a Subset Sum solution back to a SAT assignment.
    
    Args:
        subset: Solution to the Subset Sum instance.
        reduction: The reduction result containing mappings.
        num_variables: Number of variables in original SAT.
    
    Returns:
        Variable assignment for the SAT instance.
    
    
    """
    assignment: dict[int, bool] = {}

    # Convert subset to a set for fast lookup
    subset_set = set(subset)

    for var in range(1, num_variables + 1):
        pos_index = reduction.variable_positive_indices[var]
        neg_index = reduction.variable_negative_indices[var]

        pos_number = reduction.numbers[pos_index]
        neg_number = reduction.numbers[neg_index]

        if pos_number in subset_set and neg_number in subset_set:
            raise ValueError(
                f"Inconsistent Subset Sum solution: both x{var} and ¬x{var} selected."
            )

        if pos_number in subset_set:
            assignment[var] = True
        elif neg_number in subset_set:
            assignment[var] = False
        else:
            raise ValueError(
                f"Incomplete Subset Sum solution: neither x{var} nor ¬x{var} selected."
            )

    return assignment
