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
from pathlib import Path
from pathlib import PurePath
from enum import Enum
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_add_configured_solver_help as sacsh
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_slurm_help as ssh
from sparkle_help.sparkle_settings import PerformanceMeasure


class InstanceType(Enum):
	TRAIN = 1
	TEST = 2


def get_smac_run_obj() -> str:
	# Get smac_run_obj from general settings
	smac_run_obj = sgh.settings.get_general_performance_measure()

	# Convert to SMAC format
	if smac_run_obj == PerformanceMeasure.RUNTIME:
		smac_run_obj = smac_run_obj.name
	elif smac_run_obj == PerformanceMeasure.QUALITY_ABSOLUTE:
		smac_run_obj = 'QUALITY'
	else:
		print('c Warning: Unknown performance measure', smac_run_obj, '! This is a bug in Sparkle.')

	return smac_run_obj

def get_smac_settings():
	smac_each_run_cutoff_length = sgh.settings.get_smac_target_cutoff_length()
	smac_run_obj = get_smac_run_obj()
	smac_whole_time_budget = sgh.settings.get_config_budget_per_run()
	smac_each_run_cutoff_time = sgh.settings.get_general_target_cutoff_time()
	num_of_smac_run = sgh.settings.get_config_number_of_runs()
	num_of_smac_run_in_parallel = sgh.settings.get_slurm_number_of_runs_in_parallel()

	return smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run, num_of_smac_run_in_parallel

'''
TODO: fix ablation settings
		elif mylist[0] == 'ablation_concurrent_clis':
			ablation_concurrent_clis = mylist[2]
		elif mylist[0] == 'ablation_racing':
			ablation_racing = mylist[2].lower() in ['true', '1']
	fin.close()

	return_list = [smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run_str, num_of_smac_run_in_parallel_str]
	if with_ablation:
		return_list.append(ablation_concurrent_clis)
		return_list.append(ablation_racing)
'''


# Copy file listing the training instances from the instance directory to the solver directory
def handle_file_instance_train(solver_name, instance_set_name):
	file_postfix = r'_train.txt'
	handle_file_instance(solver_name, instance_set_name, file_postfix)

	return


# Copy file listing the testing instances from the instance directory to the solver directory
def handle_file_instance_test(solver_name, instance_set_name):
	file_postfix = r'_test.txt'
	handle_file_instance(solver_name, instance_set_name, file_postfix)

	return


# Copy file with the specified postfix listing instances from the instance directory to the solver directory
def handle_file_instance(solver_name, instance_set_name, file_postfix):
	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + r'/'
	smac_instance_set_dir = sgh.smac_dir + '/example_scenarios/instances/' + instance_set_name + r'/'
	smac_file_instance_path_ori = sgh.smac_dir + '/example_scenarios/instances/' + instance_set_name + file_postfix
	smac_file_instance_path_target = smac_solver_dir + instance_set_name + file_postfix

	command_line = r'cp ' + smac_file_instance_path_ori + r' ' + smac_file_instance_path_target
	os.system(command_line)

	return


def get_solver_deterministic(solver_name):
	deterministic = ''
	target_solver_path = 'Solvers/' + solver_name
	solver_list_path = sgh.solver_list_path

	fin = open(solver_list_path, 'r+')
	fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
	while True:
		myline = fin.readline()
		if not myline: break
		myline = myline.strip()
		mylist = myline.split()
		if(mylist[0] == target_solver_path):
			deterministic = mylist[1]
			break

	return deterministic


