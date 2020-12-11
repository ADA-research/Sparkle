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
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_compute_features_help as scf
from sparkle_help import sparkle_compute_features_parallel_help as scfp
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_experiments_related_help
from sparkle_help import sparkle_logging as sl


if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('extractor_path', metavar='extractor-path', type=str, help='path to the feature extractor')
	parser.add_argument('--run-extractor-later', action='store_true', help='do not immediately run the newly added feature extractor')
	parser.add_argument('--nickname', type=str, help='set a nickname for the feature extractor')
	parser.add_argument('--parallel', action='store_true', help='run the feature extractor on multiple instances in parallel')

	# Process command line arguments
	args = parser.parse_args()
	extractor_source = args.extractor_path
	if not os.path.exists(extractor_source):
		print(r'c Feature extractor path ' + "\'" + extractor_source + "\'" + r' does not exist!')
		sys.exit()

	my_flag_run_extractor_later = args.run_extractor_later
	nickname_str = args.nickname
	my_flag_parallel = args.parallel

	# Start add feature extractor
	last_level_directory = r''
	last_level_directory = sfh.get_last_level_directory_name(extractor_source)

	extractor_directory = r'Extractors/' + last_level_directory
	if not os.path.exists(extractor_directory): os.mkdir(extractor_directory)
	else:
		print(r'c Feature extractor ' + sfh.get_last_level_directory_name(extractor_directory) + r' already exists!')
		print(r'c Do not add feature extractor ' + sfh.get_last_level_directory_name(extractor_directory))
		sys.exit()

	os.system(r'cp -r ' + extractor_source + r'/* ' + extractor_directory)

	sparkle_global_help.extractor_list.append(extractor_directory)
	sfh.add_new_extractor_into_file(extractor_directory)
	
	##pre-run the feature extractor on a testing instance, to obtain the feature names
	instance_path = os.path.join(extractor_directory, 'sparkle_test_instance.cnf')
	if not os.path.isfile(instance_path):
		instance_path = os.path.join(extractor_directory, 'sparkle_test_instance.txt')
	result_path = r'Tmp/' + sfh.get_last_level_directory_name(extractor_directory) + r'_' + sfh.get_last_level_directory_name(instance_path) + r'_' + sparkle_basic_help.get_time_pid_random_string() + r'.rawres'
	command_line = extractor_directory + r'/' + sparkle_global_help.sparkle_run_default_wrapper + r' ' + extractor_directory + r'/' + r' ' + instance_path + r' ' + result_path
	os.system(command_line)

	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(sparkle_global_help.feature_data_csv_path)

	tmp_fdcsv = sfdcsv.Sparkle_Feature_Data_CSV(result_path)
	list_columns = tmp_fdcsv.list_columns()
	for column_name in list_columns:
		feature_data_csv.add_column(column_name)

	feature_data_csv.update_csv()
	
	sparkle_global_help.extractor_feature_vector_size_mapping[extractor_directory] = len(list_columns)
	sfh.add_new_extractor_feature_vector_size_into_file(extractor_directory, len(list_columns))

	command_line = r'rm -f ' + result_path
	os.system(command_line)
	
	print('c Adding feature extractor ' + sfh.get_last_level_directory_name(extractor_directory) + ' done!')

	if os.path.exists(sparkle_global_help.sparkle_portfolio_selector_path):
		command_line = r'rm -f ' + sparkle_global_help.sparkle_portfolio_selector_path
		os.system(command_line)
		print('c Removing Sparkle portfolio selector ' + sparkle_global_help.sparkle_portfolio_selector_path + ' done!')

	if os.path.exists(sparkle_global_help.sparkle_report_path):
		command_line = r'rm -f ' + sparkle_global_help.sparkle_report_path
		os.system(command_line)
		print('c Removing Sparkle report ' + sparkle_global_help.sparkle_report_path + ' done!')

	if nickname_str is not None:
		sparkle_global_help.extractor_nickname_mapping[nickname_str] = extractor_directory
		sfh.add_new_extractor_nickname_into_file(nickname_str, extractor_directory)
		pass

	if not my_flag_run_extractor_later:
		if not my_flag_parallel:
			print('c Start computing features ...')
			scf.computing_features(sparkle_global_help.feature_data_csv_path, 1)
			print('c Feature data file ' + sparkle_global_help.feature_data_csv_path + ' has been updated!')
			print('c Computing features done!')
		else:
			num_job_in_parallel = sparkle_experiments_related_help.num_job_in_parallel
			scfp.computing_features_parallel(sparkle_global_help.feature_data_csv_path, num_job_in_parallel, 1)
			print('c Computing features in parallel ...')


