"""Tools to parse runsolver I/O."""

from pathlib import Path
import fcntl
import ast
import re
import math

import global_variables as ga

def get_runtime(runsolver_values_path: Path) -> tuple[float, float]:
    """Return the CPU and wallclock time reported by runsolver."""
    cpu_time = -1.0
    wc_time = -1.0
    if runsolver_values_path.exists():
        with runsolver_values_path.open("r+") as infile:
            fcntl.flock(infile.fileno(), fcntl.LOCK_EX)
            lines = [line.strip().split("=") for line in infile.readlines()
                     if len(line.split("=")) == 2]
            for keyword, value in lines:
                if keyword == "WCTIME":
                    wc_time = float(value)
                elif keyword == "CPUTIME":
                    cpu_time = float(value)
                    # Order is fixed, CPU is the last thing we want to read, so break
                    break
    return cpu_time, wc_time

def get_solver_args(runsolver_log_path: Path) -> dict:
    if runsolver_log_path.exists():
        for line in runsolver_log_path.open("r").readlines():
            if line.startswith("command line:"):
                return line.split(ga.sparkle_solver_wrapper, 1)[1]
    return ""

def get_solver_output(runsolver_configuration: list[str],
                      process_output: str,
                      log_dir: Path) -> dict[str, str]:
    """Decode solver output dictionary when called with runsolver."""
    solver_output = ""
    value_data_file = None
    for idx, conf in enumerate(runsolver_configuration):
        if not isinstance(conf, str):
            # Looking for arg names
            continue
        if "-o" in conf or "--solver-data" in conf:
            # solver output was redirected
            solver_data_file = Path(runsolver_configuration[idx + 1])
            solver_output = (log_dir / solver_data_file).open("r").read()
            
        if "-v" in conf or "--var" in conf:
            value_data_file = Path(runsolver_configuration[idx + 1])

    if solver_output == "":
        # Still empty, try to read from subprocess
        solver_output = process_output
    # Format output to only the brackets (dict)
    # NOTE: It should have only one match, do we want some error logging here?
    try:
        solver_regex_filter = re.findall("\{.*\}", solver_output)[0]
        output_dict = ast.literal_eval(solver_regex_filter)
    except Exception as ex:
        print(f"WARNING: Solver output decoding failed with exception: [{ex}]. "
              f"Assuming TIMEOUT.")
        output_dict = {"status": "TIMEOUT", "quality": math.nan}

    if value_data_file is not None:
        cpu_time, wc_time = get_runtime(log_dir / value_data_file)
        output_dict["cpu_time"] = cpu_time
        output_dict["wc_time"] = wc_time
        output_dict["runtime"] = cpu_time
        if cpu_time == -1.0:
            # If we don't have cpu time, try to fall back on wc
            output_dict["runtime"] = wc_time
    else:
        output_dict["runtime"] = math.nan

    return output_dict