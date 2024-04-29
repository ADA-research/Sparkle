"""Test public methods of configuration scenario class."""

from __future__ import annotations

import shutil

from unittest import TestCase
from unittest.mock import patch
from unittest.mock import Mock
from pathlib import Path

from sparkle.configurator.configuration_scenario import ConfigurationScenario
from sparkle.solver.solver import Solver
from sparkle.platform import settings_help
import global_variables as sgh

global settings
sgh.settings = settings_help.Settings()


class TestConfigurationScenario(TestCase):
    """Class bundling all tests regarding ConfigurationScenario."""
    def setUp(self: TestConfigurationScenario) -> None:
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
        self.time_budget = 600
        self.cutoff_time = 60
        self.cutoff_length = "max"
        self.sparkle_objective =\
            sgh.settings.get_general_sparkle_objectives()[0]

        self.scenario = ConfigurationScenario(
            solver=self.solver,
            instance_directory=self.instance_directory,
            number_of_runs=self.run_number,
            time_budget=self.time_budget,
            cutoff_time=self.cutoff_time,
            cutoff_length=self.cutoff_length,
            sparkle_objective=self.sparkle_objective,
            use_features=False,
            configurator_target=Path(sgh.smac_target_algorithm))

    def tearDown(self: TestConfigurationScenario) -> None:
        """Cleanup executed after each test."""
        shutil.rmtree(self.parent_directory, ignore_errors=True)

    def test_configuration_scenario_init(self: TestConfigurationScenario) -> None:
        """Test if all variables that are set in the init are correct."""
        self.assertEqual(self.scenario.solver, self.solver)
        self.assertEqual(self.scenario.instance_directory,
                         self.instance_directory)
        self.assertFalse(self.scenario.use_features)
        self.assertEqual(self.scenario.feature_data, None)
        self.assertEqual(self.scenario.name,
                         f"{self.solver.name}_{self.instance_directory.name}")

    @patch.object(Solver, "is_deterministic")
    def test_configuration_scenario_check_scenario_directory(
        self: TestConfigurationScenario,
        mock_deterministic: Mock
    ) -> None:
        """Test if create_scenario() correctly creates the scenario directory."""
        self.scenario.create_scenario(self.parent_directory)

        self.assertTrue(self.scenario.directory.is_dir())
        self.assertEqual((self.scenario.directory
                          / "outdir_train_configuration").is_dir(),
                         True)
        self.assertTrue((self.scenario.directory / "tmp").is_dir())

        self.assertTrue((self.scenario.directory
                         / self.solver.get_pcs_file().name).is_file())

    @patch.object(Solver, "is_deterministic")
    def test_configuration_scenario_check_result_directory(
        self: TestConfigurationScenario,
        mock_deterministic: Mock
    ) -> None:
        """Test if create_scenario() creates the result directory."""
        self.scenario.create_scenario(self.parent_directory)

        self.assertTrue(self.scenario.result_directory.is_dir())

    @patch.object(Solver, "is_deterministic")
    def test_configuration_scenario_check_instance_directory(
        self: TestConfigurationScenario,
        mock_deterministic: Mock
    ) -> None:
        """Test if create_scenario() creates the instance directory."""
        self.scenario.create_scenario(self.parent_directory)

        self.assertTrue(self.scenario.instance_directory.is_dir())

    @patch.object(Solver, "is_deterministic")
    @patch("pathlib.Path.absolute")
    def test_configuration_scenario_check_scenario_file(
        self: TestConfigurationScenario,
        mock_abs: Mock,
        mock_deterministic: Mock
    ) -> None:
        """Test if create_scenario() correctly creates the scenario file."""
        inst_list_path = Path("tests/test_files/test_configurator/scenarios/instances/"
                              "Test-Instance-Set/Test-Instance-Set_train.txt")
        mock_abs.side_effect = [Path("tests/test_files/test_configurator"),
                                Path("/configurator_dir/target_algorithm.py"),
                                self.solver_path,
                                inst_list_path,
                                inst_list_path]
        mock_deterministic.return_value = "0"
        self.scenario.create_scenario(self.parent_directory)

        scenario_file_path = self.scenario.directory / self.scenario.scenario_file_name
        reference_scenario_file = Path("tests", "test_files", "reference_files",
                                       "scenario_file.txt")

        # Use to show full diff of file
        self.maxDiff = None

        self.assertTrue(scenario_file_path.is_file())
        self.assertEqual(scenario_file_path.open().read(),
                         reference_scenario_file.open().read())
