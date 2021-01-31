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
from pathlib import Path
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_instances_help as sih


if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('instances_path', metavar='instances-path', type=str, help='path to or nickname of the instance set')
	parser.add_argument('--nickname', action='store_true', help='if given instances_path is used as a nickname for the instance set')

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
	list_instances = sfh.get_instance_list_from_reference(instances_path)

	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(sgh.feature_data_csv_path)
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sgh.performance_data_csv_path)

	for i in range(0, len(list_instances)):
		intended_instance = list_instances[i]

		# Remove instance records
		sgh.instance_list.remove(intended_instance)
		sfh.remove_line_from_file(intended_instance, sgh.instance_list_path)
		feature_data_csv.delete_row(intended_instance)
		performance_data_csv.delete_row(intended_instance)

		# Delete instance file(s)
		for instance_file in intended_instance.split():
			print('Removing instance file', instance_file)
			instance_path = Path(instance_file)
			sfh.rmfile(instance_path)

		print(r'c Instance ' + intended_instance + r' has been removed!')

	sfh.rmdir(Path(instances_path))

	# Remove instance reference list (for multi-file instances)
	instance_set_name = Path(instances_path).name
	sih.remove_reference_instance_list(instance_set_name)

	# Remove instance set from SMAC directories
	smac_train_instances_path = sgh.smac_dir + r'/' + r'example_scenarios/' + r'instances/' + sfh.get_last_level_directory_name(instances_path)
	file_smac_train_instances = sgh.smac_dir + r'/' + r'example_scenarios/' + r'instances/' + sfh.get_last_level_directory_name(instances_path) + r'_train.txt'
	#print(smac_train_instances_path, file_smac_train_instances)
	os.system(r'rm -rf ' + smac_train_instances_path)
	os.system(r'rm -f ' + file_smac_train_instances)
	
	smac_test_instances_path = sgh.smac_dir + r'/' + r'example_scenarios/' + r'instances_test/' + sfh.get_last_level_directory_name(instances_path)
	file_smac_test_instances = sgh.smac_dir + r'/' + r'example_scenarios/' + r'instances_test/' + sfh.get_last_level_directory_name(instances_path) + r'_test.txt'
	os.system(r'rm -rf ' + smac_test_instances_path)
	os.system(r'rm -f ' + file_smac_test_instances)

	sfh.write_instance_list()
	feature_data_csv.update_csv()
	performance_data_csv.update_csv()
	
	if os.path.exists(sgh.sparkle_portfolio_selector_path):
		command_line = r'rm -f ' + sgh.sparkle_portfolio_selector_path
		os.system(command_line)
		print('c Removing Sparkle portfolio selector ' + sgh.sparkle_portfolio_selector_path + ' done!')
	
	if os.path.exists(sgh.sparkle_report_path):
		command_line = r'rm -f ' + sgh.sparkle_report_path
		os.system(command_line)
		print('c Removing Sparkle report ' + sgh.sparkle_report_path + ' done!')
	
	print('c Removing instances in directory ' + instances_path + ' done!')

