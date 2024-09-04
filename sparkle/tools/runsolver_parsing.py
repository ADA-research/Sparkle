"""Tools to parse runsolver I/O."""
import sys
from pathlib import Path
import ast
import re
import math

from sparkle.types import SolverStatus


def get_runtime(runsolver_values_path: Path,
                not_found: float = -1.0) -> tuple[float, float]:
    """Return the CPU and wallclock time reported by runsolver in values log."""
    cpu_time, wall_time = not_found, not_found
    if runsolver_values_path.exists():
        with runsolver_values_path.open("r") as infile:
            lines = [line.strip().split("=") for line in infile.readlines()
                     if line.count("=") == 1]
            for keyword, value in lines:
                if keyword == "WCTIME":
                    wall_time = float(value)
                elif keyword == "CPUTIME":
                    cpu_time = float(value)
                    # Order is fixed, CPU is the last thing we want to read, so break
                    break
    return cpu_time, wall_time


def get_status(runsolver_values_path: Path, runsolver_raw_path: Path) -> SolverStatus:
    """Get run status from runsolver logs."""
    if not runsolver_values_path.exists():
        # Runsolver value log was not created, job was stopped ''incorrectly''
        return SolverStatus.KILLED
    # First check if runsolver reported time out
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


def get_solver_args(runsolver_log_path: Path) -> str:
    """Retrieves solver arguments dict from runsolver log."""
    if runsolver_log_path.exists():
        for line in runsolver_log_path.open("r").readlines():
            if line.startswith("command line:"):
                return line.split("sparkle_solver_wrapper.py", 1)[1].strip().strip("'")
    return ""


def get_solver_output(runsolver_configuration: list[str],
                      process_output: str,
                      log_dir: Path) -> dict[str, str | object]:
    """Decode solver output dictionary when called with runsolver."""
    solver_input = None
    solver_output = ""
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
            if (log_dir / solver_data_file).exists():
                solver_output = (log_dir / solver_data_file).open("r").read()
        if "-v" in conf or "--var" in conf:
            value_data_file = Path(runsolver_configuration[idx + 1])
        if "--cpu-limit" in conf:
            cutoff_time = float(runsolver_configuration[idx + 1])
        if "-w" in conf or "--watcher-data" in conf:
            watch_file = Path(runsolver_configuration[idx + 1])
            contents = (log_dir / watch_file).open("r").readlines()
            runsolver_call = " ".join(str(c) for c in runsolver_configuration)
            for line in contents:
                if runsolver_call in line:
                    solver_input = re.findall("{.*}", line)[0]
                    solver_input = ast.literal_eval(solver_input)
                    break

    if solver_output == "":
        # Still empty, try to read from subprocess
        solver_output = process_output
    # Format output to only the brackets (dict)
    # NOTE: It should have only one match, do we want some error logging here?
    try:
        solver_regex_filter = re.findall("{.*}", solver_output)[0]
        output_dict = ast.literal_eval(solver_regex_filter)
    except Exception as ex:
        print(f"WARNING: Solver output decoding failed with exception: [{ex}]. "
              f"Assuming TIMEOUT.")
        output_dict = {"status": SolverStatus.TIMEOUT, "quality": math.nan}

    output_dict["cutoff_time"] = cutoff_time
    if value_data_file is not None:
        cpu_time, wall_time = get_runtime(log_dir / value_data_file)
        output_dict["cpu_time"] = cpu_time
        output_dict["wall_time"] = wall_time
    if output_dict["cpu_time"] > cutoff_time:
        output_dict["status"] = SolverStatus.TIMEOUT
    # Add the missing objectives (runtime based)
    if solver_input is not None and "objectives" in solver_input:
        objectives = solver_input["objectives"]
        for o_name in objectives:
            if o_name not in output_dict:
                output_dict[o_name] = None
    return output_dict
