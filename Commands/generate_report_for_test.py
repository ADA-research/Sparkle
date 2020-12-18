#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import sys
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_generate_report_for_test_help 
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings


if __name__ == r'__main__':
	# Initialise settings
	global settings
	sgh.settings = sparkle_settings.Settings()

	# Log command call
	sl.log_command(sys.argv)

	if len(sys.argv) != 2:
		print(r'c Command error!')
		print(r'c Usage: ' + sys.argv[0] + r' ' + r'<test_case_directory>')
		sys.exit()
	
	test_case_directory = sys.argv[1]
	
	print(r'c Generating report for test ...')
	sparkle_generate_report_for_test_help.generate_report_for_test(test_case_directory)
	print(r'c Report for test generated ...')

	# Write used settings to file
	sgh.settings.write_used_settings()

