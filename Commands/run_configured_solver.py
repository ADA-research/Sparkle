#!/usr/bin/env python3
"""Sparkle command to execute a configured solver."""

import sys
import argparse
from pathlib import Path

from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings
from sparkle_help.sparkle_settings import SettingState
from sparkle_help.sparkle_settings import PerformanceMeasure
from sparkle_help import sparkle_run_configured_solver_help as srcsh
from sparkle_help.reporting_scenario import ReportingScenario
from sparkle_help import sparkle_command_help as sch


def parser_function():
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "instance_path",
        type=Path,
        nargs="+",
        help=("Path(s) to instance file(s) (when multiple files are given, it is assumed"
              " this is a multi-file instance) or instance directory."))
    parser.add_argument(
        "--settings-file",
        type=Path,
        help=("settings file to use instead of the default (default: "
              f"{sgh.settings.DEFAULT_settings_path})"))
    parser.add_argument(
        "--performance-measure",
        choices=PerformanceMeasure.__members__,
        help=("the performance measure, e.g. runtime"
              f" (default: {sgh.settings.DEFAULT_general_performance_measure.name})"))
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="run the solver on multiple instances in parallel")
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
    instance_path = args.instance_path

    sch.check_for_initialize(["add_solver"])

    if args.settings_file is not None:
        # Do first, so other command line options can override settings from the file
        sgh.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)
    if args.performance_measure is not None:
        sgh.settings.set_general_performance_measure(
            PerformanceMeasure.from_str(args.performance_measure), SettingState.CMD_LINE)

    # Initialise latest scenario
    sgh.latest_scenario = ReportingScenario()

    # Validate input (is directory, or single instance (single-file or multi-file))
    if ((len(instance_path) == 1 and instance_path[0].is_dir())
            or (all([path.is_file() for path in instance_path]))):
        # Call the configured solver
        job_id_str = srcsh.call_configured_solver(args.instance_path, args.parallel)
    else:
        sys.exit("ERROR: Faulty input instance or instance directory!")

    # Print result
    if args.parallel:
        print("Running configured solver in parallel. Waiting for Slurm job(s) with "
              f"id(s): {job_id_str}")
    else:
        print("Running configured solver done!")

    # Write used settings to file
    sgh.settings.write_used_settings()
