"""Solution verifiers tests."""
import sys
from sparkle.solver import verifiers
from sparkle.types import SolverStatus
from pathlib import Path


def test_sat_verifier() -> None:
    """Test if SATVerifier correctly returns value."""
    if sys.platform != "linux":
        return  # SAT Verifier is Linux only
    instance_sat = Path("Examples/Resources/Instances/PTN2/Ptn-7824-b08.cnf")
    solver_call_sat = ["tests/test_files/verifier/sat_solver_runsolver.rawres"]
    solver_call_unsat = ["tests/test_files/verifier/unsat_solver_runsolver.rawres"]
    solver_call_timeout = ["tests/test_files/verifier/timeout_solver_runsolver.rawres"]
    solver_call_wrong = ["tests/test_files/verifier/wrong_solver_runsolver.rawres"]
    assert (
        verifiers.SATVerifier.verify(instance_sat, {"status": "SAT"}, solver_call_sat)
        == SolverStatus.SAT
    )
    assert (
        verifiers.SATVerifier.verify(
            instance_sat, {"status": "UNSAT"}, solver_call_unsat
        )
        == SolverStatus.UNSAT
    )
    assert (
        verifiers.SATVerifier.verify(
            instance_sat, {"status": "TIMEOUT"}, solver_call_timeout
        )
        == SolverStatus.TIMEOUT
    )
    assert (
        verifiers.SATVerifier.verify(instance_sat, {"status": "SAT"}, solver_call_wrong)
        == SolverStatus.WRONG
    )


def test_solution_file_verifier() -> None:
    """Test if SolutionFileVerifier correctly returns value."""
    file = Path("tests/test_files/verifier/verifier_file.csv")
    solver_call_sat = ["tests/test_files/verifier/sat_solver_runsolver.rawres"]
    solver_call_unsat = ["tests/test_files/verifier/unsat_solver_runsolver.rawres"]
    verifier = verifiers.SolutionFileVerifier(file)
    assert (
        verifier.verify(Path("a/instance1.txt"), {"status": "SAT"}, solver_call_sat)
        == SolverStatus.SAT
    )
    assert (
        verifier.verify(Path("b/instance2.txt"), {"status": "UNSAT"}, solver_call_unsat)
        == SolverStatus.UNSAT
    )
    assert (
        verifier.verify(
            Path("c/instance3.txt"), {"coolmetric": "15.1", "status": "SUCCESS"}, []
        )
        == SolverStatus.WRONG
    )
    assert (
        verifier.verify(
            Path("c/instance3.txt"), {"coolmetric": "15.0", "status": "SUCCESS"}, []
        )
        == SolverStatus.SUCCESS
    )
    assert (
        verifier.verify(
            Path("d/idonotexist.txt"), {"coolmetric": "123", "status": "SUCCESS"}, []
        )
        == SolverStatus.UNKNOWN
    )
    assert (
        verifier.verify(
            Path("c/instance3.txt"), {"idonotexist": "123", "status": "SUCCESS"}, []
        )
        == SolverStatus.UNKNOWN
    )
    # If the solver reports timeout, nothing should be checked
    assert (
        verifier.verify(
            Path("c/instance3.txt"), {"idonotexist": "123", "status": "TIMEOUT"}, []
        )
        == SolverStatus.TIMEOUT
    )
