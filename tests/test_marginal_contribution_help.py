"""Test functionalities related to the compute marginal contribution help module."""

from __future__ import annotations
from unittest import TestCase
from pathlib import Path

from sparkle.CLI.support import compute_marginal_contribution_help as scmch
from sparkle.structures import FeatureDataFrame, PerformanceDataFrame

from unittest.mock import patch
from unittest.mock import MagicMock


class TestMarginalContribution(TestCase):
    """Tests function of Marginal Contribution help."""

    @patch("sparkle.CLI.support.compute_marginal_contribution_help."
           "compute_actual_performance_for_instance")
    @patch("sparkle.structures.PerformanceDataFrame.save_csv")
    @patch("sparkle.solver.selector.Selector.run")
    def test_compute_actual_selector_performance(
            self: TestCase,
            patch_selector_run: MagicMock,
            patch_save: MagicMock,
            patch_perf_for_instance: MagicMock) -> None:
        """Test for method compute_actual_selector_performance."""
        pth = Path("tests/CLI/test_files/Sparkle_Portfolio_Selector/"
                   "sparkle_portfolio_selector")
        perf_path = Path("tests/CLI/test_files/Performance_Data/"
                         "test_construct_sparkle_portfolio_selector.csv")
        feature_csv_path = Path("tests/CLI/test_files/Feature_Data/"
                                "test_construct_sparkle_portfolio_selector.csv")

        result = 526.805294
        patch_selector_run.return_value = None
        patch_save.return_value = None
        patch_perf_for_instance.side_effect = [61.0, 28.1747, 61.0, 9.98625,
                                               0.107158, 61.0, 0.537186, 61.0,
                                               61.0, 61.0, 61.0, 61.0]
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

    def test_compute_actual_selector_marginal_contribution(self: TestCase
                                                           ) -> None:
        """Test for method compute_actual_selector_marginal_contribution."""
        # TODO: Write test
        pass

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
