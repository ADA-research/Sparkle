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
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_system_status_help
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_run_status_help
from sparkle_help import sparkle_generate_report_help
from sparkle_help import sparkle_generate_report_for_test_help
from sparkle_help import sparkle_configure_solver_help as scsh
from sparkle_help import sparkle_file_help as sfh

if __name__ == r'__main__':
	solver = ''
	instance_set = ''
	
	flag_solver = False
	flag_instance_set = False
	
	len_argv = len(sys.argv)
	i = 1
	while i<len_argv:
		if sys.argv[i] == '-solver':
			i += 1
			solver = sys.argv[i]
			flag_solver = True
		elif sys.argv[i] == '-instance_set':
			i += 1
			instance_set = sys.argv[i]
			flag_instance_set = True
		else:
			print('c Argument Error!')
			print('c Usage: %s -solver <solver> -instance_set <instance_set>' % sys.argv[0])
			sys.exit(-1)
		i += 1
	
	if not (flag_solver and flag_instance_set):
		print('c Argument Error!')
		print('c Usage: %s -solver <solver> -instance_set <instance_set>' % sys.argv[0])
		sys.exit(-1)
	
	solver_name = sfh.get_last_level_directory_name(solver)
	instance_set_name = sfh.get_last_level_directory_name(instance_set)
	
	optimised_configuration_str, optimised_configuration_performance_par10, optimised_configuration_seed = scsh.get_optimised_configuration(solver_name, instance_set_name)
	#print(optimised_configuration_str, optimised_configuration_performance_par10, optimised_configuration_seed)
	
	scsh.generate_configure_solver_wrapper(solver_name, instance_set_name, optimised_configuration_str)
	
	ori_smac_generate_sbatch_script_path = sparkle_global_help.smac_dir + '/example_scenarios/' + 'generate_sbatch_script.py'
	ori_smac_runsolver_path = sparkle_global_help.smac_dir + '/example_scenarios/' + 'runsolver'
	smac_solver_dir = sparkle_global_help.smac_dir + '/example_scenarios/' + solver_name + '/'
	
	command_line = 'cp ' + ori_smac_generate_sbatch_script_path + ' ' + smac_solver_dir
	os.system(command_line)
	
	command_line = 'cp ' + ori_smac_runsolver_path + ' ' + smac_solver_dir
	os.system(command_line)
	
	smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run_str, num_of_smac_run_in_parallel_str = scsh.get_smac_settings()
	
	ori_path = os.getcwd()
	command_line = 'cd ' + smac_solver_dir + ' ; ' + './generate_sbatch_script.py ' + sparkle_global_help.sparkle_run_configured_wrapper + ' ' + '../instances_test/' + instance_set_name + '/ ' + 'results/' + sparkle_global_help.sparkle_run_configured_wrapper + '_' + instance_set_name + '/ ' + str(smac_each_run_cutoff_time) + ' ' +  str(num_of_smac_run_in_parallel_str) + ' test ; ' + 'cd ' + ori_path
	os.system(command_line)
	
	command_line = 'cd ' + smac_solver_dir + ' ; ' + 'sbatch ' + sparkle_global_help.sparkle_run_configured_wrapper + '_' + instance_set_name + '_test_exp_sbatch.sh' + ' ; ' + 'cd ' + ori_path
	os.system(command_line)
	
	command_line = 'cd ' + smac_solver_dir + ' ; ' + './generate_sbatch_script.py ' + sparkle_global_help.sparkle_run_default_wrapper + ' ' + '../instances_test/' + instance_set_name + '/ ' + 'results/' + sparkle_global_help.sparkle_run_default_wrapper + '_' + instance_set_name + '/ ' + str(smac_each_run_cutoff_time) + ' ' +  str(num_of_smac_run_in_parallel_str) + ' test ; ' + 'cd ' + ori_path
	os.system(command_line)
	
	command_line = 'cd ' + smac_solver_dir + ' ; ' + 'sbatch ' + sparkle_global_help.sparkle_run_default_wrapper + '_' + instance_set_name + '_test_exp_sbatch.sh' + ' ; ' + 'cd ' + ori_path
	os.system(command_line)
	
	
	command_line = 'cd ' + smac_solver_dir + ' ; ' + './generate_sbatch_script.py ' + sparkle_global_help.sparkle_run_configured_wrapper + ' ' + '../instances/' + instance_set_name + '/ ' + 'results_train/' + sparkle_global_help.sparkle_run_configured_wrapper + '_' + instance_set_name + '/ ' + str(smac_each_run_cutoff_time) + ' ' + str(num_of_smac_run_in_parallel_str) + ' train ; ' + 'cd ' + ori_path
	os.system(command_line)
	
	command_line = 'cd ' + smac_solver_dir + ' ; ' + 'sbatch ' + sparkle_global_help.sparkle_run_configured_wrapper + '_' + instance_set_name + '_train_exp_sbatch.sh' + ' ; ' + 'cd ' + ori_path
	os.system(command_line)
	
	
	command_line = 'cd ' + smac_solver_dir + ' ; ' + './generate_sbatch_script.py ' + sparkle_global_help.sparkle_run_default_wrapper + ' ' + '../instances/' + instance_set_name + '/ ' + 'results_train/' + sparkle_global_help.sparkle_run_default_wrapper + '_' + instance_set_name + '/ ' + str(smac_each_run_cutoff_time) + ' ' + str(num_of_smac_run_in_parallel_str) + ' train ; ' + 'cd ' + ori_path
	os.system(command_line)
	
	command_line = 'cd ' + smac_solver_dir + ' ; ' + 'sbatch ' + sparkle_global_help.sparkle_run_default_wrapper + '_' + instance_set_name + '_train_exp_sbatch.sh' + ' ; ' + 'cd ' + ori_path
	os.system(command_line)
	

