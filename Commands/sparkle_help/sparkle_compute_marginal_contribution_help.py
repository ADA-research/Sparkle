#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for marginal contribution computation."""

from __future__ import annotations

import subprocess
import sys
import csv
from pathlib import Path
from typing import Callable
from statistics import mean

from Commands.sparkle_help import sparkle_basic_help
from Commands.sparkle_help import sparkle_file_help as sfh
from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from Commands.sparkle_help import sparkle_performance_data_csv_help as spdcsv
from Commands.sparkle_help.sparkle_performance_data_csv_help import \
    SparklePerformanceDataCSV
from Commands.sparkle_help import sparkle_construct_portfolio_selector_help as scps
from Commands.sparkle_help import sparkle_run_portfolio_selector_help as srps
from Commands.sparkle_help import sparkle_logging as sl
from Commands.sparkle_help.sparkle_settings import PerformanceMeasure
from Commands.sparkle_help.sparkle_feature_data_csv_help import SparkleFeatureDataCSV


def read_marginal_contribution_csv(path: Path) -> list[tuple[str, float]]:
    """Read the marginal contriutions from a CSV file.

    Args:
        path: Path to the source CSV file.

    Returns:
        A list of tuples containing the marginal contributions data.
    """
    content = []

    with path.open("r") as input_file:
        reader = csv.reader(input_file)
        for row in reader:
            # 0 is the solver, 1 the marginal contribution
            content.append((row[0], float(row[1])))

    return content


def write_marginal_contribution_csv(path: Path,
                                    content: list[tuple[str, float]]) -> None:
    """Write the marginal contributions to a CSV file.

    Args:
        path: Target path to the CSV file.
        content: A list of 2-tuples. The first component is the string name of the
        solver and the second is the algorithms' marginal contribution.
    """
    with path.open("w") as output_file:
        writer = csv.writer(output_file)
        writer.writerows(content)

        # Add file to log
        sl.add_output(str(path),
                      "Marginal contributions to the portfolio selector per solver.")


def compute_perfect_selector_marginal_contribution(
        aggregation_function: Callable[[list[float]], float] = mean,
        capvalue_list: list[float] = None,
        minimise: bool = min,
        performance_data_csv_path: Path = sgh.performance_data_csv_path,
        flag_recompute: bool = False) -> list[tuple[str, float]]:
    """Return the marginal contributions of solvers for the VBS.

    Args:
      aggregation_function: function to aggregate the per instance scores
      capvalue_list: list of cap values
      minimise: flag indicating if scores should be minimised or maximised
      performance_data_csv_path: Path to the CSV file containing the performance data.
      flag_recompute: Boolean indicating whether a recomputation of the marginal
        contribution is enforced.

    Returns:
      A list of 2-tuples of the form (solver name, marginal contribution).
    """
    perfect_margi_cont_path = sgh.sparkle_marginal_contribution_perfect_path

    # If the marginal contribution already exists in file, read it and return
    if not flag_recompute and perfect_margi_cont_path.is_file():
        print("Marginal contribution for the perfect selector already computed, reading "
              "from file instead! Use --recompute to force recomputation.")
        return read_marginal_contribution_csv(perfect_margi_cont_path)

    print("In this calculation, cutoff time for each run is "
          f"{sgh.settings.get_general_target_cutoff_time()} seconds")

    rank_list = []
    performance_data_csv = spdcsv.SparklePerformanceDataCSV(performance_data_csv_path)

    print("Computing virtual best performance for portfolio selector with all solvers "
          "...")
    virtual_best_performance = (
        performance_data_csv.calc_virtual_best_performance_of_portfolio(
            aggregation_function, minimise, capvalue_list))
    print("Virtual best performance for portfolio selector with all solvers is "
          f"{str(virtual_best_performance)}")
    print("Computing done!")

    for solver in performance_data_csv.list_columns():
        print("Computing virtual best performance for portfolio selector excluding "
              f"solver {sfh.get_last_level_directory_name(solver)} ...")
        tmp_performance_data_csv = spdcsv.SparklePerformanceDataCSV(
            performance_data_csv_path)
        tmp_performance_data_csv.delete_column(solver)
        tmp_virt_best_perf = (
            tmp_performance_data_csv.calc_virtual_best_performance_of_portfolio(
                aggregation_function, minimise, capvalue_list))
        print("Virtual best performance for portfolio selector excluding solver "
              f"{sfh.get_last_level_directory_name(solver)} is "
              f"{str(tmp_virt_best_perf)}")
        print("Computing done!")
        if minimise and tmp_virt_best_perf > virtual_best_performance or\
           not minimise and tmp_virt_best_perf < virtual_best_performance:
            marginal_contribution = tmp_virt_best_perf / virtual_best_performance
        else:
            marginal_contribution = 0.0

        solver_tuple = (solver, marginal_contribution)
        rank_list.append(solver_tuple)
        print("Marginal contribution (to Perfect Selector) for solver "
              f"{sfh.get_last_level_directory_name(solver)} is "
              f"{str(marginal_contribution)}")

    rank_list.sort(key=lambda marginal_contribution: marginal_contribution[1],
                   reverse=True)

    # Write perfect selector contributions to file
    write_marginal_contribution_csv(perfect_margi_cont_path, rank_list)

    return rank_list


