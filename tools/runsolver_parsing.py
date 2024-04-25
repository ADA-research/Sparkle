"""Tools to parse runsolver I/O."""

from pathlib import Path
import fcntl
import ast
import re

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

def get_solver_output(runsolver_configuration: list[str],
                      process_output: str) -> dict[str, str]:
    """Decode solver output dictionary when called with runsolver."""
    solver_output = ""
    watcher_data_file = None
    for conf in runsolver_configuration:
        if "-o" in conf or "--solver-data" in conf:
            # solver output was redirected
            solver_data_file = Path(conf.split(" ", 1)[1])
            solver_output = solver_data_file.open("r").read()
            print(solver_output)
            
        if "-w" in conf or "--watcher-data" in conf:
            watcher_data_file = Path(conf.split(" ", 1)[1])
    if solver_output == "":
        # Still empty, try to read from subprocess
        solver_output = process_output
    # Format output to only the brackets (dict)
    # NOTE: It should have only one match, do we want some error logging here?
    solver_regex_filter = re.findall("\{.*\}", solver_output)[0]
    try:
        output_dict = ast.literal_eval(solver_regex_filter)
    except Exception as ex:
        print(f"ERROR: Solver output decoding failed with exception {ex}:\n"
              f"{solver_output}")
        output_dict = {}

    if watcher_data_file is not None:
        cpu_time, wc_time = get_runtime(watcher_data_file)
        print(cpu_time, wc_time)
        output_dict["cpu_time"] = cpu_time
        output_dict["wc_time"] = wc_time
        output_dict["runtime"] = cpu_time
        if cpu_time == -1.0:
            # If we don't have cpu time, try to fall back on wc
            output_dict["runtime"] = wc_time

    return output_dict