"""Test public methods of IRACE configurator."""
from pathlib import Path

from sparkle.CLI import initialise

from sparkle.configurator.implementations import IRACE, IRACEScenario
from sparkle.solver import Solver
from sparkle.instance import instance_set
from sparkle.types import resolve_objective


def test_irace_scenario_file() -> None:
    """Test IRACE scenario file creation."""
    if not IRACE.configurator_executable.exists():
        initialise.initialise_irace()  # Ensure IRACE is compiled
    solver = Solver("tests/test_files/Solvers/Test-Solver")
    set = instance_set(Path("tests/test_files/Instances/Train-Instance-Set"))
    obj_par, obj_acc = resolve_objective("PAR10"), resolve_objective("accuray:max")
    scenario = IRACEScenario(solver, set, number_of_runs=5,
                             solver_calls=5, cpu_time=10, wallclock_time=10,
                             cutoff_time=10, cutoff_length=10,
                             sparkle_objectives=[obj_par, obj_acc], feature_data_df=None)
    scenario.create_scenario_file()