def get_list_predict_schedule(actual_portfolio_selector_path: str,
                              feature_data_csv: SparkleFeatureDataCSV,
                              instance: int) -> list[float]:
    """Return the solvers schedule suggested by the selector as a list.

    Args:
      actual_portfolio_selector_path: Path to portfolio selector.
      feature_data_csv: SparkleFeatureDataCSV object with the feature data.
      instance: Instance ID, i.e., the number of the instance.

    Returns:
      List of floating point numbers.
    """
    list_predict_schedule = []
    python_executable = sgh.python_executable
    if not Path("Tmp/").exists():
        Path("Tmp/").mkdir()
    feature_vector_string = feature_data_csv.get_feature_vector_string(instance)

    pred_sched_file = ("predict_schedule_"
                       f"{sparkle_basic_help.get_time_pid_random_string()}.predres")
    log_file = "predict_schedule_autofolio.out"
    err_file = "predict_schedule_autofolio.err"
    predict_schedule_result_file = str(sl.caller_log_dir) + "/" + pred_sched_file
    log_path = sl.caller_log_dir / log_file
    err_path_str = str(sl.caller_log_dir) + "/" + err_file

    cmd = [python_executable, sgh.autofolio_path, "--load",
           actual_portfolio_selector_path, "--feature_vec", feature_vector_string]

    with log_path.open("a+") as log_file:
        print("Running command below to get predicted schedule from autofolio:\n",
              cmd, file=log_file)

    process = subprocess.run(cmd,
                             stdout=Path(predict_schedule_result_file).open("w+"),
                             stderr=Path(err_path_str).open("w+"))
    list_predict_schedule = (
        srps.get_list_predict_schedule_from_file(predict_schedule_result_file))
    if process.returncode != 0:
        sl.add_output(str(log_path), "Predicted portfolio schedule command line call")
        sl.add_output(predict_schedule_result_file, "Predicted portfolio schedule")
        sl.add_output(err_path_str, "Predicted portfolio schedule error output")
    else:
        sfh.rmfiles([predict_schedule_result_file, err_path_str, log_path])

    return list_predict_schedule


def compute_actual_selector_performance(
        actual_portfolio_selector_path: str,
        performance_data_csv_path: str,
        feature_data_csv_path: str,
        minimise: bool,
        aggregation_function: Callable[[list[float]], float],
        capvalue_list: list[float] | None = None) -> float:
    """Return the performance of the selector over all instances.

    Args:
      actual_portfolio_selector_path: Path to portfolio selector.
      performance_data_csv_path: Path to the CSV file with the performance data.
      feature_data_csv_path: path to the CSV file with the features.
      minimise: Flag indicating, if scores should be minimised.
      aggregation_function: function to aggregate the performance per instance
      capvalue_list: Optional list of cap-values.

    Returns:
      The selector performance as a single floating point number.
    """
    performance_data_csv = spdcsv.SparklePerformanceDataCSV(performance_data_csv_path)
    penalty_factor = sgh.settings.get_general_penalty_multiplier()
    performances = []
    perf_measure = sgh.settings.get_general_performance_measure()
    capvalue = None
    for index, instance in enumerate(performance_data_csv.list_rows()):
        if capvalue_list is not None:
            capvalue = capvalue_list[index]
        performance_instance, flag_success = compute_actual_performance_for_instance(
            actual_portfolio_selector_path, instance, feature_data_csv_path,
            performance_data_csv, minimise, perf_measure, capvalue)

        if not flag_success and capvalue is not None:
            performance_instance = capvalue * penalty_factor

        performances.append(performance_instance)

    return aggregation_function(performances)


