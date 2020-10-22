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
import argparse
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_compute_features_help as scf
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_logging as sl


if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('instances_path', metavar='instances-path', type=str, help='path to or nickname of the instance set')
	parser.add_argument('--nickname', action='store_true', help='if set to True instances_path is used as a nickname for the instance set')

	# Process command line arguments
	args = parser.parse_args()
	instances_path = args.instances_path

	if args.nickname:
		instances_path = r'Instances/' + nickname_str
	if not os.path.exists(instances_path):
		print(r'c Instances path ' + "\'" + instances_path + "\'" + r' does not exist!')
		sys.exit()

	if instances_path[-1] == r'/': instances_path = instances_path[:-1]

	print('c Start removing all instances in directory ' + instances_path + r' ...')

	list_all_filename = sfh.get_list_all_filename(instances_path)

	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(sparkle_global_help.feature_data_csv_path)
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)

	for i in range(0, len(list_all_filename)):
		intended_filename = list_all_filename[i]
		
		intended_filename_path = instances_path + r'/' + intended_filename
		sparkle_global_help.instance_list.remove(intended_filename_path)
		output = sparkle_global_help.instance_reference_mapping.pop(intended_filename_path)
		
		feature_data_csv.delete_row(intended_filename_path)
		performance_data_csv.delete_row(intended_filename_path)
		os.system(r'rm -f ' + instances_path + r'/' + intended_filename)
		print(r'c Instance ' + sfh.get_last_level_directory_name(intended_filename) + r' has been removed!')

	os.system(r'rm -rf ' + instances_path)
	
	smac_train_instances_path = sparkle_global_help.smac_dir + r'/' + r'example_scenarios/' + r'instances/' + sfh.get_last_level_directory_name(instances_path)
	file_smac_train_instances = sparkle_global_help.smac_dir + r'/' + r'example_scenarios/' + r'instances/' + sfh.get_last_level_directory_name(instances_path) + r'_train.txt'
	#print(smac_train_instances_path, file_smac_train_instances)
	os.system(r'rm -rf ' + smac_train_instances_path)
	os.system(r'rm -f ' + file_smac_train_instances)
	
	smac_test_instances_path = sparkle_global_help.smac_dir + r'/' + r'example_scenarios/' + r'instances_test/' + sfh.get_last_level_directory_name(instances_path)
	file_smac_test_instances = sparkle_global_help.smac_dir + r'/' + r'example_scenarios/' + r'instances_test/' + sfh.get_last_level_directory_name(instances_path) + r'_test.txt'
	os.system(r'rm -rf ' + smac_test_instances_path)
	os.system(r'rm -f ' + file_smac_test_instances)

	sfh.write_instance_list()
	sfh.write_instance_reference_mapping()
	feature_data_csv.update_csv()
	performance_data_csv.update_csv()
	
	if os.path.exists(sparkle_global_help.sparkle_portfolio_selector_path):
		command_line = r'rm -f ' + sparkle_global_help.sparkle_portfolio_selector_path
		os.system(command_line)
		print('c Removing Sparkle portfolio selector ' + sparkle_global_help.sparkle_portfolio_selector_path + ' done!')
	
	if os.path.exists(sparkle_global_help.sparkle_report_path):
		command_line = r'rm -f ' + sparkle_global_help.sparkle_report_path
		os.system(command_line)
		print('c Removing Sparkle report ' + sparkle_global_help.sparkle_report_path + ' done!')
	
	print('c Removing instances in directory ' + instances_path + ' done!')

