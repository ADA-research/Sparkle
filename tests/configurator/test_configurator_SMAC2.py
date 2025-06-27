"""Test methods of SMAC2 configurator."""
from __future__ import annotations

import shutil
from unittest.mock import Mock, ANY
from unittest import TestCase
from unittest.mock import patch
from pathlib import Path

import runrunner as rrr

from sparkle.solver import Solver
from sparkle.instance import Instance_Set
from sparkle.structures import PerformanceDataFrame
from sparkle.configurator.implementations import SMAC2, SMAC2Scenario
from sparkle.types.objective import PAR


class TestConfiguratorSMAC2(TestCase):
    """Class bundling all tests regarding SMAC2 Configurator."""

    def __init__(self: TestConfiguratorSMAC2, *args: any, **kwargs: any) -> None:
        """Test that Configurator initialization calls create_scenario() correctly."""
        super(TestConfiguratorSMAC2, self).__init__(*args, **kwargs)
        sparkle_objective = PAR(10)
        self.test_files = Path("tests", "test_files")
        self.base_dir = self.test_files / "tmp"
        output = Path("Output")
        self.smac2_conf = SMAC2(self.base_dir, output)
        self.train_set = Instance_Set(self.test_files / "Instances/Train-Instance-Set")
        self.solver = Solver(self.test_files / "Solvers/Test-Solver")
        self.conf_scenario = SMAC2Scenario(
            self.solver, self.train_set, [sparkle_objective], 2, self.base_dir,
            solver_calls=25,
            wallclock_time=80,
            solver_cutoff_time=60,
            target_cutoff_length=10,
        )
        assert self.smac2_conf.multiobjective is False

    @patch("shutil.which")
    @patch("runrunner.add_to_queue")
    def test_smac2_configure(self: TestConfiguratorSMAC2,
                             mock_add_to_queue: Mock,
                             mock_which: Mock) -> None:
        """Testing configure call of SMAC2."""
        # Testing without validation afterwards
        # Mock shlex to avoid Sparkle throwing an exception because Java is not loaded
        mock_which.return_value("Java")
        mock_add_to_queue.return_value = None

        # We currently cannot test these strings as they are using absolute paths
        expected_cmds = ANY
        expected_outputs = ANY

        # Make a copy so we don't modify the original
        data_target = PerformanceDataFrame(
            Path("tests/test_files/performance/example_empty_runs.csv"))
        data_target = data_target.clone(Path("tmp-pdf.csv"))

        runs = self.smac2_conf.configure(self.conf_scenario,
                                         data_target=data_target,
                                         validate_after=False,
                                         base_dir=self.base_dir)
        mock_add_to_queue.assert_called_once_with(
            runner=rrr.Runner.SLURM,
            base_dir=self.base_dir,
            cmd=expected_cmds,
            name=f"{SMAC2.__name__}: {self.conf_scenario.solver.name} on "
                 f"{self.conf_scenario.instance_set.name}",
            output_path=expected_outputs,
            parallel_jobs=None,
            sbatch_options=[],
            prepend=None,
        )
        assert runs == [None]
        # TODO: Test with validation_after=True
        # TODO: Make this all happen in a tmp dir so we don't have to unlink
        data_target.csv_filepath.unlink()

    def test_smac2_organise_output(self: TestConfiguratorSMAC2) -> None:
        """Testing SMAC2 ability to retrieve output from raw file."""
        raw_out = self.test_files / "Configuration" / "results" /\
            "PbO-CCSAT-Generic_PTN_seed_3_smac.txt"
        # By not specifiying an output file, the result is returned to us
        assert SMAC2.organise_output(raw_out, None, None, 1) == {
            "gamma_hscore2": "351", "init_solution": "1", "p_swt": "0.20423712003341465",
            "perform_aspiration": "1", "perform_clause_weight": "1",
            "perform_double_cc": "0", "perform_first_div": "0", "perform_pac": "1",
            "prob_pac": "0.005730374136488115", "q_swt": "0.6807207179674418",
            "sel_clause_div": "1", "sel_clause_weight_scheme": "1",
            "sel_var_break_tie_greedy": "4", "sel_var_div": "2", "threshold_swt": "32",
            "configuration_id": 1}

    def test_smac2_get_status_from_logs(self: TestConfiguratorSMAC2) -> None:
        """Testing status retrievel from logs."""
        # TODO: Write test
        return


class TestConfigurationScenarioSMAC2(TestCase):
    """Class bundling all tests regarding ConfigurationScenario."""
    def setUp(self: TestConfigurationScenarioSMAC2) -> None:
        """Setup executed before each test."""
        self.solver_path = Path("tests", "test_files", "Solvers", "Test-Solver")
        self.solver = Solver(self.solver_path)

        self.instance_set = Instance_Set(
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
        self.configurator = SMAC2(Path(), Path())
        self.scenario = SMAC2Scenario(
            solver=self.solver,
            instance_set=self.instance_set,
            sparkle_objectives=[self.sparkle_objective],
            number_of_runs=self.run_number,
            parent_directory=self.parent_directory,
            wallclock_time=self.wallclock_time,
            solver_cutoff_time=self.cutoff_time,
            target_cutoff_length=self.cutoff_length)

    def tearDown(self: TestConfigurationScenarioSMAC2) -> None:
        """Cleanup executed after each test."""
        shutil.rmtree(self.parent_directory, ignore_errors=True)

    def test_configuration_scenario_init(self: TestConfigurationScenarioSMAC2) -> None:
        """Test if all variables that are set in the init are correct."""
        self.assertEqual(self.scenario.solver, self.solver)
        self.assertEqual(self.scenario.instance_set.directory,
                         self.instance_set.directory)
        self.assertIsNone(self.scenario.feature_data)
        self.assertEqual(self.scenario.name,
                         f"{self.solver.name}_{self.instance_set.name}")

    def test_smac2_scenario_check_scenario_directory(
        self: TestConfigurationScenarioSMAC2
    ) -> None:
        """Test if create_scenario() correctly creates the scenario directories."""
        self.scenario.create_scenario()

        self.assertTrue(self.scenario.directory.is_dir())
        self.assertEqual((self.scenario.directory
                          / "outdir_train_configuration").is_dir(),
                         True)
        self.assertTrue((self.scenario.directory / "tmp").is_dir())
        self.assertTrue(self.scenario.results_directory.is_dir())

    def test_from_file(self: TestConfigurationScenarioSMAC2) -> None:
        """Test if ConfigurationScenario can be created from file."""
        file = Path("tests/test_files/Configuration/test_smac2_scenario.txt")
        scenario = SMAC2Scenario.from_file(file)
        self.assertEqual(scenario.solver.name, "PbO-CCSAT-Generic")
        self.assertEqual(scenario.instance_set.name, "PTN")
        self.assertEqual(scenario.sparkle_objectives[0].name, "PAR10")
        self.assertEqual(scenario.wallclock_time, 600)
        self.assertEqual(scenario.solver_cutoff_time, 60)
