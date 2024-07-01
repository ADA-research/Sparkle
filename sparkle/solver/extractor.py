"""Methods regarding feature extractors."""
from __future__ import annotations
from pathlib import Path
import runrunner as rrr
from runrunner import Runner
from sparkle.types import SparkleCallable


class Extractor(SparkleCallable):
    """Extractor base class for extracting features from instances."""

    def __init__(self: Extractor,
                 directory: Path,
                 runsolver_exec: Path = None,
                 raw_output_directory: Path = None,
                 ) -> None:
        """Initialize solver.

        Args:
            directory: Directory of the solver.
            raw_output_directory: Directory where solver will write its raw output.
                Defaults to solver_directory / tmp
            runsolver_exec: Path to the runsolver executable.
                By default, runsolver in solver_directory.
            deterministic: Bool indicating determinism of the algorithm.
                Defaults to False.
        """
        super.__init__(directory, runsolver_exec, raw_output_directory)
        
    def build_cmd(self: SparkleCallable) -> None:
        return super().build_cmd()

    def run(extractor_path: Path,
                   instance: Path,
                   output_file: Path,
                   runsolver_args: list[int | Path] = None,
                   run_options: list[any] = None,
                   run_on: Runner = Runner.SLURM) -> rrr.LocalRun | rrr.SlurmRun:
        """Runs an extractor job with Runrunner.

        Args:
            extractor_path: Path to the executable
            instance: Path to the instance to run on
            output_file: Target output
            runsolver_args: List of CPU-limit, runsolver executable path, log path
                and variable path. If none, no runsolver is used.
            run_options: The RunRunner options list of job name, base_dir, sbatch
                options list, srun options list.
            run_on: Platform to run on

        Returns:
            Local- or SlurmRun."""
        cmd_list_extractor = []
        if runsolver_args is not None:
            cmd_list_extractor = [runsolver_args[0],
                                    "--cpu-limit", str(runsolver_args[1]),
                                    "-w", runsolver_args[2],  # Set log path
                                    "-v", runsolver_args[3]]  # Set information path
        cmd_list_extractor += [f"{extractor_path}",
                                "-extractor_dir", f"{extractor_path.parent}/",
                                "-instance_file", instance,
                                "-output_file", output_file]
        run_options = [] if run_options is None else run_options

        return rrr.add_to_queue(
            runner=run_on,
            cmd=cmd_list_extractor,
            name=run_options[0],
            base_dir=run_options[1],
            sbatch_options=run_options[2],
            srun_options=run_options[3]
            )

# NOTE: This file should be a class like Solver and share a base class with Solver
def call_extractor(extractor_path: Path,
                   instance: Path,
                   output_file: Path,
                   runsolver_args: list[int | Path] = None,
                   run_options: list[any] = None,
                   run_on: Runner = Runner.SLURM) -> rrr.LocalRun | rrr.SlurmRun:
    """Runs an extractor job with Runrunner.

    Args:
        extractor_path: Path to the executable
        instance: Path to the instance to run on
        output_file: Target output
        runsolver_args: List of CPU-limit, runsolver executable path, log path
            and variable path. If none, no runsolver is used.
        run_options: The RunRunner options list of job name, base_dir, sbatch
            options list, srun options list.
        run_on: Platform to run on

    Returns:
        Local- or SlurmRun."""
    cmd_list_extractor = []
    if runsolver_args is not None:
        cmd_list_extractor = [runsolver_args[0],
                              "--cpu-limit", str(runsolver_args[1]),
                              "-w", runsolver_args[2],  # Set log path
                              "-v", runsolver_args[3]]  # Set information path
    cmd_list_extractor += [f"{extractor_path}",
                          "-extractor_dir", f"{extractor_path.parent}/",
                          "-instance_file", instance,
                          "-output_file", output_file]
    run_options = [] if run_options is None else run_options

    return rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list_extractor,
        name=run_options[0],
        base_dir=run_options[1],
        sbatch_options=run_options[2],
        srun_options=run_options[3]
        )