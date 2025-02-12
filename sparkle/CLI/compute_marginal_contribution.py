#!/usr/bin/env python3
"""Sparkle command for the computation of the marginal contributions."""
import sys
import argparse
from pathlib import Path
import operator

import tabulate

from sparkle.solver import Selector
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.platform.settings_objects import SettingState
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.initialise import check_for_initialise
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.types import SparkleObjective


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Command to compute the marginal contribution of solvers to the "
                    "portfolio.")
    parser.add_argument(*ac.PerfectSelectorMarginalContributionArgument.names,
                        **ac.PerfectSelectorMarginalContributionArgument.kwargs)
    parser.add_argument(*ac.ActualMarginalContributionArgument.names,
                        **ac.ActualMarginalContributionArgument.kwargs)
    parser.add_argument(*ac.ObjectivesArgument.names,
                        **ac.ObjectivesArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)

    return parser


def compute_selector_performance(
        actual_portfolio_selector: Path,
        performance_data: PerformanceDataFrame,
        feature_data: FeatureDataFrame,
        objective: SparkleObjective) -> float:
    """Return the performance of a selector over all instances.

    Args:
      actual_portfolio_selector: Path to portfolio selector.
      performance_data: The performance data.
      feature_data: The feature data.
      objective: Objective to compute the performance for

    Returns:
      The selector performance as a single floating point number.
    """
    performance_path = actual_portfolio_selector.parent / "performance.csv"
    if performance_path.exists():
        selector_performance_data = PerformanceDataFrame(performance_path)
        return objective.instance_aggregator(
            selector_performance_data.get_values("portfolio_selector",
                                                 objective=str(objective)))
    selector_performance_data = performance_data.clone()

    selector_performance_data.add_solver("portfolio_selector")
    selector_performance_data.csv_filepath =\
        actual_portfolio_selector.parent / "performance.csv"
    selector = Selector(gv.settings().get_selection_class(),
                        gv.settings().get_selection_model())

    schedule = {}
    for instance in performance_data.instances:
        # We get the performance for an instance by infering the model predicition
        # for the instance.
        schedule[instance] = selector.run(actual_portfolio_selector,
                                          instance,
                                          feature_data)

    schedule_performance = selector_performance_data.schedule_performance(
        schedule, target_solver="portfolio_selector", objective=objective)
    # Remove solvers from the dataframe
    selector_performance_data.remove_solver(performance_data.solvers)
    selector_performance_data.save_csv()  # Save the results to disk
    return objective.instance_aggregator(schedule_performance)


def compute_selector_marginal_contribution(
        performance_data: PerformanceDataFrame,
        feature_data: FeatureDataFrame,
        selector_scenario: Path,
        objective: SparkleObjective) -> list[tuple[str, float]]:
    """Compute the marginal contributions of solvers in the selector.

    Args:
      performance_data: Performance data object
      feature_data_csv_path: Path to the CSV file with the feature data.
      selector_scenario: Path to the selector scenario for which to compute
        marginal contribution.
      objective: Objective to compute the marginal contribution for.

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
        feature_data, objective)

    rank_list = []
    compare = operator.lt if objective.minimise else operator.gt
    # Compute contribution per solver
    # NOTE: This could be parallelised
    for solver in performance_data.solvers:
        solver_name = Path(solver).name
        # 1. Copy the dataframe original df
        tmp_performance_df = performance_data.clone()
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
            feature_data, objective)

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
        scenario: Path, compute_perfect: bool, compute_actual: bool) -> None:
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
    objective = gv.settings().get_general_sparkle_objectives()[0]

    if compute_perfect:
        # Perfect selector is the computation of the best performance per instance
        print("Computing each solver's marginal contribution to perfect selector ...")
        contribution_data = performance_data.marginal_contribution(
            objective=objective.name, sort=True)
        table = tabulate.tabulate(
            contribution_data,
            headers=["Solver", "Marginal Contribution", "Best Performance"],)
        print(table, "\n")
        print("Marginal contribution (perfect selector) computing done!")

    if compute_actual:
        print("Start computing marginal contribution per Solver to actual selector...")
        contribution_data = compute_selector_marginal_contribution(
            performance_data,
            feature_data,
            scenario,
            objective
        )
        table = tabulate.tabulate(
            contribution_data,
            headers=["Solver", "Marginal Contribution", "Best Performance"],)
        print(table, "\n")
        print("Marginal contribution (actual selector) computing done!")


def main(argv: list[str]) -> None:
    """Main function of the marginal contribution command."""
    # Log command call
    sl.log_command(sys.argv)
    check_for_initialise()

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)

    if ac.set_by_user(args, "settings_file"):
        gv.settings().read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file
    if ac.set_by_user(args, "objectives"):
        gv.settings().set_general_sparkle_objectives(
            args.objectives, SettingState.CMD_LINE
        )
    selection_scenario = gv.latest_scenario().get_selection_scenario_path()

    if not (args.perfect | args.actual):
        print("ERROR: compute_marginal_contribution called without a flag set to"
              " True, stopping execution")
        sys.exit(-1)

    compute_marginal_contribution(selection_scenario, args.perfect, args.actual)

    # Write used settings to file
    gv.settings().write_used_settings()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
