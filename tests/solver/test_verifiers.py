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
    assert verifier.verify(Path("a/instance1.txt"),
                           {"status": "SAT"}, None) == SolverStatus.SAT
    assert verifier.verify(Path("b/instance2.txt"),
                           {"status": "UNSAT"}, None) == SolverStatus.UNSAT
    assert verifier.verify(Path("c/instance3.txt"),
                           {"coolmetric": "15.1"}, None) == SolverStatus.WRONG
    assert verifier.verify(Path("c/instance3.txt"),
                           {"coolmetric": "15.0"}, None) == SolverStatus.SUCCESS
    assert verifier.verify(Path("d/idonotexist.txt"),
                           {"coolmetric": "123"}, None) == SolverStatus.UNKNOWN
    assert verifier.verify(Path("c/instance3.txt"),
                           {"idonotexist": "123"}, None) == SolverStatus.UNKNOWN
