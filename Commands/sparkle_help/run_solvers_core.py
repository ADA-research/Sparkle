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
import argparse

try:
	from sparkle_help import sparkle_global_help as sgh
	from sparkle_help import sparkle_basic_help
	from sparkle_help import sparkle_file_help as sfh
	from sparkle_help import sparkle_experiments_related_help as ser
	from sparkle_help import sparkle_run_solvers_help as srs
except ImportError:
	import sparkle_global_help as sgh
	import sparkle_basic_help
	import sparkle_file_help as sfh
	import sparkle_experiments_related_help as ser
	import sparkle_run_solvers_help as srs


if __name__ == r'__main__':
	# Define command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--instance', required=False, type=str, help='path to instance to run on')
	parser.add_argument('--solver', required=True, type=str, help='path to solver')
	parser.add_argument('--objective', choices=sgh.PerformanceMeasures.__members__, default=sgh.PerformanceMeasures.RUNTIME, help='the objective to measure, e.g. runtime')
	parser.add_argument('--verifier', choices=sgh.SolutionVerifiers.__members__, default=sgh.SolutionVerifiers.NONE, help='use a domain specific verifier to check solutions found by solvers are correct')
	args = parser.parse_args()

	# Process command line arguments
	instance_path = args.instance
	solver_path = args.solver
	objective = sgh.parse_arg_performance(args.objective)
	verifier = sgh.parse_arg_verifier(args.verifier)

	key_str = sfh.get_last_level_directory_name(solver_path) + r'_' + sfh.get_last_level_directory_name(instance_path) + r'_' + sparkle_basic_help.get_time_pid_random_string()
	raw_result_path = r'Tmp/' + key_str + r'.rawres'
	processed_result_path = r'Performance_Data/Tmp/' + key_str + r'.result'
	
	task_run_status_path = r'Tmp/SBATCH_Solver_Jobs/' + key_str + r'.statusinfo'
	status_info_str = 'Status: Running\n' + 'Solver: %s\n' %(sfh.get_last_level_directory_name(solver_path)) + 'Instance: %s\n' % (sfh.get_last_level_directory_name(instance_path))
	
	start_time = time.time()
	status_info_str += 'Start Time: ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time)) + '\n'
	status_info_str += 'Start Timestamp: ' + str(start_time) + '\n'
	cutoff_str = 'Cutoff Time: ' + str(ser.cutoff_time_each_run) + ' second(s)' + '\n'
	status_info_str += cutoff_str
	sfh.write_string_to_file(task_run_status_path, status_info_str)
	solver_wrapper_path = solver_path + '/' + sgh.sparkle_run_default_wrapper
	runsolver_values_path = raw_result_path.replace('.rawres', '.val')
	seed = sgh.get_seed()
	srs.run_solver_on_instance(solver_path, solver_wrapper_path, instance_path, raw_result_path, runsolver_values_path, seed)
	end_time = time.time()

	runtime, quality, status = srs.process_results(raw_result_path, solver_wrapper_path, runsolver_values_path)
	runtime, status = srs.handle_timeouts(runtime, status)
	status = srs.verify(instance_path, raw_result_path, solver_path, verifier, status)
		
	description_str = r'[Solver: ' + sfh.get_last_level_directory_name(solver_path) + r', Instance: ' + sfh.get_last_level_directory_name(instance_path) + r']'
	start_time_str = r'[Start Time: ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time)) + r']'
	end_time_str = r'[End Time: ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(end_time)) + r']'
	run_time_str = r'[Actual Run Time: ' + str(end_time-start_time) + r' second(s)]'
	recorded_run_time_str = r'[Recorded Run Time: ' + str(runtime) + r' second(s)]'
	status_str = '[Run Status: ' + status + ']'
		
	log_str = description_str + r', ' + start_time_str + r', ' + end_time_str + r', ' + run_time_str + r', ' + recorded_run_time_str + ', ' + status_str

	sfh.append_string_to_file(sgh.sparkle_system_log_path, log_str)
	os.system('rm -f ' + task_run_status_path)

	if objective == sgh.PerformanceMeasures.QUALITY_ABSOLUTE:
		obj_str = str(quality[0]) # TODO: Handle the multi-objective case
	else:
		obj_str = str(runtime)
	
	fout = open(processed_result_path, 'w+')
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
	fout.write(instance_path + '\n')
	fout.write(solver_path + '\n')
	fout.write(obj_str + '\n')
	fout.close()
	
	command_line = r'rm -f ' + raw_result_path
	os.system(command_line)

