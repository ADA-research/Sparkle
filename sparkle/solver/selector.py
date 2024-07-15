"""File to handle a Selector for selecting Solvers."""
from __future__ import annotations
from pathlib import Path
import subprocess

from sparkle.types import SparkleCallable

class Selector(SparkleCallable):
    """The Selector class for handling Algorithm Selection."""

    def __init__(self: SparkleCallable,
                 executable_path: Path,
                 runsolver_exec: Path = None,
                 raw_output_directory: Path = None) -> None:
        """Initialize the Selector object.

        Args:
            directory: Path of the Selector executable.
            runsolver_exec: Path to the runsolver executable.
                By default, runsolver in solver_directory.
            raw_output_directory: Directory where the Selector will write its raw output.
                Defaults to directory / tmp
        """
        super().__init__(executable_path.parent, runsolver_exec, raw_output_directory)
        self.selector_path = executable_path
        self.name = self.selector_path.name

    def build_construction_cmd(self: Selector,
                               target_file: Path,
                               performance_data: Path,
                               feature_data: Path,
                               objective: str,
                               runtime_cutoff: str = None,
                               wallclock_limit: str = None) -> list[str | Path]:
        """Builds the commandline call string for constructing the Selector."""
        
        cmd = [self.selector_path,
               "--performance_csv", performance_data,
               "--feature_csv", feature_data,
               "--objective", objective,
               "--save", target_file]
        if runtime_cutoff is not None:
            cmd.extend(["--runtime_cutoff", str(runtime_cutoff), "--tune"])
        if wallclock_limit is not None:
            cmd.extend(["--wallclock_limit", str(wallclock_limit)])
        return cmd

    def construct(self: Selector,
                  target_file: Path | str,
                  performance_data: Path,
                  feature_data: Path,
                  objective: str,
                  runtime_cutoff: str = None,
                  wallclock_limit: str = None) -> Path:
        """Construct the Selector.

        Args:
            target_file: Path to the file to save the Selector to.
            performance_data: Path to the performance data csv.
            feature_data: Path to the feature data csv.
            objective: The objective to optimize for selection.
            runtime_cutoff: Cutoff for the runtime in seconds.
            wallclock_limit: Cutoff for the wallclock time in seconds.

        Returns:
            Path to the constructed Selector."""
        if isinstance(target_file, str):
            target_file = self.raw_output_directory / target_file
        cmd = self.build_construction_cmd(target_file, 
                                          performance_data,
                                          feature_data,
                                          objective,
                                          runtime_cutoff,
                                          wallclock_limit)

        construct = subprocess.run(cmd, capture_output=True)
        if construct.returncode != 0:
            print(f"Selector construction of {self.name} failed! Error:\n"
                  f"{construct.stderr}")
            return None
        return target_file

    def build_cmd(self: Selector, selector_path: Path, feature_vector: str) -> list[str | Path]:
         """Builds the commandline call string for running the Selector."""
         cmd = [self.selector_path,
                "--load", selector_path,
                "--feature_vec", feature_vector]
         return cmd

    def run(self: Selector) -> list:
        """Run the Selector, returning the prediction schedule upon success."""
        return