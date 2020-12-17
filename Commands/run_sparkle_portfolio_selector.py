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
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_run_portfolio_selector_help as srps
from sparkle_help import sparkle_experiments_related_help as ser
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings


if __name__ == r'__main__':
	# Initialise settings
	global settings
	sgh.settings = sparkle_settings.Settings()

	# Log command call
	sl.log_command(sys.argv)

	if len(sys.argv) != 2:
		print(r'c Arguments error!')
		print(r'c Usage: ' + sys.argv[0] + ' <instance or instance directory>')
		sys.exit()
	
	input_path = sys.argv[1]
	
	if os.path.isfile(input_path):
		srps.call_sparkle_portfolio_selector_solve_instance(input_path)
		print('c Running Sparkle portfolio selector done!')
	elif os.path.isdir(input_path):
		srps.call_sparkle_portfolio_selector_solve_instance_directory(input_path)
		print('c Sparkle portfolio selector is running ...')
	else:
		print('c Input instance or instance directory error!')

	# Write used settings to file
	sgh.settings.write_used_settings()

