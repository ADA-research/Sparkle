"""Methods related to SAT specific runs."""
from pathlib import Path
import subprocess

from sparkle.solver import Solver

sat_verifier_path = Path("sparkle/Components/Sparkle-SAT-verifier/SAT")


def sat_verify(instance: Path, raw_result: Path, solver: Solver) -> str:
    """Run a SAT verifier and return its status."""
    status = sat_judge_correctness_raw_result(instance, raw_result)

    if status != "SAT" and status != "UNSAT" and status != "WRONG":
        status = "UNKNOWN"
        print(f"Warning: Verification result was UNKNOWN for solver {solver.name} on "
              f"instance {instance.name}!")

    # TODO: Make removal conditional on a success status (SAT or UNSAT)
    # sfh.rmfiles(raw_result_path)
    return status


def sat_get_verify_string(sat_output: str) -> str:
    """Return the status of the SAT verifier.

    Four statuses are possible: "SAT", "UNSAT", "WRONG", "UNKNOWN"
    """
    lines = [line.strip() for line in sat_output.splitlines()]
    for index, line in enumerate(sat_output.splitlines()):
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


def sat_judge_correctness_raw_result(instance: Path, raw_result: Path) -> str:
    """Run a SAT verifier to determine correctness of a result.

    Args:
        instance: path to the instance
        raw_result: path to the result to verify

    Returns:
        The status of the solver on the instance
    """
    print("Run SAT verifier")
    sat_verify = subprocess.run([sat_verifier_path, instance, raw_result],
                                capture_output=True)
    print("SAT verifier done")
    return sat_get_verify_string(sat_verify.stdout.decode())
