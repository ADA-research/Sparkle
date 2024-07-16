"""Test functionalities related to the compute marginal contribution help module."""

from __future__ import annotations
from unittest import TestCase
from pathlib import Path

from CLI.support import compute_marginal_contribution_help as scmch
from sparkle.structures import FeatureDataFrame, PerformanceDataFrame
import global_variables as gv
from sparkle.platform.settings_objects import Settings

from unittest.mock import patch
from unittest.mock import MagicMock, Mock

global settings
gv.settings = Settings()


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
        performance_data = PerformanceDataFrame(
            Path("CLI/test/test_files/Performance_Data/"
                 "test_construct_sparkle_portfolio_selector.csv"))
        result = [("Solvers/CSCCSat", 1.7980089765503102, 33117.589),
                  ("Solvers/MiniSAT", 0.0, 18419.034293999997)]
        output = scmch.compute_perfect_selector_marginal_contribution(
            aggregation_function=sum,
            minimise=True,
            performance_data=performance_data
        )
        self.assertListEqual(output, result)

    @patch("CLI.support.compute_marginal_contribution_help."
           "compute_actual_performance_for_instance")
    def test_compute_actual_selector_performance(
            self: TestCase, patch_perf_for_instance: MagicMock) -> None:
        """Test for method compute_actual_selector_performance."""
        pth = "CLI/test/test_files/Sparkle_Portfolio_Selector/"\
              "sparkle_portfolio_selector"
        perf_path = Path("CLI/test/test_files/Performance_Data/"
                         "test_construct_sparkle_portfolio_selector.csv")
        feature_csv_path = Path("CLI/test/test_files/Feature_Data/"
                                "test_construct_sparkle_portfolio_selector.csv")

        result = 526.805294
        patch_perf_for_instance.side_effect = [(61.0, False), (28.1747, True),
                                               (61.0, False), (9.98625, True),
                                               (0.107158, True), (61.0, False),
                                               (0.537186, True), (61.0, False),
                                               (61.0, False), (61.0, False),
                                               (61.0, False), (61.0, False)]
        performance_df = PerformanceDataFrame(perf_path)
        feature_df = FeatureDataFrame(feature_csv_path)
        output = scmch.compute_actual_selector_performance(pth,
                                                           performance_df,
                                                           feature_df,
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
        performance_data = PerformanceDataFrame(
            Path("CLI/test/test_files/Performance_Data/"
                 "test_construct_sparkle_portfolio_selector.csv"))
        feature_data = FeatureDataFrame(
            Path("CLI/test/test_files/Feature_Data/"
                 "test_construct_sparkle_portfolio_selector.csv"))
        mock_actual_performance.side_effect = [526.805294,
                                               526.805294,
                                               732.0]

        result = [("Solvers/CSCCSat", 1.3895076764357648), ("Solvers/MiniSAT", 0.0)]

        output = scmch.compute_actual_selector_marginal_contribution(
            aggregation_function=sum,
            minimise=True,
            performance_data=performance_data,
            feature_data=feature_data,
            flag_recompute=True,
            selector_timeout=60
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
