"""Tests for all helper functions in sparkle_generate_report_for_configuration_help."""
from __future__ import annotations
from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import patch
from pathlib import Path

from sparkle.solver.ablation import AblationScenario
from sparkle.platform import generate_report_for_configuration as sgrch
from sparkle.configurator.implementations import SMAC2
from sparkle.types.objective import SparkleObjective, PAR
from sparkle.solver import Solver
from sparkle.instance import Instance_Set


class TestGenerateConfigurationReport(TestCase):
    """Tests function of generate_report_for_configuration."""

    @patch("pathlib.Path.mkdir")
    def setUp(self: TestGenerateConfigurationReport,
              mock_mkdir: Mock) -> None:
        """Setup executed before each test."""
        mock_mkdir.return_value = None
        self.test_objective_runtime = PAR(10)
        self.test_objective_quality = SparkleObjective("ACCURACY")
        self.configurator = SMAC2(Path(), Path())
        self.solver_path = Path("tests/test_files/Solvers/Test-Solver")
        self.solver = Solver(self.solver_path, raw_output_directory=Path(""))
        train_instance_set = Instance_Set(Path(
            "tests/test_files/Instances/Train-Instance-Set"))
        test_instance_set = Instance_Set(Path(
            "tests/test_files/Instances/Test-Instance-Set"))
        self.configurator_path = self.configurator.configurator_path
        self.configuration_scenario = self.configurator.scenario_class()(
            self.solver,
            train_instance_set,
            [self.test_objective_runtime],
            self.configurator.output_path)
        self.ablation_scenario = AblationScenario(
            self.configuration_scenario, test_instance_set, Path(""))

    @patch("sparkle.solver.ablation.AblationScenario.check_for_ablation")
    def test_get_ablation_bool_true(
            self: TestGenerateConfigurationReport,
            mock_check: Mock) -> None:
        """Test get_ablation_bool returns correct string if get_ablation_bool is True."""
        mock_check.return_value = True
        ablation_bool = sgrch.get_ablation_bool(self.ablation_scenario)
        mock_check.assert_called_once()
        assert ablation_bool == r"\ablationtrue"

    @patch("sparkle.solver.ablation.AblationScenario.check_for_ablation")
    def test_get_ablation_bool_false(
            self: TestGenerateConfigurationReport,
            mock_check: Mock) -> None:
        """Test get_ablation_bool returns if get_ablation_bool is False."""
        mock_check.return_value = False
        ablation_bool = sgrch.get_ablation_bool(self.ablation_scenario)
        mock_check.assert_called_once()
        assert ablation_bool == r"\ablationfalse"

    @patch("sparkle.solver.ablation.AblationScenario.read_ablation_table")
    def test_get_ablation_table(
            self: TestGenerateConfigurationReport,
            mock_table: Mock) -> None:
        """Test get_ablation_table calls and transforms its string."""
        sah_ablation_table = (
            [["Round", "Flipped parameter", "Source value", "Target value",
              "Validation result"],
             ["0", "-source-", "N/A", "N/A", "76.53275"],
             ["1", "sel_var_div", "3", "6", "68.41392"],
             ["2", "-target-", "N/A", "N/A", "92.06944"]])
        mock_table.return_value = sah_ablation_table

        table_string = sgrch.get_ablation_table(self.ablation_scenario)

        mock_table.assert_called_once()
        assert table_string == (r"\begin{tabular}{rp{0.25\linewidth}rrr}"
                                r"\textbf{Round} & \textbf{Flipped parameter} & "
                                r"\textbf{Source value} & \textbf{Target value} & "
                                r"\textbf{Validation result} \\ \hline "
                                r"0 & -source- & N/A & N/A & 76.53275 \\ "
                                r"1 & sel_var_div & 3 & 6 & 68.41392 \\ "
                                r"2 & -target- & N/A & N/A & 92.06944 \\ "
                                r"\end{tabular}")
