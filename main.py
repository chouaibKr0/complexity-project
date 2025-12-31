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
    """Full project Experiment: generation, reduction, solving, verification, experiment/progress tracking, results/plots."""
    from src.benchmarks import generate_random_sat, generate_random_3sat, generate_random_subset_sum, plot_complexity
    from src.reductions import reduce_sat_to_3sat, reduce_3sat_to_subset_sum
    from src.solvers import SATSolver, ThreeSATSolver, SubsetSumSolver
    from src.verifiers import verify_sat_solver_result, verify_3sat_solver_result, verify_subset_sum_solution
    from src.utils import ResultsSerializer, ProgressTracker
    from src.utils.experiment import ExperimentTracker
    from src.utils.parsers import write_dimacs_cnf, write_subset_sum_file, SATInstance, SubsetSumInstance
    from src.utils.logging import setup_logging, get_logger
    from src.utils.config import settings, ensure_directories
    from src.utils.serialization import ExperimentResult
    from datetime import datetime
    
    # Generate single timestamp for this entire run
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Setup
    ensure_directories()
    setup_logging(settings.log_level)
    logger = get_logger("main")
    logger.info(f"NP-Complexity Project - Run: {timestamp}")

    # Experiment and progress tracking
    tracker = ExperimentTracker()
    progress = ProgressTracker()
    serializer = ResultsSerializer()

    print("=" * 60)
    print("NP-Complexity Project: Full Experiment")
    print(f"Run ID: {timestamp}")
    print("=" * 60)

    # Problem sizes for complexity analysis
    problem_sizes = [10, 15, 20, 25, 30]
    results = []

    # 1. Generate, reduce, and solve SAT instances
    print("\n--- SAT Problem ---")
    for size in problem_sizes:
        # Generate SAT instance
        sat_instance = generate_random_sat(num_variables=size, num_clauses=size*4, seed=None)
        sat_path = settings.paths.data_dir / f"generated_sat_{timestamp}_n{size}.cnf"
        write_dimacs_cnf(sat_instance, sat_path)
        progress.log(f"SAT instance (n={size}) written to {sat_path}", style="bold green")
        
        # Solve with different algorithms
        for algo in ["dpll", "backtrack"]:
            exp = tracker.create(f"sat_{algo}_n{size}", "sat", algo)
            tracker.start()
            
            with progress.task(f"Solving SAT (n={size}) with {algo}"):
                solver = SATSolver(algorithm=algo)
                result = solver.solve(sat_instance.clauses)
                is_valid = verify_sat_solver_result(sat_instance.clauses, result) if result.satisfiable else None
            
            tracker.complete({
                "satisfiable": result.satisfiable,
                "solution_valid": is_valid,
                "time_seconds": result.time_seconds,
            })
            
            exp_result = ExperimentResult(
                problem_type="sat",
                algorithm=algo,
                instance_name=f"sat_n{size}",
                instance_size={
                    "variables": sat_instance.num_variables,
                    "clauses": sat_instance.num_clauses,
                    "numbers": 0,
                },
                is_satisfiable=result.satisfiable,
                solution=result.solution,
                nodes_explored=result.nodes_explored,
                time_seconds=result.time_seconds,
                metadata={"solution_valid": is_valid, "size": size}
            )
            results.append(exp_result)
            serializer.save_result(exp_result)
            progress.log(f"SAT (n={size}, {algo}) solved in {result.time_seconds:.4f}s", style="bold blue")

    # Reduction example: SAT -> 3-SAT (using first instance)
    sat_instance = generate_random_sat(num_variables=20, num_clauses=80, seed=None)
    sat_reduction_path = settings.paths.data_dir / f"reduction_sat_{timestamp}.cnf"
    write_dimacs_cnf(sat_instance, sat_reduction_path)
    
    with progress.task("Reducing SAT to 3-SAT"):
        reduced_3sat = reduce_sat_to_3sat(sat_instance.clauses, sat_instance.num_variables)
        reduced_sat_instance = SATInstance(
            clauses=reduced_3sat.reduced_instance,
            num_variables=reduced_3sat.reduced_variables,
            num_clauses=reduced_3sat.reduced_clauses
        )
        write_dimacs_cnf(reduced_sat_instance, sat_reduction_path.parent / f"{sat_reduction_path.stem}_to_3sat.cnf")

    # 2. Generate, reduce, and solve 3-SAT instances
    print("\n--- 3-SAT Problem ---")
    for size in problem_sizes:
        # Generate 3-SAT instance
        three_sat_instance = generate_random_3sat(num_variables=size, num_clauses=size*4, seed=None)
        three_sat_path = settings.paths.data_dir / f"generated_3sat_{timestamp}_n{size}.cnf"
        write_dimacs_cnf(three_sat_instance, three_sat_path)
        progress.log(f"3-SAT instance (n={size}) written to {three_sat_path}", style="bold green")
        
        # Solve with different algorithms
        for algo in ["dpll", "backtrack"]:
            exp = tracker.create(f"3sat_{algo}_n{size}", "3sat", algo)
            tracker.start()
            
            with progress.task(f"Solving 3-SAT (n={size}) with {algo}"):
                solver = ThreeSATSolver(algorithm=algo)
                result = solver.solve(three_sat_instance.clauses)
                is_valid = verify_3sat_solver_result(three_sat_instance.clauses, result) if result.satisfiable else None
            
            tracker.complete({
                "satisfiable": result.satisfiable,
                "solution_valid": is_valid,
                "time_seconds": result.time_seconds,
            })
            
            exp_result = ExperimentResult(
                problem_type="3sat",
                algorithm=algo,
                instance_name=f"3sat_n{size}",
                instance_size={
                    "variables": three_sat_instance.num_variables,
                    "clauses": three_sat_instance.num_clauses,
                    "numbers": 0,
                },
                is_satisfiable=result.satisfiable,
                solution=result.solution,
                nodes_explored=result.nodes_explored,
                time_seconds=result.time_seconds,
                metadata={"solution_valid": is_valid, "size": size}
            )
            results.append(exp_result)
            serializer.save_result(exp_result)
            progress.log(f"3-SAT (n={size}, {algo}) solved in {result.time_seconds:.4f}s", style="bold blue")

    # Reduction example: 3-SAT -> Subset Sum (using first instance)
    three_sat_instance = generate_random_3sat(num_variables=15, num_clauses=60, seed=None)
    three_sat_reduction_path = settings.paths.data_dir / f"reduction_3sat_{timestamp}.cnf"
    write_dimacs_cnf(three_sat_instance, three_sat_reduction_path)
    
    with progress.task("Reducing 3-SAT to Subset Sum"):
        reduced_subsum = reduce_3sat_to_subset_sum(three_sat_instance.clauses, three_sat_instance.num_variables)
        reduced_3sat_instance = SubsetSumInstance(numbers=reduced_subsum.numbers, target=reduced_subsum.target)
        write_subset_sum_file(reduced_3sat_instance, three_sat_reduction_path.parent / f"{three_sat_reduction_path.stem}_to_subsum.txt")

    # 3. Generate and solve Subset Sum instances
    print("\n--- Subset Sum Problem ---")
    for size in problem_sizes:
        # Generate Subset Sum instance
        subset_sum_instance = generate_random_subset_sum(num_elements=size, max_value=50, seed=None)
        subset_sum_path = settings.paths.data_dir / f"generated_subset_sum_{timestamp}_n{size}.txt"
        write_subset_sum_file(subset_sum_instance, subset_sum_path)
        progress.log(f"Subset Sum instance (n={size}) written to {subset_sum_path}", style="bold green")
        
        # Solve with different algorithms
        for algo in ["dynamic", "backtrack"]:
            exp = tracker.create(f"subset_sum_{algo}_n{size}", "subset_sum", algo)
            tracker.start()
            
            with progress.task(f"Solving Subset Sum (n={size}) with {algo}"):
                solver = SubsetSumSolver(algorithm=algo)
                result = solver.solve(subset_sum_instance.numbers, subset_sum_instance.target)
                is_valid = verify_subset_sum_solution(
                    subset_sum_instance.numbers, 
                    subset_sum_instance.target, 
                    result.solution
                ) if result.satisfiable else None
            
            tracker.complete({
                "satisfiable": result.satisfiable,
                "solution_valid": is_valid,
                "time_seconds": result.time_seconds,
            })
            
            exp_result = ExperimentResult(
                problem_type="subset_sum",
                algorithm=algo,
                instance_name=f"subset_sum_n{size}",
                instance_size={
                    "variables": 0,
                    "clauses": 0,
                    "numbers": len(subset_sum_instance.numbers),
                },
                is_satisfiable=result.satisfiable,
                solution=result.solution,
                time_seconds=result.time_seconds,
                nodes_explored=result.nodes_explored,
                metadata={"solution_valid": is_valid, "size": size}
            )
            results.append(exp_result)
            serializer.save_result(exp_result)
            progress.log(f"Subset Sum (n={size}, {algo}) solved in {result.time_seconds:.4f}s", style="bold blue")

    # 4. Save batch results and experiment summary
    serializer.save_batch(results, f"experiment_batch_results_{timestamp}.json")
    tracker.save_summary(f"experiment_summary_{timestamp}.json")
    progress.log("Batch results and experiment summary saved.", style="bold green")

    # 5. Plot benchmarks
    print("\n--- Generating Complexity Plots ---")
    with progress.task("Plotting complexity curves"):
        def flatten_result(r):
            """Flatten ExperimentResult for DataFrame conversion."""
            data = vars(r).copy()
            if 'instance_size' in data:
                size_info = data.pop('instance_size')
                data.update(size_info)
            return data
        
        for problem_type in ["sat", "3sat", "subset_sum"]:
            type_results = [flatten_result(r) for r in results if r.problem_type == problem_type]
            
            if type_results:
                try:
                    df = pd.DataFrame(type_results)
                    logger.info(f"Plotting {problem_type}: {len(df)} results")
                    logger.info(f"Columns: {df.columns.tolist()}")
                    
                    saved_plots = plot_complexity(df, output_dir=settings.paths.plots_dir, show=False)
                    logger.info(f"Saved {len(saved_plots)} plots for {problem_type}")
                    progress.log(f"Generated {len(saved_plots)} plots for {problem_type}", style="bold magenta")
                    
                except Exception as e:
                    logger.error(f"Failed to plot {problem_type}: {e}", exc_info=True)
                    progress.log(f"Error plotting {problem_type}: {e}", style="bold red")
            else:
                logger.warning(f"No results found for {problem_type}")
    
    progress.log(f"All plots saved to {settings.paths.plots_dir}", style="bold magenta")

    print("=" * 60)
    print(f"Experiment complete!")
    print(f"  Results: {settings.paths.results_dir}")
    print(f"  Data: {settings.paths.data_dir}")
    print(f"  Plots: {settings.paths.plots_dir}")
    print(f"  Logs: {settings.paths.logs_dir}")
    print(f"  Run ID: {timestamp}")
    print("=" * 60)


