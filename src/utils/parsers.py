"""Data parsers for problem instances."""
from pathlib import Path
from dataclasses import dataclass
from typing import TextIO


@dataclass
class SATInstance:
    """Parsed SAT instance."""
    num_variables: int
    num_clauses: int
    clauses: list[list[int]]
    name: str = ""


@dataclass
class SubsetSumInstance:
    """Parsed Subset Sum instance."""
    numbers: list[int]
    target: int
    name: str = ""


def parse_dimacs_cnf(file_path: str | Path) -> SATInstance:
    """
    Parse a DIMACS CNF file format.
    
    Format:
        c comment line
        p cnf <num_vars> <num_clauses>
        1 -2 3 0   (clause ending with 0)
        ...
    """
    clauses = []
    num_vars = 0
    num_clauses = 0
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c'):
                continue
            if line.startswith('p'):
                parts = line.split()
                num_vars = int(parts[2])
                num_clauses = int(parts[3])
            else:
                # Clause line
                literals = [int(x) for x in line.split()]
                if literals and literals[-1] == 0:
                    literals = literals[:-1]
                if literals:
                    clauses.append(literals)
    
    return SATInstance(
        num_variables=num_vars,
        num_clauses=num_clauses,
        clauses=clauses,
        name=Path(file_path).stem
    )


def write_dimacs_cnf(instance: SATInstance, file_path: str | Path):
    """Write a SAT instance to DIMACS CNF format."""
    with open(file_path, 'w') as f:
        f.write(f"c {instance.name}\n")
        f.write(f"p cnf {instance.num_variables} {instance.num_clauses}\n")
        for clause in instance.clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")


def parse_subset_sum_file(file_path: str | Path) -> SubsetSumInstance:
    """
    Parse a Subset Sum instance file.
    
    Format:
        n <number_of_elements>
        t <target>
        <num1>
        <num2>
        ...
    """
    numbers = []
    target = 0
    n = 0
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('n '):
                n = int(line.split()[1])
            elif line.startswith('t '):
                target = int(line.split()[1])
            else:
                numbers.append(int(line))
    
    return SubsetSumInstance(
        numbers=numbers,
        target=target,
        name=Path(file_path).stem
    )


def write_subset_sum_file(instance: SubsetSumInstance, file_path: str | Path):
    """Write a Subset Sum instance to file."""
    with open(file_path, 'w') as f:
        f.write(f"# {instance.name}\n")
        f.write(f"n {len(instance.numbers)}\n")
        f.write(f"t {instance.target}\n")
        for num in instance.numbers:
            f.write(f"{num}\n")


def parse_sat_from_string(cnf_string: str) -> list[list[int]]:
    """Parse CNF from a string (simple format: one clause per line)."""
    clauses = []
    for line in cnf_string.strip().split('\n'):
        line = line.strip()
        if line and not line.startswith('c') and not line.startswith('p'):
            literals = [int(x) for x in line.split() if x != '0']
            if literals:
                clauses.append(literals)
    return clauses
