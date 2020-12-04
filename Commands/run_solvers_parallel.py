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
import argparse
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
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings
from sparkle_help.sparkle_settings import PerformanceMeasure
from sparkle_help.sparkle_settings import SettingState
from sparkle_help import argparse_custom as ac


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
	# Initialise settings
	global settings
	sgh.settings = sparkle_settings.Settings()

	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--recompute', action='store_true', help='recompute the performance of all solvers on all instances')
	parser.add_argument('--performance-measure', choices=PerformanceMeasure.__members__, default=sgh.settings.DEFAULT_general_performance_measure, action=ac.SetByUser, help='the performance measure, e.g. runtime')
	parser.add_argument('--also-construct-selector-and-report', action='store_true', help='after running the solvers also construct the selector and generate the report')

	# Process command line arguments
	args = parser.parse_args()
	my_flag_recompute = args.recompute
	if ac.set_by_user(args, 'performance_measure'): sgh.settings.set_general_performance_measure(args.performance_measure, SettingState.CMD_LINE)
	my_flag_also_construct_selector_and_report = args.also_construct_selector_and_report

	print('c Start running solvers ...')

	run_solvers_parallel(my_flag_recompute, my_flag_also_construct_selector_and_report)

