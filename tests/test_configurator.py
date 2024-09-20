"""Test public methods of configurator class."""

from __future__ import annotations

import pytest
from unittest.mock import Mock, ANY
import csv
from pathlib import Path

import runrunner as rrr

from sparkle.platform import CommandName
from sparkle.solver import Solver
from sparkle.instance import instance_set
from sparkle.configurator.configurator import Configurator
from sparkle.configurator.implementations import SMAC2, SMAC2Scenario
from sparkle.types.objective import PAR


sparkle_objective = PAR(10)
objectives = [sparkle_objective]
test_files = Path("tests", "test_files")
base_dir = test_files / "tmp"
output = Path("Output")
smac2_conf = SMAC2(objectives, base_dir, output)
train_set = instance_set(test_files / "Instances/Train-Instance-Set")
solver = Solver(test_files / "Solvers/Test-Solver")
conf_scenario = SMAC2Scenario(
    solver, train_set,
    number_of_runs=2,
    solver_calls=25,
    wallclock_time=80,
    cutoff_time=60,
    cutoff_length=10,
    sparkle_objectives=[sparkle_objective],
    use_features=False,
    configurator_target=(
        SMAC2.configurator_path / SMAC2.target_algorithm))


class TestConfigurator():
    """Class bundling all tests regarding Configurator."""

    def test_init(self: TestConfigurator) -> None:
        """Test that Configurator initialization calls create_scenario() correctly."""
        exec_path = Path("dir/exec.exe")
        configurator = Configurator(
            output_path=Path(),
            validator=None,
            executable_path=exec_path,
            configurator_target=None,
            base_dir=Path(),
            tmp_path=Path(),
            objectives=objectives)

        assert configurator.executable_path == exec_path

    def test_smac2_init(self: TestConfigurator) -> None:
        """Testing SMAC2 configurator initialisation."""
        conf = SMAC2(objectives, base_dir, output)
        assert conf.base_dir == base_dir
        assert conf.output_path == output / SMAC2.__name__
        assert conf.objectives == objectives
        assert conf.multiobjective is False
        assert conf.tmp_path == output / SMAC2.__name__ / "tmp"

    def test_smac2_configure(self: TestConfigurator,
                             monkeypatch: pytest.fixture) -> None:
        """Testing configure call of SMAC2."""
        # Testing without validation afterwards
        mock_runrunner_conf = Mock(return_value=None)
        monkeypatch.setattr("runrunner.add_to_queue", mock_runrunner_conf)

        # We currently cannot test these strings as they are using absolute paths
        expected_cmds = ANY
        expected_outputs = ANY

        runs = smac2_conf.configure(conf_scenario,
                                    validate_after=False,
                                    base_dir=base_dir)
        mock_runrunner_conf.assert_called_once_with(runner=rrr.Runner.SLURM,
                                                    base_dir=base_dir,
                                                    cmd=expected_cmds,
                                                    name=CommandName.CONFIGURE_SOLVER,
                                                    output_path=expected_outputs,
                                                    parallel_jobs=2,
                                                    sbatch_options=[],
                                                    srun_options=["-N1", "-n1"]
                                                    )
        assert runs == [None]

        # TODO: Test with validation_after=True

    def test_smac2_get_optimal_configuration(self: TestConfigurator,
                                             mocker: Mock) -> None:
        """Tests the retrieval of the optimal configuration from SMAC2 run."""
        # Mock the validator call
        csv_file = Path("tests/test_files/Validator/validation_configuration.csv")
        csv_lines = [line for line in csv.reader(csv_file.open("r"))]
        mocker.patch("sparkle.solver.validator.Validator.get_validation_results",
                     return_value=csv_lines)
        opt_conf = smac2_conf.get_optimal_configuration(
            solver, train_set, PAR(10))

        expect_conf = (11.206219166666667, "-gamma_hscore2 '351' -init_solution '1' "
                       "-p_swt '0.20423712003341465' -perform_aspiration '1' "
                       "-perform_clause_weight '1' -perform_double_cc '0' "
                       "-perform_first_div '0' -perform_pac '1' -prob_pac "
                       "'0.005730374136488115' -q_swt '0.6807207179674418' "
                       "-sel_clause_div '1' -sel_clause_weight_scheme '1' "
                       "-sel_var_break_tie_greedy '4' -sel_var_div '2' -threshold_swt "
                       "'32'")
        assert opt_conf == expect_conf

    def test_smac2_organise_output(self: TestConfigurator) -> None:
        """Testing SMAC2 ability to retrieve output from raw file."""
        raw_out = test_files / "Configuration/PbO-CCSAT-Generic_PTN_seed_3_smac.txt"
        # By not specifiying an output file, the result is returned to us
        expected = (
            "-gamma_hscore2 '351' -init_solution '1' -p_swt '0.20423712003341465'"
            " -perform_aspiration '1' -perform_clause_weight '1' "
            "-perform_double_cc '0' -perform_first_div '0' -perform_pac '1' "
            "-prob_pac '0.005730374136488115' -q_swt '0.6807207179674418' "
            "-sel_clause_div '1' -sel_clause_weight_scheme '1' "
            "-sel_var_break_tie_greedy '4' -sel_var_div '2' -threshold_swt '32'")
        assert SMAC2.organise_output(raw_out) == expected

    def test_smac2_get_status_from_logs(self: TestConfigurator) -> None:
        """Testing status retrievel from logs."""
        # TODO: Write test
        return
