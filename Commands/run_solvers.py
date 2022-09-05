#!/usr/bin/env python3

import sys
import argparse
from typing import List
from pathlib import Path

from sparkle_help import sparkle_record_help as srh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_run_solvers_parallel_help as srsp
from sparkle_help import sparkle_job_parallel_help as sjph
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings
from sparkle_help.sparkle_settings import PerformanceMeasure
from sparkle_help.sparkle_settings import SolutionVerifier
from sparkle_help.sparkle_settings import SettingState
from sparkle_help import argparse_custom as ac
from sparkle_help.sparkle_command_help import CommandName


def parser_function():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--recompute',
        action='store_true',
        help='recompute the performance of all solvers on all instances',
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='run the solver on multiple instances in parallel',
    )
    parser.add_argument(
        '--performance-measure',
        choices=PerformanceMeasure.__members__,
        default=sgh.settings.DEFAULT_general_performance_measure,
        action=ac.SetByUser,
        help='the performance measure, e.g. runtime',
    )
    parser.add_argument(
        '--target-cutoff-time',
        type=int,
        default=sgh.settings.DEFAULT_general_target_cutoff_time,
        action=ac.SetByUser,
        help='cutoff time per target algorithm run in seconds',
    )
    parser.add_argument(
        '--also-construct-selector-and-report',
        action='store_true',
        help=('after running the solvers also construct the selector and generate'
              ' the report'),
    )
    parser.add_argument(
        '--verifier',
        choices=SolutionVerifier.__members__,
        default=sgh.settings.DEFAULT_general_solution_verifier,
        action=ac.SetByUser,
        help=('problem specific verifier that should be used to verify solutions found'
              ' by a target algorithm'),
    )
    parser.add_argument(
        '--settings-file',
        type=Path,
        default=sgh.settings.DEFAULT_settings_path,
        action=ac.SetByUser,
        help=('specify the settings file to use in case you want to use one other than'
              ' the default'),
    )
    return parser


def run_solvers_parallel(flag_recompute, flag_also_construct_selector_and_report=False):
    num_job_in_parallel = sgh.settings.get_slurm_number_of_runs_in_parallel()

    if flag_recompute:
        performance_data_csv = spdcsv.SparklePerformanceDataCSV(
            sgh.performance_data_csv_path
        )
        performance_data_csv.clean_csv()
        run_solvers_parallel_jobid = srsp.running_solvers_parallel(
            sgh.performance_data_csv_path, num_job_in_parallel, 2
        )
    else:
        run_solvers_parallel_jobid = srsp.running_solvers_parallel(
            sgh.performance_data_csv_path, num_job_in_parallel, 1
        )

    dependency_jobid_list = []

    if run_solvers_parallel_jobid:
        dependency_jobid_list.append(run_solvers_parallel_jobid)

    # Update performance data csv after the last job is done
    job_script = 'Commands/sparkle_help/sparkle_csv_merge_help.py'
    run_job_parallel_jobid = sjph.running_job_parallel(
        job_script, dependency_jobid_list, CommandName.RUN_SOLVERS
    )
    dependency_jobid_list.append(run_job_parallel_jobid)

    # TODO: Check output (files) for error messages, e.g.:
    # error: unrecognized arguments
    # srun: error:
    # TODO: Check performance data CSV for missing values

    # Only do selector construction and report generation if the flag is set;
    # Default behaviour is not to run them, like the sequential run_solvers command
    if flag_also_construct_selector_and_report:
        run_job_parallel_jobid = construct_selector_and_report(dependency_jobid_list)
        dependency_jobid_list.append(run_job_parallel_jobid)

    job_id_str = ','.join(dependency_jobid_list)
    print(f'Running solvers in parallel. Waiting for Slurm job(s) with id(s): '
          f'{job_id_str}')

    return


def construct_selector_and_report(dependency_jobid_list: List[str] = []):
    job_script = 'Commands/construct_sparkle_portfolio_selector.py'
    run_job_parallel_jobid = sjph.running_job_parallel(
        job_script,
        dependency_jobid_list,
        CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR,
    )

    if run_job_parallel_jobid:
        dependency_jobid_list.append(run_job_parallel_jobid)
    job_script = 'Commands/generate_report.py'
    run_job_parallel_jobid = sjph.running_job_parallel(
        job_script, dependency_jobid_list, CommandName.GENERATE_REPORT
    )

    return run_job_parallel_jobid


if __name__ == '__main__':
    # Initialise settings
    global settings
    sgh.settings = sparkle_settings.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    flag_recompute = args.recompute
    flag_parallel = args.parallel
    flag_also_construct_selector_and_report = args.also_construct_selector_and_report

    if ac.set_by_user(args, 'settings_file'):
        sgh.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file
    if ac.set_by_user(args, 'performance_measure'):
        sgh.settings.set_general_performance_measure(
            PerformanceMeasure.from_str(args.performance_measure), SettingState.CMD_LINE
        )
    if ac.set_by_user(args, 'verifier'):
        sgh.settings.set_general_solution_verifier(
            SolutionVerifier.from_str(args.verifier), SettingState.CMD_LINE
        )
    if ac.set_by_user(args, 'target_cutoff_time'):
        sgh.settings.set_general_target_cutoff_time(
            args.target_cutoff_time, SettingState.CMD_LINE
        )

    print('Start running solvers ...')

    if not srh.detect_current_sparkle_platform_exists():
        print('No Sparkle platform found; please first run the initialise command')
        exit()

    if not flag_parallel:
        if flag_recompute:
            performance_data_csv = spdcsv.SparklePerformanceDataCSV(
                sgh.performance_data_csv_path
            )
            performance_data_csv.clean_csv()
            srs.running_solvers(sgh.performance_data_csv_path, 2)
        else:
            srs.running_solvers(sgh.performance_data_csv_path, 1)

        if flag_also_construct_selector_and_report:
            construct_selector_and_report()

        print('Running solvers done!')
    else:
        run_solvers_parallel(flag_recompute, flag_also_construct_selector_and_report)

    # Write used settings to file
    sgh.settings.write_used_settings()
