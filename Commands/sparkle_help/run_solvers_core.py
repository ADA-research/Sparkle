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

try:
	from sparkle_help import sparkle_global_help as sgh
	from sparkle_help import sparkle_basic_help
	from sparkle_help import sparkle_file_help as sfh
	from sparkle_help import sparkle_performance_data_csv_help as spdcsv
	from sparkle_help import sparkle_experiments_related_help as ser
	from sparkle_help import sparkle_job_help
	from sparkle_help import sparkle_run_solvers_help as srs
	from sparkle_help import sparkle_customized_config_help as scch
except ImportError:
	import sparkle_global_help as sgh
	import sparkle_basic_help
	import sparkle_file_help as sfh
	import sparkle_performance_data_csv_help as spdcsv
	import sparkle_experiments_related_help as ser
	import sparkle_job_help
	import sparkle_run_solvers_help as srs
	import sparkle_customized_config_help as scch


if __name__ == r'__main__':
	instance_path = sys.argv[1]
	solver_path = sys.argv[2]
	performance_data_csv_path = sys.argv[3]
	
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	
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
		
	description_str = r'[Solver: ' + sfh.get_last_level_directory_name(solver_path) + r', Instance: ' + sfh.get_last_level_directory_name(instance_path) + r']'
	start_time_str = r'[Start Time: ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time)) + r']'
	end_time_str = r'[End Time: ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(end_time)) + r']'
	run_time_str = r'[Actual Run Time: ' + str(end_time-start_time) + r' second(s)]'
	recorded_run_time_str = r'[Recorded Run Time: ' + str(runtime) + r' second(s)]'
		
	log_str = description_str + r', ' + start_time_str + r', ' + end_time_str + r', ' + run_time_str + r', ' + recorded_run_time_str

	sfh.append_string_to_file(sgh.sparkle_system_log_path, log_str)
	os.system('rm -f ' + task_run_status_path)

	if scch.objective_type == 'solution_quality':
		obj_str = str(quality)
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


# if __name__ == r'__main__':
# 	cutoff_time_each_run = ser.cutoff_time_each_run
# 	par_num = ser.par_num
# 	penalty_time = ser.penalty_time
	
# 	instance_path = sys.argv[1]
# 	solver_path = sys.argv[2]
# 	performance_data_csv_path = sys.argv[3]
	
# 	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	
# 	key_str = sfh.get_last_level_directory_name(solver_path) + r'_' + sfh.get_last_level_directory_name(instance_path) + r'_' + sparkle_basic_help.get_time_pid_random_string()
# 	raw_result_path = r'TMP/' + key_str + r'.rawres'
# 	processed_result_path = r'Performance_Data/TMP/' + key_str + r'.result'
	
# 	task_run_status_path = r'TMP/SBATCH_Solver_Jobs/' + key_str + r'.statusinfo'
# 	status_info_str = 'Status: Running\n' + 'Solver: %s\n' %(sfh.get_last_level_directory_name(solver_path)) + 'Instance: %s\n' % (sfh.get_last_level_directory_name(instance_path))
	
# 	start_time = time.time()
# 	status_info_str += 'Start Time: ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time)) + '\n'
# 	status_info_str += 'Start Timestamp: ' + str(start_time) + '\n'
# 	cutoff_str = 'Cutoff Time: ' + str(ser.cutoff_time_each_run) + ' second(s)' + '\n'
# 	status_info_str += cutoff_str
# 	sfh.write_string_to_file(task_run_status_path, status_info_str)
# 	srs.run_solver_on_instance(solver_path, solver_path+r'/'+sparkle_global_help.sparkle_run_default_wrapper, instance_path, raw_result_path, ser.cutoff_time_each_run)
# 	end_time = time.time()
	
# 	verify_string = srs.judge_correctness_raw_result(instance_path, raw_result_path)
	
# 	runtime = 0
	
