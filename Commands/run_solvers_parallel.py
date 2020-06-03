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
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_run_solvers_parallel_help as srsp
from sparkle_help import sparkle_csv_merge_help as scmh
from sparkle_help import sparkle_experiments_related_help
from sparkle_help import sparkle_job_parallel_help

def run_solvers_parallel(my_flag_recompute, my_flag_also_construct_selector_and_report=False):
	num_job_in_parallel = sparkle_experiments_related_help.num_job_in_parallel
	
	if my_flag_recompute:
		performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)
		performance_data_csv.clean_csv()
		run_solvers_parallel_jobid = srsp.running_solvers_parallel(sparkle_global_help.performance_data_csv_path, num_job_in_parallel, 2)
	else:
		run_solvers_parallel_jobid = srsp.running_solvers_parallel(sparkle_global_help.performance_data_csv_path, num_job_in_parallel, 1)

	dependency_jobid_list = []
	# Only do selector construction and report generation if the flag is set;
	# Default behaviour is not to run them, like the sequential run_solvers command
	if my_flag_also_construct_selector_and_report:
		if run_solvers_parallel_jobid:
			dependency_jobid_list.append(run_solvers_parallel_jobid)
		job_script = 'Commands/construct_sparkle_portfolio_selector.py'
		run_job_parallel_jobid = sparkle_job_parallel_help.running_job_parallel(job_script, dependency_jobid_list)
		
		if run_job_parallel_jobid:
			dependency_jobid_list.append(run_job_parallel_jobid)
		job_script = 'Commands/generate_report.py'
		run_job_parallel_jobid = sparkle_job_parallel_help.running_job_parallel(job_script, dependency_jobid_list)
	else:
		# Update performance data csv after the last job is done
		if run_solvers_parallel_jobid:
			dependency_jobid_list.append(run_solvers_parallel_jobid)

		job_script = 'Commands/sparkle_help/sparkle_csv_merge_help.py'
		run_job_parallel_jobid = sparkle_job_parallel_help.running_job_parallel(job_script, dependency_jobid_list)

	last_job_id = run_job_parallel_jobid

	print("c Running solvers in parallel. Waiting for Slurm job with id:")
	print(last_job_id)

	return

if __name__ == r'__main__':

	
	print('c Start running solvers ...')

	my_flag_recompute = False
	my_flag_also_construct_selector_and_report = False

	len_argv = len(sys.argv)
	i = 1
	while i<len_argv:
		if sys.argv[i] == r'-recompute':
			my_flag_recompute = True
		elif sys.argv[i] == r'-also-construct-selector-and-report':
			my_flag_also_construct_selector_and_report = True
		i += 1

	run_solvers_parallel(my_flag_recompute, my_flag_also_construct_selector_and_report)

