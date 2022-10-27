#!/usr/bin/env python3
'''Sparkle command to add a solver to the Sparkle platform.'''

import os
import sys
import argparse
from pathlib import Path

from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_run_solvers_parallel_help as srsp
from sparkle_help import sparkle_job_parallel_help
from sparkle_help import sparkle_add_solver_help as sash
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings
from sparkle_help.sparkle_command_help import CommandName


def parser_function():
    '''Define the command line arguments.'''
    parser = argparse.ArgumentParser(
        description='Add a solver to the Sparkle platform.',
        epilog='')
    parser.add_argument(
        '--deterministic',
        required=True,
        type=int,
        choices=[0, 1],
        help='indicate whether the solver is deterministic or not',
    )
    group_solver_run = parser.add_mutually_exclusive_group()
    group_solver_run.add_argument(
        '--run-solver-now',
        default=False,
        action='store_true',
        help='immediately run the newly added solver on all instances',
    )
    group_solver_run.add_argument(
        '--run-solver-later',
        dest='run_solver_now',
        action='store_false',
        help='do not immediately run the newly added solver on all instances (default)',
    )
    parser.add_argument(
        '--nickname',
        type=str,
        help='set a nickname for the solver'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='run the solver on multiple instances in parallel',
    )
    parser.add_argument(
        '--solver-variations',
        default=1,
        type=int,
        help=('Use this option to add multiple variations of the solver by using a '
              'different random seed for each varation.'))
    parser.add_argument(
        'solver_path',
        metavar='solver-path',
        type=str,
        help='path to the solver'
    )

    return parser


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
    solver_source = args.solver_path
    if not os.path.exists(solver_source):
        print(f'Solver path "{solver_source}" does not exist!')
        sys.exit()

    deterministic = args.deterministic
    nickname_str = args.nickname
    my_flag_parallel = args.parallel
    solver_variations = args.solver_variations

    if solver_variations < 1:
        print('ERROR: Invalid number of solver variations given '
              f'({str(solver_variations)}), '
              'a postive integer must be used. Stopping execution.')
        sys.exit(0)

    # Start add solver
    last_level_directory = ''
    last_level_directory = sfh.get_last_level_directory_name(solver_source)

    solver_directory = sash.get_solver_directory(last_level_directory)
    if not os.path.exists(solver_directory):
        Path(solver_directory).mkdir(parents=True, exist_ok=True)
    else:
        print('Solver ' + last_level_directory + ' already exists!')
        print('Do not add solver ' + last_level_directory)
        sys.exit()

    os.system('cp -r ' + solver_source + '/* ' + solver_directory)

    performance_data_csv = spdcsv.SparklePerformanceDataCSV(
        sgh.performance_data_csv_path
    )
    performance_data_csv.add_column(solver_directory)
    performance_data_csv.update_csv()

    sgh.solver_list.append(solver_directory)
    sfh.add_new_solver_into_file(solver_directory, deterministic, solver_variations)

    if sash.check_adding_solver_contain_pcs_file(solver_directory):
        print('one pcs file detected, this is a configurable solver')

    sfh.check_file_is_executable(Path(solver_directory, sgh.sparkle_smac_wrapper))

    print(f'Adding solver {sfh.get_last_level_directory_name(solver_directory)} '
          'done!')

    if os.path.exists(sgh.sparkle_portfolio_selector_path):
        command_line = 'rm -f ' + sgh.sparkle_portfolio_selector_path
        os.system(command_line)
        print('Removing Sparkle portfolio selector '
              f'{sgh.sparkle_portfolio_selector_path} done!')

    if os.path.exists(sgh.sparkle_report_path):
        command_line = 'rm -f ' + sgh.sparkle_report_path
        os.system(command_line)
        print('Removing Sparkle report ' + sgh.sparkle_report_path + ' done!')

    if nickname_str is not None:
        sgh.solver_nickname_mapping[nickname_str] = solver_directory
        sfh.add_new_solver_nickname_into_file(nickname_str, solver_directory)
        pass

    if args.run_solver_now:
        if not my_flag_parallel:
            print('Start running solvers ...')
            srs.running_solvers(sgh.performance_data_csv_path, rerun=False)
            print(
                'Performance data file '
                + sgh.performance_data_csv_path
                + ' has been updated!'
            )
            print('Running solvers done!')
        else:
            num_job_in_parallel = sgh.settings.get_slurm_number_of_runs_in_parallel()
            run_solvers_parallel_jobid = srsp.running_solvers_parallel(
                sgh.performance_data_csv_path, num_job_in_parallel, rerun=False
            )
            print('Running solvers in parallel ...')
            dependency_jobid_list = []
            if run_solvers_parallel_jobid:
                dependency_jobid_list.append(run_solvers_parallel_jobid)
            job_script = 'Commands/construct_sparkle_portfolio_selector.py'
            run_job_parallel_jobid = sparkle_job_parallel_help.running_job_parallel(
                job_script,
                dependency_jobid_list,
                CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR,
            )

            if run_job_parallel_jobid:
                dependency_jobid_list.append(run_job_parallel_jobid)
            job_script = 'Commands/generate_report.py'
            run_job_parallel_jobid = sparkle_job_parallel_help.running_job_parallel(
                job_script, dependency_jobid_list, CommandName.GENERATE_REPORT
            )

    # Write used settings to file
    sgh.settings.write_used_settings()
