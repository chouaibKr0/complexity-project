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

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import settings, ensure_directories
from src.utils.logging import setup_logging, get_logger


def main():
    """Main entry point."""
    ensure_directories()
    setup_logging(settings.log_level)
    logger = get_logger("main")
    
    logger.info("NP-Complexity Project", version="0.1.0")
    
    # Example usage - uncomment and modify as needed
    print("=" * 60)
    print("NP-Complexity Study Project")
    print("=" * 60)
    print()
    print("Available modules:")
    print("  - src.solvers: SAT, 3-SAT, Subset Sum solvers")
    print("  - src.verifiers: Solution verifiers")
    print("  - src.reductions: SAT→3-SAT, 3-SAT→Subset Sum")
    print("  - src.benchmarks: Instance generators and runners")
    print()
    print("CLI usage:")
    print("  python -m src.cli solve sat --file data/instance.cnf")
    print("  python -m src.cli solve subset-sum --numbers '1,2,3' --target 5")
    print("  python -m src.cli benchmark run --problem sat")
    print()
    print("Quick start example:")
    print("-" * 60)
    
    # Example: Solve a simple SAT instance
    # from src.solvers import SATSolver
    # 
    # # (x1 OR NOT x2) AND (x2 OR x3) AND (NOT x1 OR NOT x3)
    # clauses = [[1, -2], [2, 3], [-1, -3]]
    # 
    # solver = SATSolver(algorithm="dpll")
    # result = solver.solve(clauses)
    # 
    # print(f"Satisfiable: {result.satisfiable}")
    # print(f"Assignment: {result.solution}")
    # print(f"Time: {result.time_seconds:.4f}s")
    
    from src.cli import app
    app()  # This launches the Typer CLI



if __name__ == "__main__":
    main()
