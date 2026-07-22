"""Test public methods of sparkle performance data csv."""

from __future__ import annotations
from pathlib import Path
import math

import pytest

from sparkle.structures import PerformanceDataFrame

csv_example_path = Path("tests/test_files/performance/example-runtime-performance.csv")
pd = PerformanceDataFrame(csv_example_path)
csv_example_with_nan_path = Path(
    "tests/test_files/performance/example-runtime-performance-with-empty.csv"
)
pd_nan = PerformanceDataFrame(csv_example_with_nan_path)
csv_example_mo = Path("tests/test_files/performance/example_data_MO.csv")
pd_mo = PerformanceDataFrame(csv_example_mo)

# Instance tuples for the test fixtures
TESTSET_INSTANCES = [
    ("TestSet", "Instance1"),
    ("TestSet", "Instance2"),
    ("TestSet", "Instance3"),
    ("TestSet", "Instance4"),
    ("TestSet", "Instance5"),
]
ML_INSTANCES = [("MLDataset", "flower_petals.csv"), ("MLDataset", "mnist.csv")]


def test_from_scratch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test creating a Performance DataFrame from scratch."""
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    empty_df = PerformanceDataFrame(Path("test.csv"))
    empty_df.add_instance(("TestSet", "Instance1"))
    empty_df.add_instance(("TestSet", "Instance2"))
    empty_df.add_instance(("TestSet", "Instance3"))
    assert set(empty_df.instance_pairs) == {
        ("TestSet", "Instance3"),
        ("TestSet", "Instance1"),
        ("TestSet", "Instance2"),
    }
    empty_df.add_solver("AlgorithmA")
    empty_df.add_solver("AlgorithmB")
    empty_df.add_solver("AlgorithmC")
    assert set(empty_df.solvers) == set(["AlgorithmA", "AlgorithmB", "AlgorithmC"])
    # Test with configurations
    empty_df.add_solver("AlgorithmD", configurations=[("Config1", {}), ("Config2", {})])
    assert set(empty_df.solvers) == set(
        ["AlgorithmA", "AlgorithmB", "AlgorithmC", "AlgorithmD"]
    )
    assert empty_df.get_configurations("AlgorithmD") == ["Config1", "Config2"]
    # TODO: Test with specific setting values


def test_full_init() -> None:
    """Test creating a Performance DataFrame with all data in the constructor."""
    pass


def test_load_duplicate_index() -> None:
    """Test load duplicate index."""
    duplicate_index_path = Path(
        "tests/test_files/performance/example_duplicate_index.csv"
    )
    corrected_pdf = PerformanceDataFrame(duplicate_index_path)
    assert len(corrected_pdf.index) == 2  # Six lines representing two indices


def test_remaining_jobs() -> None:
    """Test remaining jobs method, without and with recompute bool."""
    remaining_jobs = []
    result = pd.remaining_jobs()
    assert result == remaining_jobs

    remaining_jobs = [
        ("AlgorithmA", "Default", ("TestSet", "Instance1"), 1),
        ("AlgorithmA", "Default", ("TestSet", "Instance2"), 1),
        ("AlgorithmA", "Default", ("TestSet", "Instance3"), 1),
        ("AlgorithmA", "Default", ("TestSet", "Instance4"), 1),
        ("AlgorithmA", "Default", ("TestSet", "Instance5"), 1),
        ("AlgorithmB", "Default", ("TestSet", "Instance1"), 1),
        ("AlgorithmB", "Default", ("TestSet", "Instance2"), 1),
        ("AlgorithmB", "Default", ("TestSet", "Instance3"), 1),
        ("AlgorithmB", "Default", ("TestSet", "Instance4"), 1),
        ("AlgorithmB", "Default", ("TestSet", "Instance5"), 1),
        ("AlgorithmC", "Default", ("TestSet", "Instance1"), 1),
        ("AlgorithmC", "Default", ("TestSet", "Instance2"), 1),
        ("AlgorithmC", "Default", ("TestSet", "Instance3"), 1),
        ("AlgorithmC", "Default", ("TestSet", "Instance4"), 1),
        ("AlgorithmC", "Default", ("TestSet", "Instance5"), 1),
        ("AlgorithmD", "Default", ("TestSet", "Instance1"), 1),
        ("AlgorithmD", "Default", ("TestSet", "Instance2"), 1),
        ("AlgorithmD", "Default", ("TestSet", "Instance3"), 1),
        ("AlgorithmD", "Default", ("TestSet", "Instance4"), 1),
        ("AlgorithmD", "Default", ("TestSet", "Instance5"), 1),
        ("AlgorithmE", "Default", ("TestSet", "Instance1"), 1),
        ("AlgorithmE", "Default", ("TestSet", "Instance2"), 1),
        ("AlgorithmE", "Default", ("TestSet", "Instance3"), 1),
        ("AlgorithmE", "Default", ("TestSet", "Instance4"), 1),
        ("AlgorithmE", "Default", ("TestSet", "Instance5"), 1),
    ]
    result = pd.remaining_jobs(rerun=True)
    assert set(result) == set(remaining_jobs)

    csv_actual_path = Path("tests/test_files/performance/actual-data-job-list.csv")
    actual_df = PerformanceDataFrame(csv_actual_path)
    result = actual_df.remaining_jobs()
    # Only default was run in this data case
    for solver, config, instance, run in result:
        assert config != PerformanceDataFrame.default_configuration
    assert len(result) == 18 * 23  # 18 new configuration, 23 instances


def test_num_objectives() -> None:
    """Test the number of objectives getter method."""
    num_objectives = 1
    assert pd.num_objectives == num_objectives
    assert pd_nan.num_objectives == num_objectives
    num_objectives = 3
    assert pd_mo.num_objectives == num_objectives


def test_num_instances() -> None:
    """Test the number of instances getter method."""
    num_instances = 5
    assert pd.num_instances == num_instances
    assert pd_nan.num_instances == num_instances
    num_instances = 2
    assert pd_mo.num_instances == num_instances


def test_num_runs() -> None:
    """Test the number of runs getter method."""
    num_runs = 1
    assert pd.num_runs == num_runs
    assert pd_nan.num_runs == num_runs
    assert pd_mo.num_runs == num_runs

    # TODO: Add tests that are not 1


def test_num_solvers() -> None:
    """Test the number of solvers getter method."""
    num_solvers = 5
    assert pd.num_solvers == num_solvers
    assert pd_nan.num_solvers == num_solvers
    num_solvers = 2
    assert pd_mo.num_solvers == num_solvers


def test_multi_objective() -> None:
    """Test the multi-objective getter method."""
    assert pd_mo.multi_objective is True
    assert pd.multi_objective is False


def test_solvers() -> None:
    """Test the solvers getter method."""
    solvers = ["AlgorithmA", "AlgorithmB", "AlgorithmC", "AlgorithmD", "AlgorithmE"]
    assert pd.solvers == solvers
    assert pd_nan.solvers == solvers
    solvers = ["MultiLayerPerceptron", "RandomForest"]
    assert pd_mo.solvers == solvers


def test_solver_configurations() -> None:
    """Check if configuration data is loaded correctly."""
    # Test pds without configs
    assert len(pd.attrs) == pd.num_solvers
    assert len(pd.attrs) == pd.num_solvers
    # Test pds with configs
    assert len(pd_mo.attrs) == pd_mo.num_solvers
    for solver in pd_mo.solvers:
        assert solver in pd_mo.attrs
        assert len(pd_mo.attrs[solver]) == 5
        for config in pd_mo.attrs[solver]:
            assert isinstance(pd_mo.attrs[solver][config], dict)


def test_objective_names() -> None:
    """Test the objective names getter method."""
    objective_names = ["UNKNOWN"]
    assert pd.objective_names == objective_names
    assert pd_nan.objective_names == objective_names
    objective_names = ["PAR10", "TrainAccuracy:max", "ValidationAccuracy:max"]
    assert pd_mo.objective_names == objective_names


def test_instances() -> None:
    """Test the instances getter method."""
    assert pd.instance_pairs == TESTSET_INSTANCES
    assert pd_nan.instance_pairs == TESTSET_INSTANCES
    assert pd_mo.instance_pairs == ML_INSTANCES


def test_has_missing_values() -> None:
    """Test the has_missing_values getter method."""
    assert not pd.has_missing_values
    assert pd_nan.has_missing_values
    assert not pd_mo.has_missing_values
    # Seed or config should not be included as "missing value"
    copy_pd = pd.clone()
    copy_pd.set_value(
        PerformanceDataFrame.missing_value,
        "AlgorithmA",
        ("TestSet", "Instance1"),
        solver_fields=["Seed"],
    )
    assert not copy_pd.has_missing_values


def test_verify_objective() -> None:
    """Test verify objective method."""
    pass


def test_verify_run_id() -> None:
    """Test verify run id method."""
    pass


def test_verify_indexing() -> None:
    """Test verify indexing method."""
    pass


def test_add_remove_solver() -> None:
    """Test adding and removing solvers."""
    pd_nan.add_solver("AlgorithmTmp")
    assert "AlgorithmTmp" in pd_nan.solvers
    assert pd_nan.get_value("AlgorithmTmp") == [None] * 5

    pd_nan.remove_solver("AlgorithmTmp")
    assert "AlgorithmTmp" not in pd_nan.solvers


def test_add_remove_instance() -> None:
    """Test adding and removing instances."""
    pd_nan.add_instance(("TestSet", "InstanceTmp"))
    assert ("TestSet", "InstanceTmp") in pd_nan.instance_pairs
    assert math.isnan(
        pd_nan.get_value(pd_nan.solvers[0], instance_pair=("TestSet", "InstanceTmp"))
    )
    pd_nan.remove_instance(("TestSet", "InstanceTmp"))
    assert ("TestSet", "InstanceTmp") not in pd_nan.instance_pairs


def test_add_remove_runs() -> None:
    """Test adding and removing runs."""
    pd_nan.add_runs(5)
    assert pd_nan.num_runs == 6
    pd_nan.remove_runs(3)
    assert pd_nan.num_runs == 3
    pd_nan.remove_runs(2)
    assert pd_nan.num_runs == 1

    instance_subset = pd_nan.instance_pairs[:2]
    pd_nan.add_runs(2, instance_pairs=instance_subset)
    assert pd_nan.num_runs == 3
    for instance_pair in pd_nan.instance_pairs:
        instance_set, instance_name = instance_pair
        if instance_pair in instance_subset:
            assert pd_nan.get_instance_num_runs(instance_set, instance_name) == 3
        else:
            assert pd_nan.get_instance_num_runs(instance_set, instance_name) == 1
    pd_nan.remove_runs(2, instance_pairs=instance_subset)
    assert pd_nan.num_runs == 1


def test_remove_empty_runs() -> None:
    """Test removing empty runs."""
    empty_runs_csv = Path("tests/test_files/performance/example_empty_runs.csv")
    pd_empty = PerformanceDataFrame(empty_runs_csv)
    assert pd_empty.num_runs == 26
    pd_empty.remove_empty_runs()
    assert pd_empty.num_runs == 1


def test_set_get_value() -> None:
    """Test set value method."""
    pd_mo = PerformanceDataFrame(csv_example_mo)
    # One index (e.g. one specific field)
    solver = "RandomForest"
    configuration = "Config1"
    instances = ("MLDataset", "flower_petals.csv")
    objective = "PAR10"
    run = 1
    value = 1337
    pd_mo.set_value(
        value,
        solver,
        instances,
        configuration,
        objective=objective,
        run=run,
        solver_fields=[PerformanceDataFrame.column_value],
    )
    assert (
        pd_mo.get_value(
            solver,
            instances,
            configuration,
            objective=objective,
            run=run,
            solver_fields=[PerformanceDataFrame.column_value],
        )
        == value
    )
    # One index/solver, but set value and seed
    seed = 42
    pd_mo.set_value(
        [value, seed],
        solver,
        instances,
        configuration,
        objective=objective,
        run=run,
        solver_fields=[
            PerformanceDataFrame.column_value,
            PerformanceDataFrame.column_seed,
        ],
    )
    assert pd_mo.get_value(
        solver,
        instances,
        configuration,
        objective=objective,
        run=run,
        solver_fields=[
            PerformanceDataFrame.column_value,
            PerformanceDataFrame.column_seed,
        ],
    ) == [value, seed]

    # Set multiple instances the same value
    value = 12.34
    instances = [("MLDataset", "flower_petals.csv"), ("MLDataset", "mnist.csv")]
    pd_mo.set_value(
        value,
        solver,
        instances,
        configuration,
        objective=objective,
        run=run,
        solver_fields=[PerformanceDataFrame.column_value],
    )
    assert pd_mo.get_value(
        solver,
        instances,
        configuration,
        objective=objective,
        run=run,
        solver_fields=[PerformanceDataFrame.column_value],
    ) == [value, value]
    # Set multiple instances the same value and seed
    value = 56.78
    seed = 101
    pd_mo.set_value(
        [value, seed],
        solver,
        instances,
        configuration,
        objective=objective,
        run=run,
        solver_fields=[
            PerformanceDataFrame.column_value,
            PerformanceDataFrame.column_seed,
        ],
    )
    assert (
        pd_mo.get_value(
            solver,
            instances,
            configuration,
            objective=objective,
            run=run,
            solver_fields=[
                PerformanceDataFrame.column_value,
                PerformanceDataFrame.column_seed,
            ],
        )
        == [[value, seed]] * 2
    )

    # Set multiple instances and specific subset of runs the same value
    value = 910.1112
    pd_mo.set_value(
        value,
        solver,
        instances,
        configuration,
        objective=objective,
        run=run,
        solver_fields=[PerformanceDataFrame.column_value],
    )
    assert (
        pd_mo.get_value(
            solver,
            instances,
            configuration,
            objective=objective,
            run=run,
            solver_fields=[PerformanceDataFrame.column_value],
        )
        == [value] * 2
    )
    # Set multiple instances and two objectives the same value
    value = 1314.1516
    objective = ["PAR10", "TrainAccuracy:max"]
    pd_mo.set_value(
        value,
        solver,
        instances,
        configuration,
        objective=objective,
        run=run,
        solver_fields=[PerformanceDataFrame.column_value],
    )
    assert (
        pd_mo.get_value(
            solver,
            instances,
            configuration,
            objective=objective,
            run=run,
            solver_fields=[PerformanceDataFrame.column_value],
        )
        == [value] * 4
    )
    # Set multiple instances/solvers but a specific objective and run diff value
    value = [[[1718.1920, 1920.2021], [2223.2425, 2627.2829]]]
    solver = ["RandomForest", "MultiLayerPerceptron"]
    objective = "ValidationAccuracy:max"
    pd_mo.set_value(
        value,
        solver,
        instances,
        configuration,
        objective=objective,
        run=run,
        solver_fields=[PerformanceDataFrame.column_value],
    )
    assert (
        pd_mo.get_value(
            solver,
            instances,
            configuration,
            objective=objective,
            run=run,
            solver_fields=[PerformanceDataFrame.column_value],
        )
        == value[0]
    )
    # Set a specific objective/instance/run but all configurations the same value
    solver = None
    configuration = None
    instances = ("MLDataset", "mnist.csv")
    value = 3031.3233
    objective = "PAR10"
    pd_mo.set_value(
        value,
        solver,
        instances,
        configuration,
        objective=objective,
        run=run,
        solver_fields=[PerformanceDataFrame.column_value],
    )
    assert (
        pd_mo.get_value(
            solver,
            instances,
            configuration,
            objective=objective,
            run=run,
            solver_fields=[PerformanceDataFrame.column_value],
        )
        == [value] * pd_mo.num_solver_configurations
    )

    # Set multiple objectives, both solver fields at once
    configuration = "Config1"
    instances = ("MLDataset", "mnist.csv")
    objective = ["PAR10", "TrainAccuracy:max"]
    value = [[599.0, 0.77], [seed, seed]]
    pd_mo.set_value(
        value,
        solver,
        instances,
        configuration,
        objective=objective,
        run=run,
        solver_fields=[
            PerformanceDataFrame.column_value,
            PerformanceDataFrame.column_seed,
        ],
    )
    assert (
        pd_mo.get_value(
            solver,
            instances,
            configuration,
            objective=objective,
            run=run,
            solver_fields=[
                PerformanceDataFrame.column_value,
                PerformanceDataFrame.column_seed,
            ],
        )
        == [[599.0, 0.77, float(seed), float(seed)]] * 2
    )

    # Reload the dataframe to reset it to its original values
    pd_mo = PerformanceDataFrame(csv_example_mo)


def test_get_full_configurations() -> None:
    """Test getting full configurations."""
    result = pd_mo.get_configurations("RandomForest")
    assert result == ["Config1", "Config2", "Config3", "Config4", "Config5"]
    result = pd_mo.get_full_configuration("RandomForest", result)
    assert result == [
        {"alpha": 0.05, "beta": 0.99},
        {"alpha": 0.12, "beta": 0.46},
        {"alpha": 0.29, "beta": 0.23},
        {"alpha": 0.66, "beta": 0.11},
        {"alpha": 0.69, "beta": 0.42},
    ]
    result = pd_mo.get_configurations("MultiLayerPerceptron")
    assert result == ["Config1", "Config2", "Config3", "Config4", "Config5"]
    result = pd_mo.get_full_configuration("MultiLayerPerceptron", result)
    assert result == [
        {"kappa": 0.23, "mu": "std1"},
        {"kappa": 0.46, "mu": "std2"},
        {"kappa": 0.99, "mu": "std3"},
        {"kappa": 1.0, "mu": "std2"},
        {"kappa": 0.0005, "mu": "std1"},
    ]
    # Test pd that only has default configuration
    for solver in pd.solvers:
        result = pd.get_configurations(solver)
        assert result == ["Default"]
        assert pd.get_full_configuration(solver, result) == [{}]


def test_add_remove_configurations() -> None:
    """Test adding and removing configurations."""
    pd_mo.add_configuration("RandomForest", "Config6", {"alpha": 0.05, "beta": 0.99})
    result = pd_mo.get_configurations("RandomForest")
    assert result == ["Config1", "Config2", "Config3", "Config4", "Config5", "Config6"]
    pd_mo.remove_configuration("RandomForest", "Config6")
    result = pd_mo.get_configurations("RandomForest")
    assert result == ["Config1", "Config2", "Config3", "Config4", "Config5"]


def test_configuration_performance() -> None:
    """Test getting configuration performance."""
    configuration = "Config1"
    result = pd_mo.configuration_performance(
        "RandomForest", configuration, "PAR10", ML_INSTANCES
    )
    assert result == (configuration, 4.75)

    # Test per instance results
    result = pd_mo.configuration_performance(
        "RandomForest",
        configuration,
        "PAR10",
        ML_INSTANCES,
        per_instance=True,
    )
    assert result == (configuration, [4.4, 5.1])

    # Test with large set (actual-data.csv), per all instances.
    # NOTE: The asserts below pin exact float values read from actual-data.csv. If that
    # fixture is ever regenerated, these will break. Looser assertions may be preferred
    # in the future (e.g. checking only the selected config id, or asserting values with
    # pytest.approx / a tolerance) so the test stays robust to fixture regeneration and
    # floating-point noise while still guarding the method's behaviour.
    actual_pdf = PerformanceDataFrame(
        Path("tests/test_files/performance/actual-data.csv")
    )
    solver = "Solvers/PbO-CCSAT-Generic"
    config_id = "SMAC2_20250522093407_2"
    result = actual_pdf.configuration_performance(
        solver, config_id, "PAR10", per_instance=True
    )
    # Per-instance values follow the sorted (InstanceSet, Instance) index order.
    assert result == (
        config_id,
        [
            600.0,
            600.0,
            600.0,
            28.3943,
            600.0,
            600.0,
            6.25488,
            39.9061,
            23.7353,
            26.9149,
            10.2533,
            600.0,
        ],
    )

    # Test with a subset of instances (result still in sorted index order, not input order)
    subset = [
        ("PTN", "Ptn-7824-b15"),
        ("PTN", "Ptn-7824-b19"),
        ("PTN", "Ptn-7824-b13"),
        ("PTN", "Ptn-7824-b07"),
    ]
    result = actual_pdf.configuration_performance(
        solver, config_id, "PAR10", instance_pairs=subset, per_instance=True
    )
    assert result == (config_id, [28.3943, 6.25488, 39.9061, 26.9149])


def test_best_configuration() -> None:
    """Test calculating best configuration."""
    best_conf_id = "Config5"
    best_conf = {"alpha": 0.69, "beta": 0.42}
    best_value = 3.8
    result = pd_mo.best_configuration(
        "RandomForest", "PAR10", [("MLDataset", "flower_petals.csv")]
    )
    assert result == (best_conf_id, best_value)
    assert pd_mo.get_full_configuration("RandomForest", best_conf_id) == best_conf

    best_conf_id = "Config3"
    best_conf = {"kappa": 0.99, "mu": "std3"}
    best_value = 54.8
    result = pd_mo.best_configuration(
        "MultiLayerPerceptron", "PAR10", [("MLDataset", "mnist.csv")]
    )
    assert result == (best_conf_id, best_value)
    assert (
        pd_mo.get_full_configuration("MultiLayerPerceptron", best_conf_id) == best_conf
    )

    # Test with two instances
    best_conf_id = "Config1"
    best_conf = {"alpha": 0.05, "beta": 0.99}
    best_value = 4.75
    result = pd_mo.best_configuration("RandomForest", "PAR10", ML_INSTANCES)
    assert result == (best_conf_id, best_value)
    assert pd_mo.get_full_configuration("RandomForest", best_conf_id) == best_conf

    # Test with large set (actual-data.csv): best config over all PTN instances.
    # NOTE: pins an exact float from the fixture; looser assertions may be preferred later
    # (see test_configuration_performance for the explanation).
    actual_pdf = PerformanceDataFrame(
        Path("tests/test_files/performance/actual-data.csv")
    )
    best_conf_id = "SMAC2_20250522093407_7"
    best_value = 3.505226166666667
    result = actual_pdf.best_configuration("Solvers/PbO-CCSAT-Generic", "PAR10")
    assert result == (best_conf_id, best_value)


def test_best_instance_performance_filters_by_pairs() -> None:
    """best_instance_performance must filter by (set, instance) pairs without crashing.

    Regression: after xs(objective) the frame is a 3-level (InstanceSet, Instance, Run)
    index, so a plain .loc with 2-tuples raised
    'AssertionError: Length of new_levels (3) must be <= self.nlevels (2)'.
    """
    pairs = pd_mo.instance_pairs
    # Filtering to a single pair returns exactly that instance's best value.
    single = pd_mo.best_instance_performance(
        objective="PAR10", instance_pairs=[pairs[0]]
    )
    assert list(single.index) == [pairs[0]]

    # Filtering to all pairs matches the unfiltered result.
    filtered = pd_mo.best_instance_performance(objective="PAR10", instance_pairs=pairs)
    unfiltered = pd_mo.best_instance_performance(objective="PAR10")
    assert list(filtered.index) == list(unfiltered.index)

    # best_performance delegates to it and aggregates without raising.
    assert pd_mo.best_performance(instance_pairs=pairs, objective="PAR10") == (
        pd_mo.best_performance(objective="PAR10")
    )

    # A pair absent from the frame yields an empty result rather than an error.
    assert pd_mo.best_instance_performance(
        objective="PAR10", instance_pairs=[("Nope", "missing.csv")]
    ).empty


def test_best_instance_performance() -> None:
    """Test calculating best score on instance."""
    bp_instance_runtime = [30.0, 5.0, 3.0, 8.0, 41.0]
    result_min = pd.best_instance_performance()
    for idx in range(pd.num_instances):
        assert result_min.iloc[idx] == bp_instance_runtime[idx]

    bp_instance_accuracy = [0.930, 0.819]
    result_acc = pd_mo.best_instance_performance(objective="TrainAccuracy:max")
    for idx in range(pd_mo.num_instances):
        assert result_acc.iloc[idx] == bp_instance_accuracy[idx]

    bp_instance_val_accuracy = [0.88, 0.596]
    result_acc = pd_mo.best_instance_performance(objective="ValidationAccuracy:max")
    for idx in range(pd_mo.num_instances):
        assert result_acc.iloc[idx] == bp_instance_val_accuracy[idx]


def test_best_performance() -> None:
    """Test calculating vbs on the entire portfolio."""
    vbs_portfolio = 17.4
    result = pd.best_performance()
    assert result == vbs_portfolio

    vbs_portfolio = 0.738
    results = pd_mo.best_performance(objective="ValidationAccuracy:max")
    assert results == vbs_portfolio

    vbs_portfolio = 4.449999999999999
    results = pd_mo.best_performance(objective="PAR10")
    assert results == vbs_portfolio


def test_schedule_performance() -> None:
    """Test scheduling performance."""
    pass


def test_marginal_contribution() -> None:
    """Test marginal contribution."""
    marginal = [
        ("AlgorithmA", "Default", 0.0, 17.4),
        ("AlgorithmB", "Default", 1.4252873563218393, 24.8),
        ("AlgorithmC", "Default", 1.1264367816091956, 19.6),
        ("AlgorithmD", "Default", 0.0, 17.4),
        ("AlgorithmE", "Default", 1.7471264367816093, 30.4),
    ]
    result = pd.marginal_contribution()
    assert result == marginal

    # TODO: Inspect if these results make any sense
    marginal = [
        ("MultiLayerPerceptron", "Config1", 0.0, 0.738),
        ("MultiLayerPerceptron", "Config2", 0.9728997289972899, 0.718),
        ("MultiLayerPerceptron", "Config3", 0.9939024390243903, 0.7335),
        ("MultiLayerPerceptron", "Config4", 0.0, 0.738),
        ("MultiLayerPerceptron", "Config5", 0.0, 0.738),
        ("RandomForest", "Config1", 0.0, 0.738),
        ("RandomForest", "Config2", 0.0, 0.738),
        ("RandomForest", "Config3", 0.0, 0.738),
        ("RandomForest", "Config4", 0.0, 0.738),
        ("RandomForest", "Config5", 0.0, 0.738),
    ]
    result = pd_mo.marginal_contribution(objective="ValidationAccuracy:max")
    assert result == marginal
    marginal = [
        ("MultiLayerPerceptron", "Config1", 0.0, 4.449999999999999),
        ("MultiLayerPerceptron", "Config2", 0.0, 4.449999999999999),
        ("MultiLayerPerceptron", "Config3", 0.0, 4.449999999999999),
        ("MultiLayerPerceptron", "Config4", 0.0, 4.449999999999999),
        ("MultiLayerPerceptron", "Config5", 0.0, 4.449999999999999),
        ("RandomForest", "Config1", 1.01123595505618, 4.5),
        ("RandomForest", "Config2", 0.0, 4.449999999999999),
        ("RandomForest", "Config3", 0.0, 4.449999999999999),
        ("RandomForest", "Config4", 0.0, 4.449999999999999),
        ("RandomForest", "Config5", 1.01123595505618, 4.5),
    ]
    result = pd_mo.marginal_contribution(objective="PAR10")
    assert result == marginal


def test_get_solver_ranking() -> None:
    """Test getting the solver ranking list with penalty."""
    rank_list = [
        ("AlgorithmB", "Default", 41.0),
        ("AlgorithmC", "Default", 43.6),
        ("AlgorithmE", "Default", 52.6),
        ("AlgorithmD", "Default", 54.8),
        ("AlgorithmA", "Default", 55.0),
    ]
    result = pd.get_solver_ranking()
    assert result == rank_list

    rank_list = [
        ("MultiLayerPerceptron", "Config3", 0.71425),
        ("MultiLayerPerceptron", "Config2", 0.712),
        ("MultiLayerPerceptron", "Config1", 0.69975),
        ("MultiLayerPerceptron", "Config4", 0.67797),
        ("MultiLayerPerceptron", "Config5", 0.6547000000000001),
        ("RandomForest", "Config2", 0.627),
        ("RandomForest", "Config1", 0.6085),
        ("RandomForest", "Config5", 0.5845),
        ("RandomForest", "Config4", 0.5773999999999999),
        ("RandomForest", "Config3", 0.568),
    ]
    result = pd_mo.get_solver_ranking(objective="ValidationAccuracy:max")
    assert result == rank_list

    rank_list = [
        ("RandomForest", "Config1", 4.75),
        ("RandomForest", "Config2", 4.85),
        ("RandomForest", "Config5", 4.890000000000001),
        ("RandomForest", "Config4", 5.0),
        ("RandomForest", "Config3", 5.05),
        ("MultiLayerPerceptron", "Config4", 44.5),
        ("MultiLayerPerceptron", "Config3", 44.55),
        ("MultiLayerPerceptron", "Config2", 52.0),
        ("MultiLayerPerceptron", "Config5", 58.489999999999995),
        ("MultiLayerPerceptron", "Config1", 311.7),
    ]
    result = pd_mo.get_solver_ranking(objective="PAR10")
    assert result == rank_list


def test_save_csv() -> None:
    """Test for method save_csv."""
    # TODO: Write test
    pass


def test_clone() -> None:
    """Test for method clone."""
    copy_nan = pd_nan.clone()
    assert isinstance(copy_nan, PerformanceDataFrame)


@pytest.mark.filterwarnings("ignore::FutureWarning")
def test_clean_csv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test for method clean_csv."""
    monkeypatch.chdir(tmp_path)
    copy_pd = pd.clone(csv_filepath=Path("test.csv"))
    copy_pd.clean_csv()
    assert copy_pd.isnull().all().all()
