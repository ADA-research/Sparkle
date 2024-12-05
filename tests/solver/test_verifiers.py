"""Solution verifiers tests."""
from sparkle.solver import verifiers
from sparkle.types import SolverStatus
from pathlib import Path


def test_sat_verifier() -> None:
    """Test if SATVerifier correctly returns value."""
    # TODO: write test
    pass


def test_solution_file_verifier() -> None:
    """Test if SolutionFileVerifier correctly returns value."""
    file = Path("tests/test_files/verifier/verifier_file.csv")
    verifier = verifiers.SolutionFileVerifier(file)
    assert verifier.verify(Path("a/instance1.txt"), "SAT") == SolverStatus.SAT
    assert verifier.verify(Path("b/instance2.txt"), "UNSAT") == SolverStatus.UNSAT
    assert verifier.verify(Path("c/instance3.txt"), "15.1") == SolverStatus.WRONG
    assert verifier.verify(Path("c/instance3.txt"), "15.0") == SolverStatus.SUCCESS
    assert verifier.verify(Path("d/idonotexist.txt"), "123") == SolverStatus.UNKNOWN
