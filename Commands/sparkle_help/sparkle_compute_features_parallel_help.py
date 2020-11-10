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
try:
	from sparkle_help import sparkle_global_help
	from sparkle_help import sparkle_basic_help
	from sparkle_help import sparkle_file_help as sfh
	from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
	from sparkle_help import sparkle_experiments_related_help as ser
	from sparkle_help import sparkle_job_help
	from sparkle_help import sparkle_compute_features_help as scf
except ImportError:
	import sparkle_global_help
	import sparkle_basic_help
	import sparkle_file_help as sfh
	import sparkle_feature_data_csv_help as sfdcsv
	import sparkle_experiments_related_help as ser
	import sparkle_job_help
	import sparkle_compute_features_help as scf

def generate_computing_features_sbatch_shell_script(sbatch_shell_script_path, num_job_in_parallel, feature_data_csv_path, list_jobs, start_index, end_index):
	####
	# This function is used for generating sbatch script (slurm system required) for executing feature computation jobs in parallel.
	# The 1st argument (sbatch_shell_script_path) specifies the path of the sbatch shell script to be generated.
	# The 2nd argument (num_job_in_paralle) specifies the number of jobs that will be executing in parallel.
	# The 3rd argument (feature_data_csv_path) specifies the path of the csv file where the resulting feature data would be placed.
	# The 4th argument (list_jobs) specifies the list of jobs to be computed.
	# The 5th argument (start_index) specifies the start index (included) of the job list to be handled in this sbatch script.
	# The 6th argument (end_index) specifies the end index (excluded) of the job list to be handled in this sbatch script.
	####
	job_name = sfh.get_file_name(sbatch_shell_script_path) # specify the name of this sbatch script
	num_job_total = end_index - start_index # calculate the total number of jobs to be handled in this sbatch script
	if num_job_in_parallel > num_job_total:
		num_job_in_parallel = num_job_total # update the number of jobs in parallel accordingly if it is greater than the total number of jobs
	command_prefix = r'srun -N1 -n1 --exclusive python3 Commands/sparkle_help/compute_features_core.py ' # specify the prefix of the executing command
	
	fout = open(sbatch_shell_script_path, 'w+') # open the file of sbatch script
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX) # using the UNIX file lock to prevent other attempts to visit this sbatch script
	
	####
	# specify the options of sbatch in the top of this sbatch script
	fout.write(r'#!/bin/bash' + '\n') # use bash to execute this script
	fout.write(r'###' + '\n')
	fout.write(r'#SBATCH --job-name=' + job_name + '\n') # specify the job name in this sbatch script
	fout.write(r'#SBATCH --output=' + r'TMP/' + job_name + r'.txt' + '\n') # specify the file for normal output
	fout.write(r'#SBATCH --error=' + r'TMP/' + job_name + r'.err' + '\n') # specify the file for error output
	fout.write(r'###' + '\n')
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
		extractor_path = list_jobs[i][1]
		fout.write('\'%s %s\' \\' % (instance_path, extractor_path) + '\n') # each parameter tuple contains instance path and extractor path
	
	fout.write(r')' + '\n')
	####	
		
	command_line = command_prefix + r' ' + r'${params[$SLURM_ARRAY_TASK_ID]}' + r' ' + feature_data_csv_path # specify the complete command
	
	fout.write(command_line + '\n') # write the complete command in this sbatch script
	
	fout.close() # close the file of the sbatch script
	return


def computing_features_parallel(feature_data_csv_path, num_job_in_parallel, mode):
	####
	# This function is used for computing features in parallel.
	# The 1st argument (feature_data_csv_path) specifies the path of the csv file where the resulting feature data would be placed.
	# The 2nd argument (num_job_in_parallel) specifies the number of jobs that will be executing in parallel.
	# The 3nd argument (mode) specifies the mode of computation. It has 2 possible values (1 or 2). If this value is 1, it means that this function will compute the remaining jobs for feature computation. Otherwise (if this value is 2), it means that this function will re-compute all jobs for feature computation.
	####
	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path) # open the csv file in terms of feature data
	if mode == 1: list_feature_computation_job = feature_data_csv.get_list_remaining_feature_computation_job() # the value of mode is 1, so the list of computation jobs is the list of the remaining jobs
	elif mode == 2: list_feature_computation_job = feature_data_csv.get_list_recompute_feature_computation_job() # the value of mode is 2, so the list of computation jobs is the list of all jobs (recomputing)
	else: # the abnormal case, exit
		print('c Computing features mode error!')
		print('c Do not compute features')
		sys.exit()
	
	####
	# set the options to the runsolver software
	runsolver_path = sparkle_global_help.runsolver_path
	if len(sparkle_global_help.extractor_list)==0: cutoff_time_each_extractor_run = ser.cutoff_time_total_extractor_run_on_one_instance + 1
	else: cutoff_time_each_extractor_run = ser.cutoff_time_total_extractor_run_on_one_instance/len(sparkle_global_help.extractor_list) + 1
	cutoff_time_each_run_option = r'-C ' + str(cutoff_time_each_extractor_run)
	print('c Cutoff time for each run on computing features is set to ' + str(cutoff_time_each_extractor_run) + ' seconds') # print the information about the cutoff time
	####
	
	####
	# expand the job list
	total_job_num = sparkle_job_help.get_num_of_total_job_from_list(list_feature_computation_job)
	print('c The number of total running jobs: ' + str(total_job_num))
	total_job_list = sparkle_job_help.expand_total_job_from_list(list_feature_computation_job)
	####
	
	####
	# generate the sbatch script
	i = 0
	j = len(total_job_list)
	sbatch_shell_script_path = r'TMP/' + r'computing_features_sbatch_shell_script_' + str(i) + r'_' + str(j) + r'_' + sparkle_basic_help.get_time_pid_random_string() + r'.sh'
	generate_computing_features_sbatch_shell_script(sbatch_shell_script_path, num_job_in_parallel, feature_data_csv_path, total_job_list, i, j)
	os.system(r'chmod a+x ' + sbatch_shell_script_path)
	command_line = r'sbatch ' + sbatch_shell_script_path
	####
	
	os.system(command_line) # execute the sbatch script via slurm
	return





	
