"""Test public methods of ParamILS configurator."""
import pytest
from pathlib import Path
from sparkle.configurator.implementations import ParamILSScenario

"""
from sparkle.CLI import initialise

from sparkle.solver import Solver
from sparkle.instance import Instance_Set
from sparkle.types import resolve_objective

from tests.CLI import tools as cli_tools
"""


def test_paramils_organise_output(tmp_path: Path,
                                  monkeypatch: pytest.MonkeyPatch) -> None:
    """Test IRACE organise output method."""
    pass


def test_paramils_scenario_file(tmp_path: Path,
                                monkeypatch: pytest.MonkeyPatch) -> None:
    """Test IRACE scenario file creation."""
    pass


def test_paramils_scenario_from_file() -> None:
    """Test ParamILS scenario file creation."""
    scenario_file = Path("tests/test_files/Configuration/test_paramils_scenario.txt")
    scenario = ParamILSScenario.from_file(scenario_file)
    assert scenario.solver.name == "PbO-CCSAT-Generic"
    assert scenario.instance_set.name == "PTN"
    assert scenario.number_of_runs == 2
    assert scenario.cutoff_time == 60
