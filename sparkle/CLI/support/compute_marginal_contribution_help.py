#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for marginal contribution computation."""
from __future__ import annotations
import sys
import ast
import operator
from pathlib import Path
from typing import Callable
from statistics import mean
import tabulate

from sparkle.CLI.help import global_variables as gv
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.types.objective import PerformanceMeasure


def compute_perfect_selector_marginal_contribution(
        performance_data: PerformanceDataFrame,
        aggregation_function: Callable[[list[float]], float] = mean,
        minimise: bool = True) -> list[tuple[str, float]]:
    """Return the marginal contributions of solvers for the VBS.

    Args:
      performance_data: Performance DataFrame to compute the contribution for.
      aggregation_function: function to aggregate the per instance scores
      minimise: flag indicating if scores should be minimised or maximised

    Returns:
      A list of 3-tuples of the form:
        (solver name, marginal contribution, best score w/o solver).
    """
    contribution_data = performance_data.marginal_contribution(aggregation_function,
                                                               minimise)
    contribution_data.sort(key=lambda contribution: contribution[1], reverse=True)
    return contribution_data


def compute_actual_selector_performance(
        actual_portfolio_selector: Path,
        performance_data: PerformanceDataFrame,
        feature_data: FeatureDataFrame,
        minimise: bool,
        aggregation_function: Callable[[list[float]], float],
        performance_cutoff: int | float = None) -> float:
    """Return the performance of the selector over all instances.

    Args:
      actual_portfolio_selector: Path to portfolio selector.
      performance_data: The performance data.
      feature_data: The feature data.
      minimise: Flag indicating, if scores should be minimised.
      aggregation_function: function to aggregate the performance per instance
      performance_cutoff: Optional performance cutoff.

    Returns:
      The selector performance as a single floating point number.
    """
    penalty_factor = gv.settings().get_general_penalty_multiplier()
    performances = []
    perf_measure = gv.settings().get_general_sparkle_objectives()[0].PerformanceMeasure
    for instance in performance_data.instances:
        # We get the performance for an instance by infering the model predicition
        # for the instance.
        performance_instance, flag_success = compute_actual_performance_for_instance(
            actual_portfolio_selector, instance, feature_data,
            performance_data, minimise, perf_measure, performance_cutoff)

        if not flag_success and performance_cutoff is not None:
            performance_instance = performance_cutoff * penalty_factor

        performances.append(performance_instance)

    return aggregation_function(performances)


def compute_actual_performance_for_instance(
        actual_portfolio_selector: Path,
        instance: str,
        feature_data: FeatureDataFrame,
        performance_data: PerformanceDataFrame,
        minimise: bool,
        objective_type: PerformanceMeasure,
        performance_cutoff: float = None) -> tuple[float, bool]:
    """Return the actual performance of the selector on a given instance.

    Args:
      actual_portfolio_selector: Path to the portfolio selector.
      instance: Instance name.
      feature_data: The feature data.
      performance_data: The Performance data
      minimise: Whether the performance value should be minimized or maximized
      objective_type: Whether we are dealing with run time or not.
      performance_cutoff: Cutoff value for this instance

    Returns:
      A 2-tuple where the first entry is the performance measure and
      the second entry is a Boolean indicating whether the instance was solved
      within the cutoff time (Runtime) or at least one solver performance
      did not exceed capvalue
    """
    # Get the prediction of the selector over the solvers
    selector = gv.settings().get_general_sparkle_selector()
    feature_vector = feature_data.get_instance(instance)
    predict_schedule = selector.run(actual_portfolio_selector, feature_vector)
    compare = operator.lt if minimise else operator.gt

    performance = None
    flag_successfully_solving = False
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
                if sum(performance_list) <= performance_cutoff:
                    flag_successfully_solving = True
                break
            # 3. Else, we set the failed solver to the cutoff time
            performance_list[-1] = schedule_cutoff
            performance = sum(performance_list)
            # 4. If we have exceeded cutoff_time, we are done
            if performance_cutoff is not None and performance > performance_cutoff:
                break
    else:
        # Minimum or maximum of predicted solvers
        for solver, _ in predict_schedule:
            solver_performance = float(performance_data.get_value(solver, instance))
            if performance is None or compare(solver_performance, performance):
                performance = solver_performance

    return performance, flag_successfully_solving


