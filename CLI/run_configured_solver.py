#!/usr/bin/env python3
"""Sparkle command to execute a configured solver."""

import sys
import argparse
from pathlib import Path, PurePath

from runrunner.base import Runner

import global_variables as gv
import sparkle_logging as sl
from sparkle.platform import settings_help
from sparkle.platform.settings_help import SettingState, Settings
from CLI.support import run_configured_solver_help as srcsh
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise
from CLI.help import argparse_custom as ac
from CLI.help.nicknames import resolve_object_name


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(*ac.InstancePathRunConfiguredSolverArgument.names,
                        **ac.InstancePathRunConfiguredSolverArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    parser.add_argument(*ac.PerformanceMeasureSimpleArgument.names,
                        **ac.PerformanceMeasureSimpleArgument.kwargs)
    parser.add_argument(*ac.ParallelArgument.names,
                        **ac.ParallelArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
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
    if isinstance(args.instance_path, list):
        instance_path = [resolve_object_name(instance, target_dir=gv.instance_dir)
                         for instance in args.instance_path]
    else:
        instance_path = resolve_object_name(args.instance_path,
                                            target_dir=gv.instance_dir)
    run_on = args.run_on

    check_for_initialise(sys.argv,
                         ch.COMMAND_DEPENDENCIES[ch.CommandName.RUN_CONFIGURED_SOLVER])

    if args.settings_file is not None:
        # Do first, so other command line options can override settings from the file
        gv.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)
    if args.performance_measure is not None:
        gv.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE
        )

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings, prev_settings)

    # Validate input (is directory, or single instance (single-file or multi-file))
    if ((len(instance_path) == 1 and instance_path[0].is_dir())
            or (all([path.is_file() for path in instance_path]))):
        # Get the name of the configured solver and the training set
        solver_name = Path(gv.latest_scenario().get_config_solver()).name
        instance_set_name = Path(
            gv.latest_scenario().get_config_instance_set_train()).name
        if solver_name is None or instance_set_name is None:
            # Print error and stop execution
            print("ERROR: No configured solver found! Stopping execution.")
            sys.exit(-1)

        # Get optimised configuration
        configurator = gv.settings.get_general_sparkle_configurator()
        _, config_str = configurator.get_optimal_configuration(solver_name,
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
    gv.settings.write_used_settings()
