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
from pathlib import Path
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_generate_report_for_test_help 
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings
from sparkle_help import argparse_custom as ac


if __name__ == r'__main__':
	# Initialise settings
	global settings
	sgh.settings = sparkle_settings.Settings()

	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('test_case_directory', type=str, help='Path to test case directory of an instance set')
	parser.add_argument('--settings-file', type=Path, default=sgh.settings.DEFAULT_settings_path, action=ac.SetByUser, help='specify the settings file to use in case you want to use one other than the default')

	# Process command line arguments
	args = parser.parse_args()
	test_case_directory = args.test_case_directory

	print(r'c Generating report for test ...')
	sparkle_generate_report_for_test_help.generate_report_for_test(test_case_directory)
	print(r'c Report for test generated ...')

	# Write used settings to file
	sgh.settings.write_used_settings()

