"""Test public methods of solver class."""

import shutil

from unittest import TestCase, mock
from pathlib import Path

from sparkle_help.solver import Solver


class TestSolver(TestCase):
    """Class bundling all tests regarding Solver."""
    def setUp(self):
        """Setup executed before each test."""
        self.solver_path = Path("tests", "test_files", "test_solver")
        self.solver_path.mkdir(parents=True)

    def tearDown(self):
        """Cleanup executed after each test."""
        shutil.rmtree(self.solver_path)

    def test_init_variables(self):
        """Test if all variables that are set in the init are correct."""
        solver = Solver(Path("test/directory/solver_executable"))

        self.assertEqual(solver.directory, Path("test/directory/solver_executable"))
        self.assertEqual(solver.name, "solver_executable")

    def test_pcs_file_correct_name(self):
        """Test if get_pcs_file() returns the correct path if file exists."""
        (self.solver_path / "paramfile.pcs").open("a").close()

        solver = Solver(self.solver_path)

        self.assertEqual(solver.get_pcs_file(), self.solver_path / "paramfile.pcs")

    def test_pcs_file_none(self):
        """Test for SystemExit if get_pcs_file() is called, but file doesn't exist."""
        solver = Solver(self.solver_path)

        with self.assertRaises(SystemExit):
            solver.get_pcs_file()

    def test_pcs_file_multiple(self):
        """Test for SystemExit if get_pcs_file() is called, but multiple files exist."""
        (self.solver_path / "paramfile1.pcs").open("a").close()

        (self.solver_path / "paramfile2.pcs", "w").open("a").close()

        solver = Solver(self.solver_path)

        with self.assertRaises(SystemExit):
            solver.get_pcs_file()

    def test_is_deterministic_false(self):
        """Test if is_deterministic() correctly returns False."""
        file_string = "Solvers/test_solver 0 1"
        solver = Solver(self.solver_path)

        with mock.patch("builtins.open",
                        mock.mock_open(read_data=file_string)) as mock_file:
            self.assertEqual(solver.is_deterministic(), "0")
            mock_file.assert_called_with("Reference_Lists/sparkle_solver_list.txt", "r+")

    def test_is_deterministic_true(self):
        """Test if is_deterministic() correctly returns True."""
        file_string = "Solvers/test_solver 1 1"
        solver = Solver(self.solver_path)

        with mock.patch("builtins.open",
                        mock.mock_open(read_data=file_string)) as mock_file:
            self.assertEqual(solver.is_deterministic(), "1")
            mock_file.assert_called_with("Reference_Lists/sparkle_solver_list.txt", "r+")
