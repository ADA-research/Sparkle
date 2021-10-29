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
import fcntl
import argparse
import shutil
from pathlib import Path
from pathlib import PurePath

try:
	from sparkle_help import sparkle_global_help as sgh
	from sparkle_help import sparkle_basic_help as sbh
	from sparkle_help import sparkle_file_help as sfh
	from sparkle_help import sparkle_run_solvers_help as srs
	from sparkle_help.sparkle_settings import PerformanceMeasure
	from sparkle_help import sparkle_settings
except ImportError:
	import sparkle_global_help as sgh
	import sparkle_basic_help as sbh
	import sparkle_file_help as sfh
	import sparkle_run_solvers_help as srs
	from sparkle_settings import PerformanceMeasure
	import sparkle_settings


if __name__ == r'__main__':
	# Initialise settings
	global settings
	settings_dir = Path('Settings')
	file_path_latest = PurePath(settings_dir / 'latest.ini')
	sgh.settings = sparkle_settings.Settings(file_path_latest)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--instance', required=False, type=str, nargs='+', help='path to instance to run on')
	parser.add_argument('--solver', required=True, type=str, help='path to solver')
	parser.add_argument('--performance-measure', choices=PerformanceMeasure.__members__, default=sgh.settings.DEFAULT_general_performance_measure, help='the performance measure, e.g. runtime')
	parser.add_argument('--run-status-path',
						choices=['Tmp/SBATCH_Solver_Jobs/',
						'Tmp/SBATCH_Parallel_Portfolio_Jobs/'],
						default='Tmp/SBATCH_Solver_Jobs/',
						help='set the runstatus path of the process')
	parser.add_argument('--seed', type=str, required=False,
						help='sets the seed used for the solver')
	args = parser.parse_args()

	# Process command line arguments
	instance_path = " ".join(args.instance) # Turn multiple instance files into a space separated string
	solver_path = args.solver
	if args.seed is not None:
		seed = args.seed
		# Creating a new directory for the solver to facilitate running several
		# solver_instances in parallel.
		new_solver_directory_path = (
			f'Tmp/{sfh.get_last_level_directory_name(solver_path)}_seed_{str(seed)}_'
			f'{sfh.get_last_level_directory_name(instance_path)}')
		command_line = 'cp -a -r ' + str(solver_path) + ' ' + str(new_solver_directory_path)
		os.system(command_line)
		solver_path = new_solver_directory_path
	else:
		seed = ''
	performance_measure = PerformanceMeasure.from_str(args.performance_measure)
	run_status_path = args.run_status_path
	key_str = sfh.get_last_level_directory_name(solver_path) + r'_' + sfh.get_last_level_directory_name(instance_path) + r'_' + sbh.get_time_pid_random_string()
	raw_result_path = r'Tmp/' + key_str + r'.rawres'
	processed_result_path = r'Performance_Data/Tmp/' + key_str + r'.result'
	if run_status_path == 'Tmp/SBATCH_Parallel_Portfolio_Jobs/':
		processed_result_path = 'Performance_Data/Tmp_PaP/' + key_str + '.result'
	task_run_status_path = run_status_path + key_str + '.statusinfo'
	status_info_str = 'Status: Running\n' + 'Solver: %s\n' %(sfh.get_last_level_directory_name(solver_path)) + 'Instance: %s\n' % (sfh.get_last_level_directory_name(instance_path))
	
	start_time = time.time()
	status_info_str += 'Start Time: ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time)) + '\n'
	status_info_str += 'Start Timestamp: ' + str(start_time) + '\n'
	cutoff_str = 'Cutoff Time: ' + str(sgh.settings.get_general_target_cutoff_time()) + ' second(s)' + '\n'
	status_info_str += cutoff_str
	sfh.write_string_to_file(task_run_status_path, status_info_str)

	cpu_time, wc_time, cpu_time_penalised, quality, status, raw_result_path = (
		srs.run_solver_on_instance_and_process_results(solver_path, instance_path, seed))

	description_str = r'[Solver: ' + sfh.get_last_level_directory_name(solver_path) + r', Instance: ' + sfh.get_last_level_directory_name(instance_path) + r']'
	start_time_str = '[Start Time: ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time)) + ']'
	end_time_str = r'[End Time (after completing run time + processing time): ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + r']'
	run_time_str = r'[Actual Run Time (wall clock): ' + str(wc_time) + r' second(s)]'
	recorded_run_time_str = r'[Recorded Run Time (CPU PAR' + str(sgh.settings.get_general_penalty_multiplier()) + '): ' + str(cpu_time_penalised) + r' second(s)]'
	status_str = '[Run Status: ' + status + ']'
		
	log_str = description_str + r', ' + start_time_str + r', ' + end_time_str + r', ' + run_time_str + r', ' + recorded_run_time_str + ', ' + status_str

	sfh.append_string_to_file(sgh.sparkle_system_log_path, log_str)
	os.system('rm -f ' + task_run_status_path)

	if run_status_path != 'Tmp/SBATCH_Parallel_Portfolio_Jobs/':
		if solver_path.startswith('Tmp/'):
			shutil.rmtree(solver_path)
	
	if performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE:
		obj_str = str(quality[0]) # TODO: Handle the multi-objective case
	else:
		obj_str = str(cpu_time_penalised)
	
	fout = open(processed_result_path, 'w+')
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
	fout.write(instance_path + '\n')
	fout.write(solver_path + '\n')
	fout.write(obj_str + '\n')
	fout.close()

	# TODO: Make removal conditional on a success status (SUCCESS, SAT or UNSAT)
	#command_line = r'rm -f ' + raw_result_path
	#os.system(command_line)

