"""Test public methods of solver class."""

from __future__ import annotations

import shutil

from unittest import TestCase
from pathlib import Path
from sparkle.solver import Solver


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
        (self.solver_path / "paramfile1.pcs").open("a").close()
        (self.solver_path / "paramfile2.pcs").open("a").close()

        solver = Solver(self.solver_path)
        assert solver.get_pcs_file() is None

    def test_is_deterministic_false(self: TestSolver) -> None:
        """Test if is_deterministic() correctly returns False."""
        solver = Solver(self.solver_path)
        self.assertEqual(solver.deterministic, False)

    def test_is_deterministic_true(self: TestSolver) -> None:
        """Test if is_deterministic() correctly returns True."""
        solver = Solver(self.solver_path, deterministic=True)
        self.assertEqual(solver.deterministic, True)
