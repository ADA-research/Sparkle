"""Methods related to SAT specific runs."""
from __future__ import annotations
from pathlib import Path
import subprocess

from sparkle.types import SolverStatus


class SolutionVerifier:
    """Solution verifier base class."""

    def __init__(self: SolutionVerifier) -> None:
        """Initialize the solution verifier."""
        raise NotImplementedError

    def verifiy(self: SolutionVerifier) -> SolverStatus:
        """Verify the solution."""
        raise NotImplementedError


class SATVerifier(SolutionVerifier):
    """Class to handle the SAT verifier."""
    sat_verifier_path = Path("sparkle/Components/Sparkle-SAT-verifier/SAT")

    def __init__(self: SATVerifier) -> None:
        """Initialize the SAT verifier."""
        return

    def __str__(self: SATVerifier) -> str:
        """Return the name of the SAT verifier."""
        return "SATVerifier"

    def verify(self: SATVerifier, instance: Path, raw_result: Path) -> SolverStatus:
        """Run a SAT verifier and return its status."""
        return SATVerifier.sat_judge_correctness_raw_result(instance, raw_result)

    @staticmethod
    def sat_get_verify_string(sat_output: str) -> SolverStatus:
        """Return the status of the SAT verifier.

        Four statuses are possible: "SAT", "UNSAT", "WRONG", "UNKNOWN"
        """
        lines = [line.strip() for line in sat_output.splitlines()]
        for index, line in enumerate(lines):
            if line == "Solution verified.":
                if lines[index + 2] == "11":
                    return SolverStatus.SAT
            elif line == "Solver reported unsatisfiable. I guess it must be right!":
                if lines[index + 2] == "10":
                    return SolverStatus.UNSAT
            elif line == "Wrong solution.":
                if lines[index + 2] == "0":
                    return SolverStatus.WRONG
        return SolverStatus.UNKNOWN

    @staticmethod
    def sat_judge_correctness_raw_result(instance: Path,
                                         raw_result: Path) -> SolverStatus:
        """Run a SAT verifier to determine correctness of a result.

        Args:
            instance: path to the instance
            raw_result: path to the result to verify

        Returns:
            The status of the solver on the instance
        """
        sat_verify = subprocess.run([SATVerifier.sat_verifier_path,
                                     instance,
                                     raw_result],
                                    capture_output=True)
        return SATVerifier.sat_get_verify_string(sat_verify.stdout.decode())