if __name__ == "__main__":
    main()

# #!/usr/bin/env python3
# """
# NP-Complexity Project - Main Entry Point
# 
# Study of NP-complete problems: SAT, 3-SAT, and Subset Sum.
# 
# Usage:
#     python main.py                    # Interactive mode
#     python main.py --help            # Show help
#     python -m src.cli solve sat ...  # CLI mode
# """
# import sys
# from pathlib import Path
# import pandas as pd
# 
# # Add src to path
# sys.path.insert(0, str(Path(__file__).parent))
# 
# def main():
#     """Full project Experiment: generation, reduction, solving, verification, experiment/progress tracking, results/plots."""
#     from src.benchmarks import generate_random_sat, generate_random_3sat, generate_random_subset_sum, BenchmarkRunner, plot_complexity
#     from src.reductions import reduce_sat_to_3sat, reduce_3sat_to_subset_sum
#     from src.solvers import SATSolver, ThreeSATSolver, SubsetSumSolver
#     from src.verifiers import verify_sat_solver_result, verify_3sat_solver_result, verify_subset_sum_solution
#     from src.utils import ResultsSerializer, ProgressTracker
#     from src.utils.experiment import ExperimentTracker
#     from src.utils.parsers import write_dimacs_cnf, write_subset_sum_file, SATInstance, SubsetSumInstance
#     from src.utils.logging import setup_logging, get_logger
#     from src.utils.config import settings, ensure_directories
#     from datetime import datetime
#     # Setup
#     ensure_directories()
#     setup_logging(settings.log_level)
#     logger = get_logger("main")
#     logger.info("NP-Complexity Project", version="0.1.0")
# 
# 
# 
#     # Experiment and progress tracking
#     tracker = ExperimentTracker()
#     progress = ProgressTracker()
#     serializer = ResultsSerializer()
# 
#     print("=" * 60)
#     print("NP-Complexity Project: Full Experiment")
#     print("=" * 60)
# 
#     # 1. Generate instances and write to files
#     sat_instance = generate_random_sat(num_variables=20, num_clauses=91, seed=None)
#     sat_path = settings.paths.data_dir / f"generated_sat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.cnf"
#     write_dimacs_cnf(sat_instance, sat_path)
#     progress.log(f"SAT instance written to {sat_path}", style="bold green")
# 
#     three_sat_instance = generate_random_3sat(num_variables=20, num_clauses=91, seed=None)
#     three_sat_path = settings.paths.data_dir / f"generated_3sat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.cnf"
#     write_dimacs_cnf(three_sat_instance, three_sat_path)
#     progress.log(f"3-SAT instance written to {three_sat_path}", style="bold green")
# 
#     subset_sum_instance = generate_random_subset_sum(num_elements=10, max_value=50, seed=None)
#     subset_sum_path = settings.paths.data_dir / f"generated_subset_sum_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
#     write_subset_sum_file(subset_sum_instance, subset_sum_path)
#     progress.log(f"Subset Sum instance written to {subset_sum_path}", style="bold green")
# 
#     # 2. Reductions: SAT -> 3-SAT -> Subset Sum
#     with progress.task("Reducing SAT to 3-SAT"):
#         reduced_3sat = reduce_sat_to_3sat(sat_instance.clauses, sat_instance.num_variables)
#         reduced_sat_instance = SATInstance(clauses=reduced_3sat.reduced_instance,num_variables=reduced_3sat.reduced_variables, num_clauses=reduced_3sat.reduced_clauses)
#         write_dimacs_cnf(reduced_sat_instance, sat_path.parent / f"{sat_path.stem}_to_3sat.cnf")
#     with progress.task("Reducing 3-SAT to Subset Sum"):
#         reduced_subsum = reduce_3sat_to_subset_sum(three_sat_instance.clauses, three_sat_instance.num_variables)
#         reduced_3sat_instance = SubsetSumInstance(numbers=reduced_subsum.numbers, target=reduced_subsum.target)
#         write_subset_sum_file(reduced_3sat_instance, three_sat_path.parent / f"{three_sat_path.stem}_to_subsum.txt")
#     # 3. Run solvers on sample problems (with experiment tracking)
#     sample_problems = [
#         ("sat", sat_instance, SATSolver, ["dpll", "backtrack"]),
#         ("3sat", three_sat_instance, ThreeSATSolver, ["dpll", "backtrack"]),
#         ("subset_sum", subset_sum_instance, SubsetSumSolver, ["dynamic", "backtrack"]),
#     ]
# 
#     results = []
#     for problem_type, instance, SolverClass, algorithms in sample_problems:
#         for algo in algorithms:
#             exp = tracker.create(f"{problem_type}_{algo}", problem_type, algo)
#             tracker.start()
#             with progress.task(f"Solving {problem_type} with {algo}"):
#                 if problem_type == "sat":
#                     solver = SolverClass(algorithm=algo)
#                     result = solver.solve(instance.clauses)
#                     if result.satisfiable:
#                         is_valid = verify_sat_solver_result(instance.clauses, result)
#                     else:
#                         is_valid = None  # No solution to verify
#                 elif problem_type == "3sat":
#                     solver = SolverClass(algorithm=algo)
#                     result = solver.solve(instance.clauses)
#                     if result.satisfiable:
#                         is_valid = verify_3sat_solver_result(instance.clauses, result)
#                     else:
#                         is_valid = None  # No solution to verify
#                 elif problem_type == "subset_sum":
#                     solver = SolverClass(algorithm=algo)
#                     result = solver.solve(instance.numbers, instance.target)
#                     if result.satisfiable:
#                         is_valid = verify_subset_sum_solution(instance.numbers, instance.target, result.solution)
#                     else:
#                         is_valid = None  # No solution to verify
#                 else:
#                     continue
#             tracker.complete({
#                 "satisfiable": result.satisfiable,
#                 "solution_valid": is_valid,
#                 "time_seconds": result.time_seconds,
#             })
#             # Save result
#             from src.utils.serialization import ExperimentResult
#             exp_result = ExperimentResult(
#                 problem_type=problem_type,
#                 algorithm=algo,
#                 instance_name=instance.name,
#                 instance_size={
#                     "variables": getattr(instance, "num_variables", None),
#                     "clauses": getattr(instance, "num_clauses", None),
#                     "numbers": len(getattr(instance, "numbers", [])),
#                 },
#                 is_satisfiable=result.satisfiable,
#                 solution=result.solution,
#                 time_seconds=result.time_seconds,
#                 metadata={"solution_valid": is_valid}
#             )
#             results.append(exp_result)
#             serializer.save_result(exp_result)
#             progress.log(f"Result for {problem_type} ({algo}) saved.", style="bold blue")
# 
#     # 4. Save batch results and experiment summary
#     serializer.save_batch(results, f"experiment_batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
#     tracker.save_summary(f"experiment_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
#     progress.log("Batch results and experiment summary saved.", style="bold green")
# 
#     # 5. Plot benchmarks (example)
#     with progress.task("Plotting complexity curves"):
#         # Flatten results to proper DataFrame structure
#         def flatten_result(r):
#             data = vars(r).copy()
#             # Extract nested instance_size fields
#             if 'instance_size' in data:
#                 size = data.pop('instance_size')
#                 data.update(size)  # Add variables, clauses, numbers as separate columns
#             return data
#         
#         sat_results = [flatten_result(r) for r in results if r.problem_type == "sat"]
#         if sat_results:
#             sat_df = pd.DataFrame(sat_results)
#             print(f"SAT DataFrame columns: {sat_df.columns.tolist()}")  # Debug
#             plot_complexity(sat_df, output_dir=settings.paths.plots_dir)
#         
#         # Repeat for 3sat and subset_sum
#         three_sat_results = [flatten_result(r) for r in results if r.problem_type == "3sat"]
#         if three_sat_results:
#             plot_complexity(pd.DataFrame(three_sat_results), output_dir=settings.paths.plots_dir)
#         
#         subset_sum_results = [flatten_result(r) for r in results if r.problem_type == "subset_sum"]
#         if subset_sum_results:
#             plot_complexity(pd.DataFrame(subset_sum_results), output_dir=settings.paths.plots_dir)
#     
#     progress.log(f"Plots saved to {settings.paths.plots_dir}.", style="bold magenta")
# 
#     print("=" * 60)
#     print(f"Experiment complete. See results, logs, and plots in the {settings.paths.results_dir} directory.")
#     print("=" * 60)
# 
# if __name__ == "__main__":
#     main()
# 