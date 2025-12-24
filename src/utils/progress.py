"""Progress tracking utilities."""
from tqdm import tqdm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.console import Console
from contextlib import contextmanager
from typing import Iterable, Any

console = Console()


class ProgressTracker:
    """Unified progress tracking for experiments."""
    
    def __init__(self, use_rich: bool = True):
        self.use_rich = use_rich
    
    def iterate(self, iterable: Iterable, description: str = "Processing", total: int = None) -> Iterable:
        """Wrap an iterable with progress tracking."""
        if self.use_rich:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(description, total=total or len(list(iterable)))
                for item in iterable:
                    yield item
                    progress.advance(task)
        else:
            yield from tqdm(iterable, desc=description, total=total)
    
    @contextmanager
    def task(self, description: str):
        """Context manager for a single task with spinner."""
        if self.use_rich:
            with console.status(f"[bold green]{description}..."):
                yield
            console.print(f"[green]✓[/green] {description} complete")
        else:
            print(f"Starting: {description}")
            yield
            print(f"Complete: {description}")
    
    def log(self, message: str, style: str = ""):
        """Print a styled message."""
        if self.use_rich:
            console.print(message, style=style)
        else:
            print(message)


# Simple tqdm wrapper for quick use
def progress_bar(iterable: Iterable, desc: str = "", **kwargs) -> Iterable:
    """Simple progress bar wrapper."""
    return tqdm(iterable, desc=desc, **kwargs)
