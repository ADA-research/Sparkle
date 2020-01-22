#!/usr/bin/env python2.7
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
from enum import Enum
import sparkle_file_help as sfh
import sparkle_global_help
import sparkle_add_configured_solver_help as sacsh

class InstanceType(Enum):
	TRAIN = 1
	TEST = 2

def get_smac_settings():
	smac_run_obj = ''
	smac_whole_time_budget = ''
	smac_each_run_cutoff_time = ''
	smac_each_run_cutoff_length = ''
	num_of_smac_run_str = ''
	num_of_smac_run_in_parallel_str = ''
	sparkle_smac_settings_path = sparkle_global_help.sparkle_smac_settings_path
	
	fin = open(sparkle_smac_settings_path, 'r')
	while True:
		myline = fin.readline()
		if not myline: break
		mylist = myline.strip().split()
		if mylist[0] == 'smac_run_obj':
			smac_run_obj = mylist[2]
			if not (smac_run_obj == 'RUNTIME' or smac_run_obj == 'QUALITY'):
				sys.exit(-1)
		elif mylist[0] == 'smac_whole_time_budget':
			smac_whole_time_budget = mylist[2]
		elif mylist[0] == 'smac_each_run_cutoff_time':
			smac_each_run_cutoff_time = mylist[2]
		elif mylist[0] == 'smac_each_run_cutoff_length':
			smac_each_run_cutoff_length = mylist[2]
		elif mylist[0] == 'num_of_smac_run':
			num_of_smac_run_str = mylist[2]
		elif mylist[0] == 'num_of_smac_run_in_parallel':
			num_of_smac_run_in_parallel_str = mylist[2]
	fin.close()
	return smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run_str, num_of_smac_run_in_parallel_str

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
	smac_solver_dir = sparkle_global_help.smac_dir + '/example_scenarios/' + solver_name + r'/'
	smac_instance_set_dir = sparkle_global_help.smac_dir + '/example_scenarios/instances/' + instance_set_name + r'/'
	smac_file_instance_path_ori = sparkle_global_help.smac_dir + '/example_scenarios/instances/' + instance_set_name + file_postfix
	smac_file_instance_path_target = smac_solver_dir + instance_set_name + file_postfix
	
	command_line = r'cp ' + smac_file_instance_path_ori + r' ' + smac_file_instance_path_target
	os.system(command_line)
	return

def get_solver_deterministic(solver_name):
	deterministic = ''
	target_solver_path = 'Solvers/' + solver_name
	solver_list_path = sparkle_global_help.solver_list_path
	
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

	smac_solver_dir = sparkle_global_help.smac_dir + '/example_scenarios/' + solver_name + r'/'
	scenario_file_name = instance_set_name + '_' + inst_type + '_' + config_type + r'_scenario.txt'
	smac_file_scenario = smac_solver_dir + scenario_file_name
	
	smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run_str, num_of_smac_run_in_parallel_str = get_smac_settings()
	
	smac_paramfile = 'example_scenarios/' + solver_name + r'/' + sacsh.get_pcs_file_from_solver_directory(smac_solver_dir)
	smac_outdir = 'example_scenarios/' + solver_name + r'/' + 'outdir_' + inst_type + '_' + config_type + '/'
	smac_instance_file = 'example_scenarios/' + solver_name + r'/' + instance_set_name + '_' + inst_type + '.txt'
	smac_test_instance_file = smac_instance_file
	
	fout = open(smac_file_scenario, 'w+')
	fout.write('algo = ./' + sparkle_global_help.sparkle_smac_wrapper + '\n')
	fout.write('execdir = example_scenarios/' + solver_name + '/' + '\n')
	fout.write('deterministic = ' + get_solver_deterministic(solver_name) + '\n')
	fout.write('run_obj = ' + smac_run_obj + '\n')
	fout.write('wallclock-limit = ' + smac_whole_time_budget + '\n')
	fout.write('cutoffTime = ' + smac_each_run_cutoff_time + '\n')
	fout.write('cutoff_length = ' + smac_each_run_cutoff_length + '\n')
	fout.write('paramfile = ' + smac_paramfile + '\n')
	fout.write('outdir = ' + smac_outdir + '\n')
	fout.write('instance_file = ' + smac_instance_file + '\n')
	fout.write('test_instance_file = ' + smac_test_instance_file + '\n')
	fout.close()
	return scenario_file_name

