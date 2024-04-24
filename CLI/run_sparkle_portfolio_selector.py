#!/usr/bin/env python3
"""Sparkle command to execute a portfolio selector."""

import sys
import argparse
from pathlib import Path

from runrunner.base import Runner

import global_variables as sgh
from CLI.support import run_portfolio_selector_help as srpsh
import sparkle_logging as sl
from sparkle.platform import settings_help
from sparkle.platform.settings_help import SettingState
from CLI.help import argparse_custom as ac
from sparkle.types.objective import PerformanceMeasure
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "instance_path",
        type=str,
        nargs="+",
        help="Path to instance or instance directory",
    )
    parser.add_argument(
        "--run-on",
        default=Runner.SLURM,
        choices=[Runner.LOCAL, Runner.SLURM],
        help=("On which computer or cluster environment to execute the calculation."))
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
        default=sgh.settings.DEFAULT_general_sparkle_objective.PerformanceMeasure,
        action=ac.SetByUser,
        help="the performance measure, e.g. runtime",
    )

    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    sgh.settings = settings_help.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    instance_path = " ".join(
        args.instance_path
    )  # Turn multiple instance files into a space separated string
    run_on = args.run_on

    check_for_initialise(
        sys.argv,
        ch.COMMAND_DEPENDENCIES[ch.CommandName.RUN_SPARKLE_PORTFOLIO_SELECTOR]
    )

    if ac.set_by_user(args, "settings_file"):
        sgh.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file
    if ac.set_by_user(args, "performance_measure"):
        sgh.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE
        )

    if sgh.settings.get_general_sparkle_objectives()[0].PerformanceMeasure\
            == PerformanceMeasure.QUALITY_ABSOLUTE:
        print(
            "ERROR: The run_sparkle_portfolio_selector command is not yet implemented"
            " for the QUALITY_ABSOLUTE performance measure! (functionality coming soon)"
        )
        sys.exit(-1)

    # Directory
    if Path(instance_path).is_dir():
        srpsh.call_sparkle_portfolio_selector_solve_directory(
            instance_path, run_on=run_on)
        if run_on == Runner.LOCAL:
            print("Running Sparkle portfolio selector done!")
        else:
            print("Sparkle portfolio selector is running ...")
    # Single instance (single-file or multi-file)
    elif Path(instance_path).is_file() or Path(instance_path.split()[0]).is_file():
        srpsh.call_sparkle_portfolio_selector_solve_instance(instance_path)
        print("Running Sparkle portfolio selector done!")
    else:
        print("Input instance or instance directory error!")

    # Write used settings to file
    sgh.settings.write_used_settings()
