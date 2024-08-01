#!/usr/bin/env python3
"""Sparkle command for the computation of the marginal contributions."""

import sys
import argparse

from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.support import compute_marginal_contribution_help as scmch
from sparkle.CLI.help import sparkle_logging as sl
from sparkle.platform.settings_objects import SettingState
from sparkle.CLI.help import argparse_custom as ac
from sparkle.platform import CommandName, COMMAND_DEPENDENCIES
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as apc


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

    print("[Deprecated] command, functionality is called automatically by other commands"
          " when needed.")
    if ac.set_by_user(args, "settings_file"):
        gv.settings().read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file
    if ac.set_by_user(args, "performance_measure"):
        gv.settings().set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE
        )
    selection_scenario = gv.latest_scenario().get_selection_scenario_path()

    scmch.compute_marginal_contribution(
        selection_scenario, args.perfect, args.actual
    )

    # Write used settings to file
    gv.settings().write_used_settings()
