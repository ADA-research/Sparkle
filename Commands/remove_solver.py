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
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_csv_merge_help

if __name__ == r'__main__':

	my_flag_nickname = False
	nickname_str = r''
	solver_path = r''

	len_argv = len(sys.argv)
	i = 1
	while i<len_argv:
		if sys.argv[i] == r'-nickname':
			my_flag_nickname = True
			i += 1
			nickname_str = sys.argv[i]
		else:
			solver_path = sys.argv[i]
		i += 1

	if my_flag_nickname: solver_path = sparkle_global_help.solver_nickname_mapping[nickname_str]

	if not os.path.exists(solver_path):
		print(r'c Feature solver path ' + "\'" + solver_path + "\'" + r' does not exist!')
		print(r'c Usage: ' + sys.argv[0] + r' [-nickname <nickname>]')
		print(r'c Or usage: ' + sys.argv[0] + r' <solver_directory>')
		sys.exit()

	if solver_path[-1] == r'/': solver_path = solver_path[:-1]

	print('c Starting removing solver ' + sfh.get_last_level_directory_name(solver_path) + ' ...')

	solver_list = sparkle_global_help.solver_list
	if bool(solver_list):
		solver_list.remove(solver_path)
		sfh.write_solver_list()
	
	solver_nickname_mapping = sparkle_global_help.solver_nickname_mapping
	if bool(solver_nickname_mapping):
		for key in solver_nickname_mapping:
			if solver_nickname_mapping[key] == solver_path:
				output = solver_nickname_mapping.pop(key)
				break
		sfh.write_solver_nickname_mapping()

	if os.path.exists(sparkle_global_help.performance_data_csv_path):
		performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)
		for column_name in performance_data_csv.list_columns():
			if solver_path == column_name:
				performance_data_csv.delete_column(column_name)
		performance_data_csv.update_csv()
	
	command_line = r'rm -rf ' + solver_path
	os.system(command_line)
	
	solver_name = sfh.get_last_level_directory_name(solver_path)
	smac_solver_path = sparkle_global_help.smac_dir + r'/' + r'example_scenarios/' + solver_name + r'/'
	if os.path.exists(smac_solver_path):
		command_line = r'rm -rf ' + smac_solver_path
		os.system(command_line)
	
	if os.path.exists(sparkle_global_help.sparkle_portfolio_selector_path):
		command_line = r'rm -f ' + sparkle_global_help.sparkle_portfolio_selector_path
		os.system(command_line)
		print('c Removing Sparkle portfolio selector ' + sparkle_global_help.sparkle_portfolio_selector_path + ' done!')
	
	if os.path.exists(sparkle_global_help.sparkle_report_path):
		command_line = r'rm -f ' + sparkle_global_help.sparkle_report_path
		os.system(command_line)
		print('c Removing Sparkle report ' + sparkle_global_help.sparkle_report_path + ' done!')
	
	print('c Removing solver ' + sfh.get_last_level_directory_name(solver_path) + ' done!')