# Create a file with the configuration scenario to be used for smac validation in the solver directory
def create_file_scenario_validate(solver_name, instance_set_name, instance_type, default):
	if instance_type is InstanceType.TRAIN:
		inst_type = 'train'
	else:
		inst_type = 'test'

	if default is True:
		config_type = 'default'
	else:
		config_type = 'configured'

	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + r'/'
	scenario_file_name = instance_set_name + '_' + inst_type + '_' + config_type + r'_scenario.txt'
	smac_file_scenario = smac_solver_dir + scenario_file_name

	smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run, num_of_smac_run_in_parallel = get_smac_settings()

	smac_paramfile = 'example_scenarios/' + solver_name + r'/' + sacsh.get_pcs_file_from_solver_directory(smac_solver_dir)
	smac_outdir = 'example_scenarios/' + solver_name + r'/' + 'outdir_' + inst_type + '_' + config_type + '/'
	smac_instance_file = 'example_scenarios/' + solver_name + r'/' + instance_set_name + '_' + inst_type + '.txt'
	smac_test_instance_file = smac_instance_file

	fout = open(smac_file_scenario, 'w+')
	fout.write('algo = ./' + sgh.sparkle_smac_wrapper + '\n')
	fout.write('execdir = example_scenarios/' + solver_name + '/' + '\n')
	fout.write('deterministic = ' + get_solver_deterministic(solver_name) + '\n')
	fout.write('run_obj = ' + smac_run_obj + '\n')
	fout.write('wallclock-limit = ' + str(smac_whole_time_budget) + '\n')
	fout.write('cutoffTime = ' + str(smac_each_run_cutoff_time) + '\n')
	fout.write('cutoff_length = ' + smac_each_run_cutoff_length + '\n')
	fout.write('paramfile = ' + smac_paramfile + '\n')
	fout.write('outdir = ' + smac_outdir + '\n')
	fout.write('instance_file = ' + smac_instance_file + '\n')
	fout.write('test_instance_file = ' + smac_test_instance_file + '\n')
	fout.close()

	return scenario_file_name


# Create a file with the configuration scenario in the solver directory
def create_file_scenario_configuration(solver_name, instance_set_name):
	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + r'/'
	smac_file_scenario = smac_solver_dir + solver_name + r'_' + instance_set_name + r'_scenario.txt'

	smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run, num_of_smac_run_in_parallel = get_smac_settings()

	smac_paramfile = 'example_scenarios/' + solver_name + r'/' + sacsh.get_pcs_file_from_solver_directory(smac_solver_dir)
	smac_outdir = 'example_scenarios/' + solver_name + r'/' + 'outdir_train_configuration/'
	smac_instance_file = 'example_scenarios/' + solver_name + r'/' + instance_set_name + '_train.txt'
	smac_test_instance_file = smac_instance_file

	fout = open(smac_file_scenario, 'w+')
	fout.write('algo = ./' + sgh.sparkle_smac_wrapper + '\n')
	fout.write('execdir = example_scenarios/' + solver_name + '/' + '\n')
	fout.write('deterministic = ' + get_solver_deterministic(solver_name) + '\n')
	fout.write('run_obj = ' + smac_run_obj + '\n')
	fout.write('wallclock-limit = ' + str(smac_whole_time_budget) + '\n')
	fout.write('cutoffTime = ' + str(smac_each_run_cutoff_time) + '\n')
	fout.write('cutoff_length = ' + smac_each_run_cutoff_length + '\n')
	fout.write('paramfile = ' + smac_paramfile + '\n')
	fout.write('outdir = ' + smac_outdir + '\n')
	fout.write('instance_file = ' + smac_instance_file + '\n')
	fout.write('test_instance_file = ' + smac_test_instance_file + '\n')
	fout.write('validation = true' + '\n')
	fout.close()

	return


def prepare_smac_execution_directories_configuration(solver_name):
	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + r'/'
	smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run, num_of_smac_run_in_parallel = get_smac_settings()

	for i in range(1, num_of_smac_run+1):
		# Create directories, -p makes sure any missing parents are also created
		cmd = "mkdir -p " + smac_solver_dir + str(i) + '/tmp/'
		os.system(cmd)

		solver_diretory = r'Solvers/' + solver_name + r'/*'
		cmd = r'cp -r ' + solver_diretory + r' ' + smac_solver_dir + str(i)
		os.system(cmd)

	return


def prepare_smac_execution_directories_validation(solver_name):
	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + r'/'
	smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run, num_of_smac_run_in_parallel = get_smac_settings()

	for i in range(1, num_of_smac_run+1):
		solver_diretory = r'Solvers/' + solver_name + r'/*'

		## Train default
		execdir = "validate_train_default/"

		# Create directories, -p makes sure any missing parents are also created
		cmd = "mkdir -p " + smac_solver_dir + execdir + '/tmp/'
		os.system(cmd)
		# Copy solver to execution directory
		cmd = r'cp -r ' + solver_diretory + r' ' + smac_solver_dir + execdir
		os.system(cmd)

		## Test default
		execdir = "validate_test_default/"

		# Create directories, -p makes sure any missing parents are also created
		cmd = "mkdir -p " + smac_solver_dir + execdir + '/tmp/'
		os.system(cmd)
		# Copy solver to execution directory
		cmd = r'cp -r ' + solver_diretory + r' ' + smac_solver_dir + execdir
		os.system(cmd)

		## Test configured
		execdir = "validate_test_configured/"

		# Create directories, -p makes sure any missing parents are also created
		cmd = "mkdir -p " + smac_solver_dir + execdir + '/tmp/'
		os.system(cmd)
		# Copy solver to execution directory
		cmd = r'cp -r ' + solver_diretory + r' ' + smac_solver_dir + execdir
		os.system(cmd)

	return


