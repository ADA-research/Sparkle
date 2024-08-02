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
    performance_path = actual_portfolio_selector.parent / "performance.csv"
    if performance_path.exists():
        selector_performance_data = PerformanceDataFrame(performance_path)
        return aggregation_function(
            selector_performance_data.get_values("portfolio_selector"))
    penalty_factor = gv.settings().get_general_penalty_multiplier()
    objective = gv.settings().get_general_sparkle_objectives()[0]
    perf_measure = objective.PerformanceMeasure
    selector_performance_data = performance_data.copy()
    for solver in selector_performance_data.solvers:
        selector_performance_data.remove_solver(solver)
    selector_performance_data.add_solver("portfolio_selector")
    selector_performance_data.csv_filepath =\
        actual_portfolio_selector.parent / "performance.csv"
    selector = gv.settings().get_general_sparkle_selector()
    for instance in performance_data.instances:
        # We get the performance for an instance by infering the model predicition
        # for the instance.
        feature_vector = feature_data.get_instance(instance)
        predict_schedule = selector.run(actual_portfolio_selector, feature_vector)
        performance_instance = compute_actual_performance_for_instance(
            predict_schedule, instance, performance_data, minimise,
            perf_measure, performance_cutoff)
        selector_performance_data.set_value(performance_instance,
                                            "portfolio_selector",
                                            instance,
                                            objective=objective.str_id)
    if performance_cutoff is not None:
        selector_performance_data.penalise(performance_cutoff,
                                           performance_cutoff * penalty_factor,
                                           lower_bound=minimise)
    selector_performance_data.save_csv()
    return aggregation_function(
        selector_performance_data.get_values("portfolio_selector"))


def compute_actual_performance_for_instance(
        predict_schedule: list[tuple[str, float]],
        instance: str,
        performance_data: PerformanceDataFrame,
        minimise: bool,
        objective_type: PerformanceMeasure,
        performance_cutoff: float = None) -> float:
    """Return the actual performance of the selector on a given instance.

    Args:
      predict_schedule: The prediction schedule.
      instance: Instance name.
      performance_data: The Performance data
      minimise: Whether the performance value should be minimized or maximized
      objective_type: Whether we are dealing with run time or not.
      performance_cutoff: Cutoff value for this instance

    Returns:
      The aggregated performance measure aggregated over all instances.
    """
    compare = operator.lt if minimise else operator.gt
    total_performance = None
    if objective_type == PerformanceMeasure.RUNTIME:
        performance_list = []
        # A prediction schedule yields a solver and for how long its allowed to run
        for solver, schedule_cutoff in predict_schedule:
            # A prediction is a solver and its MAXIMUM RUNTIME
            solver_performance = float(performance_data.get_value(solver, instance))
            # We run the solver up to its scheduled cut off
            performance_list.append(min(schedule_cutoff, solver_performance))
            total_performance = sum(performance_list)
            # If the solver was not killed by the selector
            if solver_performance <= schedule_cutoff:
                break  # We have found a working solver, break
            # If we have exceeded cutoff_time, we are done
            if performance_cutoff is not None and total_performance > performance_cutoff:
                break
    else:
        # Minimum or maximum of predicted solvers
        for solver, _ in predict_schedule:
            solver_performance = float(performance_data.get_value(solver, instance))
            if total_performance is None or compare(solver_performance,
                                                    total_performance):
                total_performance = solver_performance
    return total_performance


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
