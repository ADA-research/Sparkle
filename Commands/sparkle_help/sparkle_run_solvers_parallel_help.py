#!/usr/bin/env python2.7
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
import sparkle_global_help
import sparkle_basic_help
import sparkle_file_help as sfh
import sparkle_performance_data_csv_help as spdcsv
import sparkle_experiments_related_help as ser
import sparkle_job_help
import sparkle_run_solvers_help as srs


####
# settings of experimental configurations
global cutoff_time_each_run
global par_num
global penalty_time

cutoff_time_each_run = ser.cutoff_time_each_run # cutoff time for each run (a solver tries to solve an instance)
par_num = ser.par_num # the penalty number related to the penalty time
penalty_time = ser.penalty_time # the penalty time = cutoff time * penalty number
sleep_time_after_each_solver_run = ser.sleep_time_after_each_solver_run #the sleep time for the system after each run (add at version 1.0.2)
####

def generate_running_solvers_sbatch_shell_script(sbatch_shell_script_path, num_job_in_parallel, performance_data_csv_path, list_jobs, start_index, end_index):
	####
	# This function is used for generating sbatch script (slurm system required) for executing performance computation jobs in parallel.
	# The 1st argument (sbatch_shell_script_path) specifies the path of the sbatch shell script to be grenerated.
	# The 2nd argument (num_job_in_parallel) specifies the number of jobs that will be executing in parallel.
	# The 3rd argument (performance_data_csv_path) specifies the path of the csv file where the resulting performance data would be placed.
	# The 4th argument (list_jobs) specifies the list of jobs to be computed.
	# The 5th argument (start_index) specifies the start index (included) of the job  list to be handled in this sbatch script.
	# The 6th argument (end_index) specifies the end index (excluded) of the job list to be handled in this sbatch script.
	####
	job_name = sfh.get_file_name(sbatch_shell_script_path) # specify the name of this sbatch script
	num_job_total = end_index - start_index # calculate the total number of jobs to be handled in this sbatch script
	if num_job_in_parallel > num_job_total:
		num_job_in_parallel = num_job_total # update the number of jobs in parallel accordingly if it is greater than the total number of jobs
	command_prefix = r'srun -N1 -n1 --exclusive python2 Commands/sparkle_help/run_solvers_core.py ' # specify the prefix of the executing command
	
	fout = open(sbatch_shell_script_path, 'w+') # open the file of sbatch script
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX) # using the UNIX file lock to prevent other attempts to visit this sbatch script
	
	####
	# specify the options of sbatch in the top of this sbatch script
	fout.write(r'#!/bin/bash' + '\n') # use bash to execute this script
	fout.write(r'###' + '\n')
	fout.write(r'###' + '\n')
	fout.write(r'#SBATCH --job-name=' + job_name + '\n') # specify the job name in this sbatch script
	fout.write(r'#SBATCH --output=' + r'TMP/' + job_name + r'.txt' + '\n') # specify the file for normal output
	fout.write(r'#SBATCH --error=' + r'TMP/' + job_name + r'.err' + '\n') # specify the file for error output
	fout.write(r'###' + '\n')
	fout.write(r'#SBATCH --partition=grace30' + '\n')
	fout.write('#SBATCH --mem-per-cpu=%d' % (ser.memory_limit_each_solver_run) + '\n') #assigned preset memory for each cpu
	fout.write(r'#SBATCH --array=0-' + str(num_job_total-1) + r'%' + str(num_job_in_parallel) + '\n') # using slurm job array and specify the number of jobs executing in parallel in this sbatch script
	fout.write(r'###' + '\n')
	####
	
	####
	# specify the array of parameters for each command
	fout.write('params=( \\' + '\n')
	
	for i in range(start_index, end_index):
		instance_path = list_jobs[i][0]
		solver_path = list_jobs[i][1]
		fout.write('\'%s %s\' \\' % (instance_path, solver_path) + '\n') # each parameter tuple contains instance path and extractor path
	
	fout.write(r')' + '\n')
	####
	
	command_line = command_prefix + r' ' + r'${params[$SLURM_ARRAY_TASK_ID]}' + r' ' + performance_data_csv_path # specify the complete command
	
	fout.write(command_line + '\n') # write the complete command in this sbatch script
	
	fout.close() # close the file of the sbatch script
	return


def running_solvers_parallel(performance_data_csv_path, num_job_in_parallel, mode):
	####
	# This function is used for running solvers in parallel.
	# The 1st argument (performance_data_csv_path) specifies the path of the csv file where the resulting performance data would be placed.
	# The 2nd argument (num_job_in_parallel) specifies the number of jobs that will be executing in parallel.
	# The 3nd argument (mode) specifies the mode of computation. It has 2 possible values (1 or 2). If this value is 1, it means that this function will compute the remaining jobs for performance computation. Otherwise (if this value is 2), it means that this function will re-compute all jobs for performance computation.
	####
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path) # open the csv file in terms of performance data
	if mode == 1: list_performance_computation_job = performance_data_csv.get_list_remaining_performance_computation_job() # the value of mode is 1, so the list of computation jobs is the list of the remaining jobs
	elif mode == 2: list_performance_computation_job = performance_data_csv.get_list_recompute_performance_computation_job() # the value of mode is 2, so the list of computation jobs is the list of all jobs (recomputing)
	else: # the abnormal case, exit
		print 'c Running solvers mode error!'
		print 'c Do not run solvers'
		sys.exit()
	
	print 'c Cutoff time for each run on solving an instance is set to ' + str(cutoff_time_each_run) + ' seconds' # print the information about the cutoff time
	
	####
	# expand the job list
	total_job_num = sparkle_job_help.get_num_of_total_job_from_list(list_performance_computation_job)
	print 'c The number of total running jobs: ' + str(total_job_num)
	total_job_list = sparkle_job_help.expand_total_job_from_list(list_performance_computation_job)
	####
	
	if len(total_job_list) == 0:
		return ''
	
	####
	# generate the sbatch script
	i = 0
	j = len(total_job_list)
	sbatch_shell_script_path = r'TMP/'+ r'running_solvers_sbatch_shell_script_' + str(i) + r'_' + str(j) + r'_' + sparkle_basic_help.get_time_pid_random_string() + r'.sh'
	generate_running_solvers_sbatch_shell_script(sbatch_shell_script_path, num_job_in_parallel, performance_data_csv_path, total_job_list, i, j)
	os.system(r'chmod a+x ' + sbatch_shell_script_path)
	command_line = r'sbatch ' + sbatch_shell_script_path
	####
	
	#os.system(command_line) # execute the sbatch script via slurm
	output_list = os.popen(command_line).readlines()
	if len(output_list) > 0 and len(output_list[0].strip().split())>0:
		run_solvers_parallel_jobid = output_list[0].strip().split()[-1]
	else:
		run_solvers_parallel_jobid = ''
	
	####
	# record the experimental settings 
	sfh.write_string_to_file(sparkle_global_help.cutoff_time_information_txt_path, "cutoff_time_each_run = " + str(cutoff_time_each_run))
	sfh.append_string_to_file(sparkle_global_help.cutoff_time_information_txt_path, "par_num = " + str(par_num))
	####
	return run_solvers_parallel_jobid




	
