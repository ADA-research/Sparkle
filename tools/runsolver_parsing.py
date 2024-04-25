"""Tools to parse runsolver I/O."""

from pathlib import Path
import fcntl

def get_runtime_from_runsolver(runsolver_values_path: Path) -> tuple[float, float]:
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

def get_solver_output(runsolver_configuration: str,
                      process_output: str) -> dict[str, str]:
    """Decode solver output dictionary when called with runsolver."""
    
    return {}