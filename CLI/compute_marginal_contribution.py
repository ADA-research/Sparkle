#!/usr/bin/env python3
"""Sparkle command for the computation of the marginal contributions."""

import sys
import argparse

import global_variables as gv
from CLI.support import compute_marginal_contribution_help as scmch
import sparkle_logging as sl
from sparkle.platform import settings_help
from sparkle.platform.settings_help import SettingState
from CLI.help import argparse_custom as ac
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise
from CLI.help import argparse_custom as apc


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(*apc.PerfectArgument.names,
                       **apc.PerfectArgument.kwargs)
    group.add_argument(*apc.ActualArgument.names,
                       **apc.ActualArgument.kwargs)
    parser.add_argument(*apc.RecomputeMarginalContributionArgument.names,
                        **apc.RecomputeMarginalContributionArgument.kwargs)
    parser.add_argument(*apc.SelectorTimeoutArgument.names,
                        **apc.SelectorTimeoutArgument.kwargs)
    parser.add_argument(*apc.PerformanceMeasureArgument.names,
                        **apc.PerformanceMeasureArgument.kwargs)
    parser.add_argument(*apc.SettingsFileArgument.names,
                        **apc.SettingsFileArgument.kwargs)

    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    gv.settings = settings_help.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    check_for_initialise(
        sys.argv,
        ch.COMMAND_DEPENDENCIES[ch.CommandName.COMPUTE_MARGINAL_CONTRIBUTION]
    )

    print("[Deprecated] command, functionality is called automatically by other commands"
          " when needed.")
    if ac.set_by_user(args, "settings_file"):
        gv.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file
    if ac.set_by_user(args, "performance_measure"):
        gv.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE
        )

    scmch.compute_marginal_contribution(
        args.perfect, args.actual, args.recompute, args.selector_timeout
    )

    # Write used settings to file
    gv.settings.write_used_settings()