# 	if verify_string == r'SAT':
# 		runtime = srs.get_runtime(raw_result_path)
# 		if runtime > cutoff_time_each_run: runtime = penalty_time
# 		#performance_data_csv.set_value(instance_path, solver_path, runtime)
# 		#if sparkle_global_help.instance_reference_mapping[instance_path] != r'SAT':
# 		#	sparkle_global_help.instance_reference_mapping[instance_path] = r'SAT'
# 		#	sfh.write_instance_reference_mapping()
# 		#print r'c Running Result: ' + verify_string + r' , Runtime: ' + str(runtime)
# 	elif verify_string == r'UNSAT':
# 		runtime = srs.get_runtime(raw_result_path)
# 		if runtime > cutoff_time_each_run: runtime = penalty_time
# 		#performance_data_csv.set_value(instance_path, solver_path, runtime)
# 		#if sparkle_global_help.instance_reference_mapping[instance_path] != r'UNSAT':
# 		#	sparkle_global_help.instance_reference_mapping[instance_path] = r'UNSAT'
# 		#	sfh.write_instance_reference_mapping()
# 		#print r'c Running Result: ' + verify_string + r' , Runtime: ' + str(runtime)
# 	elif verify_string == r'UNKNOWN':
# 		runtime = penalty_time
# 		#performance_data_csv.set_value(instance_path, solver_path, runtime)
# 		#print r'c Running Result: ' + verify_string + r' , Runtime (Penalized): ' + str(runtime)
# 	elif verify_string == r'WRONG':
# 		runtime = penalty_time
# 		#wrong_solver_list.append(solver_path)
# 		#print r'c Solver ' + sfh.get_last_level_directory_name(solver_path) + r' reports wrong answer on instance ' + sfh.get_last_level_directory_name(instance_path) + r'!'
# 		#print r'c Solver ' + sfh.get_last_level_directory_name(solver_path) + r' will be removed!'
	
# 		#performance_data_csv.delete_column(solver_path)
# 		#sparkle_global_help.solver_list.remove(solver_path)
# 		#output = sparkle_global_help.solver_nickname_mapping.pop(solver_path)
# 		#sfh.write_solver_list()
# 		#sfh.write_solver_nickname_mapping()
		
# 		#print r'c Solver ' + sfh.get_last_level_directory_name(solver_path) + r' is a wrong solver'
# 		#print r'c Executing Progress: ' + str(current_job_num) + ' out of ' + str(total_job_num)
# 		#current_job_num += 1
# 		#print r'c Solver ' + sfh.get_last_level_directory_name(solver_path) + ' running on instance ' + sfh.get_last_level_directory_name(instance_path) + ' ignored!'
# 		#print r'c'
		
# 		#continue
# 	else:
# 		#the same as unknown
# 		verify_string = r'UNKNOWN' #treated as unknown
# 		runtime = penalty_time
# 		#performance_data_csv.set_value(instance_path, solver_path, runtime)
# 		#print r'c Running Result: ' + verify_string + r' , Runtime (Penalized): ' + str(runtime)
	
# 	description_str = r'[Solver: ' + sfh.get_last_level_directory_name(solver_path) + r', Instance: ' + sfh.get_last_level_directory_name(instance_path) + r']'
# 	start_time_str = r'[Start Time: ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time)) + r']'
# 	end_time_str = r'[End Time: ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(end_time)) + r']'
# 	run_time_str = r'[Actual Run Time: ' + str(end_time-start_time) + r' second(s)]'
# 	verify_string_str = r'[Verify String: ' + verify_string + r']'
# 	recorded_run_time_str = r'[Recorded Run Time: ' + str(runtime) + r' second(s)]'
	
# 	log_str = description_str + r', ' + start_time_str + r', ' + end_time_str + r', ' + run_time_str + r', ' + verify_string_str + r', ' + recorded_run_time_str
	
# 	time.sleep(random.randint(1, 5))
	
# 	sfh.append_string_to_file(sparkle_global_help.sparkle_system_log_path, log_str)
# 	os.system('rm -f ' + task_run_status_path)
	
# 	fout = open(processed_result_path, 'w+')
# 	fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
# 	fout.write(instance_path + '\n')
# 	fout.write(solver_path + '\n')
# 	fout.write(verify_string + '\n')
# 	fout.write(str(runtime) + '\n')
# 	fout.close()
	
# 	command_line = r'rm -f ' + raw_result_path
# 	os.system(command_line)

