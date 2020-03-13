#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import fcntl

from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_configure_solver_help as scsh

def get_slurm_options_list(path_modifier=None):
	if path_modifier is None:
		path_modifier = ''

	slurm_options_list = []
	sparkle_slurm_settings_path = str(path_modifier) + sgh.sparkle_slurm_settings_path
	
	settings_file = open(sparkle_slurm_settings_path, 'r')
	while True:
		current_line = settings_file.readline()
		if not current_line:
			break
		if current_line[0] == '-':
			current_line = current_line.strip()
			slurm_options_list.append(current_line)
	settings_file.close()

	return slurm_options_list

# Get a list of options to be used with sbatch calls
def get_slurm_sbatch_user_options_list(path_modifier=None):
	return get_slurm_options_list(path_modifier)

def get_slurm_sbatch_default_options_list():
	return ['--partition=graceADA']

def get_slurm_srun_user_options_list(path_modifier=None):
	return get_slurm_options_list(path_modifier)

def get_slurm_srun_user_options_str(path_modifier=None):
	srun_options_list = get_slurm_srun_user_options_list(path_modifier)
	srun_options_str = ''

	for i in srun_options_list:
		srun_options_str += i + ' '

	return srun_options_str

def generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list, job_params_list, srun_options_str, target_call_str, job_output_list=None):
	fout = open(sbatch_script_path, 'w+') # open the file of sbatch script
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX) # using the UNIX file lock to prevent other attempts to visit this sbatch script
	
	# specify the options of sbatch in the top of this sbatch script
	fout.write(r'#!/bin/bash' + '\n') # use bash to execute this script
	fout.write(r'###' + '\n')
	fout.write(r'###' + '\n')

	for i in sbatch_options_list:
		fout.write(r'#SBATCH ' + str(i) + '\n')

	fout.write(r'###' + '\n')

	# specify the array of parameters for each command
	fout.write('params=( \\' + '\n')

	for i in range(0, len(job_params_list)):
		fout.write('\'%s\' \\' % (job_params_list[i]) + '\n')

	fout.write(r')' + '\n')

	# if there is a list of output file paths, write the output parameter
	if job_output_list is not None:
		fout.write('output=( \\' + '\n')

		for i in range(0, len(job_output_list)):
			fout.write('\'%s\' \\' % (job_output_list[i]) + '\n')

		fout.write(r')' + '\n')

	command_prefix = r'srun ' + srun_options_str + ' ' + target_call_str # specify the prefix of the executing command
	# specify the complete command
	command_line = command_prefix + r' ' + r'${params[$SLURM_ARRAY_TASK_ID]}'

	# add output file paths to the command if given
	if job_output_list is not None:
		command_line = command_line + r' > ${output[$SLURM_ARRAY_TASK_ID]}'

	fout.write(command_line + '\n') # write the complete command in this sbatch script
	fout.close() # close the file of the sbatch script

	return

def generate_sbatch_script_for_validation(solver_name, instance_set_train_name, instance_set_test_name):
	## Set script name and path
	sbatch_script_name = solver_name + '_' + instance_set_train_name + '_' + instance_set_test_name + '_validation_sbatch.sh'
	sbatch_script_path = sgh.smac_dir + sbatch_script_name

	## Set sbatch options
	max_jobs = 50
	num_jobs = 3
	if num_jobs < max_jobs:
		max_jobs = num_jobs
	job_name = '--job-name=' + sbatch_script_name
	output = '--output=tmp/' + sbatch_script_name + '.txt'
	error = '--error=tmp/' + sbatch_script_name + '.err'
	array = '--array=0-' + str(num_jobs-1) + '%' + str(max_jobs)

	sbatch_options_list = [job_name, output, error, array]
	sbatch_options_list.extend(get_slurm_sbatch_default_options_list())
	sbatch_options_list.extend(get_slurm_sbatch_user_options_list()) # Get user options second to overrule defaults

	# Train default
	default = True
	scenario_file_name = scsh.create_file_scenario_validate(solver_name, instance_set_train_name, scsh.InstanceType.TRAIN, default)
	scenario_file_path = 'example_scenarios/' + solver_name + '/' + scenario_file_name
	exec_dir = 'example_scenarios/' + solver_name + '/validate_train_default/'
	configuration_str = 'DEFAULT'
	train_default_out = 'results/' + solver_name + '_validation_' + scenario_file_name

	train_default = ' --scenario-file ' + scenario_file_path + ' --execdir ' + exec_dir + ' --configuration ' + configuration_str

	# Test default
	default = True
	scenario_file_name = scsh.create_file_scenario_validate(solver_name, instance_set_test_name, scsh.InstanceType.TEST, default)
	scenario_file_path = 'example_scenarios/' + solver_name + '/' + scenario_file_name
	exec_dir = 'example_scenarios/' + solver_name + '/validate_test_default/'
	configuration_str = 'DEFAULT'
	test_default_out = 'results/' + solver_name + '_validation_' + scenario_file_name

	test_default = ' --scenario-file ' + scenario_file_path + ' --execdir ' + exec_dir + ' --configuration ' + configuration_str

	# Test configured
	default = False
	scenario_file_name = scsh.create_file_scenario_validate(solver_name, instance_set_test_name, scsh.InstanceType.TEST, default)
	scenario_file_path = 'example_scenarios/' + solver_name + '/' + scenario_file_name
	optimised_configuration_str, optimised_configuration_performance_par10, optimised_configuration_seed = scsh.get_optimised_configuration(solver_name, instance_set_train_name)
	exec_dir = 'example_scenarios/' + solver_name + '/validate_test_configured/'
	configuration_str = '\"' + str(optimised_configuration_str) + '\"'

	# Write configuration to file to be used by smac-validate
	config_file_path = 'example_scenarios/' + solver_name + '/configuration_for_validation.txt'
	fout = open(sgh.smac_dir + config_file_path, 'w+') # open the file of sbatch script
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX) # using the UNIX file lock to prevent other attempts to visit this sbatch script
	fout.write(optimised_configuration_str + '\n')

	test_configured_out = 'results/' + solver_name + '_validation_' + scenario_file_name

	test_configured = ' --scenario-file ' + scenario_file_path + ' --execdir ' + exec_dir + ' --configuration-list ' + config_file_path

	# Create job list
	job_params_list = [train_default, test_default, test_configured]
	job_output_list = [train_default_out, test_default_out, test_configured_out]

	## Set srun options
	n_cpus = 1

	srun_options_str = '-N1 -n1 --cpus-per-task ' + str(n_cpus)
	srun_options_str = srun_options_str + ' ' + get_slurm_srun_user_options_str()

	## Create target call
	n_cores = 16 # Number of cores available on a Grace GPU

	target_call_str = './smac-validate --use-scenario-outdir true --num-run 1 --cli-cores ' + str(n_cores)

	## Generate script
	generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list, job_params_list, srun_options_str, target_call_str, job_output_list)

	return sbatch_script_name
