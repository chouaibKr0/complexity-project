"""
Command Line Interface for NP-Complexity Project.

Usage:
    python -m src.cli solve sat --file instance.cnf
    python -m src.cli solve 3sat --file instance.cnf
    python -m src.cli solve subset-sum --numbers "1,2,3,4" --target 5
    python -m src.cli benchmark --problem sat --sizes 5,10,15,20
    python -m src.cli reduce sat-to-3sat --file instance.cnf
"""
import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table

from .utils.config import settings, ensure_directories
from .utils.logging import setup_logging, get_logger

app = typer.Typer(help="NP-Complexity Study CLI")
console = Console()

# Sub-commands
solve_app = typer.Typer(help="Solve problem instances")
benchmark_app = typer.Typer(help="Run benchmarks")
reduce_app = typer.Typer(help="Perform reductions")

app.add_typer(solve_app, name="solve")
app.add_typer(benchmark_app, name="benchmark")
app.add_typer(reduce_app, name="reduce")


@app.callback()
def main_callback(
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
    log_level: str = typer.Option("INFO", "--log-level", "-l", help="Log level"),
):
    """NP-Complexity Study - SAT, 3-SAT, and Subset Sum."""
    ensure_directories()
    setup_logging(log_level if not debug else "DEBUG")


@solve_app.command("sat")
def solve_sat(
    file: Path = typer.Option(None, "--file", "-f", help="CNF file in DIMACS format"),
    algorithm: str = typer.Option("dpll", "--algo", "-a", help="Algorithm: brute_force, backtrack, dpll"),
):
    """Solve a SAT instance."""
    from .solvers import SATSolver
    from .utils.parsers import parse_dimacs_cnf
    
    console.print(f"[bold]Solving SAT with {algorithm}[/bold]")
    
    if file:
        instance = parse_dimacs_cnf(file)
        solver = SATSolver(algorithm=algorithm)
        result = solver.solve(instance.clauses, instance.num_variables)
        
        if result.satisfiable:
            console.print("[green]SATISFIABLE[/green]")
            console.print(f"Assignment: {result.solution}")
        else:
            console.print("[red]UNSATISFIABLE[/red]")
        console.print(f"Time: {result.time_seconds:.4f}s")
    else:
        console.print("[yellow]No input file provided. Use --file to specify a CNF file.[/yellow]")


@solve_app.command("3sat")
def solve_3sat(
    file: Path = typer.Option(None, "--file", "-f", help="3-CNF file"),
    algorithm: str = typer.Option("dpll", "--algo", "-a", help="Algorithm"),
):
    """Solve a 3-SAT instance."""
    from .solvers import ThreeSATSolver
    from .utils.parsers import parse_dimacs_cnf
    
    console.print(f"[bold]Solving 3-SAT with {algorithm}[/bold]")
    
    if file:
        instance = parse_dimacs_cnf(file)
        solver = ThreeSATSolver(algorithm=algorithm)
        result = solver.solve(instance.clauses, instance.num_variables)
        
        if result.satisfiable:
            console.print("[green]SATISFIABLE[/green]")
        else:
            console.print("[red]UNSATISFIABLE[/red]")
        console.print(f"Time: {result.time_seconds:.4f}s")


@solve_app.command("subset-sum")
def solve_subset_sum(
    numbers: str = typer.Option(..., "--numbers", "-n", help="Comma-separated numbers"),
    target: int = typer.Option(..., "--target", "-t", help="Target sum"),
    algorithm: str = typer.Option("dynamic", "--algo", "-a", help="Algorithm"),
):
    """Solve a Subset Sum instance."""
    from .solvers import SubsetSumSolver
    
    nums = [int(x.strip()) for x in numbers.split(",")]
    console.print(f"[bold]Solving Subset Sum with {algorithm}[/bold]")
    console.print(f"Numbers: {nums}, Target: {target}")
    
    solver = SubsetSumSolver(algorithm=algorithm)
    result = solver.solve(nums, target)
    
    if result.satisfiable:
        console.print("[green]SOLUTION FOUND[/green]")
        console.print(f"Subset: {result.solution}")
    else:
        console.print("[red]NO SOLUTION[/red]")
    console.print(f"Time: {result.time_seconds:.4f}s")


@benchmark_app.command("run")
def run_benchmark(
    problem: str = typer.Option("sat", "--problem", "-p", help="Problem type: sat, 3sat, subset_sum"),
    sizes: str = typer.Option("5,10,15", "--sizes", "-s", help="Comma-separated sizes"),
    algorithms: str = typer.Option("dpll,backtrack", "--algos", "-a", help="Comma-separated algorithms"),
    instances: int = typer.Option(5, "--instances", "-n", help="Instances per size"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Run benchmarks."""
    console.print(f"[bold]Running {problem} benchmarks[/bold]")
    console.print(f"Sizes: {sizes}, Algorithms: {algorithms}")
    # TODO: Connect to benchmark runner


@reduce_app.command("sat-to-3sat")
def reduce_sat_to_3sat_cmd(
    file: Path = typer.Option(..., "--file", "-f", help="Input SAT CNF file"),
    output: Path = typer.Option(None, "--output", "-o", help="Output 3-SAT file"),
):
    """Reduce SAT to 3-SAT."""
    from .reductions import reduce_sat_to_3sat
    from .utils.parsers import parse_dimacs_cnf, write_dimacs_cnf, SATInstance
    
    console.print("[bold]Reducing SAT to 3-SAT[/bold]")
    instance = parse_dimacs_cnf(file)
    result = reduce_sat_to_3sat(instance.clauses, instance.num_variables)
    
    console.print(f"Original: {result.original_variables} vars, {result.original_clauses} clauses")
    console.print(f"Reduced:  {result.reduced_variables} vars, {result.reduced_clauses} clauses")
    
    if output:
        out_instance = SATInstance(
            num_variables=result.reduced_variables,
            num_clauses=result.reduced_clauses,
            clauses=result.reduced_instance,
            name=f"{file.stem}_3sat"
        )
        write_dimacs_cnf(out_instance, output)
        console.print(f"Saved to: {output}")


@reduce_app.command("3sat-to-subset-sum")
def reduce_3sat_to_ss_cmd(
    file: Path = typer.Option(..., "--file", "-f", help="Input 3-SAT CNF file"),
):
    """Reduce 3-SAT to Subset Sum."""
    from .reductions import reduce_3sat_to_subset_sum
    from .utils.parsers import parse_dimacs_cnf
    
    console.print("[bold]Reducing 3-SAT to Subset Sum[/bold]")
    instance = parse_dimacs_cnf(file)
    result = reduce_3sat_to_subset_sum(instance.clauses, instance.num_variables)
    
    console.print(f"Numbers: {len(result.numbers)}")
    console.print(f"Target: {result.target}")


if __name__ == "__main__":
    app()
