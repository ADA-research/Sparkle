"""Class for handling the Runsolver Wrapper."""
from __future__ import annotations
import sys
import ast
import re
import warnings
from pathlib import Path

from sparkle.types import SolverStatus
from sparkle.tools.general import get_time_pid_random_string


class RunSolver:
    """Class representation of RunSolver.

    For more information see: http://www.cril.univ-artois.fr/~roussel/runsolver/
    """

    def __init__(self: RunSolver) -> None:
        """Currently RunSolver has no instance specific methods or properties."""
        pass

    @staticmethod
    def wrap_command(
            runsolver_executable: Path,
            command: list[str],
            cutoff_time: int,
            log_directory: Path,
            log_name_base: str = None,
            raw_results_file: bool = True) -> list[str]:
        """Wrap a command with the RunSolver call and arguments.

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
        # Create RunSolver Logs
        # --timestamp
        #  instructs to timestamp each line of the solver standard output and
        #  error files (which are then redirected to stdout)

        # --use-pty
        # use a pseudo-terminal to collect the solver output. Currently only
        # available when lines are timestamped. Some I/O libraries (including
        # the C library) automatically flushes the output after each line when
        # the standard output is a terminal. There's no automatic flush when
        # the standard output is a pipe or a plain file. See setlinebuf() for
        # some details. This option instructs runsolver to use a
        # pseudo-terminal instead of a pipe/file to collect the solver
        # output. This fools the solver which will line-buffer its output.

        # -w filename or --watcher-data filename
        # sends the watcher informations to filename

        # -v filename or --var filename
        # save the most relevant information (times,...)
        # in an easy to parse VAR=VALUE file

        # -o filename or --solver-data filename
        # redirects the solver output (both stdout and stderr) to filename
        log_name_base = "runsolver" if log_name_base is None else log_name_base
        unique_stamp = get_time_pid_random_string()
        raw_result_path = log_directory / Path(f"{log_name_base}_{unique_stamp}.rawres")
        watcher_data_path = raw_result_path.with_suffix(".log")
        var_values_path = raw_result_path.with_suffix(".val")

        return [str(runsolver_executable.absolute()),
                "--timestamp", "--use-pty",
                "--cpu-limit", str(cutoff_time),
                "-w", str(watcher_data_path),
                "-v", str(var_values_path)] + (
                    ["-o", str(raw_result_path)] if raw_results_file else []) + command

    @staticmethod
    def get_measurements(runsolver_values_path: Path,
                         not_found: float = -1.0) -> tuple[float, float, float]:
        """Return the CPU and wallclock time reported by runsolver in values log."""
        cpu_time, wall_time, memory = not_found, not_found, not_found
        if runsolver_values_path.exists():
            with runsolver_values_path.open("r") as infile:
                lines = [line.strip().split("=") for line in infile.readlines()
                         if line.count("=") == 1]
                for keyword, value in lines:
                    if keyword == "WCTIME":
                        wall_time = float(value)
                    elif keyword == "CPUTIME":
                        cpu_time = float(value)
                    elif keyword == "MAXVM":
                        memory = float(int(value) / 1024.0)  # MB
                        # Order is fixed, CPU is the last thing we want to read, so break
                        break
        return cpu_time, wall_time, memory

    @staticmethod
    def get_status(runsolver_values_path: Path,
                   runsolver_raw_path: Path) -> SolverStatus:
        """Get run status from runsolver logs."""
        if not runsolver_values_path.exists() and (runsolver_raw_path is not None
                                                   and not runsolver_raw_path.exists()):
            # Runsolver logs were not created, job was stopped ''incorrectly''
            return SolverStatus.CRASHED
        # First check if runsolver reported time out
        if runsolver_values_path.exists():
            for line in reversed(runsolver_values_path.open("r").readlines()):
                if line.strip().startswith("TIMEOUT="):
                    if line.strip() == "TIMEOUT=true":
                        return SolverStatus.TIMEOUT
                    break
        if runsolver_raw_path is None:
            return SolverStatus.UNKNOWN
        if not runsolver_raw_path.exists():
            # Runsolver log was not created, job was stopped ''incorrectly''
            return SolverStatus.KILLED
        # Last line of runsolver log should contain the raw sparkle solver wrapper output
        runsolver_raw_contents = runsolver_raw_path.open("r").read().strip()
        # cutoff_time =
        sparkle_wrapper_dict_str = runsolver_raw_contents.splitlines()[-1]
        solver_regex_filter = re.findall("{.*}", sparkle_wrapper_dict_str)[0]
        output_dict = ast.literal_eval(solver_regex_filter)
        status = SolverStatus(output_dict["status"])
        # if status == SolverStatus.CRASHED and cpu_time > cutoff_time
        return status

    @staticmethod
    def get_solver_args(runsolver_log_path: Path) -> str:
        """Retrieves solver arguments dict from runsolver log."""
        if runsolver_log_path.exists():
            for line in runsolver_log_path.open("r").readlines():
                if line.startswith("command line:"):
                    return (line.split("sparkle_solver_wrapper.py", 1)[1]
                            .strip().strip("'"))
        return ""

    @staticmethod
    def get_solver_output(runsolver_configuration: list[str | Path],
                          process_output: str) -> dict[str, str | object]:
        """Decode solver output dictionary when called with runsolver."""
        solver_input = None
        solver_output = None
        value_data_file = None
        cutoff_time = sys.maxsize
        for idx, conf in enumerate(runsolver_configuration):
            if not isinstance(conf, str):
                # Looking for arg names
                continue
            conf = conf.strip()
            if conf == "-o" or conf == "--solver-data":
                # solver output was redirected
                solver_data_file = Path(runsolver_configuration[idx + 1])
                if solver_data_file.exists():
                    solver_output = solver_data_file.open("r").read()
            if "-v" in conf or "--var" in conf:
                value_data_file = Path(runsolver_configuration[idx + 1])
            if "--cpu-limit" in conf:
                cutoff_time = float(runsolver_configuration[idx + 1])
            if "-w" in conf or "--watcher-data" in conf:
                watch_file = Path(runsolver_configuration[idx + 1])
                args_str = RunSolver.get_solver_args(watch_file)
                if args_str == "":  # Could not find log file or args
                    continue
                solver_input = re.findall("{.*}", args_str)[0]
                solver_input = ast.literal_eval(solver_input)
                cutoff_time = float(solver_input["cutoff_time"])

        if solver_output is None:
            # Still empty, try to read from subprocess
            solver_output = process_output
        # Format output to only the brackets (dict)
        # NOTE: It should have only one match, do we want some error logging here?
        try:
            solver_regex_filter = re.findall("{.*}", solver_output)[0]
            output_dict = ast.literal_eval(solver_regex_filter)
        except Exception:
            config_str = " ".join([str(c) for c in runsolver_configuration])
            warnings.warn("Solver output decoding failed from RunSolver configuration: "
                          f"'{config_str}'. Setting status to 'UNKNOWN'.",
                          category=RuntimeWarning)
            output_dict = {"status": SolverStatus.UNKNOWN}

        output_dict["cutoff_time"] = cutoff_time
        if value_data_file is not None:
            cpu_time, wall_time, memory = RunSolver.get_measurements(value_data_file)
            output_dict["cpu_time"] = cpu_time
            output_dict["wall_time"] = wall_time
            output_dict["memory"] = memory
        else:  # Could not retrieve cpu and wall time (log does not exist)
            output_dict["cpu_time"], output_dict["wall_time"] = -1.0, -1.0
        if output_dict["cpu_time"] > cutoff_time:
            output_dict["status"] = SolverStatus.TIMEOUT
        # Add the missing objectives (runtime based)
        if solver_input is not None and "objectives" in solver_input:
            objectives = solver_input["objectives"].split(",")
            for o_name in objectives:
                if o_name not in output_dict:
                    output_dict[o_name] = None
        return output_dict
