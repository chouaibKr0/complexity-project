"""
3-SAT Solver Implementation.

3-SAT is a restricted version of SAT where each clause has exactly 3 literals.
It remains NP-complete (Cook-Levin theorem).

This solver can either:
1. Use the general SAT solver
2. Implement specialized algorithms for 3-SAT
"""

from .base import BaseSolver, SolverResult
from .sat_solver import SATSolver
from ..utils.validation import validate_3sat_instance
from ..utils.timer import Timer


class ThreeSATSolver(BaseSolver):
    """
    Solver for 3-SAT (3-literal clause SAT).
    
    Input: CNF formula where each clause has exactly 3 literals
           Example: [[1, -2, 3], [-1, 2, -3]] 
    
    Output: SolverResult with satisfiability and assignment
    """
    
    def __init__(self, algorithm: str = "dpll"):
        """
        Initialize 3-SAT solver.
        
        Args:
            algorithm: One of "brute_force", "backtrack", "dpll"
        """
        super().__init__(name=f"3SAT-{algorithm}")
        self.algorithm = algorithm
        # Can optionally use the general SAT solver
        self._sat_solver = SATSolver(algorithm=algorithm)
    
    def solve(self, clauses: list[list[int]], num_variables: int | None = None) -> SolverResult:
        """
        Solve the 3-SAT instance.
        
        Args:
            clauses: List of 3-literal clauses in CNF form.
            num_variables: Number of variables (auto-detected if None).
        
        Returns:
            SolverResult with satisfiability and assignment.
        """
        # Validate and normalize input (variables become 1, 2, ..., n)
        clauses, num_variables = validate_3sat_instance(clauses)
        
        self.stats["calls"] += 1
        
        with Timer("3sat_solve") as timer:
            # Option 1: Use the general SAT solver
            # return self._sat_solver.solve(clauses, num_variables)
            
            # Option 2: Implement specialized 3-SAT algorithms
            if self.algorithm == "brute_force":
                sat, assignment, nodes = self._brute_force(clauses, num_variables)
            elif self.algorithm == "backtrack":
                sat, assignment, nodes = self._backtrack(clauses, num_variables)
            elif self.algorithm == "dpll":
                sat, assignment, nodes = self._dpll(clauses, num_variables)
            else:
                raise ValueError(f"Unknown algorithm: {self.algorithm}")
        
        self.stats["total_time"] += timer.elapsed
        self.stats["nodes_explored"] += nodes
        
        return SolverResult(
            satisfiable=sat,
            solution=assignment,
            time_seconds=timer.elapsed,
            nodes_explored=nodes,
            algorithm=self.algorithm
        )
    
    def _brute_force(self, clauses: list[list[int]], n: int) -> tuple[bool, dict | None, int]:
        """
        Brute force for 3-SAT.
        
        Args:
            clauses: List of clauses.
            n: Number of variables.
        Returns:
            satisfiable : bool
            assignment : dict | None
            nodes_explored : int

        """

        # # or loop using format() for Binary Strings
        # for i in range(2**n):
        #     # Convert to binary string and pad with zeros
        #     binary_str = format(i, f'0{n}b')
        #     assignment = [int(bit) for bit in binary_str]
        # 

        for i in range(2**n):
            # Convert i to binary and extract bits
            assignment = [bool((i >> j) & 1) for j in range(n)]

            satisfied = True
            
            for clause in clauses:
                if not self._assign_to_clause(assignment, clause):
                    satisfied = False
                    break
            if satisfied:
                assignment_dict = {var+1: bool(val) for var, val in enumerate(assignment)}
                return True, assignment_dict, i + 1  # Number of assignments explored
        return False, None, 2**n  # All assignments explored

    def _backtrack(self, clauses: list[list[int]], n: int, partial_assignment: dict | None = None) -> tuple[bool, dict | None, int]:
        """
        Backtracking for 3-SAT.
        Args:
            clauses: List of clauses.
            n: Number of variables.
            partial_assignment: Current partial assignment of variables.
        Returns:
            satisfiable : bool
            assignment : dict | None
            nodes_explored : int
        """
        if partial_assignment is None:
            partial_assignment = {}
        
        nodes = 1
        
        # Check for empty clause (conflict)
        if self._find_empty_clause(clauses):
            return False, None, nodes
        
        # Check if all clauses satisfied
        if self._partial_assign_to_clauses(partial_assignment, clauses)[0]:
            return True, partial_assignment, nodes
        
        # Check if no clauses left (all satisfied by apply_literal)
        if clauses == []:
            return True, partial_assignment, nodes
        
        x = self._pick_unassigned_literal(partial_assignment, n)
        
        # All variables assigned but not all clauses satisfied - shouldn't happen
        if x is None:
            return False, None, nodes
        
        
        # Try x = True
        sat1, assign1, nodes1 = self._backtrack(self._apply_literal(clauses, x, negative=False), n, {**partial_assignment, x: True})
        if sat1:
            return True, assign1, nodes + nodes1
        
        # Try x = False
        sat2, assign2, nodes2 = self._backtrack(self._apply_literal(clauses, x, negative=True), n, {**partial_assignment, x: False})
        return sat2, assign2, nodes + nodes1 + nodes2


 

    def _dpll(self, clauses: list[list[int]], n: int, partial_assignment: dict | None = None) -> tuple[bool, dict | None, int]:
        """
        DPLL for 3-SAT.
        """
        if partial_assignment is None:
            partial_assignment = {}
        else:
            partial_assignment = partial_assignment.copy()  # Don't modify original
        
        nodes = 1
        
        # Unit propagation
        unit_clauses = self._find_unit_clauses(clauses)
        for l in unit_clauses:
            clauses = self._apply_literal(clauses, abs(l), negative=(l < 0))
            partial_assignment[abs(l)] = (l > 0)
        
        # Pure literal elimination
        pure_literals = self._find_pure_literals(clauses)
        for l in pure_literals:
            clauses = self._apply_literal(clauses, abs(l), negative=(l < 0))
            partial_assignment[abs(l)] = (l > 0)
        
        # Base cases
        if clauses == []:
            return True, partial_assignment, nodes
        if self._find_empty_clause(clauses):
            return False, None, nodes
        
        # Pick a variable to branch on (from first clause)
        # Standard DPLL: just pick any unassigned variable
        var = None
        for clause in clauses:
            for lit in clause:
                if abs(lit) not in partial_assignment:
                    var = abs(lit)
                    break
            if var is not None:
                break
        
        if var is None:
            # All variables in clauses are assigned but clauses remain - check satisfaction
            return self._partial_assign_to_clauses(partial_assignment, clauses)[0], partial_assignment, nodes
        
        # Try var = True
        new_clauses = self._apply_literal(clauses, var, negative=False)
        sat1, assign1, nodes1 = self._dpll(new_clauses, n, {**partial_assignment, var: True})
        if sat1:
            return True, assign1, nodes + nodes1
        
        # Try var = False
        new_clauses = self._apply_literal(clauses, var, negative=True)
        sat2, assign2, nodes2 = self._dpll(new_clauses, n, {**partial_assignment, var: False})
        return sat2, assign2, nodes + nodes1 + nodes2
    
    def _assign_to_clause(self, assignment: list[bool], clause: list[int]) -> bool:
        """
        Check if a clause is satisfied by the current assignment.
        
        Args:
            assignment: Current variable assignment (index 0 = var 1, etc.).
            clause: A single clause (list of literals).
        Returns:
            True if clause is satisfied, False otherwise.
        """
        for lit in clause:
            var = abs(lit) - 1  # Convert to 0-indexed
            value = assignment[var]
            # lit > 0 means we need var=True, lit < 0 means we need var=False
            if (lit > 0 and value) or (lit < 0 and not value):
                return True
        return False

    def _assign_to_clauses(self, assignment: list[bool], clauses: list[list[int]]) -> tuple[bool, list[int] | None]:
        """
        Check if all clauses are satisfied by the current assignment.
        
        Args:
            assignment: Current variable assignment.
            clauses: List of clauses.
        Returns:
            Tuple of (all_satisfied: bool, first_unsatisfied_clause: list[int] | None)
        """
        for clause in clauses:
            if not self._assign_to_clause(assignment, clause):
                return False, clause
        return True, None

    def _partial_assign_to_clauses(self, partial_assignment: dict, clauses: list[list[int]]) -> tuple[bool, list[int] | None]:
        """
        Check if clauses are satisfied or undetermined by a partial assignment.
        
        Args:
            partial_assignment: Current partial variable assignment {var: bool}.
            clauses: List of clauses.
        Returns:
            Tuple of (all_satisfied: bool, first_unsatisfied_clause: list[int] | None)
            - (True, None) if all clauses are satisfied
            - (False, clause) if a clause is unsatisfied or undetermined
        """
        for clause in clauses:
            clause_satisfied = False
            for lit in clause:
                var = abs(lit)
                if var in partial_assignment:
                    value = partial_assignment[var]
                    # Check if this literal satisfies the clause
                    if (lit > 0 and value) or (lit < 0 and not value):
                        clause_satisfied = True
                        break
            if not clause_satisfied:
                return False, clause
        return True, None

    def _find_unit_clauses(self, clauses: list[list[int]]) -> list[int]:
        """
        Find all unit clauses (clauses with exactly one literal).
        
        Returns:
            List of literals from unit clauses.
        """
        unit_literals = []
        for clause in clauses:
            if len(clause) == 1:
                unit_literals.append(clause[0])
        return unit_literals

    def _find_pure_literals(self, clauses: list[list[int]]) -> set[int]:
        """
        Find pure literals (literals that appear only positive or only negative).
        
        Returns:
            Set of pure literals (with their sign).
        """
        positive = set()
        negative = set()
        
        for clause in clauses:
            for lit in clause:
                if lit > 0:
                    positive.add(lit)
                else:
                    negative.add(abs(lit))
        
        # Pure positive: appear positive but never negative
        pure_positive = positive - negative
        # Pure negative: appear negative but never positive
        pure_negative = negative - positive
        
        result = set(pure_positive)
        result.update(-lit for lit in pure_negative)
        return result

    def _find_empty_clause(self, clauses: list[list[int]]) -> bool:
        """
        Check if any clause is empty (unsatisfiable).
        
        Returns:
            True if an empty clause exists, False otherwise.
        """
        for clause in clauses:
            if len(clause) == 0:
                return True
        return False

    def _find_2literal_clause(self, clauses: list[list[int]]) -> tuple[bool, tuple[int, int] | None]:
        """
        Find a clause with exactly 2 literals.
        
        Returns:
            Tuple of (found: bool, literals: tuple[int, int] | None)
        """
        for clause in clauses:
            if len(clause) == 2:
                return True, (clause[0], clause[1])
        return False, None

    def _pick_unassigned_literal(self, partial_assignment: dict, n: int) -> int | None:
        """
        Pick an unassigned variable.
        
        Args:
            partial_assignment: Current partial assignment.
            n: Total number of variables.
        Returns:
            An unassigned variable (1 to n), or None if all assigned.
        """
        for var in range(1, n + 1):
            if var not in partial_assignment:
                return var
        return None  # All variables assigned

    def _apply_literal(self, clauses: list[list[int]], literal: int, negative: bool = False) -> list[list[int]]:
        """
        Apply a literal assignment: F|x if negative is False else F|¬x.
        Removes satisfied clauses and removes the negation from remaining clauses.
        
        Args:
            clauses: Current list of clauses.
            literal: Variable to apply (positive integer).
            negative: If True, apply ¬literal (set var to False).
        Returns:
            New list of clauses after applying the literal.
        """
        # Determine the satisfying literal and falsifying literal
        if negative:
            sat_lit = -literal   # -x satisfies when we set x=False
            false_lit = literal  # x is false when we set x=False
        else:
            sat_lit = literal    # x satisfies when we set x=True
            false_lit = -literal # -x is false when we set x=True
        
        new_clauses = []
        for clause in clauses:
            # If clause contains the satisfying literal, it's satisfied - skip it
            if sat_lit in clause:
                continue
            # Otherwise, remove the falsifying literal from the clause
            new_clause = [lit for lit in clause if lit != false_lit]
            new_clauses.append(new_clause)
        
        return new_clauses


