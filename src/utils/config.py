"""Configuration management using Pydantic."""
from pathlib import Path
from typing import Literal
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import yaml


class PathsConfig(BaseModel):
    data_dir: Path = Path("data")
    results_dir: Path = Path("results")
    logs_dir: Path = Path("results/logs")
    plots_dir: Path = Path("results/plots")


class BenchmarkConfig(BaseModel):
    timeout_seconds: int = 300
    max_variables: int = 100
    max_clauses: int = 500
    runs_per_instance: int = 3


class SATConfig(BaseModel):
    default_algorithm: Literal["dpll", "backtrack", "brute_force"] = "dpll"


class ThreeSATConfig(BaseModel):
    default_algorithm: Literal["dpll", "backtrack", "brute_force"] = "dpll"


class SubsetSumConfig(BaseModel):
    default_algorithm: Literal["dynamic", "backtrack", "brute_force"] = "dynamic"
    max_target_value: int = 1000000


class Settings(BaseSettings):
    """Main application settings."""
    app_name: str = "NP-Complexity Study"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    
    paths: PathsConfig = PathsConfig()
    benchmarks: BenchmarkConfig = BenchmarkConfig()
    sat: SATConfig = SATConfig()
    three_sat: ThreeSATConfig = ThreeSATConfig()
    subset_sum: SubsetSumConfig = SubsetSumConfig()
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

    @classmethod
    def from_yaml(cls, path: str = "config.yaml") -> "Settings":
        """Load settings from YAML file."""
        config_path = Path(path)
        if config_path.exists():
            with open(config_path) as f:
                data = yaml.safe_load(f)
            # Flatten nested config
            flat = {}
            if "app" in data:
                flat["app_name"] = data["app"].get("name", "NP-Complexity Study")
                flat["debug"] = data["app"].get("debug", False)
                flat["log_level"] = data["app"].get("log_level", "INFO")
            if "paths" in data:
                flat["paths"] = PathsConfig(**data["paths"])
            if "benchmarks" in data:
                flat["benchmarks"] = BenchmarkConfig(**data["benchmarks"])
            if "sat" in data:
                flat["sat"] = SATConfig(**data["sat"])
            if "three_sat" in data:
                flat["three_sat"] = ThreeSATConfig(**data["three_sat"])
            if "subset_sum" in data:
                flat["subset_sum"] = SubsetSumConfig(**data["subset_sum"])
            return cls(**flat)
        return cls()


# Global settings instance
settings = Settings.from_yaml()


def ensure_directories():
    """Create necessary directories."""
    settings.paths.data_dir.mkdir(parents=True, exist_ok=True)
    settings.paths.results_dir.mkdir(parents=True, exist_ok=True)
    settings.paths.logs_dir.mkdir(parents=True, exist_ok=True)
    settings.paths.plots_dir.mkdir(parents=True, exist_ok=True)
