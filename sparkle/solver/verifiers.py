"""Classes for verifying solutions."""
from __future__ import annotations
from pathlib import Path
import subprocess

from sparkle.types import SolverStatus


class SolutionVerifier:
    """Solution verifier base class."""

    def verify(self: SolutionVerifier,
               instance: Path,
               output: dict,
               solver_call: list[str]) -> SolverStatus:
        """Verify the solution."""
        raise NotImplementedError


class SATVerifier(SolutionVerifier):
    """Class to handle the SAT verifier."""
    sat_verifier_path =\
        Path(__file__).parent.parent / "Components/Sparkle-SAT-verifier/SAT"

    def __str__(self: SATVerifier) -> str:
        """Return the name of the SAT verifier."""
        return SATVerifier.__name__

    @staticmethod
    def verify(instance: Path, output: dict, solver_call: list[str]) -> SolverStatus:
        """Run a SAT verifier and return its status."""
        if SolverStatus(output["status"]) == SolverStatus.TIMEOUT:
            return SolverStatus.TIMEOUT
        raw_result = Path([s for s in solver_call if s.endswith(".rawres")][0])
        return SATVerifier.call_sat_raw_result(instance, raw_result)

    @staticmethod
    def sat_verify_output(sat_output: str) -> SolverStatus:
        """Return the status of the SAT verifier.

        Four statuses are possible: "SAT", "UNSAT", "WRONG", "UNKNOWN"
        """
        return_code = int(sat_output.splitlines()[-1])
        if return_code == 11:  # SAT code
            return SolverStatus.SAT
        if return_code == 10:  # UNSAT code
            return SolverStatus.UNSAT
        # Wrong code OR Unknown code
        if return_code == 0 and "Wrong solution." in sat_output:
            return SolverStatus.WRONG
        # Should not occur
        return SolverStatus.UNKNOWN

    @staticmethod
    def call_sat_raw_result(instance: Path,
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
        return SATVerifier.sat_verify_output(sat_verify.stdout.decode())


class SolutionFileVerifier(SolutionVerifier):
    """Class to handle the file verifier."""

    def __init__(self: SolutionFileVerifier, csv_file: Path) -> None:
        """Initialize the verifier by building dictionary from csv.

        Args:
            csv_file: path to the csv file. Requires lines to be of the form:
                instance,objective,solution
        """
        self.csv_file = csv_file
        lines = [line.split(",", maxsplit=2)
                 for line in self.csv_file.read_text().splitlines()]
        self.solutions = {instance: (objective, solution)
                          for instance, objective, solution in lines}

    def __str__(self: SATVerifier) -> str:
        """Return the name of the SAT verifier."""
        return SolutionFileVerifier.__name__

    def verify(self: SolutionFileVerifier,
               instance: Path,
               solver_output: dict[str, object],
               solver_call: list[str]) -> SolverStatus:
        """Verify the solution.

        Args:
            instance: instance to verify, solution found by instance name as key
            solver_output: outcome of the solver to verify

        Returns:
            The status of the solver on the instance
        """
        # If the solver ran out of time, we cannot verify a solution
        if SolverStatus(solver_output["status"]) == SolverStatus.TIMEOUT:
            return SolverStatus.TIMEOUT
        instance = instance.name
        if instance not in self.solutions:
            return SolverStatus.UNKNOWN

        objective, solution = self.solutions[instance]
        if objective not in solver_output:
            return SolverStatus.UNKNOWN

        outcome = solver_output[objective]
        if solution in SolverStatus._value2member_map_:  # SAT type status
            solution, outcome = SolverStatus(solution), SolverStatus(outcome)
            if solution == SolverStatus.UNKNOWN or solution == outcome:
                # Verify that the presented solution is correct
                return SATVerifier.verify(instance, solver_output, solver_call)
            else:
                return SolverStatus.WRONG

        if solution != outcome:
            return SolverStatus.WRONG
        return SolverStatus.SUCCESS


# Define a mapping so we can translate between names and classes
mapping = {SATVerifier.__name__: SATVerifier,
           SolutionFileVerifier.__name__: SolutionFileVerifier}
