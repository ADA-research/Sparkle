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


if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	parser = argparse.ArgumentParser()
	parser.add_argument('--solver', required=True, type=str, help='path to solver')
	parser.add_argument('--instance-set-train', required=True, type=str, help='path to training instance set')
	parser.add_argument('--instance-set-test', required=False, type=str, help='path to testing instance set')
	args = parser.parse_args()
	solver = args.solver
	instance_set_train = args.instance_set_train
	instance_set_test = args.instance_set_test

	solver_name = sfh.get_last_level_directory_name(solver)
	instance_set_train_name = sfh.get_last_level_directory_name(instance_set_train)
	instance_set_test_name = None

	# Make sure configuration results exist before trying to work with them
	if not scsh.check_configuration_exists(solver_name, instance_set_train_name):
		print('c Error: No configuration results found for the given solver and training instance set.')
		sys.exit(-1)

	# Record optimised configuration
	scsh.write_optimised_configuration(solver_name, instance_set_train_name)

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
	#ori_path = os.getcwd()
	#command = 'cd ' + sgh.smac_dir + ' ; sbatch ' + sbatch_script_name + ' ; cd ' + ori_path
	#os.system(r'chmod a+x ' + sbatch_script_path)
	#os.system(command)

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

