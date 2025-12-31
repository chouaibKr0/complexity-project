"""
Benchmark Analysis and Visualization.

Analyze benchmark results and create visualizations.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, List
import logging

from ..utils.config import settings
from datetime import datetime
logger = logging.getLogger(__name__)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

def validate_dataframe(df: pd.DataFrame, required_cols: List[str]) -> bool:
    """Check if DataFrame has required columns."""
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        logger.warning(f"Missing columns: {missing}")
        return False
    return True


def analyze_results(df: pd.DataFrame) -> dict:
    """
    Analyze benchmark results.
    
    Args:
        df: DataFrame with benchmark results.
    
    Returns:
        Dictionary with analysis results.
    """
    if df.empty:
        logger.warning("Empty DataFrame provided to analyze_results")
        return {}
    
    logger.info(f"Analyzing {len(df)} results with columns: {df.columns.tolist()}")
    analysis = {}

    # Determine size column
    size_col = "variables" if "variables" in df.columns else "size" if "size" in df.columns else None

    # Average time by algorithm and size
    if validate_dataframe(df, ["algorithm", "time_seconds"]) and size_col:
        try:
            analysis["avg_time_by_algo"] = (
                df.groupby(["algorithm", size_col])["time_seconds"]
                .mean()
                .unstack(fill_value=np.nan)
                .to_dict()
            )
        except Exception as e:
            logger.error(f"Error computing avg_time_by_algo: {e}")

    # Success rate (non-timeout)
    if validate_dataframe(df, ["algorithm", "is_satisfiable"]):
        try:
            success = df["is_satisfiable"].notna()
            analysis["success_rate"] = (
                df.assign(success=success)
                .groupby("algorithm")["success"]
                .mean()
                .to_dict()
            )
        except Exception as e:
            logger.error(f"Error computing success_rate: {e}")

    # Algorithm comparison
    compare_cols = ["time_seconds"]
    if "memory_mb" in df.columns:
        compare_cols.append("memory_mb")
    if "nodes_explored" in df.columns:
        compare_cols.append("nodes_explored")
    
    if validate_dataframe(df, ["algorithm"] + compare_cols):
        try:
            analysis["algo_comparison"] = (
                df.groupby("algorithm")[compare_cols]
                .mean()
                .to_dict()
            )
        except Exception as e:
            logger.error(f"Error computing algo_comparison: {e}")

    # Time complexity estimation
    if validate_dataframe(df, ["algorithm", "time_seconds"]) and size_col:
        try:
            complexity_fit = {}
            for algo, group in df.groupby("algorithm"):
                sizes = group[size_col].dropna().values
                times = group.loc[group[size_col].notna(), "time_seconds"].values
                if len(sizes) > 1:
                    complexity_fit[algo] = fit_complexity_curve(sizes, times)
            analysis["complexity_fit"] = complexity_fit
        except Exception as e:
            logger.error(f"Error computing complexity_fit: {e}")

    return analysis


def plot_complexity(
    df: pd.DataFrame,
    output_dir: Path = None,
    show: bool = True
) -> List[Path]:
    """
    Create complexity analysis plots.
    
    Args:
        df: DataFrame with benchmark results.
        output_dir: Directory to save plots.
        show: Whether to display plots.
    
    Returns:
        List of saved plot file paths.
    """
    if df.empty:
        logger.warning("Empty DataFrame provided to plot_complexity")
        return []
    
    logger.info(f"Creating plots for {len(df)} results")
    logger.info(f"Available columns: {df.columns.tolist()}")
    
    output_dir = Path(output_dir or settings.paths.plots_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_plots = []
    size_col = "variables" if "variables" in df.columns else "size" if "size" in df.columns else None

    # 1. Time vs Size (log-log scale)
    if validate_dataframe(df, ["algorithm", "time_seconds"]) and size_col:
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            plotted = False
            
            for algo in df["algorithm"].unique():
                data = df[df["algorithm"] == algo]
                if len(data) > 0:
                    means = data.groupby(size_col)["time_seconds"].mean()
                    if len(means) > 0:
                        ax.plot(means.index, means.values, marker='o', label=algo)
                        plotted = True
            
            if plotted:
                ax.set_xlabel("Problem Size")
                ax.set_ylabel("Time (seconds)")
                ax.set_title("Algorithm Complexity (log-log)")
                ax.legend()
                ax.set_xscale("log")
                ax.set_yscale("log")
                ax.grid(True, alpha=0.3)
                
                filepath = output_dir / f"complexity_loglog_{timestamp}_{timestamp}.png"
                fig.savefig(filepath, dpi=150, bbox_inches="tight")
                saved_plots.append(filepath)
                logger.info(f"Saved plot: {filepath}")
            
            if show:
                plt.show()
            plt.close(fig)
        except Exception as e:
            logger.error(f"Error creating complexity plot: {e}")
            plt.close('all')

    # 2. Algorithm comparison bar chart
    if validate_dataframe(df, ["algorithm", "time_seconds"]):
        try:
            fig, ax = plt.subplots(figsize=(8, 5))
            means = df.groupby("algorithm")["time_seconds"].mean().sort_values()
            
            if len(means) > 0:
                means.plot(kind='bar', ax=ax)
                ax.set_xlabel("Algorithm")
                ax.set_ylabel("Mean Time (seconds)")
                ax.set_title("Algorithm Mean Solve Time")
                ax.tick_params(axis='x', rotation=45)
                
                filepath = output_dir / f"algo_mean_time_{timestamp}.png"
                fig.savefig(filepath, dpi=150, bbox_inches="tight")
                saved_plots.append(filepath)
                logger.info(f"Saved plot: {filepath}")
            
            if show:
                plt.show()
            plt.close(fig)
        except Exception as e:
            logger.error(f"Error creating bar chart: {e}")
            plt.close('all')

    # 3. Phase transition plot (SAT-specific)
    if validate_dataframe(df, ["clauses", "variables", "is_satisfiable"]):
        try:
            df_copy = df.copy()
            df_copy["ratio"] = df_copy["clauses"] / df_copy["variables"]
            sat_rate = df_copy.groupby("ratio")["is_satisfiable"].mean()
            
            if len(sat_rate) > 0:
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.plot(sat_rate.index, sat_rate.values, marker='o', linewidth=2)
                ax.set_xlabel("Clause/Variable Ratio")
                ax.set_ylabel("Satisfiability Rate")
                ax.set_title("Phase Transition in 3-SAT")
                ax.axvline(4.26, color='red', linestyle='--', alpha=0.7, label='Critical ~4.26')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                filepath = output_dir / "phase_transition_{timestamp}.png"
                fig.savefig(filepath, dpi=150, bbox_inches="tight")
                saved_plots.append(filepath)
                logger.info(f"Saved plot: {filepath}")
            
            if show:
                plt.show()
            plt.close(fig)
        except Exception as e:
            logger.error(f"Error creating phase transition plot: {e}")
            plt.close('all')

    # 4. Nodes explored vs size
    if validate_dataframe(df, ["algorithm", "nodes_explored"]) and size_col:
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            plotted = False
            
            for algo in df["algorithm"].unique():
                data = df[df["algorithm"] == algo]
                valid_data = data[data["nodes_explored"].notna()]
                
                if len(valid_data) > 0:
                    means = valid_data.groupby(size_col)["nodes_explored"].mean()
                    if len(means) > 0:
                        ax.plot(means.index, means.values, marker='o', label=algo)
                        plotted = True
            
            if plotted:
                ax.set_xlabel("Problem Size")
                ax.set_ylabel("Nodes Explored")
                ax.set_title("Nodes Explored vs Size (log-log)")
                ax.legend()
                ax.set_xscale("log")
                ax.set_yscale("log")
                ax.grid(True, alpha=0.3)
                
                filepath = output_dir / f"nodes_vs_size_loglog_{timestamp}.png"
                fig.savefig(filepath, dpi=150, bbox_inches="tight")
                saved_plots.append(filepath)
                logger.info(f"Saved plot: {filepath}")
            
            if show:
                plt.show()
            plt.close(fig)
        except Exception as e:
            logger.error(f"Error creating nodes plot: {e}")
            plt.close('all')

    if not saved_plots:
        logger.warning("No plots were generated. Check if DataFrame has required columns.")
    else:
        logger.info(f"Successfully saved {len(saved_plots)} plots to {output_dir}")
    
    return saved_plots


def fit_complexity_curve(sizes: np.ndarray, times: np.ndarray) -> dict:
    """
    Fit complexity curves to empirical data.
    Tries O(n), O(n^2), O(2^n) and returns best fit.
    """
    try:
        from scipy.optimize import curve_fit
        import warnings
        warnings.filterwarnings("ignore", category=RuntimeWarning)
    except ImportError:
        logger.error("scipy not available for curve fitting")
        return {"error": "scipy not installed"}

    def linear(n, a, b):
        return a * n + b
    
    def quadratic(n, a, b):
        return a * n**2 + b
    
    def exponential(n, a, b):
        return a * 2**(n/10) + b  # Scale down exponent for stability

    models = {
        'O(n)': linear,
        'O(n^2)': quadratic,
        'O(2^n)': exponential
    }
    
    results = {}
    sizes = np.array(sizes)
    times = np.array(times)
    
    for name, func in models.items():
        try:
            popt, _ = curve_fit(func, sizes, times, maxfev=10000)
            pred = func(sizes, *popt)
            mse = np.mean((pred - times) ** 2)
            results[name] = {'params': popt.tolist(), 'mse': float(mse)}
        except Exception as e:
            logger.debug(f"Could not fit {name}: {e}")
            results[name] = {'params': None, 'mse': float('inf')}
    
    # Find best fit
    valid_fits = {k: v for k, v in results.items() if v['mse'] != float('inf')}
    if valid_fits:
        best_name = min(valid_fits.items(), key=lambda x: x[1]['mse'])[0]
        return {
            'best_fit': best_name,
            'params': results[best_name]['params'],
            'mse': results[best_name]['mse'],
            'all_fits': results
        }
    
    return {'error': 'No valid fits found', 'all_fits': results}


def plot_phase_transition(
    results: List[dict],
    output_path: Optional[Path] = None
):
    """Plot phase transition for random 3-SAT."""
    df = pd.DataFrame(results)
    
    if not validate_dataframe(df, ["clauses", "variables", "is_satisfiable"]):
        raise ValueError("results must contain 'clauses', 'variables', 'is_satisfiable'")
    
    df["ratio"] = df["clauses"] / df["variables"]
    sat_rate = df.groupby("ratio")["is_satisfiable"].mean()
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(sat_rate.index, sat_rate.values, marker='o', linewidth=2)
    ax.set_xlabel("Clause/Variable Ratio")
    ax.set_ylabel("Satisfiability Rate")
    ax.set_title(f"Phase Transition in 3-SAT {timestamp}")
    ax.axvline(4.26, color='red', linestyle='--', label='Critical ~4.26', alpha=0.7)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    if output_path:
    
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        logger.info(f"Saved phase transition plot: {output_path}")
    
    plt.show()
    plt.close(fig)
