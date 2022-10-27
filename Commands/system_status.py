#!/usr/bin/env python3
'''Sparkle command to display the status of the Sparkle platform.'''

import sys
import argparse
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_system_status_help
from sparkle_help import sparkle_logging as sl


def parser_function():
    '''Define the command line arguments.'''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='output system status in verbose mode',
    )
    return parser


if __name__ == '__main__':
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    my_flag_verbose = args.verbose

    if my_flag_verbose:
        mode = 2
    else:
        mode = 1

    print('Reporting current system status of Sparkle ...')
    sparkle_system_status_help.print_solver_list(mode)
    sparkle_system_status_help.print_extractor_list(mode)
    sparkle_system_status_help.print_instance_list(mode)
    sparkle_system_status_help.print_list_remaining_feature_computation_job(
        sparkle_global_help.feature_data_csv_path, mode
    )
    sparkle_system_status_help.print_list_remaining_performance_computation_job(
        sparkle_global_help.performance_data_csv_path, mode
    )
    sparkle_system_status_help.print_portfolio_selector_info()
    sparkle_system_status_help.print_report_info()
    print('Current system status of Sparkle reported!')
