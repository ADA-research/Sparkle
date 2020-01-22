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
from sparkle_help import sparkle_slurm_help

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

	# Make sure configuration results exist before trying to work with them
	if not scsh.check_configuration_exists(solver_name, instance_set_train_name):
		print('c Error: No configuration results found for the given solver and training instance set.')
		sys.exit(-1)

	# Copy runsolver to the solver directory
	ori_smac_runsolver_path = sparkle_global_help.smac_dir + '/example_scenarios/' + 'runsolver'
	smac_solver_dir = sparkle_global_help.smac_dir + '/example_scenarios/' + solver_name + '/'
	command_line = 'cp ' + ori_smac_runsolver_path + ' ' + smac_solver_dir
	os.system(command_line)

	# Copy test instances to smac directory (train should already be there from configuration)
	instances_directory_test = r'Instances/' + instance_set_test_name
	list_path = satih.get_list_all_path(instances_directory_test)
	inst_dir_prefix = instances_directory_test
	smac_inst_dir_prefix = sparkle_global_help.smac_dir + r'/' + 'example_scenarios/' + r'instances/' + sfh.get_last_level_directory_name(instances_directory_test)
	satih.copy_instances_to_smac(list_path, inst_dir_prefix, smac_inst_dir_prefix, r'test')

	# Copy file listing test instances to smac solver directory
	scsh.handle_file_instance_test(solver_name, instance_set_test_name)

	# Set srun and smac-validate options
	n_cpus = 1
	n_cores = 16 # Number of cores available on a Grace CPU
	srun_prefix = 'srun -N1 -n1 --cpus-per-task ' + str(n_cpus)
	srun_options_str = sparkle_slurm_help.get_slurm_srun_options_str()
	smac_validate_prefix = './smac-validate --use-scenario-outdir true --num-run 1 --cli-cores ' + str(n_cores)

	ori_path = os.getcwd()
	command_constant_prefix = 'cd ' + sparkle_global_help.smac_dir + ' ; ' + srun_prefix + ' ' + srun_options_str + ' ' + smac_validate_prefix

	# Perform validation for the default parameters on the training set
	default = True
	scenario_file_name = scsh.create_file_scenario_validate(solver_name, instance_set_train_name, scsh.InstanceType.TRAIN, default)
	scenario_file_path = 'example_scenarios/' + solver_name + '/' + scenario_file_name
	configuration_str = 'DEFAULT'
	smac_output_file = 'results/' + solver_name + '_validation_' + scenario_file_name
	command_line = command_constant_prefix + ' --scenario-file ' + scenario_file_path + ' --configuration ' + configuration_str + ' > ' + smac_output_file + ' ; ' + 'cd ' + ori_path
	os.system(command_line)

	# Perform validation for the default parameters on the testing set
	default = True
	scenario_file_name = scsh.create_file_scenario_validate(solver_name, instance_set_test_name, scsh.InstanceType.TEST, default)
	scenario_file_path = 'example_scenarios/' + solver_name + '/' + scenario_file_name
	configuration_str = 'DEFAULT'
	smac_output_file = 'results/' + solver_name + '_validation_' + scenario_file_name
	command_line = command_constant_prefix + ' --scenario-file ' + scenario_file_path + ' --configuration ' + configuration_str + ' > ' + smac_output_file + ' ; ' + 'cd ' + ori_path
	os.system(command_line)

	# Perform validation for the configured parameters on the testing set
	default = False
	scenario_file_name = scsh.create_file_scenario_validate(solver_name, instance_set_test_name, scsh.InstanceType.TEST, default)
	scenario_file_path = 'example_scenarios/' + solver_name + '/' + scenario_file_name
	optimised_configuration_str, optimised_configuration_performance_par10, optimised_configuration_seed = scsh.get_optimised_configuration(solver_name, instance_set_train_name)
	configuration_str = '\"' + str(optimised_configuration_str) + '\"'
	smac_output_file = 'results/' + solver_name + '_validation_' + scenario_file_name
	command_line = command_constant_prefix + ' --scenario-file ' + scenario_file_path + ' --configuration ' + configuration_str + ' > ' + smac_output_file + ' ; ' + 'cd ' + ori_path
	os.system(command_line)

	# Write most recent run to file
	last_test_file_path = sparkle_global_help.smac_dir + '/example_scenarios/' + solver_name + '/' + sparkle_global_help.sparkle_last_test_file_name

	fout = open(last_test_file_path, 'w+')
	fout.write('solver ' + str(solver) + '\n')
	fout.write('train ' + str(instance_set_train) + '\n')
	fout.write('test ' + str(instance_set_test) + '\n')
	fout.close()

