"""Base solver interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class SolverResult:
    """Result returned by a solver."""
    satisfiable: bool
    solution: Any | None  # Assignment dict for SAT, subset list for Subset Sum
    time_seconds: float
    nodes_explored: int = 0
    algorithm: str = ""
    
    def __bool__(self):
        return self.satisfiable


class BaseSolver(ABC):
    """Abstract base class for all solvers."""
    
    def __init__(self, name: str = "BaseSolver"):
        self.name = name
        self.stats = {
            "calls": 0,
            "total_time": 0.0,
            "nodes_explored": 0,
        }
    
    @abstractmethod
    def solve(self, instance: Any) -> SolverResult:
        """
        Solve the given problem instance.
        
        Args:
            instance: Problem-specific instance data.
        
        Returns:
            SolverResult with satisfiability and solution.
        """
        pass
    
    def reset_stats(self):
        """Reset solver statistics."""
        self.stats = {
            "calls": 0,
            "total_time": 0.0,
            "nodes_explored": 0,
        }
