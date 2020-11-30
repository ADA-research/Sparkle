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
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_configure_solver_help as scsh
from sparkle_help import sparkle_add_train_instances_help as satih
from sparkle_help import sparkle_logging as sl
from sparkle_help.sparkle_settings import PerformanceMeasure
from sparkle_help.sparkle_settings import SettingState


if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	parser = argparse.ArgumentParser()
	parser.add_argument('--solver', required=True, type=str, help='path to solver')
	parser.add_argument('--instance-set-train', required=True, type=str, help='path to training instance set')
	parser.add_argument('--performance-measure', choices=PerformanceMeasure.__members__, default=PerformanceMeasure.RUNTIME, help='the performance measure, e.g. runtime')
	parser.add_argument('--cutoff-time', type=int, help='cutoff time per target algorithm run in seconds')
	parser.add_argument('--budget-per-run', type=int, help='configuration budget per configurator run in seconds')
	parser.add_argument('--number-of-runs', type=int, help='number of configuration runs to execute')

	# Process command line arguments
	args = parser.parse_args()
	solver = args.solver
	instance_set = args.instance_set_train
	args.performance_measure = PerformanceMeasure.from_str(args.performance_measure)
	sgh.settings.set_performance_measure(args.performance_measure, SettingState.CMD_LINE)
	sgh.settings.set_config_target_cutoff_time(args.cutoff_time, SettingState.CMD_LINE)
	sgh.settings.set_config_budget_per_run(args.budget_per_run, SettingState.CMD_LINE)
	sgh.settings.set_config_number_of_runs(args.number_of_runs, SettingState.CMD_LINE)

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