def compute_actual_performance_for_instance(
        actual_portfolio_selector_path: str,
        instance: str,
        feature_data_csv_path: str,
        performance_data_csv: SparklePerformanceDataCSV,
        minimise: bool,
        objective_type: PerformanceMeasure,
        capvalue: float) -> tuple[float, bool]:
    """Return the actual performance of the selector on a given instance.

    Args:
      actual_portfolio_selector_path: Path to the portfolio selector.
      instance: Instance name.
      feature_data_csv_path: Path to the CSV file with the feature data.
      performance_data_csv: SparklePerformanceDataCSV object that holds the
        performance data.
      minimise: Whether the performance value should be minimized or maximized
      objective_type: Whether we are dealing with run time or not.
      capvalue: Cap value for this instance

    Returns:
      A 2-tuple where the first entry is the performance measure and
      the second entry is a Boolean indicating whether the instance was solved
      within the cutoff time (Runtime) or at least one solver performance
      did not exceed capvalue
    """
    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(feature_data_csv_path)
    # Get the prediction of the selector over the solvers
    list_predict_schedule = get_list_predict_schedule(actual_portfolio_selector_path,
                                                      feature_data_csv, instance)

    performance = None
    flag_successfully_solving = False
    cutoff_time = sgh.settings.get_general_target_cutoff_time()
    if objective_type == PerformanceMeasure.RUNTIME:
        performance_list = []
        # In case of Runtime, we loop through the selected solvers
        for prediction in list_predict_schedule:
            # A prediction is a solver and its score given by the Selector
            performance = float(performance_data_csv.get_value(instance, prediction[0]))
            performance_list.append(performance)
            scheduled_cutoff_time_this_run = prediction[1]
            # 1. if performance <= predicted runtime we have a successfull solver
            if performance <= scheduled_cutoff_time_this_run:
                # 2. Succes if the tried solvers < selector cutoff_time
                if sum(performance_list) <= cutoff_time:
                    flag_successfully_solving = True
                break
            # 3. Else, we sett the failed solver to the cutoff time
            performance_list[-1] = scheduled_cutoff_time_this_run

            # 4. If we have exceeded cutoff_time, we are done
            if sum(performance_list) > cutoff_time:
                break

        performance = sum(performance_list)
    else:
        # Minimum or maximum of predicted solvers (Aggregation function)
        performance_list = []
        for prediction in list_predict_schedule:
            solver_performance = performance_data_csv.get_value(instance, prediction[0])
            performance_list.append(float(solver_performance))

        if minimise:
            performance = min(performance_list)
            if performance <= capvalue:
                flag_successfully_solving = True
        else:
            performance = max(performance_list)
            if performance >= capvalue:
                flag_successfully_solving = True

    return performance, flag_successfully_solving


