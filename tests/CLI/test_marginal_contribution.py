"""Test functionalities related to the compute marginal contribution help module."""
from __future__ import annotations
import pytest
from unittest import TestCase
from pathlib import Path
from unittest.mock import patch
from unittest.mock import MagicMock

from asf import selectors
from sklearn import ensemble

from sparkle.CLI import load_snapshot
from sparkle.CLI import compute_marginal_contribution as cmc
from sparkle.structures import FeatureDataFrame, PerformanceDataFrame
from sparkle.selector import Selector, SelectionScenario
from sparkle.types.objective import PAR


class TestMarginalContribution(TestCase):
    """Tests function of Marginal Contribution help."""

    @patch("sparkle.structures.PerformanceDataFrame.save_csv")
    @patch("sparkle.selector.selector.Selector.run")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.exists")
    def test_compute_actual_selector_performance(
            self: TestCase,
            patch_exists: MagicMock,
            patch_mkdir: MagicMock,
            patch_selector_run: MagicMock,
            patch_save: MagicMock) -> None:
        """Test for method compute_actual_selector_performance."""
        perf_path = Path("tests/test_files/Selector/selector_train_performance_data.csv")
        feature_csv_path = Path("tests/test_files/Selector/"
                                "selector_train_feature_data.csv")

        objective = PAR(10)
        performance_df = PerformanceDataFrame(perf_path)
        # Filter performance df for selection
        performance_df.filter_objective(objective.name)
        feature_df = FeatureDataFrame(feature_csv_path)
        result = 3.505226166666667

        patch_exists.return_value = False  # Block loading from file
        patch_mkdir.return_value = None  # Stop creating unnecesarry dir
        patch_selector_run.side_effect =\
            [[("Solvers/PbO-CCSAT-Generic",
               "SMAC2_20250522093407_7", 60.0)]] * 12
        patch_save.return_value = None
        # Not actually called as we patch the selector call
        scenario = SelectionScenario(Path(),
                                     Selector(selectors.PairwiseClassifier,
                                              ensemble.RandomForestClassifier),
                                     objective,
                                     performance_df,
                                     feature_df)
        output = cmc.compute_selector_performance(scenario, feature_df)
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
    snapshot = Path(
        "tests/CLI/test_files/"
        "snapshot_constructed_portfolio_selector_csccsat_minisat_ptn.zip").absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    # Setup Platform
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        load_snapshot.main([str(snapshot)])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cmc.main(["--selection-scenario",
                  "Output/Selection/MultiClassClassifier_RandomForestClassifier/"
                  "CSCCSat_MiniSAT_PbO-CCSAT-Generic/scenario.txt",
                  "--perfect", "--actual"])
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0
