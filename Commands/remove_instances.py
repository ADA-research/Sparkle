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
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_compute_features_help as scf
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_csv_merge_help

if __name__ == r'__main__':

	my_flag_nickname = False
	nickname_str = r''
	instances_path = r''

	len_argv = len(sys.argv)
	i = 1
	while i<len_argv:
		if sys.argv[i] == r'-nickname':
			my_flag_nickname = True
			i += 1
			nickname_str = sys.argv[i]
		else:
			instances_path = sys.argv[i]
		i += 1

	if my_flag_nickname: instances_path = r'Instances/' + nickname_str

	if not os.path.exists(instances_path):
		print r'c Instances path ' + "\'" + instances_path + "\'" + r' does not exist!'
		print r'c Usage: ' + sys.argv[0] + r' [-nickname] <nickname>'
		print r'c Or usage: ' + sys.argv[0] + r' <instances_path_directory>'
		sys.exit()
	
	if instances_path[-1] == r'/': instances_path = instances_path[:-1]

	print 'c Start removing all cnf instances in directory ' + instances_path + r' ...' 

	list_all_cnf_path = sfh.get_list_all_cnf_filename(instances_path)

	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(sparkle_global_help.feature_data_csv_path)
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)

	for i in range(0, len(list_all_cnf_path)):
		intended_cnf_filename_path = list_all_cnf_path[i]
		
		sparkle_global_help.instance_list.remove(intended_cnf_filename_path)
		output = sparkle_global_help.instance_reference_mapping.pop(intended_cnf_filename_path)
		
		feature_data_csv.delete_row(intended_cnf_filename_path)
		performance_data_csv.delete_row(intended_cnf_filename_path)
		os.system(r'rm -f ' + intended_cnf_filename_path)
		print r'c Instance ' + sfh.get_last_level_directory_name(intended_cnf_filename_path) + r' has been removed!'

	os.system(r'rm -rf ' + instances_path)

	sfh.write_instance_list()
	sfh.write_instance_reference_mapping()
	feature_data_csv.update_csv()
	performance_data_csv.update_csv()
	
	if os.path.exists(sparkle_global_help.sparkle_portfolio_selector_path):
		command_line = r'rm -f ' + sparkle_global_help.sparkle_portfolio_selector_path
		os.system(command_line)
		command_line = r'rm -f ' + sparkle_global_help.sparkle_portfolio_selector_path + '*'
		os.system(command_line)
		print 'c Removing Sparkle portfolio selector ' + sparkle_global_help.sparkle_portfolio_selector_path + ' done!'
	
	if os.path.exists(sparkle_global_help.sparkle_report_path):
		command_line = r'rm -f ' + sparkle_global_help.sparkle_report_path
		os.system(command_line)
		print 'c Removing Sparkle report ' + sparkle_global_help.sparkle_report_path + ' done!'
	
	print 'c Removing instances in directory ' + instances_path + ' done!'


