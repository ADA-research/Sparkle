#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module to manage performance data CSV files and common operations on them."""

from __future__ import annotations
from typing import Callable

import sys

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_csv_help as scsv


class SparklePerformanceDataCSV(scsv.SparkleCSV):
    """Class to manage performance data CSV files and common operations on them."""

    def __init__(self: SparklePerformanceDataCSV, csv_filepath: str) -> None:
        """Initialise a SparklePerformanceDataCSV object."""
        scsv.SparkleCSV.__init__(self, csv_filepath)

    def get_job_list(self: SparklePerformanceDataCSV, rerun: bool = False) \
            -> list[tuple[str, str]]:
        """Return a list of performance computation jobs thare are to be done.

        Get a list of tuple[instance, solver] to run from the performance data
        csv file. If rerun is False (default), get only the tuples that don't have a
        value in the table, else (True) get all the tuples.
        """
        df = self.dataframe.stack(future_stack=True)

        if not rerun:
            df = df[df.isnull()]

        return df.index.tolist()

    def get_number_of_instances(self: SparklePerformanceDataCSV) -> int:
        """Return the number of instances."""
        return self.dataframe.index.size

    def get_list_recompute_performance_computation_job(self: SparklePerformanceDataCSV)\
            -> list[list[list]]:
        """Return a list of performance computations to re-do per instance and solver."""
        list_recompute_performance_computation_job = []
        list_row_name = self.list_rows()
        list_column_name = self.list_columns()

        for row_name in list_row_name:
            list_item = [row_name, list_column_name]
            list_recompute_performance_computation_job.append(list_item)

        return list_recompute_performance_computation_job

    def get_list_remaining_performance_computation_job(self: SparklePerformanceDataCSV) \
            -> list[list[list]]:
        """Return a list of needed performance computations per instance and solver."""
        list_remaining_performance_computation_job = []
        bool_array_isnull = self.dataframe.isnull()
        for row_name in self.list_rows():
            current_solver_list = []
            for column_name in self.list_columns():
                flag_value_is_null = bool_array_isnull.at[row_name, column_name]
                if flag_value_is_null:
                    current_solver_list.append(column_name)
            list_item = [row_name, current_solver_list]
            list_remaining_performance_computation_job.append(list_item)
        return list_remaining_performance_computation_job

    def get_list_processed_performance_computation_job(self: SparklePerformanceDataCSV) \
            -> list[list[list]]:
        """Return a list of existing performance values per instance and solver."""
        list_processed_performance_computation_job = []
        bool_array_isnull = self.dataframe.isnull()
        for row_name in self.list_rows():
            current_solver_list = []
            for column_name in self.list_columns():
                flag_value_is_null = bool_array_isnull.at[row_name, column_name]
                if not flag_value_is_null:
                    current_solver_list.append(column_name)
            list_item = [row_name, current_solver_list]
            list_processed_performance_computation_job.append(list_item)
        return list_processed_performance_computation_job

    def get_maximum_performance_per_instance(self: SparklePerformanceDataCSV) \
            -> list[float]:
        """Return a list with the highest performance per instance."""
        scores = []

        for instance in self.list_rows():
            score = sys.float_info.min

            for solver in self.list_columns():
                solver_score = self.get_value(instance, solver)

                if solver_score > score:
                    score = solver_score

            scores.append(score)

        return scores

    def calc_virtual_best_score_of_portfolio_on_instance(
            self: SparklePerformanceDataCSV, instance: str,
            minimise: bool, capvalue: float = None) -> float:
        """Return the VBS performance for a specific instance.

        Args:
            instance: For which instance we shall calculate the VBS
            minimise: Whether we should minimise or maximise the score
            capvalue: The minimum/maximum scoring value the VBS is allowed to have

        Returns:
            The virtual best solver performance for this instance.
        """
        penalty_factor = sgh.settings.get_general_penalty_multiplier()
        virtual_best_score = None
        for solver in self.list_columns():
            score_solver = float(self.get_value(instance, solver))
            if virtual_best_score is None or\
                    minimise and virtual_best_score > score_solver or\
                    not minimise and virtual_best_score < score_solver:
                virtual_best_score = score_solver

        # Shouldn't this throw an error?
        if virtual_best_score is None and len(self.list_columns()) == 0:
            virtual_best_score = 0
        elif capvalue is not None:
            if minimise and virtual_best_score > capvalue or not minimise and\
                    virtual_best_score < capvalue:
                virtual_best_score = capvalue * penalty_factor

        return virtual_best_score

    def calc_virtual_best_performance_of_portfolio(
            self: SparklePerformanceDataCSV,
            aggregation_function: Callable[[list[float]], float],
            minimise: bool,
            capvalue_list: list[float]) -> float:
        """Return the overall VBS performance of the portfolio.

        Args:
            aggregation_function: The method of combining all VBS scores together
            minimise: Whether the scores are minimised or not
            capvalue_list: List of capvalue per instance

        Returns:
            The combined virtual best performance of the portfolio over all instances.
        """
        virtual_best = []
        capvalue = None
        for instance_idx in range(len(self.list_rows())):
            instance = self.get_row_name(instance_idx)
            if capvalue_list is not None:
                capvalue = capvalue_list[instance_idx]

            virtual_best_score = (
                self.calc_virtual_best_score_of_portfolio_on_instance(
                    instance, minimise, capvalue))
            virtual_best.append(virtual_best_score)

        return aggregation_function(virtual_best)

    def get_dict_vbs_penalty_time_on_each_instance(self: SparklePerformanceDataCSV) \
            -> dict:
        """Return a dictionary of penalised runtimes and instances for the VBS."""
        mydict = {}
        for instance in self.list_rows():
            vbs_penalty_time = sgh.settings.get_penalised_time()
            for solver in self.list_columns():
                runtime = self.get_value(instance, solver)
                if runtime < vbs_penalty_time:
                    vbs_penalty_time = runtime
            mydict[instance] = vbs_penalty_time

        return mydict

    def calc_vbs_penalty_time(self: SparklePerformanceDataCSV) -> float:
        """Return the penalised performance of the VBS."""
        cutoff_time = sgh.settings.get_general_target_cutoff_time()
        penalty_multiplier = sgh.settings.get_general_penalty_multiplier()

        penalty_time_each_run = cutoff_time * penalty_multiplier
        vbs_penalty_time = 0.0
        vbs_count = 0

        for instance in self.list_rows():
            vbs_penalty_time_on_this_instance = -1
            vbs_count += 1
            for solver in self.list_columns():
                this_run_time = self.get_value(instance, solver)
                if (vbs_penalty_time_on_this_instance < 0
                   or vbs_penalty_time_on_this_instance > this_run_time):
                    vbs_penalty_time_on_this_instance = this_run_time
            if vbs_penalty_time_on_this_instance > cutoff_time:
                vbs_penalty_time_on_this_instance = penalty_time_each_run
            vbs_penalty_time += vbs_penalty_time_on_this_instance

        vbs_penalty_time = vbs_penalty_time / vbs_count

        return vbs_penalty_time

    def get_solver_penalty_time_ranking_list(self: SparklePerformanceDataCSV)\
            -> list[list[float]]:
        """Return a list with solvers ranked by penalised runtime."""
        cutoff_time = sgh.settings.get_general_target_cutoff_time()
        penalty_multiplier = sgh.settings.get_general_penalty_multiplier()

        solver_penalty_time_ranking_list = []
        penalty_time_each_run = cutoff_time * penalty_multiplier

        for solver in self.list_columns():
            this_penalty_time = 0.0
            this_count = 0
            for instance in self.list_rows():
                this_run_time = self.get_value(instance, solver)
                this_count += 1
                if this_run_time <= cutoff_time:
                    this_penalty_time += this_run_time
                else:
                    this_penalty_time += penalty_time_each_run
            this_penalty_time = this_penalty_time / this_count
            solver_penalty_time_ranking_list.append([solver, this_penalty_time])

        solver_penalty_time_ranking_list.sort(
            key=lambda this_penalty_time: this_penalty_time[1])

        return solver_penalty_time_ranking_list
