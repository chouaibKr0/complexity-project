"""Experiment tracking utilities."""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
import json


@dataclass
class Experiment:
    """Track a single experiment run."""
    name: str
    problem_type: str
    algorithm: str
    parameters: dict = field(default_factory=dict)
    metrics: dict = field(default_factory=dict)
    start_time: datetime = None
    end_time: datetime = None
    status: str = "pending"  # pending, running, completed, failed
    notes: str = ""
    
    def start(self):
        self.start_time = datetime.now()
        self.status = "running"
    
    def complete(self, metrics: dict = None):
        self.end_time = datetime.now()
        self.status = "completed"
        if metrics:
            self.metrics.update(metrics)
    
    def fail(self, error: str):
        self.end_time = datetime.now()
        self.status = "failed"
        self.notes = error
    
    @property
    def duration_seconds(self) -> float | None:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "problem_type": self.problem_type,
            "algorithm": self.algorithm,
            "parameters": self.parameters,
            "metrics": self.metrics,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "status": self.status,
            "notes": self.notes,
        }


class ExperimentTracker:
    """Track multiple experiments."""
    
    def __init__(self, log_dir: Path = Path("results/logs")):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.experiments: list[Experiment] = []
        self.current: Experiment | None = None
    
    def create(self, name: str, problem_type: str, algorithm: str, **params) -> Experiment:
        """Create and register a new experiment."""
        exp = Experiment(
            name=name,
            problem_type=problem_type,
            algorithm=algorithm,
            parameters=params
        )
        self.experiments.append(exp)
        self.current = exp
        return exp
    
    def start(self, name: str = None):
        """Start the current or named experiment."""
        exp = self._get_experiment(name)
        exp.start()
        self._log(exp, "started")
    
    def log_metric(self, key: str, value: Any, name: str = None):
        """Log a metric to the current or named experiment."""
        exp = self._get_experiment(name)
        exp.metrics[key] = value
    
    def complete(self, metrics: dict = None, name: str = None):
        """Mark experiment as completed."""
        exp = self._get_experiment(name)
        exp.complete(metrics)
        self._log(exp, "completed")
    
    def fail(self, error: str, name: str = None):
        """Mark experiment as failed."""
        exp = self._get_experiment(name)
        exp.fail(error)
        self._log(exp, "failed")
    
    def _get_experiment(self, name: str = None) -> Experiment:
        if name:
            for exp in self.experiments:
                if exp.name == name:
                    return exp
            raise ValueError(f"Experiment '{name}' not found")
        if self.current is None:
            raise ValueError("No current experiment")
        return self.current
    
    def _log(self, exp: Experiment, event: str):
        """Log experiment event to file."""
        log_file = self.log_dir / "experiments.jsonl"
        with open(log_file, "a") as f:
            entry = {"event": event, **exp.to_dict()}
            f.write(json.dumps(entry) + "\n")
    
    def save_summary(self, filename: str = "experiment_summary.json"):
        """Save all experiments to a summary file."""
        filepath = self.log_dir / filename
        data = [exp.to_dict() for exp in self.experiments]
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        return filepath
