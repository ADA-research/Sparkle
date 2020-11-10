#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import os
import sys
import fcntl
import argparse
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_system_status_help
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_run_status_help
from sparkle_help import sparkle_logging as sl


if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--verbose', '-v', action='store_true', help='output system status in verbose mode')

	# Process command line arguments
	args = parser.parse_args()
	my_flag_verbose = args.verbose

	if my_flag_verbose: mode = 2
	else: mode = 1
	
	print(r'c Reporting current system status of Sparkle ...')
	sparkle_system_status_help.print_solver_list(mode)
	sparkle_system_status_help.print_extractor_list(mode)
	sparkle_system_status_help.print_instance_list(mode)
	sparkle_system_status_help.print_list_remaining_feature_computation_job(sparkle_global_help.feature_data_csv_path, mode)
	sparkle_system_status_help.print_list_remaining_performance_computation_job(sparkle_global_help.performance_data_csv_path, mode)
	sparkle_system_status_help.print_portfolio_selector_info()
	sparkle_system_status_help.print_report_info()
	print(r'c Current system status of Sparkle reported!')

