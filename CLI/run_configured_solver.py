#!/usr/bin/env python3
"""Sparkle command to execute a configured solver."""

import sys
import argparse
from pathlib import Path

from runrunner.base import Runner

import global_variables as sgh
import sparkle_logging as sl
from sparkle.platform import settings_help
from sparkle.platform.settings_help import SettingState
from sparkle.types.objective import PerformanceMeasure
from CLI.support import run_configured_solver_help as srcsh
from CLI.support import configure_solver_help as scsh
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise


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
        choices=[Runner.LOCAL, Runner.SLURM],
        help=("On which computer or cluster environment to execute the calculation.")
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
    instance_path = args.instance_path
    run_on = args.run_on

    check_for_initialise(sys.argv,
                         ch.COMMAND_DEPENDENCIES[ch.CommandName.RUN_CONFIGURED_SOLVER])

    if args.settings_file is not None:
        # Do first, so other command line options can override settings from the file
        sgh.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)
    if args.performance_measure is not None:
        sgh.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE
        )

    # Validate input (is directory, or single instance (single-file or multi-file))
    if ((len(instance_path) == 1 and instance_path[0].is_dir())
            or (all([path.is_file() for path in instance_path]))):
        # Get the name of the configured solver and the training set
        solver_name = Path(sgh.latest_scenario().get_config_solver()).name
        instance_set_name = Path(
            sgh.latest_scenario().get_config_instance_set_train()).name
        if solver_name is None or instance_set_name is None:
            # Print error and stop execution
            print("ERROR: No configured solver found! Stopping execution.")
            sys.exit(-1)

        # Get optimised configuration
        config_str = scsh.get_optimised_configuration_params(solver_name,
                                                             instance_set_name)

        # Call the configured solver
        run = srcsh.call_configured_solver(args.instance_path,
                                           solver_name,
                                           config_str,
                                           args.parallel,
                                           run_on=run_on)
    else:
        print("ERROR: Faulty input instance or instance directory!")
        sys.exit(-1)

    # Print result
    if args.parallel and run_on == Runner.SLURM:
        print(f"Running configured solver in parallel. Waiting for Slurm "
              f"job(s) with id(s): {run.run_id}")
    else:
        print("Running configured solver done!")

    # Write used settings to file
    sgh.settings.write_used_settings()
