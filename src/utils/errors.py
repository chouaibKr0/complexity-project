"""Custom exceptions and error handling."""
import functools
from typing import Callable, Any


class ComplexityProjectError(Exception):
    """Base exception for the project."""
    pass


class ValidationError(ComplexityProjectError):
    """Invalid input data."""
    pass


class SolverError(ComplexityProjectError):
    """Error during solving."""
    pass


class TimeoutError(ComplexityProjectError):
    """Solver exceeded time limit."""
    pass


class ReductionError(ComplexityProjectError):
    """Error during problem reduction."""
    pass


def error_handler(default_return: Any = None, reraise: bool = False):
    """
    Decorator for handling errors gracefully.
    
    Args:
        default_return: Value to return on error.
        reraise: Whether to re-raise the exception after logging.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ComplexityProjectError as e:
                print(f"[ERROR] {func.__name__}: {e}")
                if reraise:
                    raise
                return default_return
            except Exception as e:
                print(f"[UNEXPECTED ERROR] {func.__name__}: {type(e).__name__}: {e}")
                if reraise:
                    raise
                return default_return
        return wrapper
    return decorator


def timeout_handler(seconds: int):
    """
    Decorator to add timeout to a function.
    Note: Only works on Unix-like systems.
    """
    import signal
    
    def decorator(func: Callable) -> Callable:
        def handler(signum, frame):
            raise TimeoutError(f"{func.__name__} exceeded {seconds}s timeout")
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            old_handler = signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            return result
        return wrapper
    return decorator
