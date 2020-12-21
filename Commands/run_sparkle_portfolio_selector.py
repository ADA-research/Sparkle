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
import argparse
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_run_portfolio_selector_help as srps
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings


if __name__ == r'__main__':
	# Initialise settings
	global settings
	sgh.settings = sparkle_settings.Settings()

	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('instance_path', type=str, help='Path to instance or instance directory')

	# Process command line arguments
	args = parser.parse_args()
	instance_path = args.instance_path

	if os.path.isfile(instance_path):
		srps.call_sparkle_portfolio_selector_solve_instance(instance_path)
		print('c Running Sparkle portfolio selector done!')
	elif os.path.isdir(instance_path):
		srps.call_sparkle_portfolio_selector_solve_instance_directory(instance_path)
		print('c Sparkle portfolio selector is running ...')
	else:
		print('c Input instance or instance directory error!')

	# Write used settings to file
	sgh.settings.write_used_settings()

