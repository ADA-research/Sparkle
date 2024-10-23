"""Test public methods of IRACE configurator."""
import pytest
from pathlib import Path

from sparkle.CLI import initialise

from sparkle.configurator.implementations import IRACE, IRACEScenario
from sparkle.solver import Solver
from sparkle.instance import instance_set
from sparkle.types import resolve_objective


def test_irace_scenario_file(tmp_path: Path,
                             monkeypatch: pytest.MonkeyPatch) -> None:
    """Test IRACE scenario file creation."""
    solver = Solver(Path("tests/test_files/Solvers/Test-Solver").absolute())
    set = instance_set(Path("tests/test_files/Instances/Train-Instance-Set").absolute())
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    if not IRACE.configurator_executable.exists():
        initialise.initialise_irace()  # Ensure IRACE is compiled
    obj_par, obj_acc = resolve_objective("PAR10"), resolve_objective("accuray:max")
    scenario = IRACEScenario(solver, set, number_of_runs=2,
                             solver_calls=2, cutoff_time=2, cutoff_length=2,
                             sparkle_objectives=[obj_par, obj_acc])
    scenario.create_scenario(Path("test_irace_scenario"))
    # TODO: Add file comparison, requires variables/regex to match


def test_irace_scenario_from_file(tmp_path: Path,
                                  monkeypatch: pytest.MonkeyPatch) -> None:
    """Test IRACE scenario file creation."""
    solver = Solver(Path("Examples/Resources/Solvers/PbO-CCSAT-Generic").absolute())
    set = instance_set(Path("Examples/Resources/Instances/PTN").absolute())
    scenario_file = Path("tests/test_files/Configuration/"
                         "PbO-CCSAT-Generic_PTN_scenario_irace.txt").absolute()
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    scenario = IRACEScenario.from_file(scenario_file, solver, set)
    assert scenario.solver == solver
    assert scenario.instance_set == set
    assert scenario.number_of_runs is None  # not in scenario_file
    assert scenario.solver_calls is None
    assert scenario.cutoff_time == 60
    assert scenario.max_time == 1750
    assert scenario.sparkle_objective.name == "PAR10"
