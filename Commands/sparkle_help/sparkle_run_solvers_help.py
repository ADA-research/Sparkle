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
from pathlib import Path

try:
	from sparkle_help import sparkle_global_help as sgh
	from sparkle_help import sparkle_basic_help
	from sparkle_help import sparkle_file_help as sfh
	from sparkle_help import sparkle_performance_data_csv_help as spdcsv
	from sparkle_help import sparkle_experiments_related_help as ser
	from sparkle_help import sparkle_job_help
except ImportError:
	import sparkle_global_help as sgh
	import sparkle_basic_help
	import sparkle_file_help as sfh
	import sparkle_performance_data_csv_help as spdcsv
	import sparkle_experiments_related_help as ser
	import sparkle_job_help

import functools
print = functools.partial(print, flush=True)

global cutoff_time_each_run
global par_num
global penalty_time

cutoff_time_each_run = ser.cutoff_time_each_run
par_num = ser.par_num
penalty_time = ser.penalty_time
sleep_time_after_each_solver_run = ser.sleep_time_after_each_solver_run #add at version 1.0.2


def run_solver_on_instance(relative_path, solver_wrapper_path, instance_path, raw_result_path, cutoff_time = cutoff_time_each_run):
	if not Path(solver_wrapper_path).is_file():
		print('c Wrapper named \'' + sgh.sparkle_run_default_wrapper + '\' not found, stopping execution!')
		sys.exit()

	runsolver_path = sgh.runsolver_path
	runsolver_option = r'--timestamp --use-pty'
	#cutoff_time_each_run_option = r'-C ' + str(cutoff_time_each_run)
	cutoff_time_each_run_option = r'-C ' + str(cutoff_time)
	runsolver_watch_data_path = raw_result_path.replace('.rawres', '.log')
	runsolver_watch_data_path_option = r'-w ' + runsolver_watch_data_path
	raw_result_path_option = r'-o ' + raw_result_path
	solver_wrapper_path_option = solver_wrapper_path
	relative_path_option = relative_path
	instance_path_option = instance_path
	
	command_line = runsolver_path + r' ' + runsolver_option + r' ' + cutoff_time_each_run_option + r' ' + runsolver_watch_data_path_option + r' ' + raw_result_path_option + r' ' + solver_wrapper_path_option + r' ' + relative_path_option + r' ' + instance_path_option
	
	try:
		os.system(command_line)
	except:
		if not os.path.exists(raw_result_path):
			sfh.create_new_empty_file(raw_result_path)
	
	command_line = 'rm -f ' + runsolver_watch_data_path
	os.system(command_line)
	return


def get_runtime(raw_result_path):
	# SATISFIABLE, UNSATISFIABLE
	runtime = 0
	
	fin = open(raw_result_path, 'r+')
	fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
	while True:
		myline = fin.readline().strip()
		if not myline: break
		mylist = myline.split()
		if len(mylist)==3 and mylist[1] == r's':
			if mylist[2] == r'SATISFIABLE' or mylist[2] == r'UNSATISFIABLE':
				mylist_time = mylist[0].split(r'/')
				runtime = float(mylist_time[0]) ## use CPU time as runtime
				##runtime = float(mylist_time[1]) ## use wall-clock time as runtime
				break
	fin.close()
	return runtime


def get_verify_string(tmp_verify_result_path):
	#4 return values: 'SAT', 'UNSAT', 'WRONG', 'UNKNOWN'
	ret = 'UNKNOWN'
	fin = open(tmp_verify_result_path, 'r+')
	fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
	while True:
		myline = fin.readline()
		myline = myline.strip()
		if not myline: break
		if myline == r'Solution verified.':
			myline2 = fin.readline()
			myline2 = fin.readline().strip()
			if myline2 == r'11':
				ret = r'SAT'
				break
		elif myline == r'Solver reported unsatisfiable. I guess it must be right!':
			myline2 = fin.readline()
			myline2 = fin.readline().strip()
			if myline2 == r'10':
				ret = r'UNSAT'
				break
		elif myline == r'Wrong solution.':
			myline2 = fin.readline()
			myline2 = fin.readline().strip()
			if myline2 == r'0':
				ret = 'WRONG'
				break
		else:
			continue	
	fin.close()
	return ret



def judge_correctness_raw_result(instance_path, raw_result_path):
	SAT_verifier_path = sgh.SAT_verifier_path
	tmp_verify_result_path = r'Tmp/'+ sfh.get_last_level_directory_name(SAT_verifier_path) + r'_' + sfh.get_last_level_directory_name(raw_result_path) + r'_' + sparkle_basic_help.get_time_pid_random_string() + r'.vryres'
	command_line = SAT_verifier_path + r' ' + instance_path + r' ' + raw_result_path + r' > ' + tmp_verify_result_path
	print('c Run SAT verifier')
	os.system(command_line)
	print('c SAT verifier done')
	
	ret = get_verify_string(tmp_verify_result_path)
	
	command_line = 'rm -f ' + tmp_verify_result_path
	os.system(command_line)
	return ret
	

