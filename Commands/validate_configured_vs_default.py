#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import os
import sys
import argparse
from pathlib import Path

from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_system_status_help
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_run_status_help
from sparkle_help import sparkle_generate_report_help
from sparkle_help import sparkle_generate_report_for_test_help
from sparkle_help import sparkle_configure_solver_help as scsh
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_add_train_instances_help as satih
from sparkle_help import sparkle_slurm_help as ssh
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings
from sparkle_help.sparkle_settings import PerformanceMeasure
from sparkle_help.sparkle_settings import SettingState
from sparkle_help import argparse_custom as ac


if __name__ == r'__main__':
	# Initialise settings
	global settings
	sgh.settings = sparkle_settings.Settings()

	# Log command call
	sl.log_command(sys.argv)

	parser = argparse.ArgumentParser()
	parser.add_argument('--solver', required=True, type=str, help='path to solver')
	parser.add_argument('--instance-set-train', required=True, type=str, help='path to training instance set')
	parser.add_argument('--instance-set-test', required=False, type=str, help='path to testing instance set')
	parser.add_argument('--performance-measure', choices=PerformanceMeasure.__members__, default=sgh.settings.DEFAULT_general_performance_measure, action=ac.SetByUser, help='the performance measure, e.g. runtime')
	parser.add_argument('--target-cutoff-time', type=int, default=sgh.settings.DEFAULT_general_target_cutoff_time, action=ac.SetByUser, help='cutoff time per target algorithm run in seconds')
	parser.add_argument('--settings-file', type=Path, default=sgh.settings.DEFAULT_settings_path, action=ac.SetByUser, help='specify the settings file to use in case you want to use one other than the default')

	# Process command line arguments
	args = parser.parse_args()
	solver = args.solver
	instance_set_train = args.instance_set_train
	instance_set_test = args.instance_set_test

	if ac.set_by_user(args, 'settings_file'): sgh.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE) # Do first, so other command line options can override settings from the file
	args.performance_measure = PerformanceMeasure.from_str(args.performance_measure)
	if ac.set_by_user(args, 'performance_measure'): sgh.settings.set_general_performance_measure(args.performance_measure, SettingState.CMD_LINE)
	if ac.set_by_user(args, 'target_cutoff_time'): sgh.settings.set_general_target_cutoff_time(args.target_cutoff_time, SettingState.CMD_LINE)

	solver_name = sfh.get_last_level_directory_name(solver)
	instance_set_train_name = sfh.get_last_level_directory_name(instance_set_train)
	instance_set_test_name = None

	# Make sure configuration results exist before trying to work with them
	scsh.check_validation_prerequisites(solver_name, instance_set_train_name)

	# Record optimised configuration
	scsh.write_optimised_configuration_str(solver_name, instance_set_train_name)
	scsh.write_optimised_configuration_pcs(solver_name, instance_set_train_name)

	# Copy runsolver to the solver directory
	ori_smac_runsolver_path = sgh.smac_dir + '/example_scenarios/' + 'runsolver'
	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + '/'
	command_line = 'cp ' + ori_smac_runsolver_path + ' ' + smac_solver_dir
	os.system(command_line)

	if instance_set_test is not None:
		instance_set_test_name = sfh.get_last_level_directory_name(instance_set_test)

		# Copy test instances to smac directory (train should already be there from configuration)
		instances_directory_test = r'Instances/' + instance_set_test_name
		list_path = satih.get_list_all_path(instances_directory_test)
		inst_dir_prefix = instances_directory_test
		smac_inst_dir_prefix = sgh.smac_dir + r'/' + 'example_scenarios/' + r'instances/' + sfh.get_last_level_directory_name(instances_directory_test)
		satih.copy_instances_to_smac(list_path, inst_dir_prefix, smac_inst_dir_prefix, r'test')

		# Copy file listing test instances to smac solver directory
		scsh.handle_file_instance_test(solver_name, instance_set_test_name)

	# Create solver execution directories, and copy necessary files there
	scsh.prepare_smac_execution_directories_validation(solver_name)

	# Generate and run sbatch script for validation runs
	sbatch_script_name = ssh.generate_sbatch_script_for_validation(solver_name, instance_set_train_name, instance_set_test_name)
	sbatch_script_dir = sgh.smac_dir
	sbatch_script_path = sbatch_script_dir + sbatch_script_name

	validate_jobid = ssh.submit_sbatch_script(sbatch_script_name, sbatch_script_dir)

	print("c Running validation in parallel. Waiting for Slurm job with id:")
	print(validate_jobid)

	# Write most recent run to file
	last_test_file_path = sgh.smac_dir + '/example_scenarios/' + solver_name + '/' + sgh.sparkle_last_test_file_name

	fout = open(last_test_file_path, 'w+')
	fout.write('solver ' + str(solver) + '\n')
	fout.write('train ' + str(instance_set_train) + '\n')
	if instance_set_test is not None:
		fout.write('test ' + str(instance_set_test) + '\n')
	fout.close()

	# Write used settings to file
	sgh.settings.write_used_settings()

