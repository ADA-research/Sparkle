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
from sparkle_help import sparkle_experiments_related_help as ser

def get_list_feature_vector(extractor_path, instance_path, result_path, cutoff_time_each_extractor_run):
	runsolver_path = sgh.runsolver_path
	
	cutoff_time_each_run_option = r'-C ' + str(cutoff_time_each_extractor_run)
	err_path = result_path.replace(r'.rawres', r'.err')
	runsolver_watch_data_path = result_path.replace(r'.rawres', r'.log')
	runsolver_watch_data_path_option = r'-w ' + runsolver_watch_data_path
	
	#command_line = extractor_path + r'/' + sparkle_global_help.sparkle_run_default_wrapper + r' ' + extractor_path + r'/' + r' ' + instance_path + r' ' + result_path
	command_line = runsolver_path + r' ' + cutoff_time_each_run_option + r' ' + runsolver_watch_data_path_option + r' ' + extractor_path + r'/' + sgh.sparkle_run_default_wrapper + r' ' + extractor_path + r'/' + r' ' + instance_path + r' ' + result_path + r' 2> ' + err_path
	
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
		print(r"c ****** WARNING: The feature vector of this instance will be imputed as the mean value of all other non-missing values! ******")
		#length = int(sparkle_global_help.extractor_feature_vector_size_mapping[extractor_path])
		#list_feature_vector = [0]*length
		feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(sgh.feature_data_csv_path)
		list_feature_vector = feature_data_csv.generate_mean_value_feature_vector()
	else:
		fin = open(result_path, 'r+')
		fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
		myline = fin.readline().strip()
		myline = fin.readline().strip()
		list_feature_vector = myline.split(',')
		del list_feature_vector[0]
		fin.close()
	
	command_line = r'rm -f ' + result_path
	os.system(command_line)
	command_line = r'rm -f ' + err_path
	os.system(command_line)
	command_line = r'rm -f ' + runsolver_watch_data_path
	os.system(command_line)
	
	return list_feature_vector

def print_predict_schedule(predict_schedule_result_path):
	fin = open(predict_schedule_result_path, 'r+')
	fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
	myline = fin.readline().strip()
	print('c ' + myline)
	fin.close()
	return

def get_list_predict_schedule_from_file(predict_schedule_result_path):
	#print 'c predict_schedule_result_path = ' + predict_schedule_result_path
	list_predict_schedule = []
	prefix_string = r'Selected Schedule [(algorithm, budget)]: '
	fin = open(predict_schedule_result_path, 'r+')
	fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
	myline = fin.readline().strip()
	#print 'c myline = ' + myline
	mylist_string = myline[len(prefix_string):]
	list_predict_schedule = eval(mylist_string)
	fin.close()
	return list_predict_schedule


def print_solution(raw_result_path):
	fin = open(raw_result_path, 'r+')
	fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
	while True:
		myline = fin.readline().strip()
		if not myline: break
		mylist = myline.split()
		if mylist[1] == r's' or mylist[1] == r'v':
			string_output = ' '.join(mylist[1:])
			print(string_output)
	fin.close()
	return



def call_solver_solve_instance_within_cutoff(solver_path, instance_path, cutoff_time):
	raw_result_path = r'TMP/' + sfh.get_last_level_directory_name(solver_path) + r'_' + sfh.get_last_level_directory_name(instance_path) + r'_' + sparkle_basic_help.get_time_pid_random_string() + r'.rawres'
	srs.run_solver_on_instance(solver_path, solver_path+r'/'+sgh.sparkle_run_default_wrapper, instance_path, raw_result_path, cutoff_time)
	verify_string = srs.judge_correctness_raw_result(instance_path, raw_result_path)
	
	if verify_string == r'SAT': flag_solved = True
	elif verify_string == r'UNSAT': flag_solved = True
	elif verify_string == r'UNKNOWN': flag_solved = False
	elif verify_string == r'WRONG': flag_solved = False
	else: flag_solved = False
	
	if flag_solved: 
		print('c instance solved by solver ' + solver_path)
		print_solution(raw_result_path)
	
	os.system(r'rm -f ' + raw_result_path)
	return flag_solved


