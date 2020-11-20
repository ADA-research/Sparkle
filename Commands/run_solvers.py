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
import run_solvers_parallel as rsp
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help as srh
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_run_solvers_parallel_help as srsp
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_experiments_related_help
from sparkle_help import sparkle_job_parallel_help
from sparkle_help import sparkle_logging as sl


if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--recompute', action='store_true', help='recompute the performance of all solvers on all instances')
	parser.add_argument('--parallel', action='store_true', help='run the solver on multiple instances in parallel')
	parser.add_argument('--objective', choices=sgh.PerformanceMeasures.__members__, default=sgh.PerformanceMeasures.RUNTIME, help='the objective to measure, e.g. runtime')

	# Process command line arguments
	args = parser.parse_args()
	my_flag_recompute = args.recompute
	my_flag_parallel = args.parallel
	objective = sgh.parse_arg_performance(args.objective)

	print('c Start running solvers ...')

	if not srh.detect_current_sparkle_platform_exists():
		print('c No Sparkle platform found; please first run the initialise command')
		exit()

	if not my_flag_parallel:
		if my_flag_recompute:
			performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sgh.performance_data_csv_path)
			performance_data_csv.clean_csv()
			srs.running_solvers(sgh.performance_data_csv_path, 2, objective)
		else:
			srs.running_solvers(sgh.performance_data_csv_path, 1, objective)
	
		print('c Running solvers done!')
	else:
		# Call the parallel version of this command
		rsp.run_solvers_parallel(my_flag_recompute, objective)

