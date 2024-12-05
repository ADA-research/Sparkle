"""Test public methods of solver class."""

from __future__ import annotations

import shutil

from unittest import TestCase
from pathlib import Path
from sparkle.solver import Solver, verifiers


class TestSolver(TestCase):
    """Class bundling all tests regarding Solver."""
    def setUp(self: TestSolver) -> None:
        """Setup executed before each test."""
        self.solver_path = Path("tests", "test_files", "test_solver")
        self.solver_path.mkdir(parents=True)

    def tearDown(self: TestSolver) -> None:
        """Cleanup executed after each test."""
        shutil.rmtree(self.solver_path)

    def test_init_variables(self: TestSolver) -> None:
        """Test if all variables that are set in the init are correct."""
        solver = Solver(Path("test/directory/solver_executable"),
                        raw_output_directory=Path(""))

        self.assertEqual(solver.directory, Path("test/directory/solver_executable"))
        self.assertEqual(solver.name, "solver_executable")

    def test_pcs_file_correct_name(self: TestSolver) -> None:
        """Test if get_pcs_file() returns the correct path if file exists."""
        (self.solver_path / "paramfile.pcs").open("a").close()

        solver = Solver(self.solver_path)

        self.assertEqual(solver.get_pcs_file(), self.solver_path / "paramfile.pcs")

    def test_pcs_file_none(self: TestSolver) -> None:
        """Test for SystemExit if get_pcs_file() is called, but file doesn't exist."""
        solver = Solver(self.solver_path)
        assert solver.get_pcs_file() is None

    def test_pcs_file_multiple(self: TestSolver) -> None:
        """Test for SystemExit if get_pcs_file() is called, but multiple files exist."""
        (self.solver_path / "paramfile.pcs").open("a").close()
        (self.solver_path / "paramfile_PORTED.pcs").open("a").close()

        solver = Solver(self.solver_path)
        assert solver.get_pcs_file() == self.solver_path / "paramfile.pcs"

    def test_is_deterministic(self: TestSolver) -> None:
        """Test if deterministic correctly returns value."""
        solver = Solver(self.solver_path)
        self.assertEqual(solver.deterministic, False)

        solver = Solver(self.solver_path, deterministic=True)
        self.assertEqual(solver.deterministic, True)

    def test_verifier(self: TestSolver) -> None:
        """Test if verifier correctly returns value."""
        # No verifier
        solver = Solver(self.solver_path)
        self.assertEqual(solver.verifier, None)

        # Verifier passed by constructor
        solver = Solver(self.solver_path, verifier=verifiers.SATVerifier)
        self.assertEqual(solver.verifier, verifiers.SATVerifier)

        # None in meta file
        meta_file = self.solver_path / Solver.meta_data
        meta_data = {"deterministic": False,
                     "verifier": None}
        meta_file.open("w").write(str(meta_data))
        solver = Solver(self.solver_path)
        self.assertEqual(solver.verifier, None)

        # Verifier SAT in meta file
        meta_data = {"deterministic": False,
                     "verifier": "SATVerifier"}
        meta_file.open("w").write(str(meta_data))
        solver = Solver(self.solver_path)
        self.assertEqual(solver.verifier, verifiers.SATVerifier)

    def test_run(self: TestSolver) -> None:
        """Test if run correctly adds to RunRunner queue."""
        # TODO: write test
        pass

    def test_run_performance_dataframe(self: TestSolver) -> None:
        """Test if run_performance_dataframe correctly adds to RunRunner queue."""
        # TODO: write test
        pass
