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
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_compute_features_help as scf
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_compute_features_parallel_help as scfp
from sparkle_help import sparkle_run_solvers_parallel_help as srsp
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings


def _check_existence_of_instance_list_file(instances_source: str):
	if not os.path.isdir(instances_source):
		return False

	instance_list_file_name = 'sparkle_instance_list.txt'
	instance_list_file_path = os.path.join(instances_source, instance_list_file_name)

	if os.path.isfile(instance_list_file_path):
		return True
	else:
		return False


def _get_list_instance(instances_source: str):
	list_instance = []
	instance_list_file_name = 'sparkle_instance_list.txt'
	instance_list_file_path = os.path.join(instances_source, instance_list_file_name)
	infile = open(instance_list_file_path)
	lines = infile.readlines()
	for line in lines:
		words = line.strip().split()
		if len(words) <= 0:
			continue
		list_instance.append(line.strip())
	infile.close()

	return list_instance


if __name__ == r'__main__':
	# Initialise settings
	global settings
	sgh.settings = sparkle_settings.Settings()

	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('instances_path', metavar='instances-path', type=str, help='path to the instance set')
	parser.add_argument('--run-extractor-later', action='store_true', help='do not immediately run the feature extractor on the newly added instances')
	parser.add_argument('--run-solver-later', action='store_true', help='do not immediately run the solver(s) on the newly added instances')
	parser.add_argument('--nickname', type=str, help='set a nickname for the instance set')
	parser.add_argument('--parallel', action='store_true', help='run the solvers and feature extractor on multiple instances in parallel')

	# Process command line arguments
	args = parser.parse_args()
	instances_source = args.instances_path
	if not os.path.exists(instances_source):
		print(r'c Instance set path ' + "\'" + instances_source + "\'" + r' does not exist!')
		sys.exit()

	my_flag_run_extractor_later = args.run_extractor_later
	my_flag_run_solver_later = args.run_solver_later
	nickname_str = args.nickname
	my_flag_parallel = args.parallel

	print('c Start adding all instances in directory ' + instances_source + r' ...')

	last_level_directory = r''
	if nickname_str is not None:
		last_level_directory = nickname_str
	else:
		last_level_directory = sfh.get_last_level_directory_name(instances_source)

	instances_directory = r'Instances/' + last_level_directory
	if not os.path.exists(instances_directory): os.mkdir(instances_directory)

	if _check_existence_of_instance_list_file(instances_source):
		list_instance = _get_list_instance(instances_source)

		feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(sgh.feature_data_csv_path)
		performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sgh.performance_data_csv_path)

		num_inst = len(list_instance)
		print('c The number of intended adding instances: ' + str(num_inst))

		for i in range(0, num_inst):
			instance_line = list_instance[i]
			instance_related_files = instance_line.strip().split()
			intended_instance_line = ''

			for related_file_name in instance_related_files:
				source_file_path = os.path.join(instances_source, related_file_name)
				target_file_path = os.path.join(instances_directory, related_file_name)
				cmd = 'cp %s %s' % (source_file_path, target_file_path)
				os.system(cmd)
				intended_instance_line += target_file_path + ' '
			
			intended_instance_line = intended_instance_line.strip()
			intended_status = r'UNKNOWN'
			
			sgh.instance_list.append(intended_instance_line)
			sgh.instance_reference_mapping[intended_instance_line] = intended_status
			sfh.add_new_instance_into_file(intended_instance_line)
			sfh.add_new_instance_reference_into_file(intended_instance_line, intended_status)
			feature_data_csv.add_row(intended_instance_line)
			performance_data_csv.add_row(intended_instance_line)
			
			print(r'c Instance ' + instance_line + r' has been added!')
			print(r'c')
		
		feature_data_csv.update_csv()
		performance_data_csv.update_csv()
	else:
		#os.system(r'cp ' + instances_source + r'/*.cnf ' + instances_directory)
		list_source_all_filename = sfh.get_list_all_filename(instances_source)
		list_source_all_directory = sfh.get_list_all_directory(instances_source)
		list_target_all_filename = sfh.get_list_all_filename(instances_directory)

		feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(sgh.feature_data_csv_path)
		performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sgh.performance_data_csv_path)

		num_inst = len(list_source_all_filename)
		
		print('c The number of intended adding instances: ' + str(num_inst))

		for i in range(0, len(list_source_all_filename)):
			intended_filename = list_source_all_filename[i]
			print(r'c')
			print(r'c Adding ' + intended_filename + r' ...')
			print('c Executing Progress: ' + str(i+1) + ' out of ' + str(num_inst))
			
			if intended_filename in list_target_all_filename:
				print(r'c Instance ' + sfh.get_last_level_directory_name(intended_filename) + r' already exists in Directory ' + instances_directory)
				print(r'c Ignore adding file ' + sfh.get_last_level_directory_name(intended_filename))
				#continue
			else:
				intended_filename_path = instances_directory + r'/' + intended_filename
				intended_status = r'UNKNOWN'
				sgh.instance_list.append(intended_filename_path)
				sgh.instance_reference_mapping[intended_filename_path] = intended_status
				sfh.add_new_instance_into_file(intended_filename_path)
				sfh.add_new_instance_reference_into_file(intended_filename_path, intended_status)
				feature_data_csv.add_row(intended_filename_path)
				performance_data_csv.add_row(intended_filename_path)
				
				if list_source_all_directory[i][-1] == r'/': list_source_all_directory[i] = list_source_all_directory[i][:-1]
				os.system(r'cp ' + list_source_all_directory[i] + r'/' + intended_filename + r' ' + instances_directory)
				print(r'c Instance ' + sfh.get_last_level_directory_name(intended_filename) + r' has been added!')
				print(r'c')

		feature_data_csv.update_csv()
		performance_data_csv.update_csv()
	
	print('c Adding instances ' + sfh.get_last_level_directory_name(instances_directory) + ' done!')

	if os.path.exists(sgh.sparkle_portfolio_selector_path):
		command_line = r'rm -f ' + sgh.sparkle_portfolio_selector_path
		os.system(command_line)
		print('c Removing Sparkle portfolio selector ' + sgh.sparkle_portfolio_selector_path + ' done!')
	
	if os.path.exists(sgh.sparkle_report_path):
		command_line = r'rm -f ' + sgh.sparkle_report_path
		os.system(command_line)
		print('c Removing Sparkle report ' + sgh.sparkle_report_path + ' done!')
	
	if not my_flag_run_extractor_later:
		if not my_flag_parallel:
			print('c Start computing features ...')
			scf.computing_features(sgh.feature_data_csv_path, 1)
			print('c Feature data file ' + sgh.feature_data_csv_path + ' has been updated!')
			print('c Computing features done!')
		else:
			num_job_in_parallel = sgh.settings.get_slurm_number_of_runs_in_parallel()
			scfp.computing_features_parallel(sgh.feature_data_csv_path, num_job_in_parallel, 1)
			print('c Computing features in parallel ...')

	if not my_flag_run_solver_later:
		if not my_flag_parallel:
			print('c Start running solvers ...')
			srs.running_solvers(sgh.performance_data_csv_path, 1)
			print('c Performance data file ' + sgh.performance_data_csv_path + ' has been updated!')
			print('c Running solvers done!')
		else:
			num_job_in_parallel = sgh.settings.get_slurm_number_of_runs_in_parallel()
			srsp.running_solvers_parallel(sgh.performance_data_csv_path, num_job_in_parallel, 1)
			print('c Running solvers in parallel ...')

