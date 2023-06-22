#!/usr/bin/env python3
"""Sparkle command for the computation of the marginal contributions."""

import sys
import argparse
from pathlib import Path

from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_compute_marginal_contribution_help as scmc
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings
from sparkle_help.sparkle_settings import PerformanceMeasure
from sparkle_help.sparkle_settings import SettingState
from sparkle_help import argparse_custom as ac


def parser_function():
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--perfect",
        action="store_true",
        help="compute the marginal contribution for the perfect selector",
    )
    group.add_argument(
        "--actual",
        action="store_true",
        help="compute the marginal contribution for the actual selector",
    )
    parser.add_argument(
        "--recompute",
        action="store_true",
        help=("force marginal contribution to be recomputed even when it already exists"
              " in file for for the current selector"),
    )
    parser.add_argument(
        "--performance-measure",
        choices=PerformanceMeasure.__members__,
        default=sgh.settings.DEFAULT_general_performance_measure,
        action=ac.SetByUser,
        help="the performance measure, e.g. runtime",
    )
    parser.add_argument(
        "--settings-file",
        type=Path,
        default=sgh.settings.DEFAULT_settings_path,
        action=ac.SetByUser,
        help=("specify the settings file to use in case you want to use one other than"
              " the default"),
    )

    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    sgh.settings = sparkle_settings.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    print("[Deprecated] command, functionality is called automatically by other commands"
          "when needed.")
    if ac.set_by_user(args, "settings_file"):
        sgh.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file
    if ac.set_by_user(args, "performance_measure"):
        sgh.settings.set_general_performance_measure(
            PerformanceMeasure.from_str(args.performance_measure), SettingState.CMD_LINE
        )

    scmc.compute_marginal_contribution(
        args.perfect, args.actual, args.recompute
    )

    # Write used settings to file
    sgh.settings.write_used_settings()
