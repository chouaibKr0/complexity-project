"""
Benchmark Runner.

Run systematic benchmarks across different problem sizes and algorithms.
"""
from dataclasses import dataclass, field
from typing import Callable, Any
import pandas as pd
from pathlib import Path

from ..solvers import SATSolver, ThreeSATSolver, SubsetSumSolver
from ..utils.timer import Timer
from ..utils.progress import ProgressTracker
from ..utils.serialization import ResultsSerializer, ExperimentResult
from ..utils.config import settings


@dataclass
class BenchmarkConfig:
    """Configuration for a benchmark run."""
    problem_type: str  # "sat", "3sat", "subset_sum"
    algorithms: list[str]
    sizes: list[int]  # Variable counts or element counts
    instances_per_size: int = 5
    timeout_seconds: int = 300
    seed: int = 42


@dataclass
class BenchmarkResult:
    """Result of a single benchmark."""
    problem_type: str
    algorithm: str
    size: int
    instance_id: int
    satisfiable: bool | None
    time_seconds: float
    nodes_explored: int
    timed_out: bool = False


class BenchmarkRunner:
    """Run benchmarks and collect results."""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or settings.paths.results_dir
        self.results: list[BenchmarkResult] = []
        self.progress = ProgressTracker()
        self.serializer = ResultsSerializer(self.output_dir)
    
    def run_sat_benchmark(self, config: BenchmarkConfig) -> pd.DataFrame:
        """
        Run SAT benchmarks across different sizes and algorithms.
        """
        from .generators import generate_random_sat
        import time
        self.results.clear()
        for size in config.sizes:
            for inst_id in range(config.instances_per_size):
                clauses = generate_random_sat(size, size * 4, min_clause_size=1, max_clause_size=5, seed=config.seed + inst_id)
                for algo in config.algorithms:
                    solver = SATSolver(algorithm=algo)
                    timer = Timer()
                    timed_out = False
                    nodes = 0
                    with timer:
                        try:
                            result = solver.solve(clauses, size, timeout=config.timeout_seconds)
                            nodes = getattr(result, 'nodes_explored', 0)
                            sat = getattr(result, 'satisfiable', None)
                        except Exception:
                            sat = None
                            timed_out = True
                    self.results.append(BenchmarkResult(
                        problem_type="sat",
                        algorithm=algo,
                        size=size,
                        instance_id=inst_id,
                        satisfiable=sat,
                        time_seconds=timer.elapsed,
                        nodes_explored=nodes,
                        timed_out=timed_out or (timer.elapsed > config.timeout_seconds)
                    ))
        return self.to_dataframe()
    
    def run_3sat_benchmark(self, config: BenchmarkConfig) -> pd.DataFrame:
        """
        Run 3-SAT benchmarks.
        """
        from .generators import generate_random_3sat
        import time
        self.results.clear()
        for size in config.sizes:
            for inst_id in range(config.instances_per_size):
                clauses = generate_random_3sat(size, int(4.26 * size), seed=config.seed + inst_id)
                for algo in config.algorithms:
                    solver = ThreeSATSolver(algorithm=algo)
                    timer = Timer()
                    timed_out = False
                    nodes = 0
                    with timer:
                        try:
                            result = solver.solve(clauses, size, timeout=config.timeout_seconds)
                            nodes = getattr(result, 'nodes_explored', 0)
                            sat = getattr(result, 'satisfiable', None)
                        except Exception:
                            sat = None
                            timed_out = True
                    self.results.append(BenchmarkResult(
                        problem_type="3sat",
                        algorithm=algo,
                        size=size,
                        instance_id=inst_id,
                        satisfiable=sat,
                        time_seconds=timer.elapsed,
                        nodes_explored=nodes,
                        timed_out=timed_out or (timer.elapsed > config.timeout_seconds)
                    ))
        return self.to_dataframe()
    
    def run_subset_sum_benchmark(self, config: BenchmarkConfig) -> pd.DataFrame:
        """
        Run Subset Sum benchmarks.
        """
        from .generators import generate_random_subset_sum
        import time
        self.results.clear()
        for size in config.sizes:
            for inst_id in range(config.instances_per_size):
                numbers, target = generate_random_subset_sum(size, satisfiable=None, seed=config.seed + inst_id)
                for algo in config.algorithms:
                    solver = SubsetSumSolver(algorithm=algo)
                    timer = Timer()
                    timed_out = False
                    nodes = 0
                    with timer:
                        try:
                            result = solver.solve(numbers, target, timeout=config.timeout_seconds)
                            nodes = getattr(result, 'nodes_explored', 0)
                            sat = getattr(result, 'satisfiable', None)
                        except Exception:
                            sat = None
                            timed_out = True
                    self.results.append(BenchmarkResult(
                        problem_type="subset_sum",
                        algorithm=algo,
                        size=size,
                        instance_id=inst_id,
                        satisfiable=sat,
                        time_seconds=timer.elapsed,
                        nodes_explored=nodes,
                        timed_out=timed_out or (timer.elapsed > config.timeout_seconds)
                    ))
        return self.to_dataframe()
    
    def run_all(self, configs: list[BenchmarkConfig]) -> dict[str, pd.DataFrame]:
        """Run all configured benchmarks."""
        results = {}
        for config in configs:
            if config.problem_type == "sat":
                results["sat"] = self.run_sat_benchmark(config)
            elif config.problem_type == "3sat":
                results["3sat"] = self.run_3sat_benchmark(config)
            elif config.problem_type == "subset_sum":
                results["subset_sum"] = self.run_subset_sum_benchmark(config)
        return results
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert results to pandas DataFrame."""
        return pd.DataFrame([
            {
                "problem": r.problem_type,
                "algorithm": r.algorithm,
                "size": r.size,
                "instance": r.instance_id,
                "satisfiable": r.satisfiable,
                "time_s": r.time_seconds,
                "nodes": r.nodes_explored,
                "timed_out": r.timed_out,
            }
            for r in self.results
        ])
    
    def save_results(self, filename: str = "benchmark_results.csv"):
        """Save results to CSV."""
        df = self.to_dataframe()
        filepath = self.output_dir / filename
        df.to_csv(filepath, index=False)
        return filepath
