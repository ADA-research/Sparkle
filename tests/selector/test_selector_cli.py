"""Tests for Selector CLI entry point."""
from unittest.mock import patch, Mock

from sparkle.types import SolverStatus

from sparkle.selector.selector_cli import main as selector_cli


@patch("runrunner.add_to_queue")
def test_selector_cli(mock_add_queue: Mock) -> None:
    """Test the Selector CLI entry point."""
    # TODO: Execute in tmp dir with copy to avoid editing test files?
    arguments = [
        "--selector-scenario",
        "tests/test_files/Selector/MultiClassClassifier_RandomForestClassifier/"
        "CSCCSat_MiniSAT_PbO-CCSAT-Generic/scenario.txt",
        "--feature-data",
        "tests/test_files/Selector/example_feature_data.csv",
        "--instance", "Examples/Resources/Instances/PTN2/Ptn-7824-b12.cnf",
        "--seed", "0"]
    mock_add_queue.return_value = {"status": SolverStatus.SAT, "quality": 0,
                                   "cpu_time": 0.48925, "wall_time": 0.52824,
                                   "memory": 1537.2734375, "PAR10": 0.48925}
    selector_cli(arguments)
    # TODO: Add checks based on the patch call
    mock_add_queue.assert_called_once()
    # TODO: Add tests with schedules with multiple solvers
