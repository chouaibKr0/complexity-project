"""Performance monitoring and timing utilities."""
import time
import functools
from dataclasses import dataclass, field
from typing import Callable, Any
from contextlib import contextmanager
import tracemalloc


@dataclass
class TimingResult:
    """Result of a timed operation."""
    name: str
    elapsed_seconds: float
    memory_peak_mb: float | None = None
    
    def __str__(self):
        mem = f", peak memory: {self.memory_peak_mb:.2f}MB" if self.memory_peak_mb else ""
        return f"{self.name}: {self.elapsed_seconds:.4f}s{mem}"


@dataclass
class Timer:
    """Context manager for timing code blocks."""
    name: str = "operation"
    track_memory: bool = False
    _start: float = field(default=0, repr=False)
    _result: TimingResult | None = field(default=None, repr=False)
    
    def __enter__(self) -> "Timer":
        if self.track_memory:
            tracemalloc.start()
        self._start = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        elapsed = time.perf_counter() - self._start
        memory_peak = None
        if self.track_memory:
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            memory_peak = peak / 1024 / 1024  # Convert to MB
        self._result = TimingResult(self.name, elapsed, memory_peak)
    
    @property
    def result(self) -> TimingResult:
        return self._result
    
    @property
    def elapsed(self) -> float:
        return self._result.elapsed_seconds if self._result else 0


def performance_monitor(track_memory: bool = False):
    """Decorator to monitor function performance."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> tuple[Any, TimingResult]:
            with Timer(func.__name__, track_memory=track_memory) as t:
                result = func(*args, **kwargs)
            return result, t.result
        return wrapper
    return decorator


@contextmanager
def timed_block(name: str, track_memory: bool = False):
    """Context manager for timing a block of code."""
    timer = Timer(name, track_memory)
    with timer:
        yield timer
    print(timer.result)
