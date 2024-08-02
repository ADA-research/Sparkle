#!/usr/bin/env python3
"""Sparkle command for the computation of the marginal contributions."""
import sys
import argparse
from pathlib import Path

import tabulate

from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.support import compute_marginal_contribution_help as scmch
from sparkle.CLI.help import sparkle_logging as sl
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
        print("Computing each solver's marginal contribution to perfect selector ...")
        contribution_data = scmch.compute_perfect_selector_marginal_contribution(
            performance_data,
            aggregation_function,
            minimise)
        table = tabulate.tabulate(
            contribution_data,
            headers=["Solver", "Marginal Contribution", "Best Performance"],)
        print(table, "\n")
        print("Marginal contribution (perfect selector) computing done!")

    if compute_actual:
        print("Start computing marginal contribution per Solver to actual selector...")
        contribution_data = scmch.compute_actual_selector_marginal_contribution(
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
