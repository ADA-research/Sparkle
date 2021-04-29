#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import os
import fcntl
from pathlib import Path

from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_basic_help as sbh
from sparkle_help import sparkle_configure_solver_help as scsh
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_file_help as sfh
from sparkle_help.sparkle_command_help import CommandName
from sparkle_help import sparkle_job_help as sjh


def get_slurm_options_list(path_modifier=None):
	if path_modifier is None:
		path_modifier = ''

	#slurm_options = settings.get_slurm_extra_options()
	#slurm_options_list = ["--{}={}".format(k, v) for k, v in slurm_options.items()]
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
	if len(job_params_list) > 0:
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
	command_line = command_prefix
	if len(job_params_list) > 0:
		command_line += r' ' + r'${params[$SLURM_ARRAY_TASK_ID]}'

	# add output file paths to the command if given
	if job_output_list is not None:
		command_line += r' > ${output[$SLURM_ARRAY_TASK_ID]}'

	fout.write(command_line + '\n') # write the complete command in this sbatch script
	fout.close() # close the file of the sbatch script

	return


def generate_sbatch_script_for_validation(solver_name: str, instance_set_train_name: str, instance_set_test_name: str = None) -> str:
	## Set script name and path
	if instance_set_test_name is not None:
		sbatch_script_name = solver_name + '_' + instance_set_train_name + '_' + instance_set_test_name + '_validation_sbatch.sh'
	else:
		sbatch_script_name = solver_name + '_' + instance_set_train_name + '_validation_sbatch.sh'

	sbatch_script_path = sgh.smac_dir + sbatch_script_name

	## Set sbatch options
	max_jobs = sgh.settings.get_slurm_number_of_runs_in_parallel()
	num_jobs = 3
	if num_jobs < max_jobs:
		max_jobs = num_jobs
	std_out = 'tmp/' + sbatch_script_name + '.txt'
	std_err = 'tmp/' + sbatch_script_name + '.err'
	job_name = '--job-name=' + sbatch_script_name
	output = '--output=' + std_out
	error = '--error=' + std_err
	array = '--array=0-' + str(num_jobs-1) + '%' + str(max_jobs)
	sbatch_options_list = [job_name, output, error, array]

	# Log script and output paths
	sl.add_output(sbatch_script_path, 'Slurm batch script for validation')
	sl.add_output(sgh.smac_dir + std_out, 'Standard output of Slurm batch script for validation')
	sl.add_output(sgh.smac_dir + std_err, 'Error output of Slurm batch script for validation')

	# Train default
	default = True
	scenario_file_name = scsh.create_file_scenario_validate(solver_name, instance_set_train_name, scsh.InstanceType.TRAIN, default)
	scenario_file_path = 'example_scenarios/' + solver_name + '/' + scenario_file_name
	exec_dir = 'example_scenarios/' + solver_name + '/validate_train_default/'
	configuration_str = 'DEFAULT'
	train_default_out = 'results/' + solver_name + '_validation_' + scenario_file_name

	train_default = '--scenario-file ' + scenario_file_path + ' --execdir ' + exec_dir + ' --configuration ' + configuration_str

	# Create job list
	job_params_list = [train_default]
	job_output_list = [train_default_out]

	# If given, also validate on the test set
	if instance_set_test_name is not None:
		# Test default
		default = True
		scenario_file_name = scsh.create_file_scenario_validate(solver_name, instance_set_test_name, scsh.InstanceType.TEST, default)
		scenario_file_path = 'example_scenarios/' + solver_name + '/' + scenario_file_name
		exec_dir = 'example_scenarios/' + solver_name + '/validate_{}_test_default/'.format(instance_set_test_name)
		configuration_str = 'DEFAULT'
		test_default_out = 'results/' + solver_name + '_validation_' + scenario_file_name
	
		test_default = '--scenario-file ' + scenario_file_path + ' --execdir ' + exec_dir + ' --configuration ' + configuration_str
	
		# Test configured
		default = False
		scenario_file_name = scsh.create_file_scenario_validate(solver_name, instance_set_test_name, scsh.InstanceType.TEST, default)
		scenario_file_path = 'example_scenarios/' + solver_name + '/' + scenario_file_name
		optimised_configuration_str, optimised_configuration_performance_par10, optimised_configuration_seed = scsh.get_optimised_configuration(solver_name, instance_set_train_name)
		exec_dir = 'example_scenarios/' + solver_name + '/validate_{}_test_configured/'.format(instance_set_test_name)
		configuration_str = '\"' + str(optimised_configuration_str) + '\"'

		# Write configuration to file to be used by smac-validate
		config_file_path = 'example_scenarios/' + solver_name + '/configuration_for_validation.txt'
		fout = open(sgh.smac_dir + config_file_path, 'w+') # open the file of sbatch script
		fcntl.flock(fout.fileno(), fcntl.LOCK_EX) # using the UNIX file lock to prevent other attempts to visit this sbatch script
		fout.write(optimised_configuration_str + '\n')
	
		test_configured_out = 'results/' + solver_name + '_validation_' + scenario_file_name
	
		test_configured = '--scenario-file ' + scenario_file_path + ' --execdir ' + exec_dir + ' --configuration-list ' + config_file_path

		# Extend job list
		job_params_list.extend([test_default, test_configured])
		job_output_list.extend([test_default_out, test_configured_out])

	n_cpus = sgh.settings.get_slurm_clis_per_node() # Number of cores available on a Grace CPU

	# Adjust maximum number of cores to be the maximum of the instances we validate on
	instance_sizes = []
	# Get instance set sizes
	for instance_set_name, inst_type in [(instance_set_train_name, "train"), (instance_set_test_name, "test")]:
		if instance_set_name is not None:
			smac_instance_file = sgh.smac_dir + 'example_scenarios/' + solver_name + '/' + instance_set_name + '_' + inst_type + '.txt'
			if Path(smac_instance_file).is_file():
				instance_count = sum(1 for line in open(smac_instance_file,"r"))
				instance_sizes.append(instance_count)

	# Adjust cpus when nessacery
	if len(instance_sizes) > 0:
		max_instance_count = max(*instance_sizes) if len(instance_sizes) > 1 else instance_sizes[0]
		n_cpus = min(n_cpus, max_instance_count)

	## Extend sbatch options
	cpus = '--cpus-per-task=' + str(n_cpus)
	sbatch_options_list.append(cpus)
	sbatch_options_list.extend(get_slurm_sbatch_default_options_list())
	sbatch_options_list.extend(get_slurm_sbatch_user_options_list())  # Get user options second to overrule defaults

	## Set srun options
	srun_options_str = '--nodes=1 --ntasks=1 --cpus-per-task ' + str(n_cpus)
	srun_options_str = srun_options_str + ' ' + get_slurm_srun_user_options_str()

	## Create target call
	target_call_str = './smac-validate --use-scenario-outdir true --num-run 1 --cli-cores ' + str(n_cpus)

	# Remove possible old output
	sfh.rmfile(Path(sgh.smac_dir + std_out))
	sfh.rmfile(Path(sgh.smac_dir + std_err))

	# Remove possible old results
	for result_output_file in job_output_list:
		sfh.rmfile(Path(result_output_file))

	## Generate script
	generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list, job_params_list, srun_options_str, target_call_str, job_output_list)

	return sbatch_script_name


