from dataclasses import dataclass
from typing import List, Dict, Sequence, Union


@dataclass
class SubsetSumReduction:
    """Result of SAT -> SubsetSum reduction."""
    numbers: List[int]
    target: int
    variable_positive_indices: Dict[int, int]  # var -> index in numbers for positive
    variable_negative_indices: Dict[int, int]  # var -> index in numbers for negative
    slack_indices: List[int]  # indices of slack variables


def reduce_sat_to_subset_sum(clauses: List[List[int]], num_variables: int = None) -> SubsetSumReduction:
    if num_variables is None:
        num_variables = max((abs(lit) for clause in clauses for lit in clause), default=0)

    # Quick unsat check: empty clause means unsatisfiable
    for clause in clauses:
        if len(clause) == 0:
            raise ValueError("Instance contains an empty clause (unsatisfiable).")

    num_clauses = len(clauses)
    max_clause_size = max((len(c) for c in clauses), default=0)

    # Choose base B > maximum possible digit value to avoid carries
    B = max(2, max_clause_size + 1)

    def build_number(digits: Dict[int, int]) -> int:
        value = 0
        for pos, digit in digits.items():
            if digit >= B:
                raise ValueError(f"Digit {digit} at position {pos} >= base B={B} (would cause carry).")
            value += digit * (B ** pos)
        return value

    numbers: List[int] = []
    var_pos_idx: Dict[int, int] = {}
    var_neg_idx: Dict[int, int] = {}
    slack_indices: List[int] = []

    # 1) variable numbers (two per variable)
    for i in range(1, num_variables + 1):
        pos_digits = {i - 1: 1}
        neg_digits = {i - 1: 1}

        # add clause digits where this literal appears
        for j, clause in enumerate(clauses):
            if i in clause:
                pos_digits[num_variables + j] = pos_digits.get(num_variables + j, 0) + 1
            if -i in clause:
                neg_digits[num_variables + j] = neg_digits.get(num_variables + j, 0) + 1

        # Build numbers and append; store indices
        pos_number = build_number(pos_digits)
        var_pos_idx[i] = len(numbers)
        numbers.append(pos_number)

        neg_number = build_number(neg_digits)
        var_neg_idx[i] = len(numbers)
        numbers.append(neg_number)

    # 2) slack numbers: for each clause of size s, add (s-1) slack numbers with a 1 in clause position
    for j, clause in enumerate(clauses):
        s = len(clause)
        for _ in range(max(0, s - 1)):
            digits = {num_variables + j: 1}
            slack_indices.append(len(numbers))
            numbers.append(build_number(digits))

    # 3) target: variable digits = 1, clause digits = clause size
    target_digits: Dict[int, int] = {}
    for i in range(num_variables):
        target_digits[i] = 1
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


def verify_subset_sum_solution(indices: Sequence[int], reduction: SubsetSumReduction) -> bool:
    """Given indices of selected numbers, verify they sum to the target."""
    s = 0
    for idx in indices:
        s += reduction.numbers[idx]
    return s == reduction.target


def translate_subset_to_assignment(
    subset: Sequence[int],
    reduction: SubsetSumReduction,
    num_variables: int,
    subset_is_indices: bool = True
) -> Dict[int, bool]:
    """
    Translate Subset-Sum solution to SAT assignment.

    Arguments:
      subset: if subset_is_indices True: a sequence of indices into reduction.numbers.
              if False: a sequence of actual integer values (the numbers themselves).
      reduction: reduction result.
      num_variables: original number of variables.
      subset_is_indices: whether 'subset' contains indices (True) or numeric values (False).

    Returns:
      assignment: dict var -> bool
    """
    if subset_is_indices:
        selected_indices = set(subset)
    else:
        # map value -> list of indices available (values may repeat); pick indices accordingly
        value_to_indices: Dict[int, List[int]] = {}
        for idx, val in enumerate(reduction.numbers):
            value_to_indices.setdefault(val, []).append(idx)
        selected_indices = set()
        for val in subset:
            if val not in value_to_indices or not value_to_indices[val]:
                raise ValueError(f"Value {val} not found among reduction numbers or used more times than available.")
            selected_indices.add(value_to_indices[val].pop())

    # Optionally verify sum
    if not verify_subset_sum_solution(selected_indices, reduction):
        raise ValueError("Selected subset indices do not sum to the reduction target.")

    assignment: Dict[int, bool] = {}
    for var in range(1, num_variables + 1):
        pos_idx = reduction.variable_positive_indices[var]
        neg_idx = reduction.variable_negative_indices[var]
        pos_selected = pos_idx in selected_indices
        neg_selected = neg_idx in selected_indices

        if pos_selected and neg_selected:
            raise ValueError(f"Inconsistent solution: both x{var} and ¬x{var} selected.")
        if not (pos_selected or neg_selected):
            raise ValueError(f"Incomplete solution: neither x{var} nor ¬x{var} selected.")

        assignment[var] = pos_selected  # True if pos chosen, False if neg chosen

    return assignment
