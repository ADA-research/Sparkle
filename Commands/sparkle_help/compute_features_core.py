#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import os
import time
import random
import argparse
from pathlib import Path
from pathlib import PurePath

try:
	from sparkle_help import sparkle_global_help as sgh
	from sparkle_help import sparkle_basic_help
	from sparkle_help import sparkle_file_help as sfh
	from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
	from sparkle_help import sparkle_compute_features_help as scf
	from sparkle_help import sparkle_settings
except ImportError:
	import sparkle_global_help as sgh
	import sparkle_basic_help
	import sparkle_file_help as sfh
	import sparkle_feature_data_csv_help as sfdcsv
	import sparkle_compute_features_help as scf
	import sparkle_settings


if __name__ == r'__main__':
	# Initialise settings
	global settings
	settings_dir = Path('Settings')
	file_path_latest = PurePath(settings_dir / 'latest.ini')
	sgh.settings = sparkle_settings.Settings(file_path_latest)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--instance', required=False, type=str, nargs='+', help='path to instance file(s) to run on')
	parser.add_argument('--extractor', required=True, type=str, help='path to feature extractor')
	parser.add_argument('--feature-csv', required=True, type=str, help='path to feature data CSV file')
	args = parser.parse_args()

	# Process command line arguments
	instance_path = " ".join(args.instance) # Turn multiple instance files into a space separated string
	extractor_path = args.extractor
	feature_data_csv_path = args.feature_csv

	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
	runsolver_path = sgh.runsolver_path

	if len(sgh.extractor_list) == 0:
		cutoff_time_each_extractor_run = sgh.settings.get_general_extractor_cutoff_time()
	else:
		cutoff_time_each_extractor_run = sgh.settings.get_general_extractor_cutoff_time() / len(sgh.extractor_list)

	cutoff_time_each_run_option = r'-C ' + str(cutoff_time_each_extractor_run)

	key_str = sfh.get_last_level_directory_name(extractor_path) + r'_' + sfh.get_last_level_directory_name(instance_path) + r'_' + sparkle_basic_help.get_time_pid_random_string()
	result_path = r'Feature_Data/Tmp/' + key_str + r'.csv'
	basic_part = r'Tmp/' + key_str
	err_path = basic_part + r'.err'
	runsolver_watch_data_path = basic_part + r'.log'
	runsolver_watch_data_path_option = r'-w ' + runsolver_watch_data_path
	command_line = runsolver_path + r' ' + cutoff_time_each_run_option + r' ' + runsolver_watch_data_path_option + r' ' + extractor_path + r'/' + sgh.sparkle_run_default_wrapper + r' ' + extractor_path + r'/' + r' ' + instance_path + r' ' + result_path + r' 2> ' + err_path

	try:
		task_run_status_path = r'Tmp/SBATCH_Extractor_Jobs/' + key_str + r'.statusinfo'
		status_info_str = 'Status: Running\n' + 'Extractor: %s\n' %(sfh.get_last_level_directory_name(extractor_path)) + 'Instance: %s\n' % (sfh.get_last_level_directory_name(instance_path))
		
		start_time = time.time()
		status_info_str += 'Start Time: ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time)) + '\n'
		status_info_str += 'Start Timestamp: ' + str(start_time) + '\n'
		cutoff_str = 'Cutoff Time: ' + str(cutoff_time_each_extractor_run) + ' second(s)' + '\n'
		status_info_str += cutoff_str
		sfh.write_string_to_file(task_run_status_path, status_info_str)
		os.system(command_line)
		end_time = time.time()

	except:
		if not os.path.exists(result_path):
			sfh.create_new_empty_file(result_path)

	try:
		tmp_fdcsv = sfdcsv.Sparkle_Feature_Data_CSV(result_path)
		result_string = 'Successful'
	except:
		print('c ****** WARNING: Feature vector computing on instance ' + instance_path + ' failed! ******')
		print('c ****** WARNING: The feature vector of this instace consists of missing values ******')

		command_line = r'rm -f ' + result_path
		os.system(command_line)
		tmp_fdcsv = scf.generate_missing_value_csv_like_feature_data_csv(feature_data_csv, instance_path, extractor_path, result_path)
		result_string = 'Failed -- using missing value instead'

	description_str = r'[Extractor: ' + sfh.get_last_level_directory_name(extractor_path) + r', Instance: ' + sfh.get_last_level_directory_name(instance_path) + r']'
	start_time_str = r'[Start Time: ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time)) + r']'
	end_time_str = r'[End Time: ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(end_time)) + r']'
	run_time_str = r'[Actual Run Time: ' + str(end_time-start_time) + r' second(s)]'
	result_string_str = r'[Result String: ' + result_string + r']'

	log_str = description_str + r', ' + start_time_str + r', ' + end_time_str + r', ' + run_time_str + r', ' + result_string_str

	sfh.append_string_to_file(sgh.sparkle_system_log_path, log_str)
	os.system('rm -f ' + task_run_status_path)

	tmp_fdcsv.save_csv(result_path)

	command_line = r'rm -f ' + err_path
	os.system(command_line)
	command_line = r'rm -f ' + runsolver_watch_data_path
	os.system(command_line)

