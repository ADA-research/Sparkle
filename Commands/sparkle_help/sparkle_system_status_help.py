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
import time
import datetime
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_job_help


def print_solver_list(mode = 1):
	solver_list = sparkle_global_help.solver_list
	print(r'c')
	print(r'c Currently Sparkle has ' + str(len(solver_list)) + r' solvers:')
	
	if mode == 2:
		i=1
		for solver in solver_list:
			print(r'c [' + str(i) + r']: Solver: ' + sfh.get_last_level_directory_name(solver))
			i+=1
	
	print(r'c')
	return

def print_extractor_list(mode = 1):
	extractor_list = sparkle_global_help.extractor_list
	print(r'c')
	print(r'c Currently Sparkle has ' + str(len(extractor_list)) + r' feature extractors:')
	
	if mode == 2:
		i=1
		for extractor in extractor_list:
			print(r'c [' + str(i) + r']: Extractor: ' + sfh.get_last_level_directory_name(extractor))
			i+=1
	
	print(r'c')
	return

def print_instance_list(mode = 1):
	instance_list = sparkle_global_help.instance_list
	print(r'c')
	print(r'c Currently Sparkle has ' + str(len(instance_list)) + r' instances:')
	
	if mode == 2:
		i=1
		for instance in instance_list:
			print(r'c [' + str(i) + r']: Instance: ' + sfh.get_last_level_directory_name(instance))
			i+=1
	
	print(r'c')
	return

def print_list_remaining_feature_computation_job(feature_data_csv_path, mode = 1):
	try:
		feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
		list_feature_computation_job = feature_data_csv.get_list_remaining_feature_computation_job()
	except:
		list_feature_computation_job = []
	total_job_num = sparkle_job_help.get_num_of_total_job_from_list(list_feature_computation_job)	
	
	print(r'c')
	print(r'c Currently Sparkle has ' + str(total_job_num) + r' remaining feature computation jobs needed to be performed:')
	
	if mode == 2:
		current_job_num = 1
		for i in range(0, len(list_feature_computation_job)):
			instance_path = list_feature_computation_job[i][0]
			extractor_list = list_feature_computation_job[i][1]
			len_extractor_list = len(extractor_list)
			for j in range(0, len_extractor_list):
				extractor_path = extractor_list[j]
				print(r'c [' + str(current_job_num) + r']: Extractor: ' + sfh.get_last_level_directory_name(extractor_path) + r', Instance: ' + sfh.get_last_level_directory_name(instance_path))
				current_job_num += 1
	
	print(r'c')
	return

def print_list_remaining_performance_computation_job(performance_data_csv_path, mode = 1):
	try:
		performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
		list_performance_computation_job = performance_data_csv.get_list_remaining_performance_computation_job()
	except:
		list_performance_computation_job = []
	total_job_num = total_job_num = sparkle_job_help.get_num_of_total_job_from_list(list_performance_computation_job)
	
	print(r'c')
	print(r'c Currently Sparkle has ' + str(total_job_num) + r' remaining performance computation jobs needed to be performed:')
	
	if mode == 2:
		current_job_num = 1
		for i in range(0, len(list_performance_computation_job)):
			instance_path = list_performance_computation_job[i][0]
			solver_list = list_performance_computation_job[i][1]
			len_solver_list = len(solver_list)
			for j in range(0, len_solver_list):
				solver_path = solver_list[j]
				print(r'c [' + str(current_job_num) + r']: Solver: ' + sfh.get_last_level_directory_name(solver_path) + r', Instance: ' + sfh.get_last_level_directory_name(instance_path))
				current_job_num += 1
	
	print(r'c')
	return

def print_portfolio_selector_info():
	sparkle_portfolio_selector_path = sparkle_global_help.sparkle_portfolio_selector_path
	print(r'c')
	print(r'c Status of portfolio selector in Sparkle:')
	
	key_str = 'construct_sparkle_portfolio_selector'
	task_run_status_path = r'TMP/SBATCH_Portfolio_Jobs/' + key_str + r'.statusinfo'
	if os.path.isfile(task_run_status_path):
		print(r'c Currently Sparkle portfolio selecotr is constructing ...')
	elif os.path.isfile(sparkle_portfolio_selector_path):
		print(r'c Path: ' + sparkle_portfolio_selector_path)
		print(r'c Last modified time: ' + get_file_modify_time(sparkle_portfolio_selector_path))
	else:
		print(r'c No portfolio selector exists!')
	print(r'c')
	return

def print_report_info():
	sparkle_report_path = sparkle_global_help.sparkle_report_path
	print(r'c')
	print(r'c Status of report in Sparkle:')
	
	key_str = 'generate_report'
	task_run_status_path = r'TMP/SBATCH_Report_Jobs/' + key_str + r'.statusinfo'
	if os.path.isfile(task_run_status_path):
		print(r'c Currently Sparkle report is generating ...')
	elif os.path.isfile(sparkle_report_path):
		print(r'c Path: ' + sparkle_report_path)
		print(r'c Last modified time: ' + get_file_modify_time(sparkle_report_path))
	else:
		print(r'c No report exists!')
	print(r'c')
	return

def timestamp_to_time(timestamp):
	#time_struct = time.localtime(timestamp)
	time_struct = time.gmtime(timestamp)
	return time.strftime('%Y-%m-%d %H:%M:%S',time_struct)
	
def get_file_modify_time(file_path):
	timestamp = os.path.getmtime(file_path)
	return timestamp_to_time(timestamp) + r' (UTC+0)'

