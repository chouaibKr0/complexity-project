"""
3-SAT to Subset Sum Reduction.

This module implements the polynomial-time reduction from 3-SAT to Subset Sum.
This proves that Subset Sum is NP-hard.

This is a classic reduction that encodes the 3-SAT formula using numbers
in a clever base representation.

Reference: Standard textbook reduction (e.g., Sipser's "Introduction to the 
Theory of Computation" or Cormen et al. "Introduction to Algorithms")
"""
from dataclasses import dataclass


@dataclass
class SubsetSumReduction:
    """Result of 3-SAT to Subset Sum reduction."""
    numbers: list[int]
    target: int
    # Mapping information for solution translation
    variable_positive_indices: dict[int, int]  # var -> index in numbers for positive
    variable_negative_indices: dict[int, int]  # var -> index in numbers for negative
    slack_indices: list[int]  # indices of slack variables


def reduce_3sat_to_subset_sum(clauses: list[list[int]], num_variables: int = None) -> SubsetSumReduction:
    """
    Reduce a 3-SAT instance to a Subset Sum instance.
    
    This is a polynomial-time reduction.
    
    High-level idea:
    - Use a base-10 representation where each digit position corresponds to 
      either a variable or a clause
    - Create numbers for positive and negative literals of each variable
    - Create slack numbers for each clause
    - The target encodes that each variable is assigned exactly once and 
      each clause is satisfied at least once
    
    Args:
        clauses: 3-SAT instance (each clause has exactly 3 literals).
        num_variables: Number of variables.
    
    Returns:
        SubsetSumReduction with numbers, target, and mapping info.
    
    Complexity: O(n + m) where n = variables, m = clauses - polynomial time
    """
    if num_variables is None:
        num_variables = max(abs(lit) for clause in clauses for lit in clause) if clauses else 0
    
    num_clauses = len(clauses)
    
    # We'll use base 10 for clarity (textbooks often use base 10)
    # Total digits: num_variables (for variable positions) + num_clauses (for clause positions)
    total_positions = num_variables + num_clauses
    
    numbers = []
    var_pos_indices = {}
    var_neg_indices = {}
    slack_indices = []
    
    # For each variable x_i (1-indexed in the input, so variable i is at position i-1)
    for var in range(1, num_variables + 1):
        # Create number for positive literal (x_i = True)
        pos_num = 0
        
        # Set digit at variable position (positions 0 to num_variables-1)
        pos_num += 10 ** (total_positions - var)
        
        # Set digits for clauses where this variable appears positively
        for clause_idx, clause in enumerate(clauses):
            if var in clause:
                # Clause positions start after variable positions
                clause_pos = num_variables + clause_idx
                pos_num += 10 ** (total_positions - clause_pos - 1)
        
        var_pos_indices[var] = len(numbers)
        numbers.append(pos_num)
        
        # Create number for negative literal (x_i = False, i.e., ¬x_i)
        neg_num = 0
        
        # Set digit at variable position
        neg_num += 10 ** (total_positions - var)
        
        # Set digits for clauses where this variable appears negatively
        for clause_idx, clause in enumerate(clauses):
            if -var in clause:
                clause_pos = num_variables + clause_idx
                neg_num += 10 ** (total_positions - clause_pos - 1)
        
        var_neg_indices[var] = len(numbers)
        numbers.append(neg_num)
    
    # For each clause, create two slack variables
    # These help us reach the target of 3 in each clause position
    # (since each clause has at least 1 true literal, we need up to 2 more to reach 3)
    for clause_idx in range(num_clauses):
        clause_pos = num_variables + clause_idx
        slack_val = 10 ** (total_positions - clause_pos - 1)
        
        # Add two slack variables for this clause
        slack_indices.append(len(numbers))
        numbers.append(slack_val)
        
        slack_indices.append(len(numbers))
        numbers.append(slack_val)
    
    # Construct target:
    # - Each variable position should sum to 1 (exactly one of v_i or v'_i chosen)
    # - Each clause position should sum to 3 (at least 1 from satisfied literal + slacks)
    target = 0
    
    # Variable positions: all should be 1
    for var_pos in range(num_variables):
        target += 1 * (10 ** (total_positions - var_pos - 1))
    
    # Clause positions: all should be 3
    for clause_idx in range(num_clauses):
        clause_pos = num_variables + clause_idx
        target += 3 * (10 ** (total_positions - clause_pos - 1))
    
    return SubsetSumReduction(
        numbers=numbers,
        target=target,
        variable_positive_indices=var_pos_indices,
        variable_negative_indices=var_neg_indices,
        slack_indices=slack_indices
    )


