"""Tests for Selector CLI entry point."""
from sparkle.selector.selector_cli import main as selector_cli


def test_selector_cli() -> None:
    """Test the Selector CLI entry point."""
    arguments = [
        "--selector-scenario",
        "tests/test_files/Selector/MultiClassClassifier_RandomForestClassifier/"
        "CSCCSat_MiniSAT_PbO-CCSAT-Generic/scenario.txt",
        "--feature-data",
        "tests/test_files/Selector/example_feature_data.csv",
        "--instance", "Instances/PTN/Ptn-7824-b01.cnf",
        "--log-dir", "Output/Log/construct_portfolio_selector_2025-07-15-15.35.07"]
    # TODO: Patch the Solver resolver: It uses the Path given by the ASF selector,
    # which was trained on an existing Platform (e.g. Solvers/$SOLVER$) which does not
    # exist at test time.
    selector_cli(arguments)
    # TODO: Add checks
