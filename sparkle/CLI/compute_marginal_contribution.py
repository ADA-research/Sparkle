#!/usr/bin/env python3
"""Sparkle command for the computation of the marginal contributions."""
import sys
import argparse
import operator

import tabulate

from sparkle.selector import SelectionScenario
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.initialise import check_for_initialise
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Command to compute the marginal contribution of solvers to the "
                    "portfolio.")
    parser.add_argument(*ac.PerfectSelectorMarginalContributionArgument.names,
                        **ac.PerfectSelectorMarginalContributionArgument.kwargs)
    parser.add_argument(*ac.ActualMarginalContributionArgument.names,
                        **ac.ActualMarginalContributionArgument.kwargs)
    parser.add_argument(*ac.SelectionScenarioArgument.names,
                        **ac.SelectionScenarioArgument.kwargs)
    return parser


def compute_selector_performance(
        selector_scenario: SelectionScenario,
        feature_data: FeatureDataFrame) -> float:
    """Return the performance of a selector over all instances.

    Args:
      selector_scenario: The Selector scenario to compute the marginal contribution for.
      feature_data: The feature data of the instances.

    Returns:
      The selector performance as a single floating point number.
    """
    selector_performance_data = selector_scenario.selector_performance_data
    missing_instances =\
        [instance for instance in selector_scenario.training_instances
         if selector_performance_data.is_missing(
             SelectionScenario.__selector_solver_name__, instance)]
    if not missing_instances:
        return selector_scenario.objective.instance_aggregator(
            selector_scenario.selector_performance_data.get_value(
                SelectionScenario.__selector_solver_name__,
                instance=selector_scenario.training_instances,
                objective=selector_scenario.objective.name))

    schedule = {}
    for instance in missing_instances:
        # We get the performance for an instance by infering the model predicition
        # for the instance.
        schedule[instance] = selector_scenario.selector.run(
            selector_scenario.selector_file_path,
            instance,
            feature_data)
    schedule_performance = selector_performance_data.schedule_performance(
        schedule, target_solver=SelectionScenario.__selector_solver_name__,
        objective=selector_scenario.objective)
    selector_performance_data.save_csv()  # Save the results to disk
    return selector_scenario.objective.instance_aggregator(schedule_performance)


def compute_selector_marginal_contribution(
        feature_data: FeatureDataFrame,
        selection_scenario: SelectionScenario) -> list[tuple[str, float]]:
    """Compute the marginal contributions of solvers in the selector.

    Args:
      performance_data: Performance data object
      feature_data_csv_path: Path to the CSV file with the feature data.
      selection_scenario: The selector scenario for which to compute
        marginal contribution.
      objective: Objective to compute the marginal contribution for.

    Returns:
      A list of 4-tuples where every 4-tuple is of the form
        (solver_name, config_id, marginal contribution, best_performance).
    """
    if not selection_scenario.selector_file_path.exists():
        print(f"ERROR: Selector {selection_scenario.selector_file_path} does not exist! "
              "Cannot compute marginal contribution.")
        sys.exit(-1)

    selector_performance = compute_selector_performance(
        selection_scenario, feature_data)

    rank_list = []
    compare = operator.lt if selection_scenario.objective.minimise else operator.gt
    # Compute contribution per solver
    # NOTE: This could be parallelised
    for ablation_scenario in selection_scenario.ablation_scenarios:
        # Hacky way of getting the needed data on the ablation
        _, solver_name, config = ablation_scenario.directory.name.split("_", maxsplit=2)
        # TODO: This should be fixed through SPRK-352
        # Hacky way of reconstructing the solver id in the PDF
        solver = f"Solvers/{solver_name}"
        if not ablation_scenario.selector_file_path.exists():
            print(f"WARNING: Selector without {solver_name} does not exist! "
                  f"Cannot compute marginal contribution of {solver_name}.")
            continue

        ablated_selector_performance = compute_selector_performance(
            ablation_scenario, feature_data)

        # 1. If the performance remains equal, this solver did not contribute
        # 2. If there is a performance decay without this solver, it does contribute
        # 3. If there is a performance improvement, we have a bad portfolio selector
        if ablated_selector_performance == selector_performance:
            marginal_contribution = 0.0
        elif not compare(ablated_selector_performance, selector_performance):
            # The performance decreases, we have a contributing solver
            marginal_contribution =\
                ablated_selector_performance / selector_performance
        else:
            print("****** WARNING DUBIOUS SELECTOR/SOLVER: "
                  f"The omission of solver {solver_name} ({config}) yields an "
                  "improvement. The selector improves better without this solver. "
                  "It may be usefull to construct a portfolio without this solver.")
            marginal_contribution = 0.0

        rank_list.append((solver, config,
                          marginal_contribution, ablated_selector_performance))

    rank_list.sort(key=lambda contribution: contribution[2], reverse=True)
    return rank_list


def compute_marginal_contribution(
        scenario: SelectionScenario,
        performance_data: PerformanceDataFrame,
        feature_data: FeatureDataFrame,
        compute_perfect: bool, compute_actual: bool) -> None:
    """Compute the marginal contribution.

    Args:
        scenario: Selector scenario for which to compute marginal contribution.
        performance_data: The complete performance data object
        feature_data: Feature data object
        compute_perfect: Bool indicating if the contribution for the perfect
            portfolio selector should be computed.
        compute_actual: Bool indicating if the contribution for the actual portfolio
             selector should be computed.
    """
    if compute_perfect:
        # Perfect selector is the computation of the best performance per instance
        print("Computing each solver's marginal contribution to perfect selector ...")
        contribution_data = performance_data.marginal_contribution(
            objective=scenario.objective.name,
            instances=scenario.training_instances, sort=True)
        table = tabulate.tabulate(
            contribution_data,
            headers=["Solver", "Configuration",
                     "Marginal Contribution", "Best Performance"],)
        print(table, "\n")
        print("Marginal contribution (perfect selector) computing done!")

    if compute_actual:
        print("Start computing marginal contribution per Solver to actual selector...")
        contribution_data = compute_selector_marginal_contribution(
            feature_data,
            scenario
        )
        table = tabulate.tabulate(
            contribution_data,
            headers=["Solver", "Configuration",
                     "Marginal Contribution", "Best Performance"],)
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

    selection_scenario = SelectionScenario.from_file(args.selection_scenario)
    performance_data = PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path)
    feature_data = FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)

    if not (args.perfect | args.actual):
        print("ERROR: compute_marginal_contribution called without a flag set to"
              " True, stopping execution")
        sys.exit(-1)

    compute_marginal_contribution(selection_scenario,
                                  performance_data,
                                  feature_data,
                                  args.perfect, args.actual)

    # Write used settings to file
    gv.settings().write_used_settings()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
