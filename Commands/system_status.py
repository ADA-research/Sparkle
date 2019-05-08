#!/usr/bin/env python2.7
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

if __name__ == r'__main__':
	
	my_flag_verbose = False
	
	len_argv = len(sys.argv)
	i = 1
	while i<len_argv:
		if sys.argv[i] == r'-v':
			my_flag_verbose = True
		i += 1
	
	if my_flag_verbose: mode = 2
	else: mode = 1
	
	print r'c Reporting current system status of Sparkle ...'
	sparkle_system_status_help.print_solver_list(mode)
	sparkle_system_status_help.print_extractor_list(mode)
	sparkle_system_status_help.print_instance_list(mode)
	sparkle_system_status_help.print_list_remaining_feature_computation_job(sparkle_global_help.feature_data_csv_path, mode)
	sparkle_system_status_help.print_list_remaining_performance_computation_job(sparkle_global_help.performance_data_csv_path, mode)
	sparkle_system_status_help.print_portfolio_selector_info()
	sparkle_system_status_help.print_report_info()
	print r'c Current system status of Sparkle reported!'

