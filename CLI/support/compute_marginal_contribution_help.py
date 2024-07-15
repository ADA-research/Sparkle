#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for marginal contribution computation."""
from __future__ import annotations
import sys
import csv
from pathlib import Path
from typing import Callable
from statistics import mean

import global_variables as gv
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from CLI.construct_sparkle_portfolio_selector import construct_sparkle_portfolio_selector
import sparkle_logging as sl
from sparkle.types.objective import PerformanceMeasure


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
        minimise: bool = True,
        performance_data_csv_path: Path = gv.performance_data_csv_path,
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
    perfect_margi_cont_path = gv.sparkle_marginal_contribution_perfect_path

    # If the marginal contribution already exists in file, read it and return
    if not flag_recompute and perfect_margi_cont_path.is_file():
        print("Marginal contribution for the perfect selector already computed, reading "
              "from file instead! Use --recompute to force recomputation.")
        return read_marginal_contribution_csv(perfect_margi_cont_path)

    print("In this calculation, cutoff time for each run is "
          f"{gv.settings.get_general_target_cutoff_time()} seconds")

    rank_list = []
    penalty_list = None
    if capvalue_list is not None:
        penalty_factor = gv.settings.get_general_penalty_multiplier()
        penalty_list = [cap * penalty_factor for cap in capvalue_list]
    performance_data = PerformanceDataFrame(performance_data_csv_path)

    best_performance = performance_data.best_performance(
        aggregation_function, minimise, capvalue_list, penalty_list)
    print(f"Virtual best performance for portfolio selector is {best_performance}")

    for solver in performance_data.dataframe.columns:
        solver_name = Path(solver).name
        tmp_virt_best_perf = performance_data.best_performance(
            aggregation_function, minimise, capvalue_list, penalty_list, [solver])
        print("Virtual best performance for portfolio selector excluding solver "
              f"{solver_name} is {tmp_virt_best_perf}")
        if minimise and tmp_virt_best_perf > best_performance or\
           not minimise and tmp_virt_best_perf < best_performance:
            marginal_contribution = tmp_virt_best_perf / best_performance
        else:
            marginal_contribution = 0.0

        solver_tuple = (solver, marginal_contribution)
        rank_list.append(solver_tuple)
        print(f"Marginal contribution (to Perfect Selector) for solver {solver_name} is "
              f"{marginal_contribution}")

    rank_list.sort(key=lambda marginal_contribution: marginal_contribution[1],
                   reverse=True)

    # Write perfect selector contributions to file
    write_marginal_contribution_csv(perfect_margi_cont_path, rank_list)

    return rank_list


def compute_actual_selector_performance(
        actual_portfolio_selector_path: str,
        performance_data: PerformanceDataFrame,
        feature_data: FeatureDataFrame,
        minimise: bool,
        aggregation_function: Callable[[list[float]], float],
        capvalue_list: list[float] | None = None) -> float:
    """Return the performance of the selector over all instances.

    Args:
      actual_portfolio_selector_path: Path to portfolio selector.
      performance_data: The performance data.
      feature_data: The feature data.
      minimise: Flag indicating, if scores should be minimised.
      aggregation_function: function to aggregate the performance per instance
      capvalue_list: Optional list of cap-values.

    Returns:
      The selector performance as a single floating point number.
    """
    penalty_factor = gv.settings.get_general_penalty_multiplier()
    performances = []
    perf_measure = gv.settings.get_general_sparkle_objectives()[0].PerformanceMeasure
    capvalue = None
    for index, instance in enumerate(performance_data.instances):
        if capvalue_list is not None:
            capvalue = capvalue_list[index]
        # We get the performance for an instance by infering the model predicition
        # for the instance.
        performance_instance, flag_success = compute_actual_performance_for_instance(
            actual_portfolio_selector_path, instance, feature_data,
            performance_data, minimise, perf_measure, capvalue)

        if not flag_success and capvalue is not None:
            performance_instance = capvalue * penalty_factor

        performances.append(performance_instance)

    return aggregation_function(performances)


