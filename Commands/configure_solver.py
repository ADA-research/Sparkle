#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import argparse
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_configure_solver_help as scsh
from sparkle_help import sparkle_add_train_instances_help as satih


if __name__ == r'__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--solver', required=True, type=str, help='path to solver')
	parser.add_argument('--instance-set-train', required=True, type=str, help='path to training instance set')
	args = parser.parse_args()
	solver = args.solver
	instance_set = args.instance_set_train

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
	scsh.submit_smac_configure_sbatch_script(smac_configure_sbatch_script_name)

	# Write most recent run to file
	last_configuration_file_path = sgh.smac_dir + '/example_scenarios/' + solver_name + '/' + sgh.sparkle_last_configuration_file_name

	fout = open(last_configuration_file_path, 'w+')
	fout.write('solver ' + str(solver) + '\n')
	fout.write('train ' + str(instance_set) + '\n')
	fout.close()

