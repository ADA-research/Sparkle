"""Test public methods of IRACE configurator."""
import pytest
from pathlib import Path

from sparkle.CLI import initialise

from sparkle.configurator.implementations import IRACE, IRACEScenario
from sparkle.solver import Solver
from sparkle.instance import Instance_Set
from sparkle.types import resolve_objective


def test_irace_organise_output(tmp_path: Path,
                               monkeypatch: pytest.MonkeyPatch) -> None:
    """Test IRACE organise output method."""
    source_path = Path("tests/test_files/Configuration/"
                       "test_output_irace.Rdata").absolute()
    target_path = Path("tmp.csv")
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    IRACE.organise_output(source_path, target_path)
    assert target_path.exists()
    assert target_path.open().read().strip() == (
        "--init_solution 1 --perform_pac 0 --perform_first_div 1 --perform_double_cc 1 "
        "--perform_aspiration 1 --sel_var_break_tie_greedy 4 --perform_clause_weight 0 "
        "--sel_clause_div 2 --sel_var_div 6 --prob_first_div 0.9918 "
        "--gamma_hscore2 495644.0 --prob_novelty 0.4843")


def test_irace_scenario_file(tmp_path: Path,
                             monkeypatch: pytest.MonkeyPatch) -> None:
    """Test IRACE scenario file creation."""
    solver = Solver(Path("tests/test_files/Solvers/Test-Solver").absolute())
    set = Instance_Set(Path("tests/test_files/Instances/Train-Instance-Set").absolute())
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    if not IRACE.configurator_executable.exists():
        initialise.initialise_irace()  # Ensure IRACE is compiled
    obj_par, obj_acc = resolve_objective("PAR10"), resolve_objective("accuray:max")
    scenario = IRACEScenario(solver, set, number_of_runs=2,
                             solver_calls=2, cutoff_time=2,
                             sparkle_objectives=[obj_par, obj_acc])
    scenario.create_scenario(Path("test_irace_scenario"))
    # TODO: Add file comparison, requires variables/regex to match


def test_irace_scenario_from_file() -> None:
    """Test IRACE scenario file creation."""
    solver = Solver(Path("Examples/Resources/Solvers/PbO-CCSAT-Generic"))
    set = Instance_Set(Path("Examples/Resources/Instances/PTN"))
    scenario_file = Path("tests/test_files/Configuration/"
                         "PbO-CCSAT-Generic_PTN_scenario_irace.txt")
    scenario = IRACEScenario.from_file(scenario_file)
    assert scenario.solver.name == solver.name
    assert scenario.instance_set.name == set.name
    assert scenario.number_of_runs is None  # not in scenario_file
    assert scenario.solver_calls is None
    assert scenario.cutoff_time == 60
    assert scenario.max_time == 1750
    assert scenario.sparkle_objective.name == "PAR10"
