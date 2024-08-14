"""Test public methods of sparkle performance data csv."""

from __future__ import annotations
from unittest import TestCase
from pathlib import Path

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

    def test_get_job_list(self: TestPerformanceData) -> None:
        """Test job list method, without and with recompute bool."""
        job_list = []
        result = self.pd.get_job_list()
        assert result == job_list

        job_list = [("Instance1", "AlgorithmA"), ("Instance1", "AlgorithmB"),
                    ("Instance1", "AlgorithmC"), ("Instance1", "AlgorithmD"),
                    ("Instance1", "AlgorithmE"), ("Instance2", "AlgorithmA"),
                    ("Instance2", "AlgorithmB"), ("Instance2", "AlgorithmC"),
                    ("Instance2", "AlgorithmD"), ("Instance2", "AlgorithmE"),
                    ("Instance3", "AlgorithmA"), ("Instance3", "AlgorithmB"),
                    ("Instance3", "AlgorithmC"), ("Instance3", "AlgorithmD"),
                    ("Instance3", "AlgorithmE"), ("Instance4", "AlgorithmA"),
                    ("Instance4", "AlgorithmB"), ("Instance4", "AlgorithmC"),
                    ("Instance4", "AlgorithmD"), ("Instance4", "AlgorithmE"),
                    ("Instance5", "AlgorithmA"), ("Instance5", "AlgorithmB"),
                    ("Instance5", "AlgorithmC"), ("Instance5", "AlgorithmD"),
                    ("Instance5", "AlgorithmE")]
        result = self.pd.get_job_list(rerun=True)
        assert result == job_list

    def test_num_instances(self: TestPerformanceData) -> None:
        """Test the number of instances getter method."""
        num_instances = 5
        assert self.pd.num_instances == num_instances

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

    def test_calc_best_performance_instance(self: TestPerformanceData)\
            -> None:
        """Test calculating best score on instance."""
        bp_instance_min = [30.0, 5.0, 3.0, 8.0, 41.0]
        bp_instance_max = [64.0, 87.0, 87.0, 96.0, 86.0]
        result_min = self.pd.best_instance_performance(minimise=True)
        result_max = self.pd.best_instance_performance(minimise=False)
        for idx, _ in enumerate(self.pd.dataframe.index):
            assert result_min.iloc[idx] == bp_instance_min[idx]
            assert result_max.iloc[idx] == bp_instance_max[idx]

    def test_calc_best_performance(self: TestPerformanceData)\
            -> None:
        """Test calculating vbs on the entire portfolio."""
        vbs_portfolio = 87.0
        result = self.pd.best_performance(
            aggregation_function=sum, minimise=True)
        assert result == vbs_portfolio

        vbs_portfolio = 420.0
        result = self.pd.best_performance(
            aggregation_function=sum, minimise=False)
        assert result == vbs_portfolio

    def test_get_solver_ranking(self: TestPerformanceData) -> None:
        """Test getting the solver ranking list with penalty."""
        cutoff = 50
        multiplier = 10
        penalty = cutoff * multiplier
        rank_list = [("AlgorithmB", 210.8), ("AlgorithmC", 216.6),
                     ("AlgorithmE", 218.8), ("AlgorithmA", 310.4), ("AlgorithmD", 313.8)]
        result = self.pd.get_solver_ranking(cutoff=cutoff, penalty=penalty)
        assert result == rank_list
