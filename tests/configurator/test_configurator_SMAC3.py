"""Test methods of SMAC3 configurator."""
from pathlib import Path
import pytest

from sparkle.solver import Solver
from sparkle.instance import Instance_Set
from sparkle.types import resolve_objective
from sparkle.configurator.implementations import SMAC3Scenario


def test_smac3_scenario_to_file(tmp_path: Path,
                                monkeypatch: pytest.MonkeyPatch) -> None:
    """Test writing SMAC3 scenario file."""
    solver = Solver(Path("tests/test_files/Solvers/Test-Solver").absolute())
    instance_set = Instance_Set(
        Path("tests/test_files/Instances/Train-Instance-Set").absolute())
    objectives = [resolve_objective("PAR10"), resolve_objective("accuray:min")]

    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    scenario = SMAC3Scenario(
        solver, instance_set, objectives, Path(),
        cutoff_time=60,
        crash_cost=15.0,
        termination_cost_threshold=24.0,
        walltime_limit=10.0,
        cputime_limit=20.0,
        n_trials=5,
        use_default_config=False,
        instance_features=None,
        min_budget=50.0,
        max_budget=60.0,
        seed=42,
        n_workers=2)
    scenario.create_scenario()
    assert scenario.scenario_file_path.exists()


def test_smac3_scenario_from_file() -> None:
    """Test reading SMAC3 scenario file."""
    source = Path("tests/test_files/Configuration/test_smac3_scenario.txt")
    scenario = SMAC3Scenario.from_file(source)
    assert scenario.name == "Test-Solver_Train-Instance-Set"
    assert scenario.solver.directory == Path("tests/test_files/Solvers/Test-Solver")
    assert scenario.instance_set.directory ==\
        Path("tests/test_files/Instances/Train-Instance-Set")
    assert scenario.smac3_scenario.name == scenario.name
    assert len(scenario.smac3_scenario.objectives) == len(scenario.sparkle_objectives)
    assert scenario.directory == source.parent / scenario.name
    assert scenario.cutoff_time == 60
    assert scenario.feature_dataframe is None
    assert scenario.smac3_scenario.crash_cost == 15.0
    assert scenario.smac3_scenario.termination_cost_threshold == 24.0
    assert scenario.smac3_scenario.walltime_limit == 10.0
    assert scenario.smac3_scenario.cputime_limit == 20.0
    assert scenario.smac3_scenario.n_trials == 5
    assert scenario.smac3_scenario.use_default_config is False
    assert scenario.smac3_scenario.instance_features is None
    assert scenario.smac3_scenario.min_budget == 50.0
    assert scenario.smac3_scenario.max_budget == 60.0
    assert scenario.smac3_scenario.seed == 42
    assert scenario.smac3_scenario.n_workers == 2


def test_smac3_configure() -> None:
    """Test SMAC3 scenario configuration."""
    return
    # solver = Solver(Path("tests/test_files/Solvers/Test-Solver").absolute())
    # instance_set = Instance_Set(
    #     Path("tests/test_files/Instances/Train-Instance-Set").absolute())
    # objectives = [resolve_objective("PAR10"), resolve_objective("accuray:min")]


def test_organise_output() -> None:
    """Test SMAC3 configuration output organisation."""
    pass
