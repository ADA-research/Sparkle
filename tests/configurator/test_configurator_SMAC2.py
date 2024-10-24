"""Test public methods of SMAC2 configurator."""
from __future__ import annotations

import shutil
from unittest.mock import Mock, ANY
from unittest import TestCase
from unittest.mock import patch
import csv
from pathlib import Path

import runrunner as rrr

from sparkle.solver import Solver
from sparkle.instance import Instance_Set
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
            self.solver, self.train_set, self.base_dir,
            number_of_runs=2,
            solver_calls=25,
            wallclock_time=80,
            cutoff_time=60,
            target_cutoff_length=10,
            sparkle_objectives=[sparkle_objective],
        )
        assert self.smac2_conf.base_dir == self.base_dir
        assert self.smac2_conf.output_path == output / SMAC2.__name__
        assert self.smac2_conf.multiobjective is False
        assert self.smac2_conf.tmp_path == output / SMAC2.__name__ / "tmp"

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

        runs = self.smac2_conf.configure(self.conf_scenario,
                                         validate_after=False,
                                         base_dir=self.base_dir)
        mock_add_to_queue.assert_called_once_with(
            runner=rrr.Runner.SLURM,
            base_dir=self.base_dir,
            cmd=expected_cmds,
            name=f"{SMAC2.__name__}: {self.conf_scenario.solver.name} on "
                 f"{self.conf_scenario.instance_set.name}",
            path=ANY,
            output_path=expected_outputs,
            parallel_jobs=2,
            sbatch_options=[],
            srun_options=["-N1", "-n1"]
        )
        assert runs == [None]

        # TODO: Test with validation_after=True

    @patch("sparkle.solver.validator.Validator.get_validation_results")
    def test_smac2_get_optimal_configuration(self: TestConfiguratorSMAC2,
                                             validation_mock: Mock) -> None:
        """Tests the retrieval of the optimal configuration from SMAC2 run."""
        # Mock the validator call
        csv_file = Path("tests/test_files/Validator/validation_configuration.csv")
        csv_lines = [line for line in csv.reader(csv_file.open("r"))]
        validation_mock.return_value = csv_lines
        configuration_scenario = SMAC2Scenario(
            self.solver, self.train_set, PAR(10), csv_file.parent
        )
        opt_conf = self.smac2_conf.get_optimal_configuration(
            configuration_scenario)

        expect_conf = (11.206219166666667, "-gamma_hscore2 '351' -init_solution '1' "
                       "-p_swt '0.20423712003341465' -perform_aspiration '1' "
                       "-perform_clause_weight '1' -perform_double_cc '0' "
                       "-perform_first_div '0' -perform_pac '1' -prob_pac "
                       "'0.005730374136488115' -q_swt '0.6807207179674418' "
                       "-sel_clause_div '1' -sel_clause_weight_scheme '1' "
                       "-sel_var_break_tie_greedy '4' -sel_var_div '2' -threshold_swt "
                       "'32'")
        assert opt_conf == expect_conf

    def test_smac2_organise_output(self: TestConfiguratorSMAC2) -> None:
        """Testing SMAC2 ability to retrieve output from raw file."""
        raw_out = self.test_files / "Configuration/PbO-CCSAT-Generic_PTN_seed_3_smac.txt"
        # By not specifiying an output file, the result is returned to us
        expected = (
            "-gamma_hscore2 '351' -init_solution '1' -p_swt '0.20423712003341465'"
            " -perform_aspiration '1' -perform_clause_weight '1' "
            "-perform_double_cc '0' -perform_first_div '0' -perform_pac '1' "
            "-prob_pac '0.005730374136488115' -q_swt '0.6807207179674418' "
            "-sel_clause_div '1' -sel_clause_weight_scheme '1' "
            "-sel_var_break_tie_greedy '4' -sel_var_div '2' -threshold_swt '32'")
        assert SMAC2.organise_output(raw_out) == expected

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
            parent_directory=self.parent_directory,
            number_of_runs=self.run_number,
            wallclock_time=self.wallclock_time,
            cutoff_time=self.cutoff_time,
            target_cutoff_length=self.cutoff_length,
            sparkle_objectives=[self.sparkle_objective])

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
        self.assertTrue(self.scenario.result_directory.is_dir())

    def test_configuration_scenario_check_result_directory(
        self: TestConfigurationScenarioSMAC2,
    ) -> None:
        """Test if create_scenario() creates the result directory."""
        self.scenario.create_scenario()

    @patch("pathlib.Path.absolute")
    def test_configuration_scenario_check_scenario_file(
        self: TestConfigurationScenarioSMAC2,
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
        self.scenario.create_scenario()

        reference_scenario_file = Path("tests", "test_files", "reference_files",
                                       "scenario_file.txt")

        # Use to show full diff of file
        self.maxDiff = None
        self.assertTrue(self.scenario.scenario_file_path.is_file())
        output = self.scenario.scenario_file_path.open().read()
        # Strip the output of the homedirs (Due to absolute paths)
        output = output.replace(str(Path.home()), "")
        self.assertEqual(output, reference_scenario_file.open().read())