def compute_actual_selector_marginal_contribution(
        aggregation_function: Callable[[list[float]], float] = mean,
        capvalue_list: list[float] = None,
        minimise: bool = True,
        performance_data_csv_path: str = sgh.performance_data_csv_path,
        feature_data_csv_path: str = sgh.feature_data_csv_path,
        flag_recompute: bool = False) -> list[tuple[str, float]]:
    """Compute the marginal contributions of solvers in the selector.

    Args:
      aggregation_function: Function to aggregate score values
      capvalue_list: List of cap values
      minimise: Flag indicating if scores should be minimised
      performance_data_csv: SparklePerformanceDataCSV object that holds the
        performance data.
      feature_data_csv_path: Path to the CSV file with the feature data.
      flag_recompute: Boolean indicating whether marginal contributions should
        be recalculated even if they already exist in a file. Defaults to False.

    Returns:
      A list of 2-tuples where every 2-tuple is of the form
      (solver name, marginal contribution).
    """
    actual_margi_cont_path = sgh.sparkle_marginal_contribution_actual_path

    # If the marginal contribution already exists in file, read it and return
    if not flag_recompute and actual_margi_cont_path.is_file():
        print("Marginal contribution for the actual selector already computed, reading "
              "from file instead! Use --recompute to force recomputation.")
        rank_list = read_marginal_contribution_csv(actual_margi_cont_path)

        return rank_list

    print("In this calculation, cutoff time for each run is "
          f"{sgh.settings.get_general_target_cutoff_time()} seconds")

    rank_list = []

    # Get values from CSV while all solvers and instances are included
    performance_data_csv = spdcsv.SparklePerformanceDataCSV(performance_data_csv_path)

    if not Path("Tmp/").exists():
        Path("Tmp/").mkdir()

    # Compute performance of actual selector
    print("Computing actual performance for portfolio selector with all solvers ...")
    actual_portfolio_selector_path = sgh.sparkle_algorithm_selector_path
    scps.construct_sparkle_portfolio_selector(actual_portfolio_selector_path,
                                              performance_data_csv_path,
                                              feature_data_csv_path)

    if not Path(actual_portfolio_selector_path).exists():
        print(f"****** ERROR: {actual_portfolio_selector_path} does not exist! ******")
        print("****** ERROR: AutoFolio constructing the actual portfolio selector with"
              " all solvers failed! ******")
        print("****** Use virtual best performance instead of actual "
              "performance for this portfolio selector! ******")
        sys.exit(-1)

    actual_selector_performance = compute_actual_selector_performance(
        actual_portfolio_selector_path, performance_data_csv_path,
        feature_data_csv_path, minimise, aggregation_function, capvalue_list)

    print("Actual performance for portfolio selector with all solvers is "
          f"{str(actual_selector_performance)}")
    print("Computing done!")

    # Compute contribution per solver
    for solver in performance_data_csv.list_columns():
        solver_name = sfh.get_last_level_directory_name(solver)
        print("Computing actual performance for portfolio selector excluding solver "
              f"{solver_name} ...")
        tmp_performance_data_csv = \
            spdcsv.SparklePerformanceDataCSV(performance_data_csv_path)
        tmp_performance_data_csv.delete_column(solver)
        tmp_performance_data_csv_file = (
            f"tmp_performance_data_csv_without_{solver_name}_"
            f"{sparkle_basic_help.get_time_pid_random_string()}.csv")
        tmp_performance_data_csv_path = (
            str(Path(sl.caller_log_dir / tmp_performance_data_csv_file)))
        sl.add_output(tmp_performance_data_csv_path,
                      "[written] Temporary performance data")
        tmp_performance_data_csv.save_csv(tmp_performance_data_csv_path)
        tmp_actual_portfolio_selector_path = (
            "Tmp/tmp_actual_portfolio_selector_"
            f"{sparkle_basic_help.get_time_pid_random_string()}")
        tmp_actual_portfolio_selector_path = (
            sgh.sparkle_algorithm_selector_dir / f"without_{solver_name}"
            / f"{sgh.sparkle_algorithm_selector_name}")

        if len(tmp_performance_data_csv.list_columns()) >= 1:
            scps.construct_sparkle_portfolio_selector(
                tmp_actual_portfolio_selector_path, tmp_performance_data_csv_path,
                feature_data_csv_path)
        else:
            print("****** WARNING: No solver exists ! ******")

        if not Path(tmp_actual_portfolio_selector_path).exists():
            print(f"****** ERROR: {tmp_actual_portfolio_selector_path} does not exist!"
                  " ******")
            print("****** ERROR: AutoFolio constructing the actual portfolio selector "
                  f"excluding solver {solver_name} failed! ******")
            sys.exit(-1)

        tmp_asp = compute_actual_selector_performance(
            tmp_actual_portfolio_selector_path, tmp_performance_data_csv_path,
            feature_data_csv_path, minimise, aggregation_function, capvalue_list)

        print(f"Actual performance for portfolio selector excluding solver "
              f"{solver_name} is {str(tmp_asp)}")
        sfh.rmfiles(tmp_performance_data_csv_path)
        sl.add_output(tmp_performance_data_csv_path,
                      "[removed] Temporary performance data")
        print("Computing done!")

        # 1. If the performance remains equal, this solver has no contribution
        # 2. If there is a performance decay without this solver, it has a contribution
        # 3. If there is a performance improvement, we have a bad selector
        if tmp_asp == actual_selector_performance:
            marginal_contribution = 0.0
        elif minimise and tmp_asp > actual_selector_performance or not minimise and\
                tmp_asp < actual_selector_performance:
            marginal_contribution = tmp_asp / actual_selector_performance
        else:
            print("****** WARNING DUBIOUS SELECTOR/SOLVER:"
                  f" The omission of solver {solver_name} yields an improvement."
                  "The selector improves better without this solver. It may be usefull"
                  " to construct a portfolio without this solver.")
            marginal_contribution = 0.0

        solver_tuple = (solver, marginal_contribution)
        rank_list.append(solver_tuple)
        print(f"Marginal contribution (to Actual Selector) for solver {solver_name} is "
              f"{str(marginal_contribution)}")

    rank_list.sort(key=lambda marginal_contribution: marginal_contribution[1],
                   reverse=True)

    # Write actual selector contributions to file
    write_marginal_contribution_csv(actual_margi_cont_path, rank_list)

    return rank_list