def running_solvers(performance_data_csv_path, mode):
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	if mode == 1: list_performance_computation_job = performance_data_csv.get_list_remaining_performance_computation_job()
	elif mode == 2: list_performance_computation_job = performance_data_csv.get_list_recompute_performance_computation_job()
	else:
		print('c Running solvers mode error!')
		print('c Do not run solvers')
		sys.exit()
	
	print('c Cutoff time for each run on solving an instance is set to ' + str(cutoff_time_each_run) + ' seconds')
	
	total_job_num = sparkle_job_help.get_num_of_total_job_from_list(list_performance_computation_job)
	current_job_num = 1
	print('c The number of total running jobs: ' + str(total_job_num))
	
	wrong_solver_list = []
	
	for i in range(0, len(list_performance_computation_job)):
		instance_path = list_performance_computation_job[i][0]
		solver_list = list_performance_computation_job[i][1]
		len_solver_list = len(solver_list)
		for j in range(0, len_solver_list):
			solver_path = solver_list[j]
			
			if solver_path in wrong_solver_list:
				print(r'c')
				print(r'c Solver ' + sfh.get_last_level_directory_name(solver_path) + r' is a wrong solver')
				print(r'c Executing Progress: ' + str(current_job_num) + ' out of ' + str(total_job_num))
				current_job_num += 1
				print(r'c Solver ' + sfh.get_last_level_directory_name(solver_path) + ' running on instance ' + sfh.get_last_level_directory_name(instance_path) + ' ignored!')
				print(r'c')
				continue
			
			raw_result_path = r'Tmp/' + sfh.get_last_level_directory_name(solver_path) + r'_' + sfh.get_last_level_directory_name(instance_path) + r'_' + sparkle_basic_help.get_time_pid_random_string() + r'.rawres'
			
			time.sleep(sleep_time_after_each_solver_run) #add at version 1.0.2
			
			print(r'c')
			print('c Solver ' + sfh.get_last_level_directory_name(solver_path) + ' running on instance ' + sfh.get_last_level_directory_name(instance_path) + ' ...')
			
			run_solver_on_instance(solver_path, solver_path+r'/'+sgh.sparkle_run_default_wrapper, instance_path, raw_result_path)
		
			verify_string = judge_correctness_raw_result(instance_path, raw_result_path)
		
			runtime = 0
		
			if verify_string == r'SAT':
				runtime = get_runtime(raw_result_path)
				if runtime > cutoff_time_each_run: runtime = penalty_time
				performance_data_csv.set_value(instance_path, solver_path, runtime)
				if sgh.instance_reference_mapping[instance_path] != r'SAT':
					sgh.instance_reference_mapping[instance_path] = r'SAT'
					sfh.write_instance_reference_mapping()
				print(r'c Running Result: ' + verify_string + r' , Runtime: ' + str(runtime))
			elif verify_string == r'UNSAT':
				runtime = get_runtime(raw_result_path)
				if runtime > cutoff_time_each_run: runtime = penalty_time
				performance_data_csv.set_value(instance_path, solver_path, runtime)
				if sgh.instance_reference_mapping[instance_path] != r'UNSAT':
					sgh.instance_reference_mapping[instance_path] = r'UNSAT'
					sfh.write_instance_reference_mapping()
				print(r'c Running Result: ' + verify_string + r' , Runtime: ' + str(runtime))
			elif verify_string == r'UNKNOWN':
				runtime = penalty_time
				performance_data_csv.set_value(instance_path, solver_path, runtime)
				print(r'c Running Result: ' + verify_string + r' , Runtime (Penalized): ' + str(runtime))
			elif verify_string == r'WRONG':
				wrong_solver_list.append(solver_path)
				print(r'c Solver ' + sfh.get_last_level_directory_name(solver_path) + r' reports wrong answer on instance ' + sfh.get_last_level_directory_name(instance_path) + r'!')
				print(r'c Solver ' + sfh.get_last_level_directory_name(solver_path) + r' will be removed!')
			
				performance_data_csv.delete_column(solver_path)
				sgh.solver_list.remove(solver_path)
				output = sgh.solver_nickname_mapping.pop(solver_path)
				sfh.write_solver_list()
				sfh.write_solver_nickname_mapping()
				
				print(r'c Solver ' + sfh.get_last_level_directory_name(solver_path) + r' is a wrong solver')
				print(r'c Executing Progress: ' + str(current_job_num) + ' out of ' + str(total_job_num))
				current_job_num += 1
				print(r'c Solver ' + sfh.get_last_level_directory_name(solver_path) + ' running on instance ' + sfh.get_last_level_directory_name(instance_path) + ' ignored!')
				print(r'c')
				
				continue
			else:
				#the same as unknown
				verify_string = r'UNKNOWN' #treated as unknown
				runtime = penalty_time
				performance_data_csv.set_value(instance_path, solver_path, runtime)
				print(r'c Running Result: ' + verify_string + r' , Runtime (Penalized): ' + str(runtime))
		
			command_line = r'rm -f ' + raw_result_path
			os.system(command_line)
			
			print(r'c Executing Progress: ' + str(current_job_num) + ' out of ' + str(total_job_num))
			current_job_num += 1
			
			performance_data_csv.update_csv()
			print(r'c Solver ' + sfh.get_last_level_directory_name(solver_path) + ' running on instance ' + sfh.get_last_level_directory_name(instance_path) + ' done!')
			print(r'c')

	#performance_data_csv.update_csv()
	sfh.write_string_to_file(sgh.cutoff_time_information_txt_path, "cutoff_time_each_run = " + str(cutoff_time_each_run))
	sfh.append_string_to_file(sgh.cutoff_time_information_txt_path, "par_num = " + str(par_num))
	
	return


	
