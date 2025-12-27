"""
Benchmark Analysis and Visualization.

Analyze benchmark results and create visualizations.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional

from ..utils.config import settings


def analyze_results(df: pd.DataFrame) -> dict:
    """
    Analyze benchmark results.
    
    Args:
        df: DataFrame with benchmark results.
    
    Returns:
        Dictionary with analysis results.
    """
    analysis = {}

    # Average time by algorithm and size
    if "algorithm" in df.columns and ("size" in df.columns or "variables" in df.columns):
        size_col = "size" if "size" in df.columns else "variables"
        analysis["avg_time_by_algo"] = (
            df.groupby(["algorithm", size_col])["time_seconds"].mean().unstack().to_dict()
        )

    # Success rate (non-timeout)
    if "algorithm" in df.columns and "is_satisfiable" in df.columns:
        # Success: not NaN in is_satisfiable (means the solver finished)
        success = df["is_satisfiable"].notna()
        analysis["success_rate"] = (
            df.assign(success=success)
              .groupby("algorithm")["success"].mean().to_dict()
        )

    # Comparison between algorithms (mean time, mean memory, mean nodes if present)
    compare_cols = ["time_seconds"]
    if "memory_mb" in df.columns:
        compare_cols.append("memory_mb")
    if "nodes_explored" in df.columns:
        compare_cols.append("nodes_explored")
    if compare_cols:
        analysis["algo_comparison"] = (
            df.groupby("algorithm")[compare_cols].mean().to_dict()
        )

    # Time complexity estimation (fit curves)
    if "algorithm" in df.columns and ("size" in df.columns or "variables" in df.columns):
        size_col = "size" if "size" in df.columns else "variables"
        complexity_fit = {}
        for algo, group in df.groupby("algorithm"):
            sizes = group[size_col].values
            times = group["time_seconds"].values
            if len(sizes) > 1:
                complexity_fit[algo] = fit_complexity_curve(sizes, times)
        analysis["complexity_fit"] = complexity_fit

    return analysis


def plot_complexity(
    df: pd.DataFrame,
    output_dir: Path = None,
    show: bool = True
) -> list[Path]:
    """
    Create complexity analysis plots.
    
    Args:
        df: DataFrame with benchmark results.
        output_dir: Directory to save plots.
        show: Whether to display plots.
    
    Returns:
        List of saved plot file paths.
    """
    output_dir = output_dir or settings.paths.plots_dir
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_plots = []

    # 1. Time vs Size for each algorithm (log-log scale)
    if "algorithm" in df.columns and ("size" in df.columns or "variables" in df.columns) and "time_seconds" in df.columns:
        size_col = "size" if "size" in df.columns else "variables"
        fig, ax = plt.subplots(figsize=(10, 6))
        for algo in df["algorithm"].unique():
            data = df[df["algorithm"] == algo]
            means = data.groupby(size_col)["time_seconds"].mean()
            ax.plot(means.index, means.values, marker='o', label=algo)
        ax.set_xlabel("Problem Size")
        ax.set_ylabel("Time (seconds)")
        ax.set_title("Algorithm Complexity (log-log)")
        ax.legend()
        ax.set_xscale("log")
        ax.set_yscale("log")
        filepath = output_dir / "complexity_loglog.png"
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        saved_plots.append(filepath)
        if show:
            plt.show()
        plt.close(fig)

    # 2. Algorithm comparison bar chart (mean time)
    if "algorithm" in df.columns and "time_seconds" in df.columns:
        fig, ax = plt.subplots(figsize=(8, 5))
        means = df.groupby("algorithm")["time_seconds"].mean().sort_values()
        sns.barplot(x=means.index, y=means.values, ax=ax)
        ax.set_xlabel("Algorithm")
        ax.set_ylabel("Mean Time (seconds)")
        ax.set_title("Algorithm Mean Solve Time")
        filepath = output_dir / "algo_mean_time.png"
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        saved_plots.append(filepath)
        if show:
            plt.show()
        plt.close(fig)

    # 3. Phase transition plot for SAT (satisfiability vs clause/variable ratio)
    if all(col in df.columns for col in ["clauses", "variables", "is_satisfiable"]):
        df = df.copy()
        df["ratio"] = df["clauses"] / df["variables"]
        ratios = np.sort(df["ratio"].unique())
        sat_rate = df.groupby("ratio")["is_satisfiable"].mean()
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(sat_rate.index, sat_rate.values, marker='o')
        ax.set_xlabel("Clause/Variable Ratio")
        ax.set_ylabel("Satisfiability Rate")
        ax.set_title("Phase Transition in 3-SAT")
        filepath = output_dir / "phase_transition.png"
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        saved_plots.append(filepath)
        if show:
            plt.show()
        plt.close(fig)

    # 4. Nodes explored vs size (log-log)
    if "algorithm" in df.columns and ("size" in df.columns or "variables" in df.columns) and "nodes_explored" in df.columns:
        size_col = "size" if "size" in df.columns else "variables"
        fig, ax = plt.subplots(figsize=(10, 6))
        for algo in df["algorithm"].unique():
            data = df[df["algorithm"] == algo]
            means = data.groupby(size_col)["nodes_explored"].mean()
            ax.plot(means.index, means.values, marker='o', label=algo)
        ax.set_xlabel("Problem Size")
        ax.set_ylabel("Nodes Explored")
        ax.set_title("Nodes Explored vs Size (log-log)")
        ax.legend()
        ax.set_xscale("log")
        ax.set_yscale("log")
        filepath = output_dir / "nodes_vs_size_loglog.png"
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        saved_plots.append(filepath)
        if show:
            plt.show()
        plt.close(fig)

    return saved_plots


def fit_complexity_curve(sizes: list, times: list) -> dict:
    """
    Fit complexity curves to empirical data.
    Tries to fit O(n), O(n^2), O(2^n) and returns best fit.
    """
    from scipy.optimize import curve_fit
    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    def linear(n, a, b):
        return a * n + b
    def quadratic(n, a, b):
        return a * n**2 + b
    def exp2(n, a, b):
        return a * 2**n + b

    models = {
        'O(n)': linear,
        'O(n^2)': quadratic,
        'O(2^n)': exp2
    }
    results = {}
    sizes = np.array(sizes)
    times = np.array(times)
    for name, func in models.items():
        try:
            popt, _ = curve_fit(func, sizes, times, maxfev=10000)
            pred = func(sizes, *popt)
            mse = np.mean((pred - times) ** 2)
            results[name] = {'params': popt.tolist(), 'mse': mse}
        except Exception:
            results[name] = {'params': None, 'mse': float('inf')}
    # Pick best fit (lowest mse)
    best = min(results.items(), key=lambda x: x[1]['mse'])
    return {'best_fit': best[0], 'params': best[1]['params'], 'mse': best[1]['mse'], 'all_fits': results}


def plot_phase_transition(
    results: list[dict],
    output_path: Optional[Path] = None
):
    """
    Plot the phase transition for random 3-SAT.
    The phase transition occurs around clause/variable ratio of 4.26.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    df = pd.DataFrame(results)
    if not all(col in df.columns for col in ["clauses", "variables", "is_satisfiable"]):
        raise ValueError("results must contain 'clauses', 'variables', 'is_satisfiable'")
    df = df.copy()
    df["ratio"] = df["clauses"] / df["variables"]
    sat_rate = df.groupby("ratio")["is_satisfiable"].mean()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(sat_rate.index, sat_rate.values, marker='o')
    ax.set_xlabel("Clause/Variable Ratio")
    ax.set_ylabel("Satisfiability Rate")
    ax.set_title("Phase Transition in 3-SAT")
    ax.axvline(4.26, color='red', linestyle='--', label='Critical Ratio ~4.26')
    ax.legend()
    if output_path is not None:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()
    plt.close(fig)