# Create a file with the configuration scenario in the solver directory
def create_file_scenario(solver_name, instance_set_name):
	smac_solver_dir = sparkle_global_help.smac_dir + '/example_scenarios/' + solver_name + r'/'
	smac_file_scenario = smac_solver_dir + solver_name + r'_' + instance_set_name + r'_scenario.txt'
	
	smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run_str, num_of_smac_run_in_parallel_str = get_smac_settings()
	
	smac_paramfile = 'example_scenarios/' + solver_name + r'/' + sacsh.get_pcs_file_from_solver_directory(smac_solver_dir)
	smac_outdir = 'example_scenarios/' + solver_name + r'/' + 'outdir_train_configuration/'
	smac_instance_file = 'example_scenarios/' + solver_name + r'/' + instance_set_name + '_train.txt'
	smac_test_instance_file = smac_instance_file
	
	fout = open(smac_file_scenario, 'w+')
	fout.write('algo = ./' + sparkle_global_help.sparkle_smac_wrapper + '\n')
	fout.write('execdir = example_scenarios/' + solver_name + '/' + '\n')
	fout.write('deterministic = ' + get_solver_deterministic(solver_name) + '\n')
	fout.write('run_obj = ' + smac_run_obj + '\n')
	fout.write('wallclock-limit = ' + smac_whole_time_budget + '\n')
	fout.write('cutoffTime = ' + smac_each_run_cutoff_time + '\n')
	fout.write('cutoff_length = ' + smac_each_run_cutoff_length + '\n')
	fout.write('paramfile = ' + smac_paramfile + '\n')
	fout.write('outdir = ' + smac_outdir + '\n')
	fout.write('instance_file = ' + smac_instance_file + '\n')
	fout.write('test_instance_file = ' + smac_test_instance_file + '\n')
	fout.write('validation = true' + '\n')
	fout.close()
	return

def create_smac_configure_sbatch_script(solver_name, instance_set_name):
	smac_solver_dir = sparkle_global_help.smac_dir + '/example_scenarios/' + solver_name + r'/'
	smac_file_scenario_name = solver_name + r'_' + instance_set_name + r'_scenario.txt'
	smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run_str, num_of_smac_run_in_parallel_str = get_smac_settings()
	
	command_line = 'cd ' + sparkle_global_help.smac_dir + ' ; ' + './generate_sbatch_script.py ' + 'example_scenarios/' + solver_name + r'/' + smac_file_scenario_name + ' ' + 'results/' + solver_name + '_' + instance_set_name + '/' + ' ' + num_of_smac_run_str + ' ' + num_of_smac_run_in_parallel_str + ' ; ' + 'cd ../../'
	
	#print(command_line)
	os.system(command_line)
	
	smac_configure_sbatch_script_name = smac_file_scenario_name + '_' + num_of_smac_run_str + '_exp_sbatch.sh'
	return smac_configure_sbatch_script_name

def submit_smac_configure_sbatch_script(smac_configure_sbatch_script_name):
	ori_path = os.getcwd()
	command_line = 'cd ' + sparkle_global_help.smac_dir + ' ; ' + 'sbatch ' + smac_configure_sbatch_script_name + ' ; ' + 'cd ' + ori_path
	os.system(command_line)
	return

# Check the results directory for this solver and instance set combination exists
def check_configuration_exists(solver_name, instance_set_name):
	smac_results_dir = sparkle_global_help.smac_dir + '/results/' + solver_name + '_' + instance_set_name + '/'

	return (os.path.exists(smac_results_dir))

def get_optimised_configuration(solver_name, instance_set_name):
	optimised_configuration_str = ''
	optimised_configuration_performance_par10 = -1
	optimised_configuration_seed = -1
	
	smac_results_dir = sparkle_global_help.smac_dir + '/results/' + solver_name + '_' + instance_set_name + '/'
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
				this_configuration_performance_par10 = float(mylist[14][:-1])
				if optimised_configuration_performance_par10 < 0 or this_configuration_performance_par10 < optimised_configuration_performance_par10:
					optimised_configuration_performance_par10 = this_configuration_performance_par10

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
	
	return optimised_configuration_str, optimised_configuration_performance_par10, optimised_configuration_seed

def generate_configure_solver_wrapper(solver_name, optimised_configuration_str):
	smac_solver_dir = sparkle_global_help.smac_dir + r'/example_scenarios/' + solver_name + r'/'
	sparkle_run_configured_wrapper_path = smac_solver_dir + sparkle_global_help.sparkle_run_configured_wrapper
	
	fout = open(sparkle_run_configured_wrapper_path, 'w+')
	fout.write(r'#!/bin/bash' + '\n')
	fout.write(r'$1/' + sparkle_global_help.sparkle_run_generic_wrapper + r' $1 $2 ' + optimised_configuration_str + '\n')
	fout.close()
	
	command_line = 'chmod a+x ' + sparkle_run_configured_wrapper_path
	os.system(command_line)
	return


	
