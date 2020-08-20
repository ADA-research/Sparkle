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
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_system_status_help
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_run_status_help
from sparkle_help import sparkle_logging as sl


if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	'''
	if len(sys.argv) != 1:
		print r'c Command error!'
		print r'c Usage: ' + sys.argv[0]
		sys.exit()
	'''
	
	my_flag_verbose = False
	
	len_argv = len(sys.argv)
	i = 1
	while i<len_argv:
		if sys.argv[i] == r'-v':
			my_flag_verbose = True
		i += 1
	
	if my_flag_verbose: mode = 2
	else: mode = 1

	print(r'c Reporting current running status of Sparkle ...')
	sparkle_run_status_help.print_running_extractor_jobs(mode)
	sparkle_run_status_help.print_running_solver_jobs(mode)
	sparkle_run_status_help.print_running_portfolio_selector_jobs()
	sparkle_run_status_help.print_running_report_jobs()
	print(r'c Current running status of Sparkle reported!')