def call_sparkle_portfolio_selector_solve_instance(instance_path):
	print('c Start running Sparkle portfolio selector on solving instance ' + sfh.get_last_level_directory_name(instance_path) + ' ...')
	python_executable = sgh.python_executable
	if not os.path.exists(r'TMP/'): os.mkdir(r'TMP/')
	
	print('c Sparkle computing features of instance ' + sfh.get_last_level_directory_name(instance_path) + ' ...')
	list_feature_vector = []
	
	cutoff_time_each_extractor_run = ser.cutoff_time_total_extractor_run_on_one_instance/len(sgh.extractor_list) + 1
	
	for extractor_path in sgh.extractor_list:
		print('c Extractor ' + sfh.get_last_level_directory_name(extractor_path) + ' computing features of instance ' + sfh.get_last_level_directory_name(instance_path) + ' ...')
		result_path = r'TMP/' + sfh.get_last_level_directory_name(extractor_path) + r'_' + sfh.get_last_level_directory_name(instance_path) + r'_' + sparkle_basic_help.get_time_pid_random_string() + r'.rawres'
		
		list_feature_vector = list_feature_vector + get_list_feature_vector(extractor_path, instance_path, result_path, cutoff_time_each_extractor_run)
		print('c Extractor ' + sfh.get_last_level_directory_name(extractor_path) + ' computing features of instance ' + sfh.get_last_level_directory_name(instance_path) + ' done!')
	print('c Sparkle computing features of instance ' + sfh.get_last_level_directory_name(instance_path) + r' done!')
	
	command_line = python_executable + r' ' + sgh.autofolio_path + r' --load ' + sgh.sparkle_portfolio_selector_path + r' --feature_vec'
	for value in list_feature_vector:
		command_line = command_line + r' ' + str(value)
	predict_schedule_result_path = r'TMP/predict_schedule_' + sparkle_basic_help.get_time_pid_random_string() + r'.predres'
	command_line = command_line + r' 1> ' + predict_schedule_result_path + r' 2> ' + sgh.sparkle_err_path
	print('c Sparkle portfolio selector predicting ...')
	os.system(command_line)
	print('c Predicting done!')
	
	print_predict_schedule(predict_schedule_result_path)
	list_predict_schedule = get_list_predict_schedule_from_file(predict_schedule_result_path)
	
	os.system('rm -f ' + predict_schedule_result_path)
	os.system('rm -f ' + sgh.sparkle_err_path)

	for i in range(0, len(list_predict_schedule)):
		solver_path = list_predict_schedule[i][0]
		if i+1 < len(list_predict_schedule):
			cutoff_time = list_predict_schedule[i][1]
		else:
			cutoff_time = sgh.sparkle_maximum_int-1
			print('c This is the last solver call, so time budget for this try changes from ' + str(list_predict_schedule[-1][1]) + ' to ' + str(cutoff_time))
		print('c Calling solver ' + sfh.get_last_level_directory_name(solver_path) + ' with time budget ' + str(cutoff_time) + ' for solving ...')
		sys.stdout.flush()
		flag_solved = call_solver_solve_instance_within_cutoff(solver_path, instance_path, cutoff_time)
		print('c Calling solver ' + sfh.get_last_level_directory_name(solver_path) + ' done!')
		if flag_solved: break
		else: print('c The instance is not solved in this call')
	return


