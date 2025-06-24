"""Test public methods of ParamILS configurator."""
import pytest
from pathlib import Path
from sparkle.configurator.implementations import ParamILS, ParamILSScenario

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
    output_file = Path("tests/test_files/Configuration/results/"
                       "PbO-CCSAT-Generic_PTN_seed_2_paramils.txt")
    scenario_file = Path("tests/test_files/Configuration/test_paramils_scenario.txt")
    scenario = ParamILSScenario.from_file(scenario_file)
    configuration = ParamILS.organise_output(output_file, None, scenario, 2)
    assert configuration == {
        "beta_hscore": "233572",
        "d_hscore": "9",
        "gamma_hscore2": "100",
        "p_swt": "0.47368421052631576",
        "perform_first_div": "1",
        "prob_first_div": "0.23357214690901212",
        "prob_novelty": "1.0",
        "prob_pac": "0.03792690190732246",
        "q_swt": "0.3157894736842105",
        "sel_var_break_tie_greedy": "3",
        "sel_var_div": "2",
        "sp_paws": "0.9210526315789473",
        "sparrow_c1": "10.0",
        "sparrow_c2": "1",
        "sparrow_c3": "20000",
        "threshold_swt": "844",
        "configuration_id": 2,
    }


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
    assert scenario.solver_cutoff_time == 60
