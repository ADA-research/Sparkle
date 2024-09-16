"""Test public methods of sparkle performance data csv."""

from __future__ import annotations
from unittest import TestCase
from pathlib import Path

import pytest

from sparkle.structures import PerformanceDataFrame


class TestPerformanceData(TestCase):
    """Class for testing performance data object."""

    def setUp(self: TestPerformanceData) -> None:
        """Create csv objects from files for the tests."""
        self.csv_example_path =\
            Path("tests/test_files/performance/example-runtime-performance.csv")
        self.pd = PerformanceDataFrame(self.csv_example_path)
        self.csv_example_with_nan_path =\
            Path("tests/test_files/performance/"
                 "example-runtime-performance-with-empty.csv")
        self.pd_nan = PerformanceDataFrame(self.csv_example_with_nan_path)
        self.csv_example_mo = Path("tests/test_files/performance/example_data_MO.csv")
        self.pd_mo = PerformanceDataFrame(self.csv_example_mo)

    def test_get_job_list(self: TestPerformanceData) -> None:
        """Test job list method, without and with recompute bool."""
        job_list = []
        result = self.pd.get_job_list()
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
        result = self.pd.get_job_list(rerun=True)
        assert result == job_list

    def test_num_instances(self: TestPerformanceData) -> None:
        """Test the number of instances getter method."""
        num_instances = 5
        assert self.pd.num_instances == num_instances
        assert self.pd_nan.num_instances == num_instances
        num_instances = 2
        assert self.pd_mo.num_instances == num_instances

    def test_get_list_remaining_performance_computation_job(self: TestPerformanceData)\
            -> None:
        """Test get remaining performance computation job getter."""
        remaining = {}
        result = self.pd.remaining_jobs()
        assert result == remaining

        remaining = {"Instance1": {"AlgorithmA"}, "Instance2": {"AlgorithmA"},
                     "Instance3": {"AlgorithmC", "AlgorithmA"},
                     "Instance4": {"AlgorithmA", "AlgorithmE"},
                     "Instance5": {"AlgorithmA"}}
        result = self.pd_nan.remaining_jobs()
        assert result == remaining

        remaining = {}
        result = self.pd_mo.remaining_jobs()
        assert result == remaining

    def test_calc_best_performance_instance(self: TestPerformanceData)\
            -> None:
        """Test calculating best score on instance."""
        bp_instance_runtime = [30.0, 5.0, 3.0, 8.0, 41.0]
        result_min = self.pd.best_instance_performance()
        for idx in range(self.pd.num_instances):
            assert result_min.iloc[idx] == bp_instance_runtime[idx]

        bp_instance_accuracy = [0.930, 0.819]
        result_acc = self.pd_mo.best_instance_performance(objective="TrainAccuracy:max")
        for idx in range(self.pd_mo.num_instances):
            assert result_acc.iloc[idx] == bp_instance_accuracy[idx]

        bp_instance_val_accuracy = [0.88, 0.596]
        result_acc = self.pd_mo.best_instance_performance(
            objective="ValidationAccuracy:max")
        for idx in range(self.pd_mo.num_instances):
            assert result_acc.iloc[idx] == bp_instance_val_accuracy[idx]

    def test_calc_best_performance(self: TestPerformanceData) -> None:
        """Test calculating vbs on the entire portfolio."""
        vbs_portfolio = 17.4
        result = self.pd.best_performance()
        assert result == vbs_portfolio

        vbs_portfolio = 0.738
        results = self.pd_mo.best_performance(objective="ValidationAccuracy:max")
        assert results == vbs_portfolio

        vbs_portfolio = 4.449999999999999
        results = self.pd_mo.best_performance(objective="PAR10")
        assert results == vbs_portfolio

    def test_marginal_contribution(self: TestPerformanceData) -> None:
        """Test marginal contribution."""
        marginal = [("AlgorithmA", 0.0, 17.4),
                    ("AlgorithmB", 1.4252873563218393, 24.8),
                    ("AlgorithmC", 1.1264367816091956, 19.6),
                    ("AlgorithmD", 0.0, 17.4), ("AlgorithmE", 1.7471264367816093, 30.4)]
        result = self.pd.marginal_contribution()
        assert result == marginal

        marginal = [("RandomForest", 0.0, 0.738),
                    ("MultiLayerPerceptron", 0.8699186991869919, 0.642)]
        result = self.pd_mo.marginal_contribution(objective="ValidationAccuracy:max")
        assert result == marginal

        marginal = [("RandomForest", 8.786516853932584, 39.099999999999994),
                    ("MultiLayerPerceptron", 0.0, 4.449999999999999)]
        result = self.pd_mo.marginal_contribution(objective="PAR10")
        assert result == marginal

    @pytest.mark.filterwarnings("ignore::FutureWarning")
    def test_get_solver_ranking(self: TestPerformanceData) -> None:
        """Test getting the solver ranking list with penalty."""
        rank_list = [("AlgorithmB", 41.0), ("AlgorithmC", 43.6),
                     ("AlgorithmE", 52.6), ("AlgorithmD", 54.8), ("AlgorithmA", 55.0)]
        result = self.pd.get_solver_ranking()
        assert result == rank_list

        rank_list = [("MultiLayerPerceptron", 0.691734),
                     ("RandomForest", 0.5930799999999999)]
        result = self.pd_mo.get_solver_ranking(objective="ValidationAccuracy:max")
        assert result == rank_list

        rank_list = [("RandomForest", 4.9079999999999995),
                     ("MultiLayerPerceptron", 102.24799999999999)]
        result = self.pd_mo.get_solver_ranking(objective="PAR10")
        assert result == rank_list