def generate_running_sparkle_portfolio_selector_sbatch_shell_script(sbatch_shell_script_path, num_job_in_parallel, test_case_directory_path, performance_data_csv_path, list_jobs, start_index, end_index):
	job_name = sfh.get_file_name(sbatch_shell_script_path) # specify the name of this sbatch script
	num_job_total = end_index - start_index # calculate the total number of jobs to be handled in this sbatch script
	if num_job_in_parallel > num_job_total:
		num_job_in_parallel = num_job_total # update the number of jobs in parallel accordingly if it is greater than the total number of jobs
	command_prefix = r'srun -N1 -n1 --exclusive python Commands/sparkle_help/run_sparkle_portfolio_core.py ' # specify the prefix of the executing command
	
	fout = open(sbatch_shell_script_path, 'w+') # open the file of sbatch script
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX) # using the UNIX file lock to prevent other attempts to visit this sbatch script
	
	####
	# specify the options of sbatch in the top of this sbatch script
	fout.write(r'#!/bin/bash' + '\n') # use bash to execute this script
	fout.write(r'###' + '\n')
	fout.write(r'###' + '\n')
	fout.write(r'#SBATCH --job-name=' + job_name + '\n') # specify the job name in this sbatch script
	fout.write(r'#SBATCH --output=' + test_case_directory_path + r'TMP/' + job_name + r'.txt' + '\n') # specify the file for normal output
	fout.write(r'#SBATCH --error=' + test_case_directory_path + r'TMP/' + job_name + r'.err' + '\n') # specify the file for error output
	fout.write(r'###' + '\n')
	fout.write(r'#SBATCH --mem-per-cpu=3072' + '\n') #assigned 3GB memory for each cpu
	fout.write(r'#SBATCH --array=0-' + str(num_job_total-1) + r'%' + str(num_job_in_parallel) + '\n') # using slurm job array and specify the number of jobs executing in parallel in this sbatch script
	fout.write(r'###' + '\n')
	####
	
	####
	# specify the array of parameters for each command
	fout.write('params=( \\' + '\n')
	
	for i in range(start_index, end_index):
		instance_path = list_jobs[i][0]
		fout.write('\'%s %s\' \\' % (instance_path, test_case_directory_path) + '\n') # each parameter tuple contains instance path and extractor path
	
	fout.write(r')' + '\n')
	####
	
	command_line = command_prefix + r' ' + r'${params[$SLURM_ARRAY_TASK_ID]}' + r' ' + performance_data_csv_path # specify the complete command
	
	fout.write(command_line + '\n') # write the complete command in this sbatch script
	
	fout.close() # close the file of the sbatch script
	return



	
def call_sparkle_portfolio_selector_solve_instance_directory(instance_directory_path):
	if instance_directory_path[-1] != r'/':
		instance_directory_path += r'/'
	instance_directory_path_last_level = sfh.get_last_level_directory_name(instance_directory_path)
	if instance_directory_path_last_level[-1] != r'/':
		instance_directory_path_last_level += r'/'
	test_case_directory_path = r'Test_Cases/' + instance_directory_path_last_level
	
	list_all_cnf_filename = sfh.get_list_all_cnf_filename(instance_directory_path)
	
	if not os.path.exists(r'Test_Cases/'):
		os.system(r'mkdir Test_Cases/')
	os.system(r'mkdir -p ' + test_case_directory_path)
	os.system(r'mkdir -p ' + test_case_directory_path + r'TMP/')
	
	test_performance_data_csv_name = r'sparkle_performance_data.csv'
	test_performance_data_csv_path = test_case_directory_path + test_performance_data_csv_name
	spdcsv.Sparkle_Performance_Data_CSV.create_empty_csv(test_performance_data_csv_path)
	test_performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(test_performance_data_csv_path)
	
	total_job_list = []
	for cnf_filename in list_all_cnf_filename:
		cnf_filepath = instance_directory_path + cnf_filename
		test_performance_data_csv.add_row(cnf_filepath)
		total_job_list.append([cnf_filepath])
	
	solver_name = r'Sparkle_Portfolio_Selector'
	test_performance_data_csv.add_column(solver_name)
	
	test_performance_data_csv.update_csv()
	
	i = 0
	j = len(total_job_list)
	sbatch_shell_script_path = test_case_directory_path + r'TMP/'+ r'running_sparkle_portfolio_selector_sbatch_shell_script_' + str(i) + r'_' + str(j) + r'_' + sparkle_basic_help.get_time_pid_random_string() + r'.sh'
	generate_running_sparkle_portfolio_selector_sbatch_shell_script(sbatch_shell_script_path, ser.num_job_in_parallel, test_case_directory_path, test_performance_data_csv_path, total_job_list, i, j)
	os.system(r'chmod a+x ' + sbatch_shell_script_path)
	command_line = r'sbatch ' + sbatch_shell_script_path
	
	os.system(command_line)
	#print(command_line)
	
	return







