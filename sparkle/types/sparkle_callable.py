"""Abstract class Sparkle Callable."""
from __future__ import annotations
from pathlib import Path


class SparkleCallable:
    """Sparkle Callable class."""

    def __init__(self: SparkleCallable,
                 directory: Path,
                 runsolver_exec: Path = None,
                 raw_output_directory: Path = None) -> None:
        """Initialize callable.

        Args:
            directory: Directory of the callable.
            runsolver_exec: Path to the runsolver executable.
                By default, runsolver in solver_directory.
            raw_output_directory: Directory where callable will write its raw output.
                Defaults to directory / tmp
        """
        self.directory = directory
        self.name = directory.name
        self.raw_output_directory = raw_output_directory
        self.runsolver_exec = runsolver_exec
        if self.raw_output_directory is None:
            self.raw_output_directory = self.directory / "tmp"
            self.raw_output_directory.mkdir(exist_ok=True)
        if self.runsolver_exec is None:
            self.runsolver_exec = self.directory / "runsolver"

    def build_cmd(self: SparkleCallable) -> list[str | Path]:
        """A method that builds the commandline call string."""
        return NotImplementedError

    def run(self: SparkleCallable) -> None:
        """A method that runs the callable."""
        return NotImplementedError
