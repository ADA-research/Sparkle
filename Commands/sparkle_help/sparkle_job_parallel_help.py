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


def get_dependency_list_str(dependency_jobid_list):
	dependency_list_str = ''
	for dependency_jobid in dependency_jobid_list:
		dependency_list_str += r'afterany:' + dependency_jobid + r','
	dependency_list_str = dependency_list_str[:-1]
	return dependency_list_str


def generate_job_sbatch_shell_script(sbatch_shell_script_path, job_script, dependency_jobid_list):
	sbatch_script_name = sfh.get_file_name(sbatch_shell_script_path)
	sbatch_script_path = r'Tmp/' + sbatch_script_name
	job_name = '--job-name=' + sbatch_script_name
	output = '--output=' + sbatch_script_path + '.txt'
	error = '--error=' + sbatch_script_path + '.err'
	dependency = '--dependency='
	dependency_list_str = get_dependency_list_str(dependency_jobid_list)
	if dependency_list_str.strip() != '':
		dependency += dependency_list_str
	sbatch_options_list = [job_name, output, error, dependency]
	sbatch_options_list.extend(ssh.get_slurm_sbatch_default_options_list())
	sbatch_options_list.extend(ssh.get_slurm_sbatch_user_options_list())
	job_params_list = ['']

	srun_options_str = '-N1 -n1'
	srun_options_str = srun_options_str + ' ' + ssh.get_slurm_srun_user_options_str()
	target_call_str = job_script

	ssh.generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list, job_params_list, srun_options_str, target_call_str)
	
	return


def running_job_parallel(job_script, dependency_jobid_list):
	sbatch_shell_script_path = r'Tmp/' + r'running_job_parallel_' + sparkle_basic_help.get_time_pid_random_string() + r'.sh'
	generate_job_sbatch_shell_script(sbatch_shell_script_path, job_script, dependency_jobid_list)
	os.system(r'chmod a+x ' + sbatch_shell_script_path)
	command_line = r'sbatch ' + sbatch_shell_script_path
	output_list = os.popen(command_line).readlines()
	if len(output_list) > 0 and len(output_list[0].strip().split())>0:
		run_job_parallel_jobid = output_list[0].strip().split()[-1]
	else:
		run_job_parallel_jobid = ''
	return run_job_parallel_jobid

