"""Test public methods of sparkle performance data csv."""

from __future__ import annotations

from unittest import TestCase
from unittest.mock import Mock, patch
from pathlib import Path

from sparkle.structures.performance_dataframe import PerformanceDataFrame
from sparkle.platform import settings_help
import global_variables as sgh

global settings
sgh.settings = settings_help.Settings()


class TestPerformanceData(TestCase):
    """Class for testing performance data object."""

    def setUp(self: TestPerformanceData) -> None:
        """Create csv objects from files for the tests."""
        self.csv_example_path =\
            Path("tests/test_files/performance/example-runtime-performance.csv")
        self.pd = PerformanceDataFrame(str(self.csv_example_path))
        self.csv_example_with_nan_path =\
            Path("tests/test_files/performance/"
                 "example-runtime-performance-with-empty.csv")
        self.pd_nan = PerformanceDataFrame(str(self.csv_example_with_nan_path))

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

    def test_get_num_instances(self: TestPerformanceData) -> None:
        """Test the number of instances getter method."""
        num_instances = 5
        result = self.pd.get_num_instances()
        assert result == num_instances

    def test_get_list_recompute_performance_computation_job(self: TestPerformanceData)\
            -> None:
        """Test the list creator for which algorithm should be computed per instance."""
        algs = ["AlgorithmA", "AlgorithmB", "AlgorithmC", "AlgorithmD", "AlgorithmE"]
        list_recompute =\
            [["Instance1", algs], ["Instance2", algs], ["Instance3", algs],
             ["Instance4", algs], ["Instance5", algs]]
        result = self.pd.get_list_recompute_performance_computation_job()
        assert result == list_recompute

    def test_get_list_remaining_performance_computation_job(self: TestPerformanceData)\
            -> None:
        """Test get remaining performance computation job getter."""
        remaining = [["Instance1", []], ["Instance2", []], ["Instance3", []],
                     ["Instance4", []], ["Instance5", []]]
        result = self.pd.get_list_remaining_performance_computation_job()
        assert result == remaining

        remaining = [["Instance1", ["AlgorithmA"]], ["Instance2", ["AlgorithmA"]],
                     ["Instance3", ["AlgorithmA", "AlgorithmC"]],
                     ["Instance4", ["AlgorithmA", "AlgorithmE"]],
                     ["Instance5", ["AlgorithmA"]]]
        result = self.pd_nan.get_list_remaining_performance_computation_job()
        assert result == remaining

    def test_get_best_performance_per_instance(self: TestPerformanceData) -> None:
        """Test getting the maximum performance on each instance."""
        max_perf = [64, 87, 87, 96, 86]
        result = self.pd.get_best_performance_per_instance()
        assert result == max_perf

        max_perf = [64, 87.0, 87, 49, 86]
        result = self.pd_nan.get_best_performance_per_instance()
        assert result == max_perf

    @patch("global_variables."
           "settings.get_general_penalty_multiplier")
    def test_calc_portfolio_vbs_instance(self: TestPerformanceData,
                                         mock_penalty: Mock)\
            -> None:
        """Test calculating virtual best score on instance."""
        vbs_instance_min = [30.0, 5.0, 3.0, 8.0, 41.0]
        vbs_instance_max = [64.0, 87.0, 87.0, 96.0, 86.0]
        mock_penalty.return_value = 10
        for idx, instance in enumerate(self.pd.dataframe.index):
            result = self.pd.calc_portfolio_vbs_instance(
                instance=instance, minimise=True, capvalue=None
            )
            assert result == vbs_instance_min[idx]

            result = self.pd.calc_portfolio_vbs_instance(
                instance=instance, minimise=False, capvalue=None
            )
            assert result == vbs_instance_max[idx]

    def test_calc_virtual_best_performance_of_portfolio(self: TestPerformanceData)\
            -> None:
        """Test calculating vbs on the entire portfolio."""
        vbs_portfolio = 87.0
        result = self.pd.calc_virtual_best_performance_of_portfolio(
            aggregation_function=sum, minimise=True, capvalue_list=None
        )
        assert result == vbs_portfolio

        vbs_portfolio = 420.0
        result = self.pd.calc_virtual_best_performance_of_portfolio(
            aggregation_function=sum, minimise=False, capvalue_list=None
        )
        assert result == vbs_portfolio

    @patch("global_variables."
           "settings.get_penalised_time")
    def test_get_dict_vbs_penalty_time_on_each_instance(self: TestPerformanceData,
                                                        mock_penalty: Mock)\
            -> None:
        """Test getting a dictionary representing penalized runtime per instance."""
        mock_penalty.return_value = 40
        penalty_time_dict = {"Instance1": 30, "Instance2": 5, "Instance3": 3,
                             "Instance4": 8, "Instance5": 40}
        result = self.pd.get_dict_vbs_penalty_time_on_each_instance()
        print(result)
        assert result == penalty_time_dict

    @patch("global_variables."
           "settings.get_general_target_cutoff_time")
    @patch("global_variables."
           "settings.get_general_penalty_multiplier")
    def test_calc_vbs_penalty_time(self: TestPerformanceData,
                                   mock_cutoff: Mock,
                                   mock_multiplier: Mock) -> None:
        """Test calculating the penalized vbs."""
        mock_cutoff.return_value = 60
        mock_multiplier.return_value = 10
        vbs_penalized = 243.2
        result = self.pd.calc_vbs_penalty_time()
        assert result == vbs_penalized

    @patch("global_variables."
           "settings.get_general_target_cutoff_time")
    @patch("global_variables."
           "settings.get_general_penalty_multiplier")
    def test_get_solver_penalty_time_ranking_list(self: TestPerformanceData,
                                                  mock_cutoff: Mock,
                                                  mock_multiplier: Mock) -> None:
        """Test getting the solver ranking list with penalty."""
        mock_cutoff.return_value = 50
        mock_multiplier.return_value = 10
        rank_list = [["AlgorithmE", 400.6], ["AlgorithmC", 401.0],
                     ["AlgorithmB", 401.6], ["AlgorithmA", 500.0], ["AlgorithmD", 500.0]]
        result = self.pd.get_solver_penalty_time_ranking_list()
        assert result == rank_list
