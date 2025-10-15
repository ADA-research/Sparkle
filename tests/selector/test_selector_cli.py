"""Tests for Selector CLI entry point."""

from pathlib import Path
import shutil
import pytest
from unittest.mock import patch, Mock

from sparkle.types import SolverStatus

from sparkle.selector.selector_cli import main as selector_cli


@patch("runrunner.add_to_queue")
def test_selector_cli(
    mock_add_queue: Mock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test the Selector CLI entry point."""
    scenario_path = Path("tests/test_files/Selector/scenario").absolute()
    feature_data = Path("tests/test_files/Selector/example_feature_data.csv").absolute()
    scenario_path_absolute = scenario_path.absolute()
    instance_path = Path("Examples/Resources/Instances/PTN2/Ptn-7824-b12.cnf")
    instance_path_absolute = instance_path.absolute()
    csccsat = Path("Examples/Resources/Solvers/CSCCSat").absolute()
    # Execute tmp dir
    monkeypatch.chdir(tmp_path)
    shutil.copyfile(feature_data, Path("example_feature_data.csv"))
    instance_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(instance_path_absolute, instance_path)
    shutil.copytree(scenario_path_absolute, Path("scenario"))
    csccsat_target = Path("Solvers/CSCCSat")
    # Selector should predict CSCCSAT, copy that too
    shutil.copytree(csccsat, csccsat_target)
    arguments = [
        "--selector-scenario",
        "scenario/scenario.txt",
        "--feature-data",
        "example_feature_data.csv",
        "--instance",
        f"{instance_path}",
        "--seed",
        "0",
    ]
    mock_add_queue.return_value = {
        "status": SolverStatus.SAT,
        "quality": 0,
        "cpu_time": 0.48925,
        "wall_time": 0.52824,
        "memory": 1537.2734375,
        "PAR10": 0.48925,
    }
    selector_cli(arguments)
    # TODO: Add checks based on the patch call
    mock_add_queue.assert_called_once()