def compute_actual_performance_for_instance(
        actual_portfolio_selector_path: Path,
        instance: str,
        feature_data: FeatureDataFrame,
        performance_data: PerformanceDataFrame,
        minimise: bool,
        objective_type: PerformanceMeasure,
        capvalue: float) -> tuple[float, bool]:
    """Return the actual performance of the selector on a given instance.

    Args:
      actual_portfolio_selector_path: Path to the portfolio selector.
      instance: Instance name.
      feature_data: The feature data.
      performance_data: The Performance data
      minimise: Whether the performance value should be minimized or maximized
      objective_type: Whether we are dealing with run time or not.
      capvalue: Cap value for this instance

    Returns:
      A 2-tuple where the first entry is the performance measure and
      the second entry is a Boolean indicating whether the instance was solved
      within the cutoff time (Runtime) or at least one solver performance
      did not exceed capvalue
    """
    # Get the prediction of the selector over the solvers
    selector = gv.settings.get_general_sparkle_selector()
    feature_vector = feature_data.get_instance(instance)
    predict_schedule = selector.run(actual_portfolio_selector_path, feature_vector)

    performance = None
    flag_successfully_solving = False
    cutoff_time = gv.settings.get_general_target_cutoff_time()
    if objective_type == PerformanceMeasure.RUNTIME:
        performance_list = []
        # In case of Runtime, we loop through the selected solvers
        for solver, schedule_cutoff in predict_schedule:
            # A prediction is a solver and its score given by the Selector
            performance = float(performance_data.get_value(solver, instance))
            performance_list.append(performance)
            # 1. if performance <= predicted runtime we have a successfull solver
            if performance <= schedule_cutoff:
                # 2. Success if the tried solvers < selector cutoff_time
                if sum(performance_list) <= cutoff_time:
                    flag_successfully_solving = True
                break
            # 3. Else, we set the failed solver to the cutoff time
            performance_list[-1] = schedule_cutoff

            # 4. If we have exceeded cutoff_time, we are done
            if sum(performance_list) > cutoff_time:
                break

        performance = sum(performance_list)
    else:
        # Minimum or maximum of predicted solvers (Aggregation function)
        performance_list = []
        for solver, _ in predict_schedule:
            solver_performance = performance_data.get_value(solver, instance)
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
        performance_data_csv_path: Path = gv.performance_data_csv_path,
        feature_data_csv_path: Path = gv.feature_data_csv_path,
        flag_recompute: bool = False,
        selector_timeout: int = 172000) -> list[tuple[str, float]]:
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
    actual_margi_cont_path = gv.sparkle_marginal_contribution_actual_path

    # If the marginal contribution already exists in file, read it and return
    if not flag_recompute and actual_margi_cont_path.is_file():
        print("Marginal contribution for the actual selector already computed, reading "
              "from file instead! Use --recompute to force recomputation.")
        rank_list = read_marginal_contribution_csv(actual_margi_cont_path)

        return rank_list

    print("In this calculation, cutoff time for each run is "
          f"{gv.settings.get_general_target_cutoff_time()} seconds")

    rank_list = []

    # Get values from CSV while all solvers and instances are included
    performance_df = PerformanceDataFrame(performance_data_csv_path)
    feature_df = FeatureDataFrame(feature_data_csv_path)

    if not Path("Tmp/").exists():
        Path("Tmp/").mkdir()

    # Compute performance of actual selector
    print("Computing actual performance for portfolio selector with all solvers ...")
    actual_portfolio_selector_path = gv.sparkle_algorithm_selector_path
    construct_sparkle_portfolio_selector(actual_portfolio_selector_path,
                                         performance_df,
                                         feature_df,
                                         selector_timeout=selector_timeout)

    if not Path(actual_portfolio_selector_path).exists():
        print(f"****** ERROR: {actual_portfolio_selector_path} does not exist! ******")
        print("****** ERROR: AutoFolio constructing the actual portfolio selector with"
              " all solvers failed! ******")
        print("****** Use virtual best performance instead of actual "
              "performance for this portfolio selector! ******")
        sys.exit(-1)

    actual_selector_performance = compute_actual_selector_performance(
        actual_portfolio_selector_path, performance_df,
        feature_df, minimise, aggregation_function, capvalue_list)

    print("Actual performance for portfolio selector with all solvers is "
          f"{actual_selector_performance}")
    print("Computing done!")

    # Compute contribution per solver
    #This could be parallelised
    for solver in performance_df.dataframe.columns:
        solver_name = Path(solver).name
        print("Computing actual performance for portfolio selector excluding solver "
              f"{solver_name} ...")
        # 1. Copy the dataframe original df
        tmp_performance_df = performance_df.copy()

        # 2. Remove the solver from this copy
        tmp_performance_df.remove_solver(solver)

        # 3. create the actual selector path
        tmp_actual_portfolio_selector_path = (
            gv.sparkle_algorithm_selector_dir / f"without_{solver_name}"
            / f"{gv.sparkle_algorithm_selector_name}")

        if tmp_performance_df.num_solvers >= 1:
            # 4. Construct the portfolio selector for this subset
            construct_sparkle_portfolio_selector(
                tmp_actual_portfolio_selector_path, tmp_performance_df,
                feature_df)
        else:
            print("****** WARNING: No solver exists ! ******")

        if not Path(tmp_actual_portfolio_selector_path).exists():
            print(f"****** ERROR: {tmp_actual_portfolio_selector_path} does not exist!"
                  " ******")
            print("****** ERROR: AutoFolio constructing the actual portfolio selector "
                  f"excluding solver {solver_name} failed! ******")
            sys.exit(-1)

        tmp_asp = compute_actual_selector_performance(
            tmp_actual_portfolio_selector_path, tmp_performance_df,
            feature_df, minimise, aggregation_function, capvalue_list)

        print(f"Actual performance for portfolio selector excluding solver {solver_name}"
              f" is {tmp_asp}")
        print("Computing done!")

        # 1. If the performance remains equal, this solver did not contribute
        # 2. If there is a performance decay without this solver, it does contribute
        # 3. If there is a performance improvement, we have a bad portfolio selector
        if tmp_asp == actual_selector_performance:
            marginal_contribution = 0.0
        elif minimise and tmp_asp > actual_selector_performance or not minimise and\
                tmp_asp < actual_selector_performance:
            marginal_contribution = tmp_asp / actual_selector_performance
        else:
            print("****** WARNING DUBIOUS SELECTOR/SOLVER: "
                  f"The omission of solver {solver_name} yields an improvement. "
                  "The selector improves better without this solver. It may be usefull "
                  "to construct a portfolio without this solver.")
            marginal_contribution = 0.0

        solver_tuple = (solver, marginal_contribution)
        rank_list.append(solver_tuple)
        print(f"Marginal contribution (to Actual Selector) for solver {solver_name} is "
              f"{marginal_contribution}")

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
        flag_recompute: bool, selector_timeout: int) -> None:
    """Compute the marginal contribution.

    Args:
        flag_compute_perfect: Flag indicating if the contribution for the perfect
            portfolio selector should be computed.
        flag_compute_actual: Flag indicating if the contribution for the actual portfolio
             selector should be computed.
        flag_recompute: Flag indicating whether marginal contributions
            should be recalculated.
        selector_timeout: The cuttoff time to configure the algorithm selector.
    """
    performance_data_csv = PerformanceDataFrame(gv.performance_data_csv_path)
    performance_measure =\
        gv.settings.get_general_sparkle_objectives()[0].PerformanceMeasure
    aggregation_function = gv.settings.get_general_metric_aggregation_function()
    if performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION:
        capvalue_list = gv.settings.get_general_cap_value()
        minimise = False
    elif performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION:
        capvalue = gv.settings.get_general_cap_value()
        minimise = True
    else:
        # assume runtime optimization
        capvalue = gv.settings.get_general_target_cutoff_time()
        minimise = True

    num_of_instances = performance_data_csv.num_instances
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
            flag_recompute=flag_recompute,
            selector_timeout=selector_timeout
        )
        print_rank_list(rank_list, "actual selector")
        print("Marginal contribution (actual selector) computing done!")
