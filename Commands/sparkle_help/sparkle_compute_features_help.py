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
import sys
import fcntl
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_experiments_related_help as ser
from sparkle_help import sparkle_job_help


def generate_missing_value_csv_like_feature_data_csv(feature_data_csv, instance_path, extractor_path, result_path):
	sfdcsv.Sparkle_Feature_Data_CSV.create_empty_csv(result_path)
	zero_value_csv = sfdcsv.Sparkle_Feature_Data_CSV(result_path)
	
	for column_name in feature_data_csv.list_columns():
		zero_value_csv.add_column(column_name)
	
	length = int(sparkle_global_help.extractor_feature_vector_size_mapping[extractor_path])
	#value_list = [0] * length
	value_list = [sparkle_global_help.sparkle_missing_value] * length
	
	zero_value_csv.add_row(instance_path, value_list)
	
	return zero_value_csv


def computing_features(feature_data_csv_path, mode):
	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
	if mode == 1: list_feature_computation_job = feature_data_csv.get_list_remaining_feature_computation_job()
	elif mode == 2: list_feature_computation_job = feature_data_csv.get_list_recompute_feature_computation_job()
	else:
		print('c Computing features mode error!')
		print('c Do not compute features')
		sys.exit()
	
	runsolver_path = sparkle_global_help.runsolver_path
	if len(sparkle_global_help.extractor_list)==0: cutoff_time_each_extractor_run = ser.cutoff_time_total_extractor_run_on_one_instance + 1
	else: cutoff_time_each_extractor_run = ser.cutoff_time_total_extractor_run_on_one_instance/len(sparkle_global_help.extractor_list) + 1
	cutoff_time_each_run_option = r'-C ' + str(cutoff_time_each_extractor_run)
	print('c Cutoff time for each run on computing features is set to ' + str(cutoff_time_each_extractor_run) + ' seconds')
	
	total_job_num = sparkle_job_help.get_num_of_total_job_from_list(list_feature_computation_job)
	current_job_num = 1
	print('c The number of total running jobs: ' + str(total_job_num))
	
	#flag_exists_missing_value = False
	
	for i in range(0, len(list_feature_computation_job)):
		instance_path = list_feature_computation_job[i][0]
		extractor_list = list_feature_computation_job[i][1]
		len_extractor_list = len(extractor_list)
		for j in range(0, len_extractor_list):
			extractor_path = extractor_list[j]
			basic_part = r'TMP/' + sfh.get_last_level_directory_name(extractor_path) + r'_' + sfh.get_last_level_directory_name(instance_path) + r'_' + sparkle_basic_help.get_time_pid_random_string() 
			result_path = basic_part + r'.rawres'
			err_path = basic_part + r'.err'
			runsolver_watch_data_path = basic_part + r'.log'
			runsolver_watch_data_path_option = r'-w ' + runsolver_watch_data_path
			
			#command_line = extractor_path + r'/' + sparkle_global_help.sparkle_run_default_wrapper + r' ' + extractor_path + r'/' + r' ' + instance_path + r' ' + result_path + r' 2> ' + err_path
			
			command_line = runsolver_path + r' ' + cutoff_time_each_run_option + r' ' + runsolver_watch_data_path_option + r' ' + extractor_path + r'/' + sparkle_global_help.sparkle_run_default_wrapper + r' ' + extractor_path + r'/' + r' ' + instance_path + r' ' + result_path + r' 2> ' + err_path
			
			time.sleep(ser.sleep_time_after_each_extractor_run) #add at version 1.0.2
			
			print(r'c')
			print('c Extractor ' + sfh.get_last_level_directory_name(extractor_path) + ' computing feature vector of instance ' + sfh.get_last_level_directory_name(instance_path) + ' ...')
			
			try:
				os.system(command_line)
			except:
				if not os.path.exists(result_path):
					sfh.create_new_empty_file(result_path)
			
			try:
				tmp_fdcsv = sfdcsv.Sparkle_Feature_Data_CSV(result_path)
			except:
				print('c ****** WARNING: Feature vector computing on instance ' + instance_path + ' failed! ******')
				#print 'c ****** WARNING: Treat the feature vector of this instance as a vector whose all elements are 0 ! ******'
				#print r"c ****** WARNING: The feature vector of this instance will be imputed as the mean value of all other non-missing values after all instances' feature computation done! ******"
				print('c ****** WARNING: The feature vector of this instace consists of missing values ******')
				command_line = r'rm -f ' + result_path
				os.system(command_line)
				tmp_fdcsv = generate_missing_value_csv_like_feature_data_csv(feature_data_csv, instance_path, extractor_path, result_path)
				#flag_exists_missing_value = True
			
			feature_data_csv.combine(tmp_fdcsv)
			#print feature_data_csv.dataframe
		
			command_line = r'rm -f ' + result_path
			os.system(command_line)
			command_line = r'rm -f ' + err_path
			os.system(command_line)
			command_line = r'rm -f ' + runsolver_watch_data_path
			os.system(command_line)
			
			print('c Executing Progress: ' + str(current_job_num) + ' out of ' + str(total_job_num))
			current_job_num += 1
			
			feature_data_csv.update_csv()
			
			print('c Extractor ' + sfh.get_last_level_directory_name(extractor_path) + ' computing feature vector of instance ' + sfh.get_last_level_directory_name(instance_path) + ' done!')
			print(r'c')
	
	#feature_data_csv.update_csv()
	
	return

	






	
