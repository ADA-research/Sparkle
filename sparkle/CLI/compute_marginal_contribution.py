#!/usr/bin/env python3
"""Sparkle command for the computation of the marginal contributions."""
import sys
import argparse
from pathlib import Path
import operator
from typing import Callable
from statistics import mean

import tabulate

from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.platform.settings_objects import SettingState
from sparkle.CLI.help import argparse_custom as ac
from sparkle.platform import CommandName, COMMAND_DEPENDENCIES
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as apc
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.types.objective import PerformanceMeasure


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(*apc.PerfectArgument.names,
                        **apc.PerfectArgument.kwargs)
    parser.add_argument(*apc.ActualArgument.names,
                        **apc.ActualArgument.kwargs)
    parser.add_argument(*apc.PerformanceMeasureArgument.names,
                        **apc.PerformanceMeasureArgument.kwargs)
    parser.add_argument(*apc.SettingsFileArgument.names,
                        **apc.SettingsFileArgument.kwargs)

    return parser


def compute_selector_performance(
        actual_portfolio_selector: Path,
        performance_data: PerformanceDataFrame,
        feature_data: FeatureDataFrame,
        minimise: bool,
        aggregation_function: Callable[[list[float]], float],
        performance_cutoff: int | float = None) -> float:
    """Return the performance of a selector over all instances.

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
    selector_performance_data = performance_data.copy()

    selector_performance_data.add_solver("portfolio_selector")
    selector_performance_data.csv_filepath =\
        actual_portfolio_selector.parent / "performance.csv"
    selector = gv.settings().get_general_sparkle_selector()

    schedule = {}
    for instance in performance_data.instances:
        # We get the performance for an instance by infering the model predicition
        # for the instance.
        feature_vector = feature_data.get_instance(instance)
        schedule[instance] = selector.run(actual_portfolio_selector, feature_vector)
    schedule_performance = selector_performance_data.schedule_performance(
        schedule, target_solver="portfolio_selector", minimise=minimise)
    # Remove solvers from the dataframe
    selector_performance_data.remove_solver(performance_data.solvers)
    if performance_cutoff is not None:
        selector_performance_data.penalise(performance_cutoff,
                                           performance_cutoff * penalty_factor,
                                           lower_bound=not minimise)
    selector_performance_data.save_csv()  # Save the results to disk
    return aggregation_function(schedule_performance)


def compute_selector_marginal_contribution(
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
    portfolio_selector_path = selector_scenario / "portfolio_selector"

    if not portfolio_selector_path.exists():
        print(f"ERROR: Selector {portfolio_selector_path} does not exist! "
              "Cannot compute marginal contribution.")
        sys.exit(-1)

    selector_performance = compute_selector_performance(
        portfolio_selector_path, performance_data,
        feature_data, minimise, aggregation_function, performance_cutoff)

    rank_list = []
    compare = operator.lt if minimise else operator.gt
    # Compute contribution per solver
    # NOTE: This could be parallelised
    for solver in performance_data.solvers:
        solver_name = Path(solver).name
        # 1. Copy the dataframe original df
        tmp_performance_df = performance_data.copy()
        # 2. Remove the solver from this copy
        tmp_performance_df.remove_solver(solver)
        ablated_actual_portfolio_selector =\
            selector_scenario / f"ablate_{solver_name}" / "portfolio_selector"
        if not ablated_actual_portfolio_selector.exists():
            print(f"WARNING: Selector without {solver_name} does not exist! "
                  f"Cannot compute marginal contribution of {solver_name}.")
            continue

        ablated_selector_performance = compute_selector_performance(
            ablated_actual_portfolio_selector, tmp_performance_df,
            feature_data, minimise, aggregation_function, performance_cutoff)

        # 1. If the performance remains equal, this solver did not contribute
        # 2. If there is a performance decay without this solver, it does contribute
        # 3. If there is a performance improvement, we have a bad portfolio selector
        if ablated_selector_performance == selector_performance:
            marginal_contribution = 0.0
        elif not compare(ablated_selector_performance, selector_performance):
            # In the case that the performance decreases, we have a contributing solver
            marginal_contribution = ablated_selector_performance / selector_performance
        else:
            print("****** WARNING DUBIOUS SELECTOR/SOLVER: "
                  f"The omission of solver {solver_name} yields an improvement. "
                  "The selector improves better without this solver. It may be usefull "
                  "to construct a portfolio without this solver.")
            marginal_contribution = 0.0

        rank_list.append((solver, marginal_contribution, ablated_selector_performance))

    rank_list.sort(key=lambda contribution: contribution[1], reverse=True)
    return rank_list


def compute_marginal_contribution(
        scenario: Path,
        compute_perfect: bool, compute_actual: bool) -> None:
    """Compute the marginal contribution.

    Args:
        scenario: Path to the selector scenario for which to compute
        compute_perfect: Bool indicating if the contribution for the perfect
            portfolio selector should be computed.
        compute_actual: Bool indicating if the contribution for the actual portfolio
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

    if compute_perfect:
        # Perfect selector is the computation of the best performance per instance
        print("Computing each solver's marginal contribution to perfect selector ...")
        contribution_data = performance_data.marginal_contribution(aggregation_function,
                                                                   minimise,
                                                                   sort=True)
        table = tabulate.tabulate(
            contribution_data,
            headers=["Solver", "Marginal Contribution", "Best Performance"],)
        print(table, "\n")
        print("Marginal contribution (perfect selector) computing done!")

    if compute_actual:
        print("Start computing marginal contribution per Solver to actual selector...")
        print(f"In this calculation, cutoff is {capvalue} seconds")
        contribution_data = compute_selector_marginal_contribution(
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


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    check_for_initialise(
        COMMAND_DEPENDENCIES[CommandName.COMPUTE_MARGINAL_CONTRIBUTION]
    )

    if ac.set_by_user(args, "settings_file"):
        gv.settings().read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file
    if ac.set_by_user(args, "performance_measure"):
        gv.settings().set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE
        )
    selection_scenario = gv.latest_scenario().get_selection_scenario_path()

    if not (args.perfect | args.actual):
        print("ERROR: compute_marginal_contribution called without a flag set to"
              " True, stopping execution")
        sys.exit(-1)

    compute_marginal_contribution(selection_scenario, args.perfect, args.actual)

    # Write used settings to file
    gv.settings().write_used_settings()
