"""
Random Instance Generators.

Generate random instances for benchmarking the solvers.
"""
import random
import numpy as np
from typing import Tuple


def generate_random_sat(
    num_variables: int,
    num_clauses: int,
    min_clause_size: int = 1,
    max_clause_size: int = 5,
    seed: int = None
) -> list[list[int]]:
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
    
    TODO: Implement random SAT generation
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # TODO: Generate random SAT instance
    # For each clause:
    #   1. Choose clause size uniformly from [min_clause_size, max_clause_size]
    #   2. Choose that many distinct variables
    #   3. Randomly negate each variable
    
    raise NotImplementedError("Random SAT generator not implemented")


def generate_random_3sat(
    num_variables: int,
    num_clauses: int,
    seed: int = None
) -> list[list[int]]:
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
    
    TODO: Implement random 3-SAT generation
    """
    if num_variables < 3:
        raise ValueError("3-SAT needs at least 3 variables")
    
    if seed is not None:
        random.seed(seed)
    
    # TODO: Generate random 3-SAT instance
    # For each clause:
    #   1. Choose 3 distinct variables
    #   2. Randomly negate each
    
    raise NotImplementedError("Random 3-SAT generator not implemented")


def generate_random_subset_sum(
    num_elements: int,
    max_value: int = 1000,
    satisfiable: bool = None,
    seed: int = None
) -> Tuple[list[int], int]:
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
    
    TODO: Implement random Subset Sum generation
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # TODO: Generate random Subset Sum instance
    # If satisfiable=True:
    #   1. Generate random numbers
    #   2. Select a random subset
    #   3. Target = sum of that subset
    # If satisfiable=False:
    #   1. Generate numbers carefully to avoid solutions
    # If satisfiable=None:
    #   1. Generate random numbers and random target
    
    raise NotImplementedError("Random Subset Sum generator not implemented")


def generate_hard_sat_instance(num_variables: int, seed: int = None) -> list[list[int]]:
    """
    Generate a SAT instance near the satisfiability threshold.
    
    For 3-SAT, the hard region is around clause/variable ratio of 4.26.
    
    TODO: Implement hard instance generation
    """
    raise NotImplementedError("Hard SAT generator not implemented")
