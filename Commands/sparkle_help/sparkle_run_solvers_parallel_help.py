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
from sparkle_help import sparkle_slurm_help as ssh


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

def generate_running_solvers_sbatch_shell_script(total_job_num, num_job_in_parallel, performance_data_csv_path, total_job_list):
	sbatch_script_name = r'running_solvers_sbatch_shell_script_' + sparkle_basic_help.get_time_pid_random_string() + r'.sh'
	sbatch_script_path = r'TMP/' + sbatch_script_name
	job_name = '--job-name=' + sbatch_script_name
	output = '--output=' + sbatch_script_path + '.txt'
	error = '--error=' + sbatch_script_path + '.err'
	array = '--array=0-' + str(total_job_num-1) + '%' + str(num_job_in_parallel)

	sbatch_options_list = [job_name, output, error, array]
	sbatch_options_list.extend(ssh.get_slurm_sbatch_default_options_list())
	sbatch_options_list.extend(ssh.get_slurm_sbatch_user_options_list())
	job_params_list = []

	for job in total_job_list:
		instance_path = job[0]
		solver_path = job[1]
		job_params_list.append(instance_path + ' ' + solver_path + ' ' + performance_data_csv_path)

	srun_options_str = '-N1 -n1'
	srun_options_str = srun_options_str + ' ' + ssh.get_slurm_srun_user_options_str()
	target_call_str = 'Commands/sparkle_help/run_solvers_core.py'

	ssh.generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list, job_params_list, srun_options_str, target_call_str)

	return sbatch_script_path


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
		print('c Running solvers mode error!')
		print('c Do not run solvers')
		sys.exit()
	
	print('c Cutoff time for each run on solving an instance is set to ' + str(cutoff_time_each_run) + ' seconds') # print the information about the cutoff time
	
	####
	# expand the job list
	total_job_num = sparkle_job_help.get_num_of_total_job_from_list(list_performance_computation_job)
	print('c The number of total running jobs: ' + str(total_job_num))
	total_job_list = sparkle_job_help.expand_total_job_from_list(list_performance_computation_job)
	####
	
	if len(total_job_list) == 0:
		return ''

	sbatch_script_path = generate_running_solvers_sbatch_shell_script(total_job_num, num_job_in_parallel, performance_data_csv_path, total_job_list)
	command_line = 'sbatch ' + sbatch_script_path
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

