#!/usr/bin/env python2.7
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
import sparkle_basic_help
import sparkle_record_help
import sparkle_file_help as sfh
import sparkle_global_help
import sparkle_feature_data_csv_help as sfdcsv
import sparkle_performance_data_csv_help as spdcsv
import sparkle_run_solvers_help as srs

def generate_analysing_portfolio_selector_shell_script(sbatch_shell_script_path, num_job_in_parallel, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, par_num, list_jobs, start_index, end_index):
	job_name = sfh.get_file_name(sbatch_shell_script_path)
	num_job_total = end_index - start_index
	if num_job_in_parallel > num_job_total:
		num_job_in_parallel = num_job_total
	command_prefix = r'srun -N1 -n1 --exclusive python2 Commands/sparkle_help/analyse_portfolio_selector_core.py '
	
	fout = open(sbatch_shell_script_path, 'w+')
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
	
	fout.write(r'#!/bin/bash' + '\n')
	fout.write(r'###' + '\n')
	fout.write(r'#SBATCH --job-name=' + job_name + '\n')
	fout.write(r'#SBATCH --output=' + r'TMP/' + job_name + r'.txt' + '\n')
	fout.write(r'#SBATCH --error=' + r'TMP/' + job_name + r'.err' + '\n')
	fout.write(r'###' + '\n')
	fout.write(r'###' + '\n')
	fout.write(r'#SBATCH --partition=grace30' + '\n')
	fout.write(r'#SBATCH --exclude=ethnode[11-32]' + '\n')
	fout.write('#SBATCH --mem-per-cpu=8192' + '\n')
	fout.write(r'#SBATCH --array=0-' + str(num_job_total-1) + r'%' + str(num_job_in_parallel) + '\n')
	fout.write(r'###' + '\n')
	
	fout.write('params=( \\' + '\n')
	
	for i in range(start_index, end_index):
		portfolio_selector_path = list_jobs[i][0]
		excluded_solver = list_jobs[i][1]
		fout.write('\'%s %s %s %d %d %s\'\n' % (portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, par_num, excluded_solver))
	
	fout.write(r')' + '\n')

	command_line = command_prefix + r' ' + r'${params[$SLURM_ARRAY_TASK_ID]}'
	
	fout.write(command_line + '\n')
	
	fout.close()
	return

def analysing_portfolio_selector_parallel(portfolio_selector_path_basis, num_job_in_parallel, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, par_num):
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	
	total_job_list = []
	
	portfolio_selector_path = portfolio_selector_path_basis
	excluded_solver = ''
	total_job_list.append([portfolio_selector_path, excluded_solver])
	
	for excluded_solver in performance_data_csv.list_columns():
		portfolio_selector_path = portfolio_selector_path_basis
		total_job_list.append([portfolio_selector_path, excluded_solver])
	
	i = 0
	j = len(total_job_list)
	sbatch_shell_script_path = 'TMP/' + r'analysing_portfolio_selector_sbatch_shell_script_' + str(i) + '_' + str(j) + '_' + sparkle_basic_help.get_time_pid_random_string() + r'.sh'
	generate_analysing_portfolio_selector_shell_script(sbatch_shell_script_path, num_job_in_parallel, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, par_num, total_job_list, i, j)

	os.system(r'chmod a+x ' + sbatch_shell_script_path)
	command_line = r'sbatch ' + sbatch_shell_script_path
	os.system(command_line)
	return

