#!/usr/bin/env python3
"""Sparkle command to execute a configured solver."""

import sys
import argparse
from pathlib import Path

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_logging as sl
from Commands.sparkle_help import sparkle_settings
from Commands.sparkle_help.sparkle_settings import SettingState
from Commands.sparkle_help.sparkle_settings import PerformanceMeasure
from Commands.sparkle_help import sparkle_run_configured_solver_help as srcsh
from Commands.sparkle_help.reporting_scenario import ReportingScenario
from sparkle_help import sparkle_command_help as sch

from runrunner.base import Runner


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    perf_measure = sgh.settings.DEFAULT_general_sparkle_objective.PerformanceMeasure
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
        help=f"the performance measure, e.g. runtime (default: {perf_measure.name})")
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="run the solver on multiple instances in parallel")
    parser.add_argument(
        "--run-on",
        default=Runner.SLURM,
        help=("On which computer or cluster environment to execute the calculation."
              "Available: local, slurm. Default: slurm"))
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
    run_on = args.run_on

    sch.check_for_initialise(
        sys.argv, sch.COMMAND_DEPENDENCIES[sch.CommandName.RUN_CONFIGURED_SOLVER])

    if args.settings_file is not None:
        # Do first, so other command line options can override settings from the file
        sgh.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)
    if args.performance_measure is not None:
        sgh.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE
        )

    # Initialise latest scenario
    sgh.latest_scenario = ReportingScenario()

    # Validate input (is directory, or single instance (single-file or multi-file))
    if ((len(instance_path) == 1 and instance_path[0].is_dir())
            or (all([path.is_file() for path in instance_path]))):
        # Call the configured solver
        job_id_str = srcsh.call_configured_solver(args.instance_path,
                                                  args.parallel,
                                                  run_on=run_on)
    else:
        print("ERROR: Faulty input instance or instance directory!")
        sys.exit(-1)

    # Print result
    if args.parallel and run_on == Runner.SLURM:
        print(f"Running configured solver in parallel. Waiting for Slurm "
              f"job(s) with id(s): {job_id_str}")
    else:
        print("Running configured solver done!")

    # Write used settings to file
    sgh.settings.write_used_settings()
