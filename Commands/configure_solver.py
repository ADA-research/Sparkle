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
import os
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_configure_solver_help as scsh
from sparkle_help import sparkle_add_train_instances_help as satih
from sparkle_help import sparkle_logging as sl

from sparkle_help import sparkle_slurm_help as ssh
#from validate_configured_vs_default import validate_configured_vs_default

if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	parser = argparse.ArgumentParser()
	parser.add_argument('--validate', required=False, action="store_true", help='validate after configuration')
	parser.add_argument('--ablation', required=False, action="store_true", help='run ablation after configuration')
	parser.add_argument('--solver', required=True, type=str, help='path to solver')
	parser.add_argument('--instance-set-train', required=True, type=str, help='path to training instance set')
	parser.add_argument('--instance-set-test', required=False, type=str, help='path to testing instance set (only for validating)')
	args = parser.parse_args()

	validate = args.validate
	solver = args.solver
	instance_set_train = args.instance_set_train
	instance_set_test = args.instance_set_test

	solver_name = sfh.get_last_level_directory_name(solver)
	instance_set_train_name = sfh.get_last_level_directory_name(instance_set_train)
	instance_set_test_name = None
	if instance_set_test is not None:
		instance_set_test_name = sfh.get_last_level_directory_name(instance_set_test)


	# Copy instances to smac directory
	instances_directory = r'Instances/' + instance_set_train_name
	list_all_path = satih.get_list_all_path(instances_directory)
	inst_dir_prefix = instances_directory
	smac_inst_dir_prefix = sgh.smac_dir + r'/' + 'example_scenarios/' + r'instances/' + sfh.get_last_level_directory_name(instances_directory)
	satih.copy_instances_to_smac(list_all_path, inst_dir_prefix, smac_inst_dir_prefix, r'train')

	scsh.handle_file_instance_train(solver_name, instance_set_train_name)
	scsh.create_file_scenario_configuration(solver_name, instance_set_train_name)
	scsh.prepare_smac_execution_directories_configuration(solver_name)
	smac_configure_sbatch_script_name = scsh.create_smac_configure_sbatch_script(solver_name, instance_set_train_name)
	configure_jobid = scsh.submit_smac_configure_sbatch_script(smac_configure_sbatch_script_name)

	print("c Running configuration in parallel. Waiting for Slurm job with id: {}".format(configure_jobid))

	# Write most recent run to file
	last_configuration_file_path = sgh.smac_dir + '/example_scenarios/' + solver_name + '/' + sgh.sparkle_last_configuration_file_name

	fout = open(last_configuration_file_path, 'w+')
	fout.write('solver ' + str(solver) + '\n')
	fout.write('train ' + str(instance_set_train) + '\n')
	fout.close()

	# Set validation to wait until configuration is done
	if(validate):
		scsh.generate_validation_callback_slurm_script(solver, instance_set_train, instance_set_test, configure_jobid)

	if(ablation):
		scsh.generate_ablation_callback_slurm_script(solver, instance_set_train, instance_set_test, configure_jobid)