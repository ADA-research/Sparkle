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
	job_name = sfh.get_file_name(sbatch_shell_script_path)
	command_prefix = r'srun -N1 -n1 --exclusive python3 '
	
	fout = open(sbatch_shell_script_path, 'w+')
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
	
	fout.write(r'#!/bin/bash' + '\n')
	fout.write(r'###' + '\n')
	fout.write(r'###' + '\n')
	fout.write(r'#SBATCH --job-name=' + job_name + '\n') 
	fout.write(r'#SBATCH --output=' + r'TMP/' + job_name + r'.txt' + '\n')
	fout.write(r'#SBATCH --error=' + r'TMP/' + job_name + r'.err' + '\n')
	fout.write(r'###' + '\n')
	fout.write(r'#SBATCH --mem-per-cpu=5120' + '\n')
	dependency_list_str = get_dependency_list_str(dependency_jobid_list)
	if dependency_list_str.strip() != '':
		fout.write(r'#SBATCH --dependency=' + dependency_list_str + '\n')
	fout.write(r'###' + '\n')
	
	command_line = command_prefix + r' ' + job_script
	fout.write(command_line + '\n')
	
	fout.close()
	
	return


def running_job_parallel(job_script, dependency_jobid_list):
	sbatch_shell_script_path = r'TMP/' + r'running_job_parallel_' + sparkle_basic_help.get_time_pid_random_string() + r'.sh'
	generate_job_sbatch_shell_script(sbatch_shell_script_path, job_script, dependency_jobid_list)
	os.system(r'chmod a+x ' + sbatch_shell_script_path)
	command_line = r'sbatch ' + sbatch_shell_script_path
	output_list = os.popen(command_line).readlines()
	if len(output_list) > 0 and len(output_list[0].strip().split())>0:
		run_job_parallel_jobid = output_list[0].strip().split()[-1]
	else:
		run_job_parallel_jobid = ''
	return run_job_parallel_jobid

	
