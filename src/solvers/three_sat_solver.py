"""
3-SAT Solver Implementation.

3-SAT is a restricted version of SAT where each clause has exactly 3 literals.
It remains NP-complete (Cook-Levin theorem).

This solver can either:
1. Use the general SAT solver
2. Implement specialized algorithms for 3-SAT
    - Brute-force search
    - Backtracking
    - DPLL algorithm
"""

from src.solvers.lit import DPLL
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
        Brute-force search for satisfying assignment.
        Args:
            clauses: List of clauses in CNF form.
            n: Number of variables.
        Returns:
            Tuple of (satisfiable, assignment dict or None, nodes explored).
        """
        # # or loop using format() for Binary Strings
        # for i in range(2**n):
        #     # Convert to binary string and pad with zeros
        #     binary_str = format(i, f'0{n}b')
        #     assignment = [int(bit) for bit in binary_str]
        # 

        for i in range(2**n):
            # Convert i to binary and extract bits
            A = [bool((i >> j) & 1) for j in range(n)]

            if self._eval_cnf(clauses, A) == True:
                assignment_dict = {var+1: bool(val) for var, val in enumerate(A)}
                return (True, assignment_dict, i+1)  # i+1 nodes explored
        return (False, None, 2**n)

    def _eval_cnf(self,F: list[list[int]], A: list[bool]) -> bool:
        """
        Evaluate CNF formula F under assignment A.
        Args:
            F: CNF formula (list of clauses).
            A: Assignment list where A[i] is the value of variable (i+1).
        Returns:
            True if F is satisfied under A, False otherwise.
        """
        for C in F:
            if self._eval_clause(C, A) == False:
                return False
        return True

    def _eval_clause(self, C: list[int], A: list[bool]) -> bool:
        """
        Evaluate a single clause C under assignment A.
        Args:
            C: Clause (list of literals).
            A: Assignment list where A[i] is the value of variable (i+1).
        Returns:        
            True if C is satisfied under A, False otherwise.    
        """
        for l in C:
            if self._eval_literal(l, A) == True:
                return True
        return False
    
    def _eval_literal(self, l: int, A: list[bool]) -> bool:
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
    
    def _backtrack(self, clauses: list[list[int]], n: int, partial_assignment: dict | None = None) -> tuple[bool, dict | None, int]:
        """
        Backtracking search for satisfying assignment.
        Args:
            clauses: List of clauses in CNF form.
            n: Number of variables.
            partial_assignment: Current partial assignment (dict).
        Returns:
            Tuple of (satisfiable, assignment dict or None, nodes explored).
        """
        counter = [0]  # mutable container for node count
        ok, sol = self._bt(clauses, n, {}, counter)
        return ok, sol, counter[0]

    def _bt(self,F: list[list[int]], N: int, P: dict, counter: list[int]) -> tuple[bool, dict | None]:
        """
        Backtracking helper function.
        Args:
            F: CNF formula (list of clauses).
            N: Number of variables.
            P: Partial assignment (some variables assigned).
            counter: Mutable container for node count.
        Returns:
            Tuple of (satisfiable, assignment dict or None).
        """
        # P: partial assignment (some variables assigned)
        counter[0] += 1  # count this node
        if self._exists_falsified_clause(F, P):
            return False, None
        if len(P) == N:
            return True, P

        x = self._select_unassigned_var(N, P)

        for v in [True, False]:
            P2 = {**P, x: v}
            ok, sol = self._bt(F, N, P2, counter)
            if ok:
                return True, sol
        return False, None

    def _exists_falsified_clause(self, F: list[list[int]], P: dict) -> bool:
        """
        Check if there exists a falsified clause under partial assignment P.
        Args:
            F: CNF formula (list of clauses).
            P: Partial assignment (some variables assigned).
        Returns:
            True if there exists a falsified clause, False otherwise.
        """
        for  C in F:
            if self._clause_status(C, P) == FALSIFIED:
                return True
        return False

    def _clause_status(self, C: list[int], P: dict) -> int:
        """
        Determine the status of clause C under partial assignment P.
        Args:
            C: Clause (list of literals).
            P: Partial assignment (some variables assigned).
        Returns:
            SATISFIED, FALSIFIED, or UNRESOLVED.
        """
        all_assigned = True
        for l in C:
            var = abs(l)
            val = P.get(var)
            if val is None:
                all_assigned = False
                continue
            if val == (l > 0):
                return SATISFIED
        return FALSIFIED if all_assigned else UNRESOLVED
    
    def _select_unassigned_var(self, N: int, P: dict) -> int:
        """
        Select an unassigned variable.
        Args:
            N: Number of variables.
            P: Partial assignment (some variables assigned).
        Returns:
            An unassigned variable index.
        """
        for x in range(1, N+1):
            if x not in P:
                return x
        raise Exception("All variables assigned")

    def _dpll(self, clauses: list[list[int]], n: int, partial_assignment: dict | None = None) -> tuple[bool, dict | None, int]:
    
        """
        DPLL algorithm for solving 3-SAT.
        Args:
            clauses: List of clauses in CNF form.
            n: Number of variables.
            partial_assignment: Current partial assignment (dict).
        Returns:
            Tuple of (satisfiable, assignment dict or None, nodes explored).
        """
        nodes = 1  # Count this current function call as 1 node

        # 1. Unit Propagation
        (conflict, F1, P1) = self._unit_propagate(clauses, partial_assignment or {})
        if conflict:
            return (False, None, nodes)

        # 2. Pure Literal Elimination
        (F2, P2) = self._pure_literal_elimination(F1, P1, n)
        
        # 3. Check Base Cases
        if self._has_empty_clause(F2):
            return (False, None, nodes)
        if self._no_clauses_left(F2):
            return (True, P2, nodes)

        # 4. Branching
        x = self._choose_branch_var(F2, P2)
        # Branch 1: Try x = True
        # Note: simplify/unit_propagate will handle the logic of adding x to P
        # We pass the new assignment P2 updated with x:True
        P = {**P2, x: True}
        (ok, sol, nodes_true) = self._dpll(F2,n, P)
        nodes += nodes_true # Add nodes from left branch

        if ok:
            return (True, sol, nodes)

        # Branch 2: Try x = False
        P = {**P2, x: False}
        (ok, sol, nodes_false) = self._dpll(F2, n,P )
        nodes += nodes_false # Add nodes from right branch

        return (ok, sol, nodes)


    def _unit_propagate(self, F: list[list[int]], P: dict ) -> tuple[bool, list[list[int]], dict]:
        """
        Unit propagation step in DPLL.
        Args:
            F: Current formula (list of clauses).
            P: Current partial assignment.
        Returns:
            Tuple of (conflict detected, simplified formula, updated partial assignment).
        """
        # Make a copy of F initially so we don't modify the input list reference outside
        # (Though in your recursive structure, F is likely already a new list from simplify)
        current_F = F
        current_P = P

        while True:
            # Check for immediate conflict before looking for unit clauses
            if self._has_empty_clause(current_F):
                return (True, current_F, current_P)

            # IMPORTANT: You must find unit clauses relative to the *current simplified F*
            # In your simplify logic, clauses shrink. A unit clause is a clause of size 1.
            
            # We need to simplify first to see unit clauses exposed by previous steps?
            # Actually, simpler approach:
            # 1. Simplify F based on current P (this removes false literals)
            # 2. Check for empty clauses (conflict)
            # 3. Check for unit clauses (size 1)
            
            # Let's align with your structure:
            current_F = self._simplify(current_F, current_P)
            
            if self._has_empty_clause(current_F):
                return (True, current_F, current_P)
                
            U = self._find_unit_clause(current_F, current_P)
            if U is None:
                break

            l = U[0]
            # Update P
            current_P = {**current_P, abs(l): (l > 0)}
            # Loop continues, next iteration will simplify F with this new literal

        return (False, current_F, current_P)


    def _pure_literal_elimination(self, F: list[list[int]], P: dict, N: int) -> tuple[list[list[int]], dict]:
        """
        Pure literal elimination step in DPLL.
        Args:
            F: Current formula (list of clauses).
            P: Current partial assignment.
            N: Number of variables.
        Returns:
            Tuple of (simplified formula, updated partial assignment).
        """
        current_F = F
        current_P = P
        
        # Note: simplify must be called inside the loop because
        # eliminating one pure literal might make another one pure (or satisfy clauses)
        
        # We simplify once at start to ensure F is clean
        current_F = self._simplify(current_F, current_P)

        while (l := self._exists_pure_literal(current_F, current_P, N)):
            current_P = {**current_P, abs(l): (l > 0)}
            current_F = self._simplify(current_F, current_P)
        
        return (current_F, current_P)


    def _exists_pure_literal(self, F: list[list[int]], P: dict, N: int) -> int | None:
        """
        Check for existence of a pure literal in F under partial assignment P.
        Args:
            F: Current formula (list of clauses).
            P: Current partial assignment.
            N: Number of variables.
        Returns:
            A pure literal (int) if exists, else None.
        """
        # Optimized to check only variables present in current F
        # Tracking counts is faster than iterating N times
        
        counts = {} # var -> {True/False seen}
        
        for C in F:
            for l in C:
                var = abs(l)
                # No need to check 'if var in P' because simplify() removes assigned vars from F
                if var not in counts:
                    counts[var] = set()
                counts[var].add(l > 0)
        
        for var, polarities in counts.items():
            if len(polarities) == 1:
                is_pos = list(polarities)[0]
                return var if is_pos else -var
                
        return None


    def _simplify(self, F: list[list[int]], P: dict) -> list[list[int]]:
        """
        Simplify formula F under partial assignment P.
        Args:
            F: Current formula (list of clauses).
            P: Current partial assignment.
        Returns:
            Simplified formula (list of clauses).
        """
        F_new = []
        for C in F:
            # Logic to remove satisfied clauses and false literals
            status = self._clause_status(C, P)
            if status == SATISFIED:
                continue # Clause removed
            
            # If not satisfied, rebuild clause removing false literals
            # (Already handled by your logic below effectively, but let's be explicit)
            
            C_new = []
            for l in C:
                var = abs(l)
                is_pos = (l > 0)
                
                # If var is in P, check value
                if var in P:
                    val = P[var]
                    if val == is_pos:
                        # Clause is satisfied! We shouldn't be here due to CLAUSE_STATUS check
                        # But if we are, break outer and skip appending C_new
                        break 
                    else:
                        # Literal is False, remove it (don't add to C_new)
                        pass
                else:
                    # Var not in P, keep literal
                    C_new.append(l)
            else:
                # Only append if we didn't break (meaning clause wasn't satisfied)
                F_new.append(C_new)
                
        return F_new


    def _has_empty_clause(self, F: list[list[int]]) -> bool:
        """
        Check if there exists an empty clause in F.
        Args:
            F: Current formula (list of clauses).
        Returns:
            True if there is an empty clause, False otherwise.
        """
        return any(len(C) == 0 for C in F)


    def _find_unit_clause(self, F: list[list[int]], P: dict) -> list[int] | None:
        """
        Find a unit clause in F.
        Args:
            F: Current formula (list of clauses).
            P: Current partial assignment.
        Returns:
            A unit clause (list of one literal) if exists, else None.
        """
        for C in F:
            if len(C) == 1:
                return C
        return None


    def _choose_branch_var(self, F: list[list[int]], P: dict) -> int | None:
        """
        Simple heuristic: Pick first variable from first clause.
        Args:
            F: Current formula (list of clauses).
            P: Current partial assignment.
        Returns:
            A variable (int) to branch on if exists, else None.
        """
        for C in F:
            for l in C:
                return abs(l) # Since simplify removes assigned vars, this is safe
        return None 


    def _no_clauses_left(self, F):
        return len(F) == 0


SATISFIED = 0
FALSIFIED = 1
UNRESOLVED = 2