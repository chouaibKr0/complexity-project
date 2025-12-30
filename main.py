#!/usr/bin/env python3
"""
NP-Complexity Project - Main Entry Point

Study of NP-complete problems: SAT, 3-SAT, and Subset Sum.

Usage:
    python main.py                    # Interactive mode
    python main.py --help            # Show help
    python -m src.cli solve sat ...  # CLI mode
"""
import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Full project demo: generation, reduction, solving, verification, experiment/progress tracking, results/plots."""
    from src.benchmarks import generate_random_sat, generate_random_3sat, generate_random_subset_sum, BenchmarkRunner, plot_complexity
    from src.reductions import reduce_sat_to_3sat, reduce_3sat_to_subset_sum
    from src.solvers import SATSolver, ThreeSATSolver, SubsetSumSolver
    from src.verifiers import verify_sat_solver_result, verify_3sat_solver_result, verify_subset_sum_solution
    from src.utils import ResultsSerializer, ProgressTracker
    from src.utils.experiment import ExperimentTracker
    from src.utils.parsers import write_dimacs_cnf, write_subset_sum_file, SATInstance, SubsetSumInstance
    from src.utils.logging import setup_logging, get_logger
    from src.utils.config import settings, ensure_directories
    # Setup
    ensure_directories()
    setup_logging(settings.log_level)
    logger = get_logger("main")
    logger.info("NP-Complexity Project", version="0.1.0")



    # Experiment and progress tracking
    tracker = ExperimentTracker()
    progress = ProgressTracker()
    serializer = ResultsSerializer()

    print("=" * 60)
    print("NP-Complexity Project: Full Demo")
    print("=" * 60)

    # 1. Generate instances and write to files
    sat_instance = generate_random_sat(num_variables=20, num_clauses=91)
    sat_path = "data/demo_sat.cnf"
    write_dimacs_cnf(sat_instance, sat_path)
    progress.log(f"SAT instance written to {sat_path}", style="bold green")

    three_sat_instance = generate_random_3sat(num_variables=20, num_clauses=91)
    three_sat_path = "data/demo_3sat.cnf"
    write_dimacs_cnf(three_sat_instance, three_sat_path)
    progress.log(f"3-SAT instance written to {three_sat_path}", style="bold green")

    subset_sum_instance = generate_random_subset_sum(num_elements=10, max_value=50)
    subset_sum_path = "data/demo_subset_sum.txt"
    write_subset_sum_file(subset_sum_instance, subset_sum_path)
    progress.log(f"Subset Sum instance written to {subset_sum_path}", style="bold green")

    # 2. Reductions: SAT -> 3-SAT -> Subset Sum
    with progress.task("Reducing SAT to 3-SAT"):
        reduced_3sat = reduce_sat_to_3sat(sat_instance.clauses, sat_instance.num_variables)
        reduced_sat_instance = SATInstance(clauses=reduced_3sat.reduced_instance,num_variables=reduced_3sat.reduced_variables, num_clauses=reduced_3sat.reduced_clauses)
        write_dimacs_cnf(reduced_sat_instance, "data/demo_sat_to_3sat.cnf")
    with progress.task("Reducing 3-SAT to Subset Sum"):
        reduced_subsum = reduce_3sat_to_subset_sum(three_sat_instance.clauses, three_sat_instance.num_variables)
        reduced_3sat_instance = SubsetSumInstance(numbers=reduced_subsum.numbers, target=reduced_subsum.target)
        write_subset_sum_file(reduced_3sat_instance, "data/demo_3sat_to_subsum.txt")

    # 3. Run solvers on sample problems (with experiment tracking)
    sample_problems = [
        ("sat", sat_instance, SATSolver, ["dpll", "backtrack"]),
        ("3sat", three_sat_instance, ThreeSATSolver, ["dpll", "backtrack"]),
        ("subset_sum", subset_sum_instance, SubsetSumSolver, ["dynamic", "backtrack"]),
    ]

    results = []
    for problem_type, instance, SolverClass, algorithms in sample_problems:
        for algo in algorithms:
            exp = tracker.create(f"{problem_type}_{algo}", problem_type, algo)
            tracker.start()
            with progress.task(f"Solving {problem_type} with {algo}"):
                if problem_type == "sat":
                    solver = SolverClass(algorithm=algo)
                    result = solver.solve(instance.clauses)
                    if result.satisfiable:
                        is_valid = verify_sat_solver_result(instance.clauses, result)
                    else:
                        is_valid = None  # No solution to verify
                elif problem_type == "3sat":
                    solver = SolverClass(algorithm=algo)
                    result = solver.solve(instance.clauses)
                    if result.satisfiable:
                        is_valid = verify_3sat_solver_result(instance.clauses, result)
                    else:
                        is_valid = None  # No solution to verify
                elif problem_type == "subset_sum":
                    solver = SolverClass(algorithm=algo)
                    result = solver.solve(instance.numbers, instance.target)
                    if result.satisfiable:
                        is_valid = verify_subset_sum_solution(instance.numbers, instance.target, result.solution)
                    else:
                        is_valid = None  # No solution to verify
                else:
                    continue
            tracker.complete({
                "satisfiable": result.satisfiable,
                "solution_valid": is_valid,
                "time_seconds": result.time_seconds,
            })
            # Save result
            from src.utils.serialization import ExperimentResult
            exp_result = ExperimentResult(
                problem_type=problem_type,
                algorithm=algo,
                instance_name=instance.name,
                instance_size={
                    "variables": getattr(instance, "num_variables", None),
                    "clauses": getattr(instance, "num_clauses", None),
                    "numbers": len(getattr(instance, "numbers", [])),
                },
                is_satisfiable=result.satisfiable,
                solution=result.solution,
                time_seconds=result.time_seconds,
                metadata={"solution_valid": is_valid}
            )
            results.append(exp_result)
            serializer.save_result(exp_result)
            progress.log(f"Result for {problem_type} ({algo}) saved.", style="bold blue")

    # 4. Save batch results and experiment summary
    serializer.save_batch(results, "demo_batch_results.json")
    tracker.save_summary("demo_experiment_summary.json")
    progress.log("Batch results and experiment summary saved.", style="bold green")

    # 5. Plot benchmarks (example)
    with progress.task("Plotting complexity curves"):
        plot_complexity(pd.DataFrame([r for r in results if r.problem_type == "sat"]), output_dir=Path("results/plots"))
        plot_complexity(pd.DataFrame([r for r in results if r.problem_type == "3sat"]), output_dir=Path("results/plots"))
        plot_complexity(pd.DataFrame([r for r in results if r.problem_type == "subset_sum"]), output_dir=Path("results/plots"))
    progress.log("Plots saved to results/plots.", style="bold magenta")

    print("=" * 60)
    print("Demo complete. See results, logs, and plots in the results/ directory.")
    print("=" * 60)

if __name__ == "__main__":
    main()
