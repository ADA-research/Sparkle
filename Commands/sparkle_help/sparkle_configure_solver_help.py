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
import sparkle_file_help as sfh
import sparkle_global_help
import sparkle_add_configured_solver_help as sacsh

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

def handle_file_instance_train(solver_name, instance_set_name):
	smac_solver_dir = sparkle_global_help.smac_dir + '/example_scenarios/' + solver_name + r'/'
	smac_instance_set_dir = sparkle_global_help.smac_dir + '/example_scenarios/instances/' + instance_set_name + r'/'
	smac_file_instance_train_path_ori = sparkle_global_help.smac_dir + '/example_scenarios/instances/' + instance_set_name + r'_train.txt'
	smac_file_instance_train_path_target = smac_solver_dir + instance_set_name + r'_train.txt'
	#print(smac_file_instance_train_path_target)
	
	command_line = r'cp ' + smac_file_instance_train_path_ori + r' ' + smac_file_instance_train_path_target
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

def create_file_scenario(solver_name, instance_set_name):
	smac_solver_dir = sparkle_global_help.smac_dir + '/example_scenarios/' + solver_name + r'/'
	smac_file_scenario = smac_solver_dir + solver_name + r'_' + instance_set_name + r'_scenario.txt'
	
	smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run_str, num_of_smac_run_in_parallel_str = get_smac_settings()
	
	smac_paramfile = 'example_scenarios/' + solver_name + r'/' + sacsh.get_pcs_file_from_solver_directory(smac_solver_dir)
	smac_outdir = 'example_scenarios/' + solver_name + r'/' + 'outdir/'
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

def get_optimised_configuration(solver_name, instance_set_name):
	optimised_configuration_str = ''
	optimised_configuration_performance_par10 = -1
	optimised_configuration_seed = -1
	
	smac_results_dir = sparkle_global_help.smac_dir + '/results/' + solver_name + '_' + instance_set_name + '/'
	list_file_result_name = os.listdir(smac_results_dir)
	
	key_str_1 = 'Estimated mean quality of final incumbent config'
	
	for file_result_name in list_file_result_name:
		file_result_path = smac_results_dir + file_result_name
		fin = open(file_result_path, 'r+')
		while True:
			myline = fin.readline()
			if not myline: break
			myline = myline.strip()
			if myline.find(key_str_1) == 0:
				mylist = myline.split()
				this_configuration_performance_par10 = float(mylist[14][:-1])
				if optimised_configuration_performance_par10 < 0 or this_configuration_performance_par10 < optimised_configuration_performance_par10:
					optimised_configuration_performance_par10 = this_configuration_performance_par10
					
					myline_2 = fin.readline()
					myline_2 = fin.readline()
					mylist_2 = myline_2.strip().split()
					start_index = 8
					end_index = len(mylist_2)
					optimised_configuration_str = ''
					for i in range(start_index, end_index):
						optimised_configuration_str += ' ' + mylist_2[i]
					
					myline_3 = fin.readline()
					mylist_3 = myline_3.strip().split()
					optimised_configuration_seed = mylist_3[4]
		fin.close()
	
	return optimised_configuration_str, optimised_configuration_performance_par10, optimised_configuration_seed

def generate_configure_solver_wrapper(solver_name, instance_set_name, optimised_configuration_str):
	smac_solver_dir = sparkle_global_help.smac_dir + r'/example_scenarios/' + solver_name + r'/'
	sparkle_run_configured_wrapper_path = smac_solver_dir + sparkle_global_help.sparkle_run_configured_wrapper
	
	fout = open(sparkle_run_configured_wrapper_path, 'w+')
	fout.write(r'#!/bin/bash' + '\n')
	fout.write(r'$1/' + sparkle_global_help.sparkle_run_generic_wrapper + r' $1 $2 ' + optimised_configuration_str + '\n')
	fout.close()
	
	command_line = 'chmod a+x ' + sparkle_run_configured_wrapper_path
	os.system(command_line)
	return


	