def compute_actual_selector_marginal_contribution(
        performance_data: PerformanceDataFrame,
        feature_data: FeatureDataFrame,
        selector_scenario: Path,
        aggregation_function: Callable[[list[float]], float] = mean,
        performance_cutoff: int | float = None,
        minimise: bool = True) -> list[tuple[str, float]]:
    """Compute the marginal contributions of solvers in the selector.

    Args:
      performance_data: Performance data object
      aggregation_function: Function to aggregate score values
      minimise: Flag indicating if scores should be minimised
      performance_cutoff: The cutoff performance of a solver
      feature_data_csv_path: Path to the CSV file with the feature data.
      flag_recompute: Boolean indicating whether marginal contributions should
        be recalculated even if they already exist in a file. Defaults to False.

    Returns:
      A list of 2-tuples where every 2-tuple is of the form
        (solver name, marginal contribution, best_performance).
    """
    actual_margi_cont_path = selector_scenario / "marginal_contribution_actual.txt"
    # If the marginal contribution already exists in file, read it and return
    if actual_margi_cont_path.is_file():
        print("Marginal contribution for selector already computed, reading from file.")
        return ast.literal_eval(actual_margi_cont_path.open().read())

    print(f"In this calculation, cutoff is {performance_cutoff} seconds")

    actual_portfolio_selector_path = selector_scenario / "portfolio_selector"

    if not actual_portfolio_selector_path.exists():
        print(f"ERROR: Selector {actual_portfolio_selector_path} does not exist! "
              "Cannot compute marginal contribution.")
        sys.exit(-1)

    actual_selector_performance = compute_actual_selector_performance(
        actual_portfolio_selector_path, performance_data,
        feature_data, minimise, aggregation_function, performance_cutoff)

    print("Actual performance for portfolio selector with all solvers is "
          f"{actual_selector_performance}")

    rank_list = []
    compare = operator.lt if minimise else operator.gt
    # Compute contribution per solver
    # NOTE: This could be parallelised
    for solver in performance_data.solvers:
        solver_name = Path(solver).name
        print("Computing actual performance for portfolio selector excluding solver "
              f"{solver_name} ...")
        # 1. Copy the dataframe original df
        tmp_performance_df = performance_data.copy()
        # 2. Remove the solver from this copy
        tmp_performance_df.remove_solver(solver)
        ablated_actual_portfolio_selector =\
            selector_scenario / f"ablate_{solver_name}" / "portfolio_selector"
        if not ablated_actual_portfolio_selector.exists():
            print(f"WARNING: Selector without {solver_name} does not exist! "
                  f"Cannot compute marginal contribution without {solver_name}.")
            continue

        ablated_asp = compute_actual_selector_performance(
            ablated_actual_portfolio_selector, tmp_performance_df,
            feature_data, minimise, aggregation_function, performance_cutoff)

        print(f"Actual performance for portfolio selector ex. solver {solver_name} is "
              f"{ablated_asp}. Computing done!")

        # 1. If the performance remains equal, this solver did not contribute
        # 2. If there is a performance decay without this solver, it does contribute
        # 3. If there is a performance improvement, we have a bad portfolio selector
        if ablated_asp == actual_selector_performance:
            marginal_contribution = 0.0
        elif not compare(ablated_asp, actual_selector_performance):
            # In the case that the performance decreases, we have a contributing solver
            marginal_contribution = ablated_asp / actual_selector_performance
        else:
            print("****** WARNING DUBIOUS SELECTOR/SOLVER: "
                  f"The omission of solver {solver_name} yields an improvement. "
                  "The selector improves better without this solver. It may be usefull "
                  "to construct a portfolio without this solver.")
            marginal_contribution = 0.0

        rank_list.append((solver, marginal_contribution, ablated_asp))
        print(f"Marginal contribution (to Actual Selector) for solver {solver_name} is "
              f"{marginal_contribution}")

    rank_list.sort(key=lambda contribution: contribution[1], reverse=True)

    # Write actual selector contributions to file
    actual_margi_cont_path.open("w").write(str(rank_list))
    return rank_list


def compute_marginal_contribution(
        scenario: Path,
        flag_compute_perfect: bool, flag_compute_actual: bool) -> None:
    """Compute the marginal contribution.

    Args:
        scenario: Path to the selector scenario for which to compute
        flag_compute_perfect: Flag indicating if the contribution for the perfect
            portfolio selector should be computed.
        flag_compute_actual: Flag indicating if the contribution for the actual portfolio
             selector should be computed.
    """
    performance_data = PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path)
    feature_data = FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)
    performance_measure =\
        gv.settings().get_general_sparkle_objectives()[0].PerformanceMeasure
    aggregation_function = gv.settings().get_general_metric_aggregation_function()
    capvalue = gv.settings().get_general_cap_value()
    if performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION:
        minimise = False
    elif performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION:
        minimise = True
    else:
        # assume runtime optimization
        capvalue = gv.settings().get_general_target_cutoff_time()
        minimise = True

    if not (flag_compute_perfect | flag_compute_actual):
        print("ERROR: compute_marginal_contribution called without a flag set to"
              " True, stopping execution")
        sys.exit(-1)

    if flag_compute_perfect:
        print("Computing each solver's marginal contribution to perfect selector ...")
        contribution_data = compute_perfect_selector_marginal_contribution(
            performance_data,
            aggregation_function,
            minimise)
        table = tabulate.tabulate(
            contribution_data,
            headers=["Solver", "Marginal Contribution", "Best Performance"],)
        print(table, "\n")
        print("Marginal contribution (perfect selector) computing done!")

    if flag_compute_actual:
        print("Start computing marginal contribution per Solver to actual selector...")
        contribution_data = compute_actual_selector_marginal_contribution(
            performance_data,
            feature_data,
            scenario,
            aggregation_function,
            capvalue,
            minimise
        )
        table = tabulate.tabulate(
            contribution_data,
            headers=["Solver", "Marginal Contribution", "Best Performance"],)
        print(table, "\n")
        print("Marginal contribution (actual selector) computing done!")
