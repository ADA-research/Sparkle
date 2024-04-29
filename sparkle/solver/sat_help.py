"""Methods related to SAT specific runs."""

from pathlib import Path
import subprocess
import fcntl

import global_variables as sgh
from sparkle.platform import file_help as sfh


def sat_verify(instance_path: str, raw_result_path: str, solver_path: str) -> str:
    """Run a SAT verifier and return its status."""
    status = sat_judge_correctness_raw_result(instance_path, raw_result_path)

    if status != "SAT" and status != "UNSAT" and status != "WRONG":
        status = "UNKNOWN"
        print("Warning: Verification result was UNKNOWN for solver "
              f"{Path(solver_path).name} on instance {Path(instance_path).name}!")

    # TODO: Make removal conditional on a success status (SAT or UNSAT)
    # sfh.rmfiles(raw_result_path)
    return status


def sparkle_sat_parser(raw_result_path: str, runtime: float) -> str:
    """Parse SAT results with Sparkle's internal parser.

    NOTE: This parser probably does not work for all SAT solvers.
    """
    if runtime > sgh.settings.get_general_target_cutoff_time():
        status = "TIMEOUT"
    else:
        status = sat_get_result_status(raw_result_path)

    return status


def sat_get_result_status(raw_result_path: str) -> str:
    """Return the result status reported by a SAT solver."""
    # If no result is reported in the result file something went wrong or the solver
    # timed out
    status = "UNKNOWN"

    with Path(raw_result_path).open("r+") as infile:
        fcntl.flock(infile.fileno(), fcntl.LOCK_EX)
        lines = [line.strip().split() for line in infile.readlines()]
        for words in lines:
            if len(words) == 3 and words[1] == "s":
                if words[2] == "SATISFIABLE":
                    status = "SAT"
                elif words[2] == "UNSATISFIABLE":
                    status = "UNSAT"
                else:
                    # Something is wrong or the solver timed out
                    print(f'Warning: Unknown SAT result "{words[2]}"')
                    status = "UNKNOWN"
                break

    return status


def sat_get_verify_string(tmp_verify_result_path: str) -> str:
    """Return the status of the SAT verifier.

    Four statuses are possible: "SAT", "UNSAT", "WRONG", "UNKNOWN"
    """
    lines = []
    with Path(tmp_verify_result_path).open("r+") as fin:
        fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
        lines = [line.strip() for line in fin.readlines()]
    for index, line in enumerate(lines):
        if line == "Solution verified.":
            if lines[index + 2] == "11":
                return "SAT"
        elif line == "Solver reported unsatisfiable. I guess it must be right!":
            if lines[index + 2] == "10":
                return "UNSAT"
        elif line == "Wrong solution.":
            if lines[index + 2] == "0":
                return "WRONG"
    return "UNKNOWN"


def sat_judge_correctness_raw_result(instance_path: str, raw_result_path: str) -> str:
    """Run a SAT verifier to determine correctness of a result."""
    tmp_verify_result_path = (
        f"Tmp/{Path(sgh.sat_verifier_path).name}_"
        f"{Path(raw_result_path).name}_"
        f"{sgh.get_time_pid_random_string()}.vryres")
    # TODO: Log output file
    print("Run SAT verifier")
    subprocess.run([sgh.sat_verifier_path, instance_path, raw_result_path],
                   stdout=Path(tmp_verify_result_path).open("w+"))
    print("SAT verifier done")

    ret = sat_get_verify_string(tmp_verify_result_path)

    # TODO: Log output file removal
    sfh.rmfiles(tmp_verify_result_path)
    return ret
