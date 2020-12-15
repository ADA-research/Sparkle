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
import fcntl
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
from sparkle_help import sparkle_generate_report_for_configuration_help as sgrfch
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

	# Load solver and test instances
	parser = argparse.ArgumentParser()
	parser.add_argument('--solver', required=True, type=str, help='path to solver')
	parser.add_argument('--instance-set-train', required=False, type=str, help='path to training instance set')
	parser.add_argument('--instance-set-test', required=False, type=str, help='path to testing instance set')
	parser.add_argument('--no-ablation', required=False, dest="flag_ablation", default=True, const=False, nargs="?", help='turn off reporting on ablation')
	parser.add_argument('--settings-file', type=Path, default=sgh.settings.DEFAULT_settings_path, action=ac.SetByUser, help='specify the settings file to use in case you want to use one other than the default')

	# Process command line arguments
	args = parser.parse_args()

	if ac.set_by_user(args, 'settings_file'): sgh.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE) # Do first, so other command line options can override settings from the file

	solver = args.solver
	instance_set_train = args.instance_set_train
	instance_set_test = args.instance_set_test

	flag_instance_set_train = False if instance_set_train == None else True
	flag_instance_set_test = False if instance_set_test == None else True

	solver_name = sfh.get_last_level_directory_name(solver)

	# If no instance set(s) is/are given, try to retrieve them from the last run of validate_configured_vs_default
	if not flag_instance_set_train and not flag_instance_set_test:
		instance_set_train, instance_set_test, flag_instance_set_train, flag_instance_set_test = sgrfch.get_most_recent_test_run(solver_name)
	# If only the testing set is given return an error
	elif not flag_instance_set_train and flag_instance_set_test:
		print('c Argument Error! Only a testing set was provided, please also provide a training set')
		print('c Usage: %s --solver <solver> [--instance-set-train <instance-set-train>] [--instance-set-test <instance-set-test>]' % sys.argv[0])
		sys.exit(-1)

	# Generate a report depending on which instance sets are provided
	if (flag_instance_set_train and flag_instance_set_test):
		instance_set_train_name = sfh.get_last_level_directory_name(instance_set_train)
		instance_set_test_name = sfh.get_last_level_directory_name(instance_set_test)
		sgrfch.check_results_exist(solver_name, instance_set_train_name, instance_set_test_name)
		sgrfch.generate_report_for_configuration(solver_name, instance_set_train_name, instance_set_test_name, ablation=args.flag_ablation)
	elif flag_instance_set_train:
		instance_set_train_name = sfh.get_last_level_directory_name(instance_set_train)
		sgrfch.check_results_exist(solver_name, instance_set_train_name)
		sgrfch.generate_report_for_configuration_train(solver_name, instance_set_train_name, ablation=args.flag_ablation)
	else:
		print('c Error: No results from validate_configured_vs_default found that can be used in the report!')
		sys.exit(-1)

