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
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_run_solvers_help as srs

def get_cutoff_time_each_run_from_cutoff_time_information_txt_path(cutoff_time_information_txt_path = sgh.cutoff_time_information_txt_path):
	
	fin = open(cutoff_time_information_txt_path, 'r+')
	fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
	myline = fin.readline().strip()
	mylist = myline.split()
	cutoff_time_each_run = float(mylist[2])
	fin.close()
	
	return cutoff_time_each_run


def construct_sparkle_portfolio_selector(sparkle_portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run):
	python_executable = sgh.python_executable
<<<<<<< HEAD
	# objective_function = r'--objective runtime'
	objective_function = r'--objective solution_quality'
	if not os.path.exists(r'TMP/'): os.mkdir(r'TMP/')
=======
	objective_function = r'--objective runtime'
	if not os.path.exists(r'Tmp/'): os.mkdir(r'Tmp/')
>>>>>>> master
	
	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
	bool_exists_missing_value = feature_data_csv.bool_exists_missing_value()
	if bool_exists_missing_value:
		print('c ****** WARNING: There exists missing value, and all missing values will be imputed as the mean value of all other non-missing values! ******')
		print('c Imputing all missing values starts ...')
		feature_data_csv.impute_missing_value_of_all_columns()
		print('c Imputing all missing values done!')
		impute_feature_data_csv_path = feature_data_csv_path + r'_' + sparkle_basic_help.get_time_pid_random_string() + r'_impute.csv'
		feature_data_csv.save_csv(impute_feature_data_csv_path)
		feature_data_csv_path = impute_feature_data_csv_path
	
	#command_line = python_executable + r' ' + sparkle_global_help.autofolio_path + r' ' + objective_function + r' ' + r'--runtime_cutoff' + r' ' + str(cutoff_time_each_run) + r' ' + r'--performance_csv' + r' ' + performance_data_csv_path + r' ' + r'--feature_csv' + r' ' + feature_data_csv_path + r' ' + r'--save' + r' ' + sparkle_portfolio_selector_path + r' 2> ' + sparkle_global_help.sparkle_log_path
	
	command_line = python_executable + r' ' + sgh.autofolio_path + r' ' + r'--performance_csv' + r' ' + performance_data_csv_path + r' ' + r'--feature_csv' + r' ' + feature_data_csv_path + r' ' + objective_function + r' ' + r'--runtime_cutoff' + r' ' + str(cutoff_time_each_run) + r' ' + r'--tune' + r' ' + r'--save' + r' ' + sparkle_portfolio_selector_path + r' 1>> ' + sgh.sparkle_log_path + r' 2>> ' + sgh.sparkle_err_path

	# Write command line to log
	print('Running command below:\n', command_line, file=open(sgh.sparkle_log_path, 'a+'))
	
	#print 'c ' + command_line
	
	os.system(command_line)
	
	#if not os.path.exists(sparkle_portfolio_selector_path):
	#	print 'c ' + sparkle_portfolio_selector_path + ' does not exist!'
	#	sys.exit()
	
	if bool_exists_missing_value:
		os.system(r'rm -f ' + impute_feature_data_csv_path)
	
	return

