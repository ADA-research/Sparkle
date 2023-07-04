#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Sparkle command to execute a parallel algorithm portfolio.."""

import sys
import os
import argparse
from pathlib import Path

from Commands.sparkle_help import sparkle_logging as sl
from Commands.sparkle_help import sparkle_settings
from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help.reporting_scenario import ReportingScenario
from Commands.sparkle_help.sparkle_settings import SettingState, ProcessMonitoring
from Commands.sparkle_help import sparkle_run_parallel_portfolio_help as srpp
from Commands.sparkle_help.sparkle_settings import PerformanceMeasure
from Commands.sparkle_help import sparkle_command_help as sch


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments.

    Returns:
        parser: The parser with the parsed command line arguments
    """
    if sgh.latest_scenario is None:
        latest = "no scenario found, you have to construct a parallel portfolio first."
    else:
        latest = sgh.latest_scenario.get_parallel_portfolio_path()
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance-paths", metavar="PATH",
                        nargs="+", type=str, required=True,
                        help="Specify the instance_path(s) on which the portfolio will "
                             "run. This can be a space-separated list of instances "
                             "contain instance sets and/or singular instances. For "
                             "example --instance-paths Instances/PTN/Ptn-7824-b01.cnf "
                             "Instances/PTN2/")
    parser.add_argument("--portfolio-name", type=Path,
                        help="Specify the name of the portfolio. If the portfolio is not"
                             " in the standard directory, use its full path, the default"
                             f" directory is {sgh.sparkle_parallel_portfolio_dir}."
                             " (default: use the latest constructed portfolio)"
                             " (current latest: "
                             f"{latest}")
    parser.add_argument("--process-monitoring", choices=ProcessMonitoring.__members__,
                        type=ProcessMonitoring,
                        help="Specify whether the monitoring of the portfolio should "
                             "cancel all solvers within a portfolio once a solver "
                             "finishes (REALISTIC). Or allow all solvers within a "
                             "portfolio to get an equal chance to have the shortest "
                             "running time on an instance (EXTENDED), e.g., when this "
                             "information is needed in an experiment."
                             " (default: "
                             f"{sgh.settings.DEFAULT_paraport_process_monitoring})"
                             " (current value: "
                             f"{sgh.settings.get_paraport_process_monitoring()})")
    parser.add_argument("--performance-measure", choices=PerformanceMeasure.__members__,
                        help="The performance measure, e.g., RUNTIME (for decision "
                             "algorithms) or QUALITY_ABSOLUTE (for optimisation "
                             "algorithms)"
                             " (default: "
                             f"{sgh.settings.DEFAULT_general_performance_measure.name})"
                             " (current value: "
                             f"{sgh.settings.get_general_performance_measure().name})")
    parser.add_argument("--cutoff-time", type=int,
                        help="The duration the portfolio will run before the solvers "
                             "within the portfolio will be stopped"
                             " (default: "
                             f"{sgh.settings.DEFAULT_general_target_cutoff_time})"
                             " (current value: "
                             f"{sgh.settings.get_general_target_cutoff_time()})")
    parser.add_argument("--settings-file", type=Path,
                        help="Specify the settings file to use instead of the default"
                             f" (default: {sgh.settings.DEFAULT_settings_path}")
    return parser


if __name__ == "__main__":
    # Initialise settings
    sgh.settings = sparkle_settings.Settings()

    # Initialise latest scenario
    sgh.latest_scenario = ReportingScenario()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    sch.check_for_initialise(sys.argv, sch.COMMAND_DEPENDENCIES[
                             sch.CommandName.RUN_SPARKLE_PARALLEL_PORTFOLIO])

    # Do first, so other command line options can override settings from the file
    if args.settings_file is not None:
        sgh.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)

    portfolio_path = args.portfolio_name

    if args.portfolio_name is None:
        portfolio_path = sgh.latest_scenario.get_parallel_portfolio_path()
    elif not portfolio_path.is_dir():
        portfolio_path = Path(sgh.sparkle_parallel_portfolio_dir / args.portfolio_name)

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
        sgh.settings.set_general_target_cutoff_time(args.cutoff_time,
                                                    SettingState.CMD_LINE)

    if args.process_monitoring is not None:
        sgh.settings.set_paraport_process_monitoring(args.process_monitoring,
                                                     SettingState.CMD_LINE)

    if args.performance_measure is not None:
        sgh.settings.set_general_performance_measure(
            PerformanceMeasure.from_str(args.performance_measure), SettingState.CMD_LINE)

    # Write settings to file before starting, since they are used in callback scripts
    sgh.settings.write_used_settings()

    print("Sparkle parallel portfolio is running ...")
    # instance_paths = list of paths to all instances
    # portfolio_path = Path to the portfolio containing the solvers
    succes = srpp.run_parallel_portfolio(instance_paths, portfolio_path)

    if succes:
        sgh.latest_scenario.set_parallel_portfolio_instance_list(instance_paths)
        print("Running Sparkle parallel portfolio is done!")

        # Write used settings to file
        sgh.settings.write_used_settings()
    else:
        print("An unexpected error occurred, please check your input an try again.")
