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
from sparkle_help import sparkle_add_train_instances_help as satih

if __name__ == r'__main__':
	solver = ''
	instance_set_train = ''
	instance_set_test = ''
	
	flag_solver = False
	flag_instance_set_train = False
	flag_instance_set_test = False
	
	len_argv = len(sys.argv)
	i = 1
	while i<len_argv:
		if sys.argv[i] == '-solver':
			i += 1
			solver = sys.argv[i]
			flag_solver = True
		elif sys.argv[i] == '-instances-train':
			i += 1
			instance_set_train = sys.argv[i]
			flag_instance_set_train = True
		elif sys.argv[i] == '-instances-test':
			i += 1
			instance_set_test = sys.argv[i]
			flag_instance_set_test = True
		else:
			print('c Argument Error: Unknown argument!')
			print('c Usage: %s -solver <solver> -instances-train <instances-train> -instances-test <instances-test>' % sys.argv[0])
			sys.exit(-1)
		i += 1
	
	if not (flag_solver and flag_instance_set_train and flag_instance_set_test):
		print('c Argument Error!')
		print('c Usage: %s -solver <solver> -instances-train <instances-train> -instances-test <instances-test>' % sys.argv[0])
		sys.exit(-1)
	
	solver_name = sfh.get_last_level_directory_name(solver)
	instance_set_train_name = sfh.get_last_level_directory_name(instance_set_train)
	instance_set_test_name = sfh.get_last_level_directory_name(instance_set_test)
	
	optimised_configuration_str, optimised_configuration_performance_par10, optimised_configuration_seed = scsh.get_optimised_configuration(solver_name, instance_set_train_name)
	#print(optimised_configuration_str, optimised_configuration_performance_par10, optimised_configuration_seed)
	
	scsh.generate_configure_solver_wrapper(solver_name, optimised_configuration_str)
	
	ori_smac_generate_sbatch_script_path = sparkle_global_help.smac_dir + '/example_scenarios/' + 'generate_sbatch_script.py'
	ori_smac_runsolver_path = sparkle_global_help.smac_dir + '/example_scenarios/' + 'runsolver'
	smac_solver_dir = sparkle_global_help.smac_dir + '/example_scenarios/' + solver_name + '/'

	# Copy sbatch generation script and runsolver to the solver directory
	command_line = 'cp ' + ori_smac_generate_sbatch_script_path + ' ' + smac_solver_dir
	os.system(command_line)
	
	command_line = 'cp ' + ori_smac_runsolver_path + ' ' + smac_solver_dir
	os.system(command_line)
	
	smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run_str, num_of_smac_run_in_parallel_str = scsh.get_smac_settings()

	# Copy test instances to smac directory (train should already be there from configuration)
	instances_directory_test = r'Instances/' + instance_set_test_name
	list_cnf_path = satih.get_list_cnf_path(instances_directory_test)
	cnf_dir_prefix = instances_directory_test
	smac_cnf_dir_prefix = sparkle_global_help.smac_dir + r'/' + 'example_scenarios/' + r'instances/' + sfh.get_last_level_directory_name(instances_directory_test)
	satih.copy_instances_to_smac(list_cnf_path, cnf_dir_prefix, smac_cnf_dir_prefix, r'test')


	ori_path = os.getcwd()
	# Generate and run batch script for the configured solver with the test set
	command_line = 'cd ' + smac_solver_dir + ' ; ' + './generate_sbatch_script.py ' + sparkle_global_help.sparkle_run_configured_wrapper + ' ' + '../instances/' + instance_set_test_name + '/ ' + 'results/' + sparkle_global_help.sparkle_run_configured_wrapper + '_' + instance_set_test_name + '/ ' + str(smac_each_run_cutoff_time) + ' ' +  str(num_of_smac_run_in_parallel_str) + ' test ; ' + 'cd ' + ori_path
	os.system(command_line)
	
	command_line = 'cd ' + smac_solver_dir + ' ; ' + 'sbatch ' + sparkle_global_help.sparkle_run_configured_wrapper + '_' + instance_set_test_name + '_test_exp_sbatch.sh' + ' ; ' + 'cd ' + ori_path
	os.system(command_line)

	# Generate and run batch script for the default solver with the test set
	command_line = 'cd ' + smac_solver_dir + ' ; ' + './generate_sbatch_script.py ' + sparkle_global_help.sparkle_run_default_wrapper + ' ' + '../instances/' + instance_set_test_name + '/ ' + 'results/' + sparkle_global_help.sparkle_run_default_wrapper + '_' + instance_set_test_name + '/ ' + str(smac_each_run_cutoff_time) + ' ' +  str(num_of_smac_run_in_parallel_str) + ' test ; ' + 'cd ' + ori_path
	os.system(command_line)
	
	command_line = 'cd ' + smac_solver_dir + ' ; ' + 'sbatch ' + sparkle_global_help.sparkle_run_default_wrapper + '_' + instance_set_test_name + '_test_exp_sbatch.sh' + ' ; ' + 'cd ' + ori_path
	os.system(command_line)
	
	# Generate and run batch script for the configured solver with the train set
	command_line = 'cd ' + smac_solver_dir + ' ; ' + './generate_sbatch_script.py ' + sparkle_global_help.sparkle_run_configured_wrapper + ' ' + '../instances/' + instance_set_train_name + '/ ' + 'results_train/' + sparkle_global_help.sparkle_run_configured_wrapper + '_' + instance_set_train_name + '/ ' + str(smac_each_run_cutoff_time) + ' ' + str(num_of_smac_run_in_parallel_str) + ' train ; ' + 'cd ' + ori_path
	os.system(command_line)
	
	command_line = 'cd ' + smac_solver_dir + ' ; ' + 'sbatch ' + sparkle_global_help.sparkle_run_configured_wrapper + '_' + instance_set_train_name + '_train_exp_sbatch.sh' + ' ; ' + 'cd ' + ori_path
	os.system(command_line)
	
	# Generate and run batch script for the default solver with the train set
	command_line = 'cd ' + smac_solver_dir + ' ; ' + './generate_sbatch_script.py ' + sparkle_global_help.sparkle_run_default_wrapper + ' ' + '../instances/' + instance_set_train_name + '/ ' + 'results_train/' + sparkle_global_help.sparkle_run_default_wrapper + '_' + instance_set_train_name + '/ ' + str(smac_each_run_cutoff_time) + ' ' + str(num_of_smac_run_in_parallel_str) + ' train ; ' + 'cd ' + ori_path
	os.system(command_line)
	
	command_line = 'cd ' + smac_solver_dir + ' ; ' + 'sbatch ' + sparkle_global_help.sparkle_run_default_wrapper + '_' + instance_set_train_name + '_train_exp_sbatch.sh' + ' ; ' + 'cd ' + ori_path
	os.system(command_line)

	# Write most recent run to file
	last_test_file_path = sparkle_global_help.smac_dir + '/example_scenarios/' + sparkle_global_help.sparkle_last_test_file_name

	fout = open(last_test_file_path, 'w+')
	fout.write('solver ' + str(solver) + '\n')
	fout.write('train ' + str(instance_set_train) + '\n')
	fout.write('test ' + str(instance_set_test) + '\n')
	fout.close()

