#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import sys
import argparse
from sparkle_help import sparkle_run_status_help
from sparkle_help import sparkle_logging as sl


if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--verbose', '-v', action='store_true', help='output run status in verbose mode')

	# Process command line arguments
	args = parser.parse_args()
	my_flag_verbose = args.verbose

	if my_flag_verbose: mode = 2
	else: mode = 1

	print(r'c Reporting current running status of Sparkle ...')
	sparkle_run_status_help.print_running_extractor_jobs(mode)
	sparkle_run_status_help.print_running_solver_jobs(mode)
	sparkle_run_status_help.print_running_portfolio_selector_jobs()
	sparkle_run_status_help.print_running_report_jobs()
	print(r'c Current running status of Sparkle reported!')