def create_smac_configure_sbatch_script(solver_name, instance_set_name):
	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + r'/'
	execdir = '/example_scenarios/' + solver_name + r'/'
	smac_file_scenario_name = solver_name + r'_' + instance_set_name + r'_scenario.txt'
	smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run, num_of_smac_run_in_parallel = get_smac_settings()

	# Remove possible old results for this scenario
	result_part = 'results/' + solver_name + '_' + instance_set_name + '/'
	result_dir = sgh.smac_dir + result_part
	[item.unlink() for item in Path(result_dir).glob("*") if item.is_file()]

	command_line = 'cd ' + sgh.smac_dir + ' ; ' + './generate_sbatch_script.py ' + 'example_scenarios/' + solver_name + r'/' + smac_file_scenario_name + ' ' + result_part + ' ' + str(num_of_smac_run) + ' ' + str(num_of_smac_run_in_parallel) + ' ' + execdir + ' ; ' + 'cd ../../'

	#print(command_line)
	os.system(command_line)

	smac_configure_sbatch_script_name = smac_file_scenario_name + '_' + str(num_of_smac_run) + '_exp_sbatch.sh'

	return smac_configure_sbatch_script_name


def submit_smac_configure_sbatch_script(smac_configure_sbatch_script_name):
	ori_path = os.getcwd()
	command_line = 'cd ' + sgh.smac_dir + ' ; ' + 'sbatch ' + smac_configure_sbatch_script_name + ' ; ' + 'cd ' + ori_path
	#os.system(command_line)

	output_list = os.popen(command_line).readlines()
	if len(output_list) > 0 and len(output_list[0].strip().split())>0:
		jobid = output_list[0].strip().split()[-1]
	else:
		jobid = ''

	return jobid


# Check the results directory for this solver and instance set combination exists
# NOTE: This function assumes SMAC output
def check_configuration_exists(solver_name: str, instance_set_name: str):
	# Check the results directory exists
	smac_results_dir = Path(sgh.smac_dir + '/results/' + solver_name + '_' + instance_set_name + '/')

	all_good = smac_results_dir.is_dir()

	if not all_good:
		print('c ERROR: No configuration results found for the given solver and training instance set.')
		sys.exit(-1)

	return


def check_instance_list_file_exist(solver_name: str, instance_set_name: str):
	# Check the instance list file exists
	file_name = Path(instance_set_name + '_train.txt')
	instance_list_file_path = Path(PurePath(Path(sgh.smac_dir) / Path('example_scenarios') / Path(solver_name) / file_name))

	all_good = instance_list_file_path.is_file()

	if not all_good:
		print('c ERROR: Instance list file not found, make sure configuration was completed correctly for this solver and instance set combination.')
		sys.exit(-1)

	return


def check_validation_prerequisites(solver_name: str, instance_set_name: str):
	check_configuration_exists(solver_name, instance_set_name)
	check_instance_list_file_exist(solver_name, instance_set_name)

	return


# Write optimised configuration string to file
def write_optimised_configuration_str(solver_name, instance_set_name):
	optimised_configuration_str, optimised_configuration_performance_par10, optimised_configuration_seed = get_optimised_configuration(solver_name, instance_set_name)
	latest_configuration_str_path = sgh.sparkle_tmp_path + 'latest_configuration.txt'

	with open(latest_configuration_str_path, 'w') as outfile:
		outfile.write(optimised_configuration_str)
	# Log output
	sl.add_output(latest_configuration_str_path, 'Configured algorithm parameters of the most recent configuration process')

	return