def translate_subset_to_assignment(
    subset: list[int], 
    reduction: SubsetSumReduction,
    num_variables: int
) -> dict[int, bool]:
    """
    Translate a Subset Sum solution back to a 3-SAT assignment.
    
    Args:
        subset: Solution to the Subset Sum instance (indices into numbers list).
        reduction: The reduction result containing mappings.
        num_variables: Number of variables in original 3-SAT.
    
    Returns:
        Variable assignment for the 3-SAT instance.
    """
    assignment = {}
    
    # Check which variable numbers were selected
    for var in range(1, num_variables + 1):
        pos_idx = reduction.variable_positive_indices[var]
        neg_idx = reduction.variable_negative_indices[var]
        
        if pos_idx in subset:
            assignment[var] = True
        elif neg_idx in subset:
            assignment[var] = False
        # If neither (shouldn't happen in valid solution), we could default to False
        else:
            assignment[var] = False
    
    return assignment


def read_cnf_file(filename: str) -> tuple[list[list[int]], int]:
    """
    Read a CNF file in DIMACS format.
    
    Args:
        filename: Path to the .cnf file
    
    Returns:
        Tuple of (clauses, num_variables)
    """
    clauses = []
    num_variables = 0
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('c'):
                continue
            
            # Parse problem line: p cnf <variables> <clauses>
            if line.startswith('p'):
                parts = line.split()
                num_variables = int(parts[2])
                continue
            
            # Parse clause line
            literals = list(map(int, line.split()))
            
            # Remove the trailing 0 (DIMACS format ends clauses with 0)
            if literals and literals[-1] == 0:
                literals = literals[:-1]
            
            if literals:
                clauses.append(literals)
    
    return clauses, num_variables


def write_subset_sum_file(filename: str, reduction: SubsetSumReduction):
    """
    Write the Subset Sum instance to a file.
    
    Args:
        filename: Output file path
        reduction: The reduction result
    """
    with open(filename, 'w') as f:
        f.write(f"# Subset Sum Instance (reduced from 3-SAT)\n")
        f.write(f"# Numbers: {len(reduction.numbers)}\n")
        f.write(f"# Target: {reduction.target}\n\n")
        
        f.write("TARGET\n")
        f.write(f"{reduction.target}\n\n")
        
        f.write("NUMBERS\n")
        for i, num in enumerate(reduction.numbers):
            f.write(f"{num}\n")


# Example usage and testing
if __name__ == "__main__":
    import sys
    import os
    
    # Automatically use your 3-SAT file
    input_file = r"C:\Users\adnde\OneDrive\Desktop\complexity-project\data\sample_3sat.cnf"
    
    # Check if file exists
    if os.path.exists(input_file):
        print(f"Reading 3-SAT instance from: {input_file}")
        print()
        
        clauses, num_variables = read_cnf_file(input_file)
        
        print(f"Loaded 3-SAT instance:")
        print(f"  Variables: {num_variables}")
        print(f"  Clauses: {len(clauses)}")
        print()
        
        if clauses:
            print("Clauses:")
            for i, clause in enumerate(clauses):
                print(f"  Clause {i+1}: {clause}")
        print()
        
        # Validate it's actually 3-SAT (all clauses have exactly 3 literals)
        for i, clause in enumerate(clauses):
            if len(clause) != 3:
                print(f"ERROR: Clause {i+1} has {len(clause)} literals, but 3-SAT requires exactly 3!")
                print(f"This reduction only works for 3-SAT instances.")
                sys.exit(1)
        
    else:
        print(f"File not found: {input_file}")
        print("Using built-in example instead")
        print()
        
        # Example: (x1 ∨ x2 ∨ x3) ∧ (¬x1 ∨ ¬x2 ∨ x3) ∧ (x1 ∨ ¬x2 ∨ ¬x3)
        clauses = [
            [1, 2, 3],      # (x1 ∨ x2 ∨ x3)
            [-1, -2, 3],    # (¬x1 ∨ ¬x2 ∨ x3)
            [1, -2, -3]     # (x1 ∨ ¬x2 ∨ ¬x3)
        ]
        num_variables = 3
    
    print("Performing 3-SAT to Subset Sum reduction...")
    reduction = reduce_3sat_to_subset_sum(clauses, num_variables)
    print("Reduction complete!")
    print()
    
    print("Subset Sum Instance:")
    print(f"  Numbers: {len(reduction.numbers)}")
    print(f"  Target: {reduction.target}")
    print()
    
    if len(reduction.numbers) <= 20:
        print("Numbers:")
        for i, num in enumerate(reduction.numbers):
            print(f"  {i}: {num}")
        print()
    else:
        print("First 10 numbers:")
        for i in range(10):
            print(f"  {i}: {reduction.numbers[i]}")
        print(f"  ... and {len(reduction.numbers) - 10} more")
        print()
    
    # Optionally write output
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
        write_subset_sum_file(output_file, reduction)
        print(f"Subset Sum instance written to: {output_file}")