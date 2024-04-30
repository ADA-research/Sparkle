"""Test functionalities related to the compute marginal contribution help module."""

from __future__ import annotations
from unittest import TestCase
from pathlib import Path

from CLI.support import compute_marginal_contribution_help as scmch
from sparkle.structures.feature_data_csv_help import SparkleFeatureDataCSV
import global_variables as sgh
from sparkle.platform import settings_help

from unittest.mock import patch
from unittest.mock import MagicMock, Mock

global settings
sgh.settings = settings_help.Settings()


class TestMarginalContribution(TestCase):
    """Tests function of Marginal Contribution help."""
    def test_read_marginal_contribution_csv(self: TestCase) -> None:
        """Test for method read_marginal_contribution_csv."""
        pth = Path("test_marginal_contribution.csv")
        if not pth.exists():
            Path.write_text(pth,
                            "Solvers/CSCCSat,2.068482775510204\nSolvers/MiniSAT,0.0")

        result = [("Solvers/CSCCSat", 2.068482775510204), ("Solvers/MiniSAT", 0.0)]
        output = scmch.read_marginal_contribution_csv(pth)
        assert result == output

        pth.unlink()

    def test_write_marginal_contribution_csv(self: TestCase) -> None:
        """Test for method write_marginal_contribution_csv."""
        pth = Path("test_marginal_contribution.csv")
        object = [("Solvers/CSCCSat", 2.068482775510204), ("Solvers/MiniSAT", 0.0)]
        result = "Solvers/CSCCSat,2.068482775510204\nSolvers/MiniSAT,0.0\n"

        scmch.write_marginal_contribution_csv(pth, object)

        output = ""
        with pth.open("r") as file:
            output = file.read()

        assert result == output
        pth.unlink()

    def test_compute_perfect_selector_marginal_contribution(self: TestCase) -> None:
        """Test for method compute_perfect_selector_marginal_contribution."""
        pth = Path("CLI/test/test_files/Performance_Data/"
                   "test_construct_sparkle_portfolio_selector.csv")

        # Settings have no impact yet on the unit test, this needs to be reconfigured
        """tmp_settings = ""
        source_settings = Path("tests/test_files/Settings/mc-settings.ini")
        with Path("Settings/sparkle_settings.ini").open("r+") as file_target:
            tmp_settings = file_target.read()
            file_target.truncate()
            with source_settings.open("r") as file_source:
                source_settings = file_source.read()
                file_target.write(source_settings)"""

        result = [("Solvers/CSCCSat", 1.7980089765503102), ("Solvers/MiniSAT", 0.0)]
        output = scmch.compute_perfect_selector_marginal_contribution(
            aggregation_function=sum,
            capvalue_list=None,
            minimise=True,
            performance_data_csv_path=pth,
            flag_recompute=True
        )

        """with Path("Settings/sparkle_settings.ini").open("w") as f:
            f.truncate()
            f.write(tmp_settings)"""

        self.assertListEqual(output, result)

    def test_get_list_predict_schedule(self: TestCase) -> None:
        """Test for method get_list_predict_schedule."""
        # Does not work on server.
        # TODO: Fix with mocker commands. There is a ticket for this.
        return
        pth = "CLI/test/test_files/Sparkle_Portfolio_Selector/"\
              "sparkle_portfolio_selector__@@SPARKLE@@__"
        file = "CLI/test/test_files/Feature_Data/"\
               "test_construct_sparkle_portfolio_selector.csv"
        featurecsv = SparkleFeatureDataCSV(file)
        prefix = "Instances/PTN/"
        instance_ids = [prefix + "Ptn-7824-b03.cnf", prefix + "Ptn-7824-b15.cnf",
                        prefix + "Ptn-7824-b05.cnf", prefix + "Ptn-7824-b13.cnf",
                        prefix + "Ptn-7824-b21.cnf", prefix + "Ptn-7824-b19.cnf",
                        prefix + "Ptn-7824-b17.cnf", prefix + "bce7824.cnf",
                        prefix + "Ptn-7824-b01.cnf", prefix + "Ptn-7824-b11.cnf",
                        prefix + "Ptn-7824-b09.cnf", prefix + "Ptn-7824-b07.cnf"]
        result = [("Solvers/CSCCSat", 61.0)]

        for instance in instance_ids:
            output = scmch.get_list_predict_schedule(pth, featurecsv, instance)
            assert output == result

    @patch("CLI.support.compute_marginal_contribution_help."
           "compute_actual_performance_for_instance")
    def test_compute_actual_selector_performance(
            self: TestCase, patch_perf_for_instance: MagicMock) -> None:
        """Test for method compute_actual_selector_performance."""
        pth = "CLI/test/test_files/Sparkle_Portfolio_Selector/"\
              "sparkle_portfolio_selector__@@SPARKLE@@__"
        perf_path = "CLI/test/test_files/Performance_Data/"\
                    "test_construct_sparkle_portfolio_selector.csv"
        feature_csv_path = "CLI/test/test_files/Feature_Data/"\
                           "test_construct_sparkle_portfolio_selector.csv"

        result = 526.805294
        patch_perf_for_instance.side_effect = [(61.0, False), (28.1747, True),
                                               (61.0, False), (9.98625, True),
                                               (0.107158, True), (61.0, False),
                                               (0.537186, True), (61.0, False),
                                               (61.0, False), (61.0, False),
                                               (61.0, False), (61.0, False)]

        output = scmch.compute_actual_selector_performance(pth,
                                                           perf_path,
                                                           feature_csv_path,
                                                           True,
                                                           sum,
                                                           None)

        assert output == result

    def test_compute_actual_performance_for_instance(self: TestCase) -> None:
        """Test for method compute_actual_performance_for_instance."""
        # TODO: This method is currently not touched by the .sh test. Think of a test.
        pass

    @patch("CLI.support.compute_marginal_contribution_help."
           "compute_actual_selector_performance")
    def test_compute_actual_selector_marginal_contribution(self: TestCase,
                                                           mock_actual_performance: Mock
                                                           ) -> None:
        """Test for method compute_actual_selector_marginal_contribution."""
        # Test does not work on Mac
        perf_path = "CLI/test/test_files/Performance_Data/"\
                    "test_construct_sparkle_portfolio_selector.csv"
        feature_csv_path = "CLI/test/test_files/Feature_Data/"\
                           "test_construct_sparkle_portfolio_selector.csv"
        mock_actual_performance.side_effect = [526.805294,
                                               526.805294,
                                               732.0]

        result = [("Solvers/CSCCSat", 1.3895076764357648), ("Solvers/MiniSAT", 0.0)]

        output = scmch.compute_actual_selector_marginal_contribution(
            aggregation_function=sum,
            capvalue_list=None,
            minimise=True,
            performance_data_csv_path=perf_path,
            feature_data_csv_path=feature_csv_path,
            flag_recompute=True
        )

        self.assertEqual(output, result)

    def test_print_rank_list(self: TestCase) -> None:
        """Test for method print_rank_list. Could be irrelevant."""
        # TODO: Write test
        pass

    def test_compute_actual(self: TestCase) -> None:
        """Test for method compute_actual. Could be irrelevant."""
        # TODO: Write test
        pass

    def test_compute_marginal_contribution(self: TestCase) -> None:
        """Test for method compute_marginal_contribution. Could be irrelevant."""
        # TODO: Write test
        pass