# Write optimised configuration to a new PCS file
def write_optimised_configuration_pcs(solver_name, instance_set_name):
	# Read optimised configuration and convert to dict
	optimised_configuration_str, optimised_configuration_performance_par10, optimised_configuration_seed = get_optimised_configuration(solver_name, instance_set_name)
	optimised_configuration_str += " -arena '12345'"
	optimised_configuration_list = optimised_configuration_str.split()

	# Create dictionary
	config_dict = {}
	for i in range(0, len(optimised_configuration_list), 2):
		# Remove dashes and spaces from parameter names, and remove quotes and
		# spaces from parameter values before adding them to the dict
		config_dict[optimised_configuration_list[i].strip(" -")] = optimised_configuration_list[i+1].strip(" '")

	# Read existing PCS file and create output content
	solver_diretory = 'Solvers/' + solver_name
	pcs_file = solver_diretory + '/' + sacsh.get_pcs_file_from_solver_directory(solver_diretory)
	pcs_file_out = []

	with open(pcs_file) as infile:
		for line in infile:
			# Copy empty lines
			if not line.strip():
				line_out = line
			# Don't mess with conditional (containing '|') and forbidden (starting
			# with '{') parameter clauses, copy them as is
			elif '|' in line or line.startswith('{'):
				line_out = line
			# Also copy parameters that do not appear in the optimised list
			# (if the first word in the line does not match one of the parameter names in the dict)
			elif line.split()[0] not in config_dict:
				line_out = line
			# Modify default values with optimised values
			else:
				words = line.split('[')
				if len(words) == 2:
					# Second element is default value + possible tail
					param_name = line.split()[0]
					param_val = config_dict[param_name]
					tail = words[1].split(']')[1]
					line_out = words[0] + '[' + param_val + ']' + tail
				elif len(words) == 3:
					# Third element is default value + possible tail
					param_name = line.split()[0]
					param_val = config_dict[param_name]
					tail = words[2].split(']')[1]
					line_out = words[0] + words[1] + '[' + param_val + ']' + tail
				else:
					# This does not seem to be a line with a parameter definition, copy as is
					line_out = line
			pcs_file_out.append(line_out)

	latest_configuration_pcs_path = sgh.sparkle_tmp_path + 'latest_configuration.pcs'

	with open(latest_configuration_pcs_path, 'w') as outfile:
		for element in pcs_file_out:
			outfile.write(str(element))
	# Log output
	sl.add_output(latest_configuration_pcs_path, 'PCS file with configured algorithm parameters of the most recent configuration process as default values')

	return


def get_optimised_configuration(solver_name, instance_set_name):
	optimised_configuration_str = ''
	optimised_configuration_performance = -1
	optimised_configuration_seed = -1

	smac_results_dir = sgh.smac_dir + '/results/' + solver_name + '_' + instance_set_name + '/'
	list_file_result_name = os.listdir(smac_results_dir)

	key_str_1 = 'Estimated mean quality of final incumbent config'

	# Compare results of each run on the training set to find the best configuration among them
	for file_result_name in list_file_result_name:
		file_result_path = smac_results_dir + file_result_name
		fin = open(file_result_path, 'r+')
		while True:
			myline = fin.readline()
			if not myline: break
			myline = myline.strip()
			if myline.find(key_str_1) == 0:
				mylist = myline.split()
				# Skip 14 words leading up to the performance value
				this_configuration_performance = float(mylist[14][:-1])
				if optimised_configuration_performance < 0 or this_configuration_performance < optimised_configuration_performance:
					optimised_configuration_performance = this_configuration_performance

					# Skip the line before the line with the optimised configuration
					myline_2 = fin.readline()
					myline_2 = fin.readline()
					mylist_2 = myline_2.strip().split()
					# Skip 8 words before the configured parameters
					start_index = 8
					end_index = len(mylist_2)
					optimised_configuration_str = ''
					for i in range(start_index, end_index):
						optimised_configuration_str += ' ' + mylist_2[i]

					# Get seed used to call smac
					myline_3 = fin.readline()
					mylist_3 = myline_3.strip().split()
					optimised_configuration_seed = mylist_3[4]
		fin.close()

	return optimised_configuration_str, optimised_configuration_performance, optimised_configuration_seed


