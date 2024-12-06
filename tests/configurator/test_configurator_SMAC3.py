"""Test methods of SMAC3 configurator."""
from pathlib import Path
import pytest
from unittest.mock import patch

from sparkle.solver import Solver
from sparkle.instance import Instance_Set
from sparkle.structures import PerformanceDataFrame
from sparkle.types import resolve_objective
from sparkle.configurator.implementations import SMAC3, SMAC3Scenario


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
        number_of_runs=1,
        crash_cost=15.0,
        termination_cost_threshold=24.0,
        walltime_limit=10.0,
        cputime_limit=20.0,
        solver_calls=5,
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
    assert len(scenario.smac3_scenario.objectives) == 1
    assert scenario.directory == source.parent.parent / scenario.name
    assert scenario.cutoff_time == 60
    assert scenario.number_of_runs == 5
    assert scenario.feature_dataframe is None
    assert scenario.smac3_scenario.crash_cost == 15.0
    assert scenario.smac3_scenario.termination_cost_threshold == 24.0
    assert scenario.smac3_scenario.walltime_limit == 10.0
    assert scenario.smac3_scenario.cputime_limit == 20.0
    assert scenario.smac3_scenario.n_trials == 5
    assert scenario.smac3_scenario.use_default_config is False
    assert scenario.smac3_scenario.instance_features ==\
        {"tests/test_files/Instances/Train-Instance-Set/train_instance_1.cnf": [0]}
    assert scenario.smac3_scenario.min_budget == 50.0
    assert scenario.smac3_scenario.max_budget == 60.0
    assert scenario.smac3_scenario.seed == 42
    assert scenario.smac3_scenario.n_workers == 2


def test_smac3_configure(tmp_path: Path,
                         monkeypatch: pytest.MonkeyPatch) -> None:
    """Test SMAC3 scenario configuration."""
    solver = Solver(Path("tests/test_files/Solvers/Test-Solver").absolute())
    instance_set = Instance_Set(
        Path("tests/test_files/Instances/Train-Instance-Set").absolute())
    objectives = [resolve_objective("PAR10"), resolve_objective("accuray:min")]
    data_target = PerformanceDataFrame(
        Path("tests/test_files/performance/example_data_MO.csv"))
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir

    scenario = SMAC3Scenario(
        solver, instance_set, objectives, Path(),
        cutoff_time=60,
        number_of_runs=2,
        crash_cost=15.0,
        termination_cost_threshold=24.0,
        walltime_limit=10.0,
        cputime_limit=20.0,
        solver_calls=5,
        use_default_config=False,
        instance_features=None,
        min_budget=50.0,
        max_budget=60.0,
        seed=42,
        n_workers=2)
    scenario.create_scenario()
    smac_configurator = SMAC3(Path(), Path())
    with patch("runrunner.add_to_queue", new=lambda *args, **kwargs: None):
        runs = smac_configurator.configure(scenario, data_target)
    assert runs == [None, None]


def test_organise_output(tmp_path: Path,
                         monkeypatch: pytest.MonkeyPatch) -> None:
    """Test SMAC3 configuration output organisation."""
    file = Path("tests/test_files/Configuration/results/"
                "runhistory_PbO-CCSAT-Generic_PTN_SMAC3.json").absolute()
    solver = Solver(Path("tests/test_files/Solvers/Test-Solver").absolute())
    instance_set = Instance_Set(
        Path("tests/test_files/Instances/Train-Instance-Set").absolute())
    objectives = [resolve_objective("PAR10"), resolve_objective("accuray:min")]

    scenario = SMAC3Scenario(solver, instance_set, objectives, Path(), solver_calls=5)
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    configuration = SMAC3.organise_output(file, None, scenario, None)
    expected = {"init_solution": "2", "perform_aspiration": "1",
                "perform_clause_weight": "1",
                "perform_double_cc": "0", "perform_first_div": "0",
                "perform_pac": "1", "sel_clause_div": "2",
                "sel_var_break_tie_greedy": "2", "sel_var_div": "4",
                "beta_hscore": 2688, "d_hscore": 9, "prob_pac": 0.0028671877126,
                "sel_clause_weight_scheme": "1", "p_swt": 0.7162626739591,
                "q_swt": 0.2213662965223, "threshold_swt": 665}
    assert configuration == expected
