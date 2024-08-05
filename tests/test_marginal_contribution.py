"""Test functionalities related to the compute marginal contribution help module."""

from __future__ import annotations
from unittest import TestCase
from pathlib import Path
from statistics import mean

from sparkle.CLI import compute_marginal_contribution as cmc
from sparkle.structures import FeatureDataFrame, PerformanceDataFrame

from unittest.mock import patch
from unittest.mock import MagicMock


class TestMarginalContribution(TestCase):
    """Tests function of Marginal Contribution help."""

    @patch("sparkle.structures.PerformanceDataFrame.save_csv")
    @patch("sparkle.solver.selector.Selector.run")
    def test_compute_actual_selector_performance(
            self: TestCase,
            patch_selector_run: MagicMock,
            patch_save: MagicMock) -> None:
        """Test for method compute_actual_selector_performance."""
        pth = Path("tests/CLI/test_files/Sparkle_Portfolio_Selector/"
                   "sparkle_portfolio_selector")
        perf_path = Path("tests/CLI/test_files/Performance_Data/"
                         "test_construct_sparkle_portfolio_selector.csv")
        feature_csv_path = Path("tests/CLI/test_files/Feature_Data/"
                                "test_construct_sparkle_portfolio_selector.csv")

        result = 1534.9195245
        patch_selector_run.side_effect = [[("Solvers/CSCCSat", 61.0)]] * 12
        patch_save.return_value = None
        performance_df = PerformanceDataFrame(perf_path)
        feature_df = FeatureDataFrame(feature_csv_path)
        output = cmc.compute_selector_performance(pth,
                                                  performance_df,
                                                  feature_df,
                                                  True,
                                                  mean,
                                                  None)

        assert output == result

    def test_compute_actual_selector_marginal_contribution(self: TestCase
                                                           ) -> None:
        """Test for method compute_actual_selector_marginal_contribution."""
        # TODO: Write test
        pass

    def test_compute_marginal_contribution(self: TestCase) -> None:
        """Test for method compute_marginal_contribution. Could be irrelevant."""
        # TODO: Write test
        pass
