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
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_experiments_related_help as ser
from sparkle_help import sparkle_job_help
from sparkle_help import sparkle_run_solvers_help as srs

def run_sparkle_portfolio_selector_on_instance(solver_wrapper_path, instance_path, raw_result_path, cutoff_time = ser.cutoff_time_each_run):
	runsolver_path = sparkle_global_help.runsolver_path
	runsolver_option = r'--timestamp --use-pty'
	#cutoff_time_each_run_option = r'-C ' + str(cutoff_time_each_run)
	cutoff_time_each_run_option = r'-C ' + str(cutoff_time)
	runsolver_watch_data_path = raw_result_path.replace('.rawres', '.log')
	runsolver_watch_data_path_option = r'-w ' + runsolver_watch_data_path
	raw_result_path_option = r'-o ' + raw_result_path
	solver_wrapper_path_option = solver_wrapper_path
	instance_path_option = instance_path
	
	command_line = runsolver_path + r' ' + runsolver_option + r' ' + cutoff_time_each_run_option + r' ' + runsolver_watch_data_path_option + r' ' + raw_result_path_option + r' ' + solver_wrapper_path_option + r' ' + instance_path_option
	
	try:
		os.system(command_line)
	except:
		if not os.path.exists(raw_result_path):
			sfh.create_new_empty_file(raw_result_path)
	
	command_line = 'rm -f ' + runsolver_watch_data_path
	os.system(command_line)
	return


if __name__ == r'__main__':
	cutoff_time_each_run = ser.cutoff_time_each_run
	par_num = ser.par_num
	penalty_time = ser.penalty_time
	
	instance_path = sys.argv[1]
	test_case_directory_path = sys.argv[2]
	performance_data_csv_path = sys.argv[3]
	
	if test_case_directory_path[-1] != r'/':
		test_case_directory_path += r'/'
	
	solver_name = r'Sparkle_Portfolio_Selector'
	
	key_str = solver_name + r'_' + sfh.get_last_level_directory_name(instance_path) + r'_' + sparkle_basic_help.get_time_pid_random_string()
	raw_result_path = test_case_directory_path + r'TMP/' + key_str + r'.rawres'
	
	run_sparkle_portfolio_selector_on_instance(r'Commands/run_sparkle_portfolio_selector.py', instance_path, raw_result_path, ser.cutoff_time_each_run)
	
	verify_string = srs.judge_correctness_raw_result(instance_path, raw_result_path)
	
	runtime = 0
	
	if verify_string == r'SAT':
		runtime = srs.get_runtime(raw_result_path)
		if runtime > cutoff_time_each_run: runtime = penalty_time
	elif verify_string == r'UNSAT':
		runtime = srs.get_runtime(raw_result_path)
		if runtime > cutoff_time_each_run: runtime = penalty_time
	elif verify_string == r'UNKNOWN':
		runtime = penalty_time
	elif verify_string == r'WRONG':
		runtime = penalty_time
		### TODO: Handle the situation when wrong answer appears ####
	else:
		#the same as unknown
		verify_string = r'UNKNOWN' #treated as unknown
		runtime = penalty_time
	
	fo = open(performance_data_csv_path, 'r+')
	fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	performance_data_csv.set_value(instance_path, solver_name, runtime)
	performance_data_csv.dataframe.to_csv(performance_data_csv_path)
	fo.close()
		
	command_line = r'rm -f ' + raw_result_path
	os.system(command_line)