def print_rank_list(rank_list: list, mode: str) -> None:
    """Print the solvers ranked by marginal contribution.

    Args:
      rank_list: A list of 2-tuples as returned by function
        compute_actual_selector_marginal_contribution of the form
        (solver name, marginal contribution).
      mode: The marginal contribution mode used to calculate the rank.
            Either Actual or Virtual.
    """
    print("******")
    print("Solver ranking list via marginal contribution (Margi_Contr) with regards to "
          f"{mode}")
    for i, rank in enumerate(rank_list):
        solver = rank[0]
        marginal_contribution = rank[1]
        print(f"#{i+1}: {Path(solver).name}\t Margi_Contr: {marginal_contribution}")
    print("******")


def compute_marginal_contribution(
        flag_compute_perfect: bool, flag_compute_actual: bool,
        flag_recompute: bool) -> None:
    """Compute the marginal contribution.

    Args:
        flag_compute_perfect: Flag indicating if the contribution for the perfect
            portfolio selector should be computed.
        flag_compute_actual: Flag indicating if the contribution for the actual portfolio
             selector should be computed.
        flag_recompute: Flag indicating whether marginal contributions
            should be recalculated.
    """
    performance_data_csv = (
        spdcsv.SparklePerformanceDataCSV(sgh.performance_data_csv_path))
    performance_measure = sgh.settings.get_general_performance_measure()
    aggregation_function = sgh.settings.get_general_metric_aggregation_function()
    if performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION:
        capvalue_list = sgh.settings.get_general_cap_value()
        minimise = False
    elif performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION:
        capvalue = sgh.settings.get_general_cap_value()
        minimise = True
    else:
        # assume runtime optimization
        capvalue = sgh.settings.get_general_target_cutoff_time()
        minimise = True

    num_of_instances = performance_data_csv.get_number_of_instances()
    if capvalue is list or capvalue is None:
        capvalue_list = capvalue
    else:
        capvalue_list = [capvalue for _ in range(num_of_instances)]

    if not (flag_compute_perfect | flag_compute_actual):
        print("ERROR: compute_marginal_contribution called without a flag set to"
              " True, stopping execution")
        sys.exit(-1)
    if flag_compute_perfect:
        print("Start computing each solver's marginal contribution "
              "to perfect selector ...")
        rank_list = compute_perfect_selector_marginal_contribution(
            aggregation_function,
            capvalue_list,
            minimise,
            flag_recompute=flag_recompute
        )
        print_rank_list(rank_list, "perfect selector")
        print("Marginal contribution (perfect selector) computing done!")
    if flag_compute_actual:
        print("Start computing each solver's marginal contribution "
              "to actual selector ...")
        rank_list = compute_actual_selector_marginal_contribution(
            aggregation_function,
            capvalue_list, minimise,
            flag_recompute=flag_recompute
        )
        print_rank_list(rank_list, "actual selector")
        print("Marginal contribution (actual selector) computing done!")
