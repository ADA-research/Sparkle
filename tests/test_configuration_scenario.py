"""Test public methods of solver class."""

import shutil

from unittest import TestCase
from unittest.mock import patch
from pathlib import Path

from sparkle_help.configuration_scenario import ConfigurationScenario
from sparkle_help.solver import Solver


class TestConfigurationScenario(TestCase):
    """Class bundling all tests regarding ConfigurationScenario."""
    def setUp(self):
        """Setup executed before each test."""
        self.solver_path = Path("tests", "test_files", "Solvers", "Test-Solver")
        self.solver = Solver(self.solver_path)

        self.instance_directory = Path("tests/test_files/Instances/Test-Instance-Set")

        self.run_number = 2

        self.parent_directory = Path("tests/test_files/test_configurator")
        self.parent_directory.mkdir(parents=True, exist_ok=True)

        self.instance_file_directory = Path("tests/test_files/test_configurator"
                                            "/scenarios/instances/Test-Instance-Set")
        self.instance_file_directory.mkdir(parents=True, exist_ok=True)

        self.scenario = ConfigurationScenario(self.solver,
                                              self.instance_directory,
                                              self.run_number, False)

    def tearDown(self):
        """Cleanup executed after each test."""
        shutil.rmtree(self.parent_directory, ignore_errors=True)

    def test_configuration_scenario_init(self):
        """Test if all variables that are set in the init are correct."""
        self.assertEqual(self.scenario.solver, self.solver)
        self.assertEqual(self.scenario.instance_directory,
                         self.instance_directory)
        self.assertEqual(self.scenario.use_features, False)
        self.assertEqual(self.scenario.feature_data, None)
        self.assertEqual(self.scenario.name,
                         f"{self.solver.name}_{self.instance_directory.name}")

    @patch.object(Solver, "is_deterministic")
    def test_configuration_scenario_check_scenario_directory(self, mock_deterministic):
        """Test if create_scenario() correctly creates the scenario directory."""
        self.scenario.create_scenario(self.parent_directory)

        self.assertEqual(self.scenario.directory.is_dir(), True)
        self.assertEqual((self.scenario.directory
                          / "outdir_train_configuration").is_dir(),
                         True)
        self.assertEqual((self.scenario.directory / "tmp").is_dir(), True)

        self.assertEqual((self.scenario.directory
                          / self.solver.get_pcs_file().name).is_file(), True)

    @patch.object(Solver, "is_deterministic")
    def test_configuration_scenario_check_result_directory(self, mock_deterministic):
        """Test if create_scenario() creates the result directory."""
        self.scenario.create_scenario(self.parent_directory)

        self.assertEqual(self.scenario.result_directory.is_dir(), True)

    @patch.object(Solver, "is_deterministic")
    def test_configuration_scenario_check_run_folders(self, mock_deterministic):
        """Test if create_scenario() correctly creates the run directories."""
        self.scenario.create_scenario(self.parent_directory)

        for i in range(self.run_number):
            run_path = self.scenario.directory / str(i + 1)
            self.assertEqual(run_path.is_dir(), True)
            self.assertEqual((run_path / "PbO-CCSAT").is_file(), True)
            self.assertEqual((run_path / "tmp").is_dir(), True)

    @patch.object(Solver, "is_deterministic")
    def test_configuration_scenario_check_instance_directory(self, mock_deterministic):
        """Test if create_scenario() creates the instance directory."""
        self.scenario.create_scenario(self.parent_directory)

        self.assertTrue(self.scenario.instance_directory.is_dir())

    @patch.object(Solver, "is_deterministic")
    def test_configuration_scenario_check_scenario_file(self, mock_deterministic):
        """Test if create_scenario() correctly creates the scenario file."""
        mock_deterministic.return_value = "0"

        self.scenario.create_scenario(self.parent_directory)

        scenario_file_path = self.scenario.directory / self.scenario.scenario_file_name
        reference_scenario_file = Path("tests", "test_files", "reference_files",
                                       "scenario_file.txt")

        # Use to show full diff of file
        self.maxDiff = None

        self.assertEqual(scenario_file_path.is_file(), True)
        self.assertEqual(scenario_file_path.open().read(),
                         reference_scenario_file.open().read())
