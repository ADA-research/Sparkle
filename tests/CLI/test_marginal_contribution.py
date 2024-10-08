"""Test functionalities related to the compute marginal contribution help module."""
from __future__ import annotations
import pytest
from unittest import TestCase
from pathlib import Path
from unittest.mock import patch
from unittest.mock import MagicMock

from sparkle.CLI import load_snapshot
from sparkle.CLI import compute_marginal_contribution as cmc
from sparkle.structures import FeatureDataFrame, PerformanceDataFrame
from sparkle.types.objective import PAR


class TestMarginalContribution(TestCase):
    """Tests function of Marginal Contribution help."""

    @patch("sparkle.structures.PerformanceDataFrame.save_csv")
    @patch("sparkle.solver.selector.Selector.run")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.exists")
    def test_compute_actual_selector_performance(
            self: TestCase,
            patch_exists: MagicMock,
            patch_mkdir: MagicMock,
            patch_selector_run: MagicMock,
            patch_save: MagicMock) -> None:
        """Test for method compute_actual_selector_performance."""
        pth = Path("tests/CLI/test_files/Output/Selection/autofolio/PTN/"
                   "portfolio_selector")
        perf_path = Path("tests/test_files/Selector/selector_train_performance_data.csv")
        feature_csv_path = Path("tests/test_files/Selector/"
                                "selector_train_feature_data.csv")

        objective = PAR(10)
        performance_df = PerformanceDataFrame(perf_path)
        feature_df = FeatureDataFrame(feature_csv_path)
        result = 401.42862399999996

        patch_exists.return_value = False  # Block loading from file
        patch_mkdir.return_value = None  # Stop creating unnecesarry dir
        patch_selector_run.side_effect = [[("Solvers/CSCCSat", 61.0)]] * 12
        patch_save.return_value = None
        output = cmc.compute_selector_performance(pth,
                                                  performance_df,
                                                  feature_df,
                                                  objective)
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


@pytest.mark.integration
def test_marginal_contribution_command(tmp_path: Path,
                                       monkeypatch: pytest.MonkeyPatch) -> None:
    """Test for CLI entry point marginal_contribution."""
    snapshot = Path("tests/CLI/test_files/"
                    "snapshot_CSCCSat_MiniSAT_PTN_marginal_contribution.zip").absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    # Setup Platform
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        load_snapshot.main([str(snapshot)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cmc.main(["--perfect", "--actual", "--objectives", "PAR10"])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
