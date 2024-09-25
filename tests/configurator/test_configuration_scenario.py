"""Test public methods of configuration scenario class."""

from __future__ import annotations

import shutil

from unittest import TestCase
from unittest.mock import patch
from unittest.mock import Mock
from pathlib import Path

from sparkle.configurator.implementations import SMAC2, SMAC2Scenario
from sparkle.solver import Solver
from sparkle.instance import instance_set
from sparkle.types.objective import PAR


class TestConfigurationScenario(TestCase):
    """Class bundling all tests regarding ConfigurationScenario."""
    def setUp(self: TestConfigurationScenario) -> None:
        """Setup executed before each test."""
        self.solver_path = Path("tests", "test_files", "Solvers", "Test-Solver")
        self.solver = Solver(self.solver_path)

        self.instance_set = instance_set(
            Path("tests/test_files/Instances/Test-Instance-Set"))
        self.run_number = 2

        self.parent_directory = Path("tests/test_files/test_configurator")
        self.parent_directory.mkdir(parents=True, exist_ok=True)

        self.instance_file_directory = Path("tests/test_files/test_configurator"
                                            "/scenarios/instances/Test-Instance-Set")
        self.instance_file_directory.mkdir(parents=True, exist_ok=True)
        self.wallclock_time = 600
        self.cutoff_time = 60
        self.cutoff_length = "max"
        self.sparkle_objective = PAR(10)
        self.configurator = SMAC2([self.sparkle_objective], Path(), Path())
        self.scenario = SMAC2Scenario(
            solver=self.solver,
            instance_set=self.instance_set,
            number_of_runs=self.run_number,
            wallclock_time=self.wallclock_time,
            cutoff_time=self.cutoff_time,
            cutoff_length=self.cutoff_length,
            sparkle_objectives=[self.sparkle_objective],
            use_features=False,
            configurator_target=Path(self.configurator.target_algorithm))

    def tearDown(self: TestConfigurationScenario) -> None:
        """Cleanup executed after each test."""
        shutil.rmtree(self.parent_directory, ignore_errors=True)

    def test_configuration_scenario_init(self: TestConfigurationScenario) -> None:
        """Test if all variables that are set in the init are correct."""
        self.assertEqual(self.scenario.solver, self.solver)
        self.assertEqual(self.scenario.instance_set.directory,
                         self.instance_set.directory)
        self.assertFalse(self.scenario.use_features)
        self.assertEqual(self.scenario.feature_data, None)
        self.assertEqual(self.scenario.name,
                         f"{self.solver.name}_{self.instance_set.name}")

    def test_configuration_scenario_check_scenario_directory(
        self: TestConfigurationScenario
    ) -> None:
        """Test if create_scenario() correctly creates the scenario directory."""
        self.scenario.create_scenario(self.parent_directory)

        self.assertTrue(self.scenario.directory.is_dir())
        self.assertEqual((self.scenario.directory
                          / "outdir_train_configuration").is_dir(),
                         True)
        self.assertTrue((self.scenario.directory / "tmp").is_dir())

    def test_configuration_scenario_check_result_directory(
        self: TestConfigurationScenario,
    ) -> None:
        """Test if create_scenario() creates the result directory."""
        self.scenario.create_scenario(self.parent_directory)

        self.assertTrue(self.scenario.result_directory.is_dir())

    def test_configuration_scenario_check_instance_directory(
        self: TestConfigurationScenario
    ) -> None:
        """Test if create_scenario() creates the instance directory."""
        self.scenario.create_scenario(self.parent_directory)
        self.assertTrue(self.scenario.instance_set.directory.is_dir())

    @patch("pathlib.Path.absolute")
    def test_configuration_scenario_check_scenario_file(
        self: TestConfigurationScenario,
        mock_abs_path: Mock
    ) -> None:
        """Test if create_scenario() correctly creates the scenario file."""
        inst_list_path = Path("tests/test_files/test_configurator/scenarios/instances/"
                              "Test-Instance-Set/Test-Instance-Set_train.txt")
        mock_abs_path.side_effect = [Path("tests/test_files/test_configurator"),
                                     Path("/configurator_dir/target_algorithm.py"),
                                     self.solver_path,
                                     inst_list_path,
                                     inst_list_path,
                                     Path(),
                                     Path()]
        self.scenario.create_scenario(self.parent_directory)

        reference_scenario_file = Path("tests", "test_files", "reference_files",
                                       "scenario_file.txt")

        # Use to show full diff of file
        self.maxDiff = None
        self.assertTrue(self.scenario.scenario_file_path.is_file())
        output = self.scenario.scenario_file_path.open().read()
        # Strip the output of the homedirs (Due to absolute paths)
        output = output.replace(str(Path.home()), "")
        self.assertEqual(output,
                         reference_scenario_file.open().read())
