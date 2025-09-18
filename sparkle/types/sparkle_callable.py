"""Abstract class Sparkle Callable."""

from __future__ import annotations
from pathlib import Path


class SparkleCallable:
    """Sparkle Callable class."""

    def __init__(
        self: SparkleCallable, directory: Path, runsolver_exec: Path = None
    ) -> None:
        """Initialize callable.

        Args:
            directory: Directory of the callable.
            runsolver_exec: Path to the runsolver executable.
                By default, runsolver in solver_directory.
        """
        self.directory = directory
        self.name = directory.name
        self._runsolver_exec = runsolver_exec

    @property
    def runsolver_exec(self: SparkleCallable) -> Path:
        """Return the path of the runsolver executable."""
        if self._runsolver_exec is None:
            return self.directory / "runsolver"
        return self._runsolver_exec

    def build_cmd(self: SparkleCallable) -> list[str | Path]:
        """A method that builds the commandline call string."""
        return NotImplementedError

    def run(self: SparkleCallable) -> None:
        """A method that runs the callable."""
        return NotImplementedError
