#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import os
import argparse
from pathlib import Path

from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings
from sparkle_help import sparkle_global_help as sgh
from sparkle_help.reporting_scenario import ReportingScenario
from sparkle_help import argparse_custom as ac
from sparkle_help.sparkle_settings import SettingState, ProcessMonitoring
from sparkle_help import sparkle_run_parallel_portfolio_help as srpp
from sparkle_help.sparkle_settings import PerformanceMeasure


if __name__ == '__main__':
    # Initialise settings
    global settings
    sgh.settings = sparkle_settings.Settings()

    # Initialise latest scenario
    global latest_scenario
    sgh.latest_scenario = ReportingScenario()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--instance-paths', metavar='PATH',
                        nargs='+', type=str, action=ac.SetByUser, required=True,
                        help='Specify the instance_path(s) on which the portfolio will '
                             'run. This can be a space-separated list of instances '
                             'contain instance sets and/or singular instances. For '
                             'example --instance-paths Instances/PTN/Ptn-7824-b01.cnf '
                             'Instances/PTN2/')
    parser.add_argument('--portfolio-name',
                        default=sgh.latest_scenario.get_parallel_portfolio_path(),
                        type=Path, action=ac.SetByUser,
                        help='Specify the name of the portfolio. If the portfolio is not'
                             ' in the standard directory, use its full path, the default'
                             f' directory is {sgh.sparkle_parallel_portfolio_dir}. '
                             'If the option is '
                             'not specified, the latest constructed portfolio will be '
                             'used.')
    parser.add_argument('--process-monitoring', choices=ProcessMonitoring.__members__,
                        default=sgh.settings.get_parallel_portfolio_process_monitoring(),
                        action=ac.SetByUser,
                        help='Specify whether the monitoring of the portfolio should '
                             'cancel all solvers within a portfolio once a solver '
                             'finishes (REALISTIC). Or allow all solvers within a '
                             'portfolio to get an equal chance to have the shortest '
                             'running time on an instance (EXTENDED), e.g., when this '
                             'information is needed in an experiment.')
    parser.add_argument('--performance-measure', choices=PerformanceMeasure.__members__,
                        default=sgh.settings.get_general_performance_measure(),
                        action=ac.SetByUser,
                        help='The performance measure, e.g., RUNTIME (for decision '
                             'algorithms) or QUALITY_ABSOLUTE (for optimisation '
                             'algorithms)')
    parser.add_argument('--cutoff-time',
                        default=sgh.settings.get_general_target_cutoff_time(), type=int,
                        action=ac.SetByUser,
                        help='The duration the portfolio will run before the solvers '
                             'within the portfolio will be stopped')
    parser.add_argument('--settings-file', type=Path,
                        default=sgh.settings.DEFAULT_settings_path, action=ac.SetByUser,
                        help='Specify the settings file to use instead of the default')

    # Process command line arguments
    args = parser.parse_args()

    # Do first, so other command line options can override settings from the file
    if ac.set_by_user(args, 'settings_file'):
        sgh.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)

    portfolio_path = args.portfolio_name

    if ac.set_by_user(args, 'portfolio_name') and not portfolio_path.is_dir():
        portfolio_path = Path(sgh.sparkle_parallel_portfolio_dir / args.portfolio_name)

        if not portfolio_path.is_dir():
            sys.exit(f'c Portfolio "{portfolio_path}" not found, aborting the process.')

    # Create list of instance paths
    instance_paths = []

    for instance in args.instance_paths:
        if os.path.isfile(instance):
            print(f'c Running on instance {instance}')
            instance_paths.append(instance)
        elif not os.path.isdir(instance):
            instance = f'Instances/{instance}'

        if os.path.isdir(instance):
            print(f'c Running on {str(len(os.listdir(instance)))} instance(s) from '
                  f'directory {instance}')
            for item in os.listdir(instance):
                item_with_dir = f'{instance}/{item}'
                instance_paths.append(item_with_dir)

    if ac.set_by_user(args, 'cutoff_time'):
        sgh.settings.set_general_target_cutoff_time(args.cutoff_time,
                                                    SettingState.CMD_LINE)

    if ac.set_by_user(args, 'process_monitoring'):
        sgh.settings.set_parallel_portfolio_process_monitoring(args.process_monitoring,
                                                               SettingState.CMD_LINE)

    if ac.set_by_user(args, 'performance_measure'):
        sgh.settings.set_general_performance_measure(
            PerformanceMeasure.from_str(args.performance_measure), SettingState.CMD_LINE)

    print('c Sparkle parallel portfolio is running ...')
    # instance_paths = list of paths to all instances
    # portfolio_path = Path to the portfolio containing the solvers
    succes = srpp.run_parallel_portfolio(instance_paths, portfolio_path)

    if succes:
        sgh.latest_scenario.set_parallel_portfolio_instance_list(instance_paths)
        print('c Running Sparkle parallel portfolio is done!')

        # Write used settings to file
        sgh.settings.write_used_settings()
    else:
        print('c An unexpected error occurred, please check your input an try again.')
