"""Test public methods of sparkle performance data csv."""
from __future__ import annotations
from pathlib import Path
import math

import pytest

from sparkle.structures import PerformanceDataFrame

csv_example_path =\
    Path("tests/test_files/performance/example-runtime-performance.csv")
pd = PerformanceDataFrame(csv_example_path)
csv_example_with_nan_path =\
    Path("tests/test_files/performance/"
         "example-runtime-performance-with-empty.csv")
pd_nan = PerformanceDataFrame(csv_example_with_nan_path)
csv_example_mo = Path("tests/test_files/performance/example_data_MO.csv")
pd_mo = PerformanceDataFrame(csv_example_mo)


def test_from_scratch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test creating a Performance DataFrame from scratch."""
    monkeypatch.chdir(tmp_path)  # Execute in PyTest tmp dir
    empty_df = PerformanceDataFrame(Path("test.csv"))
    empty_df.add_instance("Instance1")
    empty_df.add_instance("Instance2")
    empty_df.add_instance("Instance3")
    assert set(empty_df.instances) == set(["Instance3", "Instance1", "Instance2"])
    empty_df.add_solver("AlgorithmA")
    empty_df.add_solver("AlgorithmB")
    empty_df.add_solver("AlgorithmC")
    assert set(empty_df.solvers) == set(["AlgorithmA", "AlgorithmB", "AlgorithmC"])


def test_full_init() -> None:
    """Test creating a Performance DataFrame with all data in the constructor."""
    pass


def test_get_job_list() -> None:
    """Test job list method, without and with recompute bool."""
    job_list = []
    result = pd.get_job_list()
    assert result == job_list

    job_list = [("Instance1", 1, "AlgorithmA"), ("Instance1", 1, "AlgorithmB"),
                ("Instance1", 1, "AlgorithmC"), ("Instance1", 1, "AlgorithmD"),
                ("Instance1", 1, "AlgorithmE"), ("Instance2", 1, "AlgorithmA"),
                ("Instance2", 1, "AlgorithmB"), ("Instance2", 1, "AlgorithmC"),
                ("Instance2", 1, "AlgorithmD"), ("Instance2", 1, "AlgorithmE"),
                ("Instance3", 1, "AlgorithmA"), ("Instance3", 1, "AlgorithmB"),
                ("Instance3", 1, "AlgorithmC"), ("Instance3", 1, "AlgorithmD"),
                ("Instance3", 1, "AlgorithmE"), ("Instance4", 1, "AlgorithmA"),
                ("Instance4", 1, "AlgorithmB"), ("Instance4", 1, "AlgorithmC"),
                ("Instance4", 1, "AlgorithmD"), ("Instance4", 1, "AlgorithmE"),
                ("Instance5", 1, "AlgorithmA"), ("Instance5", 1, "AlgorithmB"),
                ("Instance5", 1, "AlgorithmC"), ("Instance5", 1, "AlgorithmD"),
                ("Instance5", 1, "AlgorithmE")]
    result = pd.get_job_list(rerun=True)
    assert result == job_list


def test_num_objectives() -> None:
    """Test the number of objectives getter method."""
    num_objectives = 1
    print(pd)
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
    num_runs = 5
    assert pd_mo.num_runs == num_runs


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
    solvers = ["AlgorithmA", "AlgorithmB", "AlgorithmC", "AlgorithmD",
               "AlgorithmE"]
    assert pd.solvers == solvers
    assert pd_nan.solvers == solvers
    solvers = ["RandomForest", "MultiLayerPerceptron"]
    assert pd_mo.solvers == solvers


def test_objective_names() -> None:
    """Test the objective names getter method."""
    objective_names = ["UNKNOWN"]
    assert pd.objective_names == objective_names
    assert pd_nan.objective_names == objective_names
    objective_names = ["PAR10", "TrainAccuracy:max", "ValidationAccuracy:max"]
    assert pd_mo.objective_names == objective_names


def test_instances() -> None:
    """Test the instances getter method."""
    instances = ["Instance1", "Instance2", "Instance3", "Instance4", "Instance5"]
    assert pd.instances == instances
    assert pd_nan.instances == instances
    instances = ["flower_petals.csv", "mnist.csv"]
    assert pd_mo.instances == instances


def test_has_missing_values() -> None:
    """Test the has_missing_values getter method."""
    assert not pd.has_missing_values
    assert pd_nan.has_missing_values
    assert not pd_mo.has_missing_values
    # Seed or config should not be included as 'missing value'
    copy_pd = pd.clone()
    copy_pd.set_value(PerformanceDataFrame.missing_value,
                      "AlgorithmA", "Instance1", solver_fields=["Seed"])
    assert not copy_pd.has_missing_values
    copy_pd.set_value(PerformanceDataFrame.missing_value,
                      "AlgorithmA", "Instance1", solver_fields=["Configuration"])
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
    assert pd_nan.get_values("AlgorithmTmp") == [None] * 5

    pd_nan.remove_solver("AlgorithmTmp")
    assert "AlgorithmTmp" not in pd_nan.solvers


def test_add_remove_instance() -> None:
    """Test adding and removing instances."""
    pd_nan.add_instance("InstanceTmp")
    assert "InstanceTmp" in pd_nan.instances
    assert math.isnan(pd_nan.get_values(pd_nan.solvers[0],
                                        instance="InstanceTmp")[0])
    pd_nan.remove_instance("InstanceTmp")
    assert "InstanceTmp" not in pd_nan.instances


def test_add_remove_runs() -> None:
    """Test adding and removing runs."""
    pd_nan.add_runs(5)
    assert pd_nan.num_runs == 6
    pd_nan.remove_runs(3)
    assert pd_nan.num_runs == 3
    pd_nan.remove_runs(2)
    assert pd_nan.num_runs == 1

    instance_subset = pd_nan.instances[:2]
    pd_nan.add_runs(2, instance_names=instance_subset)
    assert pd_nan.num_runs == 3
    for instance in pd_nan.instances:
        if instance in instance_subset:
            assert pd_nan.get_instance_num_runs(instance) == 3
        else:
            assert pd_nan.get_instance_num_runs(instance) == 1
    pd_nan.remove_runs(2, instance_names=instance_subset)
    assert pd_nan.num_runs == 1


def test_set_get_value() -> None:
    """Test set value method."""
    pd_mo = PerformanceDataFrame(csv_example_mo)
    # One index (e.g. one specific field)
    solver = "RandomForest"
    instances = "flower_petals.csv"
    objective = "PAR10"
    run = 1
    value = 1337
    pd_mo.set_value(value, solver, instances,
                    objective=objective, run=run,
                    solver_fields=[PerformanceDataFrame.column_value])
    assert pd_mo.get_value(solver, instances,
                           objective=objective, run=run,
                           solver_fields=[PerformanceDataFrame.column_value]) == value
    # One index/solver, but set value, seed and configuration
    seed = 42
    configuration = {"parameter_alpha": 0.05}
    pd_mo.set_value([value, seed, str(configuration)], solver, instances,
                    objective=objective, run=run, solver_fields=[
                        PerformanceDataFrame.column_value,
                        PerformanceDataFrame.column_seed,
                        PerformanceDataFrame.column_configuration])
    assert pd_mo.get_value(solver, instances, objective=objective, run=run,
                           solver_fields=[PerformanceDataFrame.column_value,
                                          PerformanceDataFrame.column_seed,
                                          PerformanceDataFrame.column_configuration]) ==\
        [value, seed, str(configuration)]
    # Set multiple instances the same value
    value = 12.34
    instances = ["flower_petals.csv", "mnist.csv"]
    pd_mo.set_value(value, solver, instances,
                    objective=objective, run=run, solver_fields=[
                        PerformanceDataFrame.column_value])
    assert pd_mo.get_value(solver, instances, objective=objective, run=run,
                           solver_fields=[PerformanceDataFrame.column_value]) ==\
        [value, value]
    # Set multiple instances the same value and seed
    value = 56.78
    seed = 101
    pd_mo.set_value([value, seed], solver, instances,
                    objective=objective, run=run, solver_fields=[
                        PerformanceDataFrame.column_value,
                        PerformanceDataFrame.column_seed])
    assert pd_mo.get_value(solver, instances, objective=objective, run=run,
                           solver_fields=[PerformanceDataFrame.column_value,
                                          PerformanceDataFrame.column_seed]) ==\
        [[value, seed]] * 2

    # Set multiple instances and specific subset of runs the same value
    value = 910.1112
    run = [3, 4]
    pd_mo.set_value(value, solver, instances,
                    objective=objective, run=run, solver_fields=[
                        PerformanceDataFrame.column_value])
    assert pd_mo.get_value(solver, instances, objective=objective, run=run,
                           solver_fields=[PerformanceDataFrame.column_value]) ==\
        [value] * 4
    # Set multiple instances and two objectives the same value
    value = 1314.1516
    run = 5
    objective = ["PAR10", "TrainAccuracy:max"]
    pd_mo.set_value(value, solver, instances,
                    objective=objective, run=run, solver_fields=[
                        PerformanceDataFrame.column_value])
    assert pd_mo.get_value(solver, instances, objective=objective, run=run,
                           solver_fields=[PerformanceDataFrame.column_value]) ==\
        [value] * 4
    # Set multiple instances/solvers but a specific objective and run diff value
    value = [[[1718.1920, 1920.2021], [2223.2425, 2627.2829]]]
    solver = ["RandomForest", "MultiLayerPerceptron"]
    run = 1
    objective = "ValidationAccuracy:max"
    pd_mo.set_value(value, solver, instances,
                    objective=objective, run=run, solver_fields=[
                        PerformanceDataFrame.column_value])
    assert pd_mo.get_value(solver, instances, objective=objective, run=run,
                           solver_fields=[PerformanceDataFrame.column_value]) ==\
        value[0]
    # Set a specific objective/instance/run but all solvers the same value
    solver = None
    instances = "mnist.csv"
    value = 3031.3233
    run = 3
    objective = "PAR10"
    pd_mo.set_value(value, solver, instances,
                    objective=objective, run=run, solver_fields=[
                        PerformanceDataFrame.column_value])
    assert pd_mo.get_value(solver, instances, objective=objective, run=run,
                           solver_fields=[PerformanceDataFrame.column_value]) ==\
        [value] * pd_mo.num_solvers
    # TODO: Create tests for:
    # Set a multiple instance, specific run/solver combination
    # but all objectives the same configuration
    solver = "RandomForest"
    instances = ["flower_petals.csv", "mnist.csv"]
    configuration = str({"parameter_alpha": 0.07, "parameter_beta": 0.08})
    run = 3
    objective = None
    pd_mo.set_value(configuration, solver, instances,
                    objective=objective, run=run, solver_fields=[
                        PerformanceDataFrame.column_configuration])
    assert pd_mo.get_value(solver, instances, objective=objective, run=run,
                           solver_fields=[PerformanceDataFrame.column_configuration]) ==\
        [configuration] * pd_mo.num_objectives * 2
    # Reload the dataframe to reset it to its original values
    pd_mo = PerformanceDataFrame(csv_example_mo)


def test_get_list_remaining_jobs()\
        -> None:
    """Test get remaining performance computation job getter."""
    remaining = {}
    result = pd.remaining_jobs()
    assert result == remaining
    remaining = {"Instance1": ["AlgorithmA"], "Instance2": ["AlgorithmA"],
                 "Instance3": ["AlgorithmA", "AlgorithmC"],
                 "Instance4": ["AlgorithmA", "AlgorithmE"],
                 "Instance5": ["AlgorithmA"]}
    result = pd_nan.remaining_jobs()
    assert result == remaining
    remaining = {}
    result = pd_mo.remaining_jobs()
    assert result == remaining


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
    result_acc = pd_mo.best_instance_performance(
        objective="ValidationAccuracy:max")
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
    marginal = [("AlgorithmA", 0.0, 17.4),
                ("AlgorithmB", 1.4252873563218393, 24.8),
                ("AlgorithmC", 1.1264367816091956, 19.6),
                ("AlgorithmD", 0.0, 17.4), ("AlgorithmE", 1.7471264367816093, 30.4)]
    result = pd.marginal_contribution()
    assert result == marginal

    marginal = [("RandomForest", 0.0, 0.738),
                ("MultiLayerPerceptron", 0.8699186991869919, 0.642)]
    result = pd_mo.marginal_contribution(objective="ValidationAccuracy:max")
    assert result == marginal

    marginal = [("RandomForest", 8.786516853932584, 39.099999999999994),
                ("MultiLayerPerceptron", 0.0, 4.449999999999999)]
    result = pd_mo.marginal_contribution(objective="PAR10")
    assert result == marginal


def test_get_solver_ranking() -> None:
    """Test getting the solver ranking list with penalty."""
    rank_list = [("AlgorithmB", 41.0), ("AlgorithmC", 43.6),
                 ("AlgorithmE", 52.6), ("AlgorithmD", 54.8), ("AlgorithmA", 55.0)]
    result = pd.get_solver_ranking()
    assert result == rank_list

    rank_list = [("MultiLayerPerceptron", 0.691734),
                 ("RandomForest", 0.5930799999999999)]
    result = pd_mo.get_solver_ranking(objective="ValidationAccuracy:max")
    assert result == rank_list

    rank_list = [("RandomForest", 4.9079999999999995),
                 ("MultiLayerPerceptron", 102.24799999999999)]
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
def test_clean_csv(tmp_path: Path,
                   monkeypatch: pytest.MonkeyPatch) -> None:
    """Test for method clean_csv."""
    monkeypatch.chdir(tmp_path)
    copy_pd = pd.clone(csv_filepath=Path("test.csv"))
    copy_pd.clean_csv()
    assert copy_pd.isnull().all().all()
