#!/usr/bin/env python3
"""Sparkle command to execute a configured solver."""

import sys
import argparse
from pathlib import PurePath

from runrunner.base import Runner

from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import sparkle_logging as sl
from sparkle.platform.settings_objects import Settings, SettingState
from sparkle.CLI.help import run_solver_help as srcsh
from sparkle.instance import InstanceSet
from sparkle.platform import CommandName, COMMAND_DEPENDENCIES
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help.nicknames import resolve_object_name


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(*ac.InstancePathPositional.names,
                        **ac.InstancePathPositional.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    parser.add_argument(*ac.PerformanceMeasureSimpleArgument.names,
                        **ac.PerformanceMeasureSimpleArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    return parser


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    # Try to resolve the instance path (Dir or list instance paths)
    instance_set = resolve_object_name(
        args.instance_path,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        gv.settings().DEFAULT_instance_dir, InstanceSet)
    if instance_set is None:
        print(f"Could not resolve instance (set): {args.instance_path}! Exiting...")
        sys.exit(-1)

    if args.run_on is not None:
        gv.settings().set_run_on(
            args.run_on.value, SettingState.CMD_LINE)
    run_on = gv.settings().get_run_on()

    check_for_initialise(COMMAND_DEPENDENCIES[CommandName.RUN_CONFIGURED_SOLVER])

    if args.settings_file is not None:
        # Do first, so other command line options can override settings from the file
        gv.settings().read_settings_ini(args.settings_file, SettingState.CMD_LINE)
    if args.performance_measure is not None:
        gv.settings().set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE
        )

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings(), prev_settings)

    # Get the name of the configured solver and the training set
    solver = gv.latest_scenario().get_config_solver()
    train_set = gv.latest_scenario().get_config_instance_set_train()
    if solver is None or train_set is None:
        # Print error and stop execution
        print("ERROR: No configured solver found! Stopping execution.")
        sys.exit(-1)
    # Get optimised configuration
    configurator = gv.settings().get_general_sparkle_configurator()
    objective = gv.settings().get_general_sparkle_objectives()[0]
    _, config_str = configurator.get_optimal_configuration(
        solver, train_set, performance=objective.PerformanceMeasure)

    # Call the configured solver
    run = srcsh.call_solver(instance_set,
                            solver,
                            config=config_str,
                            commandname=CommandName.RUN_CONFIGURED_SOLVER,
                            run_on=run_on)

    # Print result
    if run_on == Runner.SLURM:
        print(f"Running configured solver. Waiting for Slurm "
              f"job(s) with id(s): {run.run_id}")
    else:
        print("Running configured solver done!")

    # Write used settings to file
    gv.settings().write_used_settings()
