"""Results serialization and storage."""
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Any
import orjson


@dataclass
class ExperimentResult:
    """Container for experiment results."""
    problem_type: str  # "sat", "3-sat", "subset_sum"
    algorithm: str
    instance_name: str
    instance_size: dict  # e.g., {"variables": 10, "clauses": 45}
    is_satisfiable: bool | None
    solution: Any | None
    time_seconds: float
    memory_mb: float | None = None
    timestamp: str = None
    metadata: dict = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


class ResultsSerializer:
    """Serialize and save experiment results."""
    
    def __init__(self, results_dir: Path = Path("results")):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def save_result(self, result: ExperimentResult, filename: str = None) -> Path:
        """Save a single result to JSON."""
        if filename is None:
            filename = f"{result.problem_type}_{result.algorithm}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.results_dir / filename
        data = asdict(result)
        
        with open(filepath, "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
        
        return filepath
    
    def save_batch(self, results: list[ExperimentResult], filename: str) -> Path:
        """Save multiple results to a single JSON file."""
        filepath = self.results_dir / filename
        data = [asdict(r) for r in results]
        
        with open(filepath, "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
        
        return filepath
    
    def load_result(self, filepath: Path) -> ExperimentResult:
        """Load a result from JSON."""
        with open(filepath, "rb") as f:
            data = orjson.loads(f.read())
        return ExperimentResult(**data)
    
    def load_batch(self, filepath: Path) -> list[ExperimentResult]:
        """Load multiple results from JSON."""
        with open(filepath, "rb") as f:
            data = orjson.loads(f.read())
        return [ExperimentResult(**r) for r in data]
    
    def append_to_log(self, result: ExperimentResult, log_file: str = "experiment_log.jsonl"):
        """Append result to a JSON Lines log file."""
        filepath = self.results_dir / log_file
        with open(filepath, "ab") as f:
            f.write(orjson.dumps(asdict(result)))
            f.write(b"\n")
