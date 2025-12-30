"""
Random Instance Generators.

Generate random instances for benchmarking the solvers.
"""
import random
import numpy as np
from typing import Tuple
from src.utils.parsers import SATInstance, SubsetSumInstance

def generate_random_sat(
    num_variables: int,
    num_clauses: int,
    min_clause_size: int = 1,
    max_clause_size: int = 5,
    seed: int = 42
) -> SATInstance:
    """
    Generate a random SAT instance in CNF form.
    
    Args:
        num_variables: Number of Boolean variables.
        num_clauses: Number of clauses.
        min_clause_size: Minimum literals per clause.
        max_clause_size: Maximum literals per clause.
        seed: Random seed for reproducibility.
    
    Returns:
        List of clauses, where each clause is a list of literals.

    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    clauses = []
    for _ in range(num_clauses):
        k = random.randint(min_clause_size, max_clause_size)
        vars_ = random.sample(range(1, num_variables + 1), k)
        clause = [v if random.choice([True, False]) else -v for v in vars_]
        clauses.append(clause)
    return SATInstance(clauses=clauses, num_variables=num_variables, num_clauses=num_clauses)


def generate_random_3sat(
    num_variables: int,
    num_clauses: int,
    seed: int = 42
) -> SATInstance:
    """
    Generate a random 3-SAT instance.
    
    Args:
        num_variables: Number of Boolean variables (must be >= 3).
        num_clauses: Number of clauses.
        seed: Random seed for reproducibility.
    
    Returns:
        List of 3-literal clauses.
    
    Note: The clause-to-variable ratio affects satisfiability probability.
          Around ratio 4.26, there's a phase transition.

    """
    if num_variables < 3:
        raise ValueError("3-SAT needs at least 3 variables")
    
    if seed is not None:
        random.seed(seed)
    
    clauses = []
    for _ in range(num_clauses):
        vars_ = random.sample(range(1, num_variables + 1), 3)
        clause = [v if random.choice([True, False]) else -v for v in vars_]
        clauses.append(clause)
    return SATInstance(clauses=clauses, num_variables=num_variables, num_clauses=num_clauses)


def generate_random_subset_sum(
    num_elements: int,
    max_value: int = 1000,
    satisfiable: bool|None = None,
    seed: int = 42
) -> SubsetSumInstance:
    """
    Generate a random Subset Sum instance.
    
    Args:
        num_elements: Number of elements in the set.
        max_value: Maximum value for each element.
        satisfiable: If True, guarantee a solution exists.
                    If False, try to make it unsatisfiable.
                    If None, random.
        seed: Random seed for reproducibility.
    
    Returns:
        Tuple of (numbers list, target).

    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    numbers = [random.randint(1, max_value) for _ in range(num_elements)]
    if satisfiable is True:
        # Pick a random subset (possibly empty)
        mask = [random.choice([True, False]) for _ in range(num_elements)]
        subset = [num for num, m in zip(numbers, mask) if m]
        target = sum(subset)
    elif satisfiable is False:
        # Try to make unsatisfiable: set target > sum(numbers)
        target = sum(numbers) + random.randint(1, max_value)
    else:
        # Random target
        target = random.randint(1, sum(numbers))
    return SubsetSumInstance(numbers=numbers, target=target)


def generate_hard_sat_instance(num_variables: int, seed: int = 42) -> SATInstance:
    """
    Generate a 3-SAT instance near the satisfiability threshold (hard region).
    For 3-SAT, the hard region is around clause/variable ratio of 4.26.
    Variables are numbered 1..num_variables.
    """
    if num_variables < 3:
        raise ValueError("3-SAT needs at least 3 variables")
    if seed is not None:
        random.seed(seed)
    ratio = 4.26
    num_clauses = int(round(ratio * num_variables))
    clauses = []
    for _ in range(num_clauses):
        vars_ = random.sample(range(1, num_variables + 1), 3)
        clause = [v if random.choice([True, False]) else -v for v in vars_]
        clauses.append(clause)
    return SATInstance(clauses=clauses, num_variables=num_variables, num_clauses=num_clauses)
