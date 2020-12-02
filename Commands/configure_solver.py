#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import argparse
import sys
from pathlib import Path

from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_configure_solver_help as scsh
from sparkle_help import sparkle_add_train_instances_help as satih
from sparkle_help import sparkle_logging as sl
from sparkle_help.sparkle_settings import PerformanceMeasure
from sparkle_help.sparkle_settings import SettingState
from sparkle_help import argparse_custom as ac


if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	parser = argparse.ArgumentParser()
	parser.add_argument('--solver', required=True, type=str, help='path to solver')
	parser.add_argument('--instance-set-train', required=True, type=str, help='path to training instance set')
	parser.add_argument('--performance-measure', choices=PerformanceMeasure.__members__, default=sgh.settings.DEFAULT_general_performance_measure, action=ac.SetByUser, help='the performance measure, e.g. runtime')
	parser.add_argument('--target-cutoff-time', type=int, default=sgh.settings.DEFAULT_config_target_cutoff_time, action=ac.SetByUser, help='cutoff time per target algorithm run in seconds')
	parser.add_argument('--budget-per-run', type=int, default=sgh.settings.DEFAULT_config_budget_per_run, action=ac.SetByUser, help='configuration budget per configurator run in seconds')
	parser.add_argument('--number-of-runs', type=int, default=sgh.settings.DEFAULT_config_number_of_runs, action=ac.SetByUser, help='number of configuration runs to execute')
	parser.add_argument('--settings-file', type=Path, default=sgh.settings.DEFAULT_settings_path, action=ac.SetByUser, help='specify the settings file to use in case you want to use one other than the default')

	# Process command line arguments
	args = parser.parse_args()
	solver = args.solver
	instance_set = args.instance_set_train

	args.performance_measure = PerformanceMeasure.from_str(args.performance_measure)
	sgh.settings.set_general_performance_measure(args.performance_measure, ac.user_set_state(args, 'performance_measure'))
	sgh.settings.set_config_target_cutoff_time(args.target_cutoff_time, ac.user_set_state(args, 'target_cutoff_time'))
	sgh.settings.set_config_budget_per_run(args.budget_per_run, ac.user_set_state(args, 'budget_per_run'))
	sgh.settings.set_config_number_of_runs(args.number_of_runs, ac.user_set_state(args, 'number_of_runs'))
	if ac.user_set_bool(args, 'settings_file'): sgh.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)

	solver_name = sfh.get_last_level_directory_name(solver)
	instance_set_name = sfh.get_last_level_directory_name(instance_set)

	# Copy instances to smac directory
	instances_directory = r'Instances/' + instance_set_name
	list_all_path = satih.get_list_all_path(instances_directory)
	inst_dir_prefix = instances_directory
	smac_inst_dir_prefix = sgh.smac_dir + r'/' + 'example_scenarios/' + r'instances/' + sfh.get_last_level_directory_name(instances_directory)
	satih.copy_instances_to_smac(list_all_path, inst_dir_prefix, smac_inst_dir_prefix, r'train')

	scsh.handle_file_instance_train(solver_name, instance_set_name)
	scsh.create_file_scenario_configuration(solver_name, instance_set_name)
	scsh.prepare_smac_execution_directories_configuration(solver_name)
	smac_configure_sbatch_script_name = scsh.create_smac_configure_sbatch_script(solver_name, instance_set_name)
	configure_jobid = scsh.submit_smac_configure_sbatch_script(smac_configure_sbatch_script_name)

	print("c Running configuration in parallel. Waiting for Slurm job with id:")
	print(configure_jobid)

	# Write most recent run to file
	last_configuration_file_path = sgh.smac_dir + '/example_scenarios/' + solver_name + '/' + sgh.sparkle_last_configuration_file_name

	fout = open(last_configuration_file_path, 'w+')
	fout.write('solver ' + str(solver) + '\n')
	fout.write('train ' + str(instance_set) + '\n')
	fout.close()

	# Write used settings to file
	sgh.settings.write_settings_ini()

