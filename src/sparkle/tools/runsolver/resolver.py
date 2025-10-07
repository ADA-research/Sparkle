"""Resolver class if RunSolver is not supported."""

from pathlib import Path

from sparkle.tools.runsolver.runsolver import RunSolver
from sparkle.tools.runsolver.py_runsolver import PyRunSolver


class RunSolverResolver(RunSolver):
    """Class representation the RunSolver Resolver."""

    @staticmethod
    def wrap_command(
        runsolver_executable: Path,
        command: list[str],
        cutoff_time: int,
        log_directory: Path,
        log_name_base: str = None,
        raw_results_file: bool = True,
    ) -> list[str]:
        """Resolves if RunSolver is available. Otherwise uses a python implementation.

        Args:
            runsolver_executable: The Path to the runsolver executable.
                Is returned as an *absolute* path in the output.
            command: The command to wrap.
            cutoff_time: The cutoff CPU time for the solver.
            log_directory: The directory where to write the solver output.
            log_name_base: A user defined name to easily identify the logs.
                Defaults to "runsolver".
            raw_results_file: Whether to use the raw results file.

        Returns:
            List of commands and arguments to execute the solver.
        """
        if runsolver_executable.exists():
            return RunSolver.wrap_command(
                runsolver_executable,
                command,
                cutoff_time,
                log_directory,
                log_name_base,
                raw_results_file,
            )
        else:
            return PyRunSolver.wrap_command(
                command, cutoff_time, log_directory, log_name_base, raw_results_file
            )
