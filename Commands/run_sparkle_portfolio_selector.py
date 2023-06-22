#!/usr/bin/env python3
"""Sparkle command to execute a portfolio selector."""

import sys
import argparse
from pathlib import Path

from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_run_portfolio_selector_help as srps
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings
from sparkle_help.sparkle_settings import SettingState
from sparkle_help import argparse_custom as ac
from sparkle_help.sparkle_settings import PerformanceMeasure
from sparkle_help import sparkle_command_help as sch


def parser_function():
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "instance_path",
        type=str,
        nargs="+",
        help="Path to instance or instance directory",
    )
    parser.add_argument(
        "--settings-file",
        type=Path,
        default=sgh.settings.DEFAULT_settings_path,
        action=ac.SetByUser,
        help="settings file to use instead of the default",
    )
    parser.add_argument(
        "--performance-measure",
        choices=PerformanceMeasure.__members__,
        default=sgh.settings.DEFAULT_general_performance_measure,
        action=ac.SetByUser,
        help="the performance measure, e.g. runtime",
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
    instance_path = " ".join(
        args.instance_path
    )  # Turn multiple instance files into a space separated string

    sch.check_for_initialize(["add_instances, ""add_feature_extractor", "add_solver"])

    if ac.set_by_user(args, "settings_file"):
        sgh.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file
    if ac.set_by_user(args, "performance_measure"):
        sgh.settings.set_general_performance_measure(
            PerformanceMeasure.from_str(args.performance_measure), SettingState.CMD_LINE
        )

    if (
        sgh.settings.get_general_performance_measure()
        == PerformanceMeasure.QUALITY_ABSOLUTE
    ):
        print(
            "ERROR: The run_sparkle_portfolio_selector command is not yet implemented"
            " for the QUALITY_ABSOLUTE performance measure! (functionality coming soon)"
        )
        sys.exit()

    # Directory
    if Path(instance_path).is_dir():
        srps.call_sparkle_portfolio_selector_solve_instance_directory(instance_path)
        print("Sparkle portfolio selector is running ...")
    # Single instance (single-file or multi-file)
    elif Path(instance_path).is_file() or Path(instance_path.split()[0]).is_file():
        srps.call_sparkle_portfolio_selector_solve_instance(instance_path)
        print("Running Sparkle portfolio selector done!")
    else:
        print("Input instance or instance directory error!")

    # Write used settings to file
    sgh.settings.write_used_settings()
