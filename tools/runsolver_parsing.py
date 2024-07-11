"""Tools to parse runsolver I/O."""

from pathlib import Path
import ast
import re
import math


def get_runtime(runsolver_values_path: Path,
                not_found: float = -1.0) -> tuple[float, float]:
    """Return the CPU and wallclock time reported by runsolver in values log."""
    cpu_time, wc_time = not_found, not_found
    if runsolver_values_path.exists():
        with runsolver_values_path.open("r") as infile:
            lines = [line.strip().split("=") for line in infile.readlines()
                     if line.count("=") == 1]
            for keyword, value in lines:
                if keyword == "WCTIME":
                    wc_time = float(value)
                elif keyword == "CPUTIME":
                    cpu_time = float(value)
                    # Order is fixed, CPU is the last thing we want to read, so break
                    break
    return cpu_time, wc_time


def handle_timeouts(runtime: float, status: str,
                    cutoff_time: float, penalty: float) -> tuple[float, str]:
    """Determines whether runtime should be penalised based on status and cutoff."""
    if runtime > cutoff_time or status == "TIMEOUT":
        if status == "CRASHED":
            status = "TIMEOUT"
        return penalty, status
    return runtime, status


def get_status(runsolver_values_path: Path, runsolver_raw_path: Path) -> str:
    """Get run status from runsolver logs."""
    if not runsolver_values_path.exists():
        # Runsolver value log was not created, job was stopped ''incorrectly''
        return "KILLED"
    # First check if runsolver reported time out
    for line in reversed(runsolver_values_path.open("r").readlines()):
        if line.strip().startswith("TIMEOUT="):
            if line.strip() == "TIMEOUT=true":
                return "TIMEOUT"
            break
    if runsolver_raw_path is None:
        return "UNKNOWN"
    if not runsolver_raw_path.exists():
        # Runsolver log was not created, job was stopped ''incorrectly''
        return "KILLED"
    # Last line of runsolver log should contain the raw sparkle solver wrapper output
    runsolver_raw_contents = runsolver_raw_path.open("r").read().strip()
    sparkle_wrapper_dict_str = runsolver_raw_contents.splitlines()[-1]
    solver_regex_filter = re.findall("{.*}", sparkle_wrapper_dict_str)[0]
    output_dict = ast.literal_eval(solver_regex_filter)
    return output_dict["status"]


def get_solver_args(runsolver_log_path: Path) -> str:
    """Retrieves solver arguments dict from runsolver log."""
    if runsolver_log_path.exists():
        for line in runsolver_log_path.open("r").readlines():
            if line.startswith("command line:"):
                # Can't take string from GV due to circular imports
                return line.split("sparkle_solver_wrapper.py", 1)[1]
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
        conf = conf.strip()
        if conf == "-o" or conf == "--solver-data":
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
        solver_regex_filter = re.findall("{.*}", solver_output)[0]
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
