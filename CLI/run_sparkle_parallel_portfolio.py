#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Sparkle command to execute a parallel algorithm portfolio.."""

import sys
import os
import argparse
from pathlib import Path, PurePath

from runrunner.base import Runner

import sparkle_logging as sl
from sparkle.platform import settings_help
import global_variables as gv
from sparkle.platform.settings_help import SettingState, Settings
from CLI.support import run_parallel_portfolio_help as srpp
from CLI.help import command_help as sch
from CLI.initialise import check_for_initialise
from CLI.help import argparse_custom as ac


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments.

    Returns:
        parser: The parser with the parsed command line arguments
    """
    if gv._latest_scenario is None:
        latest = "no scenario found, you have to construct a parallel portfolio first."
    else:
        latest = gv.latest_scenario().get_parallel_portfolio_path()
    parser = argparse.ArgumentParser()
    parser.add_argument(*ac.InstancePathsRunParallelPortfolioArgument.names,
                        **ac.InstancePathsRunParallelPortfolioArgument.kwargs)
    parser.add_argument(
        "--portfolio-name",
        type=Path,
        help="Specify the name of the portfolio. If the portfolio is not in the standard"
             " directory, use its full path, the default directory is "
             f"{gv.sparkle_parallel_portfolio_dir}. (default: use the latest "
             f"constructed portfolio) (current latest: {latest})")
    parser.add_argument(*ac.ProcessMonitoringArgument.names,
                        **ac.ProcessMonitoringArgument.kwargs)
    parser.add_argument(*ac.PerformanceMeasureSimpleArgument.names,
                        **ac.PerformanceMeasureSimpleArgument.kwargs)
    parser.add_argument(*ac.CutOffTimeArgument.names,
                        **ac.CutOffTimeArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    return parser


if __name__ == "__main__":
    # Initialise settings
    gv.settings = settings_help.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    check_for_initialise(
        sys.argv,
        sch.COMMAND_DEPENDENCIES[sch.CommandName.RUN_SPARKLE_PARALLEL_PORTFOLIO]
    )

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings, prev_settings)

    # Do first, so other command line options can override settings from the file
    if args.settings_file is not None:
        gv.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)

    portfolio_path = args.portfolio_name
    run_on = args.run_on

    if run_on == Runner.LOCAL:
        print("Parallel Portfolio is not fully supported yet for Local runs. Exiting.")
        sys.exit(-1)

    if args.portfolio_name is None:
        portfolio_path = gv.latest_scenario().get_parallel_portfolio_path()
    elif not portfolio_path.is_dir():
        portfolio_path = Path(gv.sparkle_parallel_portfolio_dir / args.portfolio_name)

        if not portfolio_path.is_dir():
            sys.exit(f'Portfolio "{portfolio_path}" not found, aborting the process.')

    # Create list of instance paths
    instance_paths = []

    for instance in args.instance_paths:
        if not Path(instance).exists():
            sys.exit(f'Instance "{instance}" not found, aborting the process.')
        if Path(instance).is_file():
            print(f"Running on instance {instance}")
            instance_paths.append(instance)
        elif not Path(instance).is_dir():
            instance = f"Instances/{instance}"

        if Path(instance).is_dir():
            print(f"Running on {str(len(os.listdir(instance)))} instance(s) from "
                  f"directory {instance}")
            for item in os.listdir(instance):
                item_with_dir = f"{instance}{item}"
                instance_paths.append(item_with_dir)

    if args.cutoff_time is not None:
        gv.settings.set_general_target_cutoff_time(args.cutoff_time,
                                                   SettingState.CMD_LINE)

    if args.process_monitoring is not None:
        gv.settings.set_paraport_process_monitoring(args.process_monitoring,
                                                    SettingState.CMD_LINE)

    if args.performance_measure is not None:
        gv.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE)

    # Write settings to file before starting, since they are used in callback scripts
    gv.settings.write_used_settings()

    print("Sparkle parallel portfolio is running ...")
    # instance_paths = list of paths to all instances
    # portfolio_path = Path to the portfolio containing the solvers
    succes = srpp.run_parallel_portfolio(instance_paths, portfolio_path, run_on=run_on)

    if succes:
        gv.latest_scenario().set_parallel_portfolio_instance_list(instance_paths)
        print("Running Sparkle parallel portfolio is done!")

        # Write used settings to file
        gv.settings.write_used_settings()
    else:
        print("An unexpected error occurred, please check your input and try again.")