def generate_configure_solver_wrapper(solver_name, optimised_configuration_str):
	smac_solver_dir = sgh.smac_dir + r'/example_scenarios/' + solver_name + r'/'
	sparkle_run_configured_wrapper_path = smac_solver_dir + sgh.sparkle_run_configured_wrapper

	fout = open(sparkle_run_configured_wrapper_path, 'w+')
	fout.write(r'#!/bin/bash' + '\n')
	fout.write(r'$1/' + sgh.sparkle_run_generic_wrapper + r' $1 $2 ' + optimised_configuration_str + '\n')
	fout.close()

	command_line = 'chmod a+x ' + sparkle_run_configured_wrapper_path
	os.system(command_line)

	return

def generate_validation_callback_slurm_script(solver, instance_set_train, instance_set_test, dependency):
	command_line = 'echo $(pwd) $(date)\n'
	command_line += 'srun -N1 -n1 ./Commands/validate_configured_vs_default.py  --settings-file Settings/latest.ini'
	command_line += ' --solver ' + solver
	command_line += ' --instance-set-train ' + instance_set_train
	if instance_set_test is not None:
		command_line += ' --instance-set-test ' + instance_set_test

	generate_generic_callback_slurm_script("validation", solver, instance_set_train, instance_set_test, dependency, command_line)

def generate_ablation_callback_slurm_script(solver, instance_set_train, instance_set_test, dependency):
	command_line = 'echo $(pwd) $(date)\n'
	command_line += 'srun -N1 -n1 ./Commands/run_ablation.py --settings-file Settings/latest.ini'
	command_line += ' --solver ' + solver
	command_line += ' --instance-set-train ' + instance_set_train
	if instance_set_test is not None:
		command_line += ' --instance-set-test ' + instance_set_test

	generate_generic_callback_slurm_script("ablation", solver, instance_set_train, instance_set_test, dependency, command_line)


def generate_generic_callback_slurm_script(name,solver, instance_set_train, instance_set_test, dependency, commands):
	solver_name = sfh.get_last_level_directory_name(solver)
	instance_set_train_name = sfh.get_last_level_directory_name(instance_set_train)
	instance_set_test_name = None
	if instance_set_test is not None:
		instance_set_test_name = sfh.get_last_level_directory_name(instance_set_test)

	delayed_validation_file_name = "delayed_{}_{}_{}".format(name,solver_name, instance_set_train_name)
	if instance_set_test is not None:
		delayed_validation_file_name += "_{}".format(instance_set_test_name)
	delayed_validation_file_name += "_script.sh"

	sfh.checkout_directory(sgh.sparkle_tmp_path)
	delayed_validation_file_path = sgh.sparkle_tmp_path + delayed_validation_file_name

	job_name = '--job-name=' + delayed_validation_file_name
	output = '--output=' + delayed_validation_file_path + '.txt'
	error = '--error=' + delayed_validation_file_path + '.err'

	sbatch_options_list = [job_name, output, error]
	sbatch_options_list.extend(ssh.get_slurm_sbatch_default_options_list())
	sbatch_options_list.extend(ssh.get_slurm_sbatch_user_options_list())  # Get user options second to overrule defaults

	#Only overwrite task specific arguments
	sbatch_options_list.append("--dependency=afterany:{}".format(dependency))
	sbatch_options_list.append("--nodes=1")
	sbatch_options_list.append("--ntasks=1")
	sbatch_options_list.append("-c1")
	sbatch_options_list.append("--mem-per-cpu=3000")

	ori_path = os.getcwd()

	command_line = commands

	fout = open(delayed_validation_file_path, "w")
	fout.write(r'#!/bin/bash' + '\n')  # use bash to execute this script
	fout.write(r'###' + '\n')
	fout.write(r'###' + '\n')
	for sbatch_option in sbatch_options_list:
		fout.write(r'#SBATCH ' + str(sbatch_option) + '\n')
	fout.write(r'###' + '\n')
	fout.write(command_line + "\n")
	fout.close()

	os.popen("chmod 755 " + delayed_validation_file_path)

	output_list = os.popen("sbatch ./" + delayed_validation_file_path).readlines()
	if len(output_list) > 0 and len(output_list[0].strip().split()) > 0:
		jobid = output_list[0].strip().split()[-1]
	else:
		jobid = ''
	#os.popen("sbatch ./" + delayed_validation_file_path)
	print("c Callback script to launch {} is placed at {}".format(name,delayed_validation_file_path))
	print("c Once configuration is finished, {name} will automatically start as a Slurm job: {jobid}".format(name=name,
																											 jobid=jobid))