def generate_sbatch_script_for_feature_computation(n_jobs, feature_data_csv_path, list_jobs):
	## Set script name and path
	sbatch_script_name = 'computing_features_sbatch_shell_script_' + str(n_jobs) + '_' + sbh.get_time_pid_random_string() + '.sh'
	sbatch_script_dir = sgh.sparkle_tmp_path
	sbatch_script_path = sbatch_script_dir + sbatch_script_name

	## Set sbatch options
	max_jobs = sgh.settings.get_slurm_number_of_runs_in_parallel()
	num_jobs = n_jobs
	if num_jobs < max_jobs:
		max_jobs = num_jobs
	job_name = '--job-name=' + sbatch_script_name
	output = '--output=' + sbatch_script_path + '.txt'
	error = '--error=' + sbatch_script_path + '.err'
	array = '--array=0-' + str(num_jobs-1) + '%' + str(max_jobs)

	sbatch_options_list = [job_name, output, error, array]
	sbatch_options_list.extend(get_slurm_sbatch_default_options_list())
	sbatch_options_list.extend(get_slurm_sbatch_user_options_list()) # Get user options second to overrule defaults

	# Create job list
	job_params_list = []

	for i in range(0, num_jobs):
		instance_path = list_jobs[i][0]
		extractor_path = list_jobs[i][1]
		job_params = '--instance ' + instance_path + ' --extractor ' + extractor_path + ' --feature-csv ' + feature_data_csv_path
		job_params_list.append(job_params)

	## Set srun options
	srun_options_str = '-N1 -n1'
	srun_options_str = srun_options_str + ' ' + get_slurm_srun_user_options_str()

	## Create target call
	target_call_str = 'Commands/sparkle_help/compute_features_core.py'

	## Generate script
	generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list, job_params_list, srun_options_str, target_call_str)

	return sbatch_script_name, sbatch_script_dir


def submit_sbatch_script(sbatch_script_name: str, command_name: CommandName, execution_dir: str = None) -> str:
	if execution_dir is None:
		execution_dir = sgh.smac_dir

	sbatch_script_path = sbatch_script_name
	ori_path = os.getcwd()
	os.system('cd ' + execution_dir + ' ; chmod a+x ' + sbatch_script_path + ' ; cd ' + ori_path)
	command = 'cd ' + execution_dir + ' ; sbatch ' + sbatch_script_path + ' ; cd ' + ori_path

	output_list = os.popen(command).readlines()

	if len(output_list) > 0 and len(output_list[0].strip().split()) > 0:
		jobid = output_list[0].strip().split()[-1]
		# Add job to active job CSV
		sjh.write_active_job(jobid, command_name)
	else:
		jobid = ''

	return jobid

