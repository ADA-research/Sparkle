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
from sparkle_help import sparkle_generate_report_help
from sparkle_help import sparkle_generate_report_for_test_help
from sparkle_help import sparkle_configure_solver_help as scsh
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_generate_report_for_configuration_help

if __name__ == r'__main__':
	solver = ''
	instance_set = ''
	
	flag_solver = False
	flag_instance_set = False
	
	len_argv = len(sys.argv)
	i = 1
	while i<len_argv:
		if sys.argv[i] == '-solver':
			i += 1
			solver = sys.argv[i]
			flag_solver = True
		elif sys.argv[i] == '-instance_set':
			i += 1
			instance_set = sys.argv[i]
			flag_instance_set = True
		else:
			print('c Argument Error!')
			print('c Usage: %s -solver <solver> -instance_set <instance_set>' % sys.argv[0])
			sys.exit(-1)
		i += 1
	
	if not (flag_solver and flag_instance_set):
		print('c Argument Error!')
		print('c Usage: %s -solver <solver> -instance_set <instance_set>' % sys.argv[0])
		sys.exit(-1)
	
	solver_name = sfh.get_last_level_directory_name(solver)
	instance_set_name = sfh.get_last_level_directory_name(instance_set)
	
	print('c Generating report for configuration ...')
	sparkle_generate_report_for_configuration_help.generate_report_for_configuration(solver_name, instance_set_name)
	print('c Generating report for configuration done!')
	
	
	

