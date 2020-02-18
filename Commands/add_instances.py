#!/usr/bin/env python2.7
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
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_compute_features_help as scf
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_compute_features_parallel_help as scfp
from sparkle_help import sparkle_run_solvers_parallel_help as srsp
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_experiments_related_help
from sparkle_help import sparkle_add_train_instances_help as satih

if __name__ == r'__main__':


	my_flag_run_extractor_later = False
	my_flag_run_solver_later = False
	my_flag_nickname = False
	my_flag_parallel = False
	nickname_str = r''
	instances_source = r''

	# Process input options
	len_argv = len(sys.argv)
	i = 1
	while i<len_argv:
		if sys.argv[i] == r'-run-extractor-later':
			my_flag_run_extractor_later = True
		elif sys.argv[i] == r'-run-solver-later':
			my_flag_run_solver_later = True
		elif sys.argv[i] == r'-nickname':
			my_flag_nickname = True
			i += 1
			nickname_str = sys.argv[i]
		elif sys.argv[i] == r'-parallel':
			my_flag_parallel = True
		else:
			instances_source = sys.argv[i]
		i += 1

	# Verify path validity for the provided instance directory
	if not os.path.exists(instances_source):
		print r'c Instances path ' + "\'" + instances_source + "\'" + r' does not exist!'
		print r'c Usage: ' + sys.argv[0] + r' [-run-extractor-later] [-run-solver-later] [-nickname <nickname>] [-parallel] <instances_source_directory>'
		sys.exit()

	print 'c Start adding all instances in directory ' + instances_source + r' ...' 

	last_level_directory = r''
	if my_flag_nickname: last_level_directory = nickname_str
	else: last_level_directory = sfh.get_last_level_directory_name(instances_source)

	instances_directory = r'Instances/' + last_level_directory
	if not os.path.exists(instances_directory): os.mkdir(instances_directory)

	#os.system(r'cp ' + instances_source + r'/*.cnf ' + instances_directory)
	list_source_all_filename = sfh.get_list_all_filename(instances_source)
	list_target_all_filename = sfh.get_list_all_filename(instances_directory)

	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(sparkle_global_help.feature_data_csv_path)
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)

	num_inst = len(list_source_all_filename)
	
	print 'c The number of intended adding instances: ' + str(num_inst)

	for i in range(0, len(list_source_all_filename)):
		intended_filename = list_source_all_filename[i]
		print r'c'
		print r'c Adding ' + intended_filename + r' ...'
		print 'c Executing Progress: ' + str(i+1) + ' out of ' + str(num_inst)
		
		if intended_filename in list_target_all_filename:
			print r'c Instance ' + sfh.get_last_level_directory_name(intended_filename) + r' already exists in Directory ' + instances_directory
			print r'c Ignore adding file ' + sfh.get_last_level_directory_name(intended_filename)
			#continue
		else:
			intended_filename_path = instances_directory + r'/' + intended_filename
			intended_status = r'UNKNOWN'
			sparkle_global_help.instance_list.append(intended_filename_path)
			sparkle_global_help.instance_reference_mapping[intended_filename_path] = intended_status
			sfh.add_new_instance_into_file(intended_filename_path)
			sfh.add_new_instance_reference_into_file(intended_filename_path, intended_status)
			feature_data_csv.add_row(intended_filename_path)
			performance_data_csv.add_row(intended_filename_path)
			
			if instances_source[-1] == r'/': instances_source = instances_source[:-1]
			os.system(r'cp ' + instances_source + r'/' + intended_filename + r' ' + instances_directory)
			print r'c Instance ' + sfh.get_last_level_directory_name(intended_filename) + r' has been added!'
			print r'c'

#	print('c Selecting training instances ...')
#	list_cnf_path = satih.get_list_cnf_path(instances_directory)
#	list_train_cnf_index = satih.get_list_train_cnf_index(list_cnf_path)
#	cnf_dir_prefix = instances_directory
#	smac_cnf_dir_prefix = sparkle_global_help.smac_dir + r'/' + 'example_scenarios/' + r'instances/' + sfh.get_last_level_directory_name(instances_directory)
#	satih.selecting_train_cnf(list_cnf_path, list_train_cnf_index, cnf_dir_prefix, smac_cnf_dir_prefix)
#	list_train_cnf_path = satih.get_list_cnf_path(smac_cnf_dir_prefix)
#	file_train_cnf = sparkle_global_help.smac_dir + r'/' + 'example_scenarios/' + r'instances/' + sfh.get_last_level_directory_name(instances_directory) + r'_train.txt'
#	
#	fout = open(file_train_cnf, 'w+')
#	for path in list_train_cnf_path:
#		fout.write(path.replace(smac_cnf_dir_prefix, '../instances/' + sfh.get_last_level_directory_name(instances_directory), 1) + '\n')
#		#print(path.replace(smac_cnf_dir_prefix, '../instances/' + sfh.get_last_level_directory_name(instances_directory), 1))
#		#print(path, smac_cnf_dir_prefix)
#	fout.close()
#	print('c Selecting training instances done!')
#	
#	print('c Selecting testing instances ...')
#	list_cnf_path = satih.get_list_cnf_path(instances_directory)
#	list_test_cnf_index = satih.get_list_test_cnf_index(list_cnf_path, list_train_cnf_index)
#	cnf_dir_prefix = instances_directory
#	smac_cnf_dir_prefix_test = sparkle_global_help.smac_dir + r'/' + 'example_scenarios/' + r'instances_test/' + sfh.get_last_level_directory_name(instances_directory)
#	satih.selecting_test_cnf(list_cnf_path, list_test_cnf_index, cnf_dir_prefix, smac_cnf_dir_prefix_test)
#	list_test_cnf_path = satih.get_list_cnf_path(smac_cnf_dir_prefix_test)
#	file_test_cnf = sparkle_global_help.smac_dir + r'/' + 'example_scenarios/' + r'instances_test/' + sfh.get_last_level_directory_name(instances_directory) + r'_test.txt'
#	
#	fout = open(file_test_cnf, 'w+')
#	for path in list_test_cnf_path:
#		fout.write(path.replace(smac_cnf_dir_prefix_test, '../instances_test/' + sfh.get_last_level_directory_name(instances_directory), 1) + '\n')
#	fout.close()
#	print('c Selecting testing instances done!')

	feature_data_csv.update_csv()
	performance_data_csv.update_csv()
	
	print 'c Adding instances ' + sfh.get_last_level_directory_name(instances_directory) + ' done!'

	if os.path.exists(sparkle_global_help.sparkle_portfolio_selector_path):
		command_line = r'rm -f ' + sparkle_global_help.sparkle_portfolio_selector_path
		os.system(command_line)
		print 'c Removing Sparkle portfolio selector ' + sparkle_global_help.sparkle_portfolio_selector_path + ' done!'
	
	if os.path.exists(sparkle_global_help.sparkle_report_path):
		command_line = r'rm -f ' + sparkle_global_help.sparkle_report_path
		os.system(command_line)
		print 'c Removing Sparkle report ' + sparkle_global_help.sparkle_report_path + ' done!'
	
	if not my_flag_run_extractor_later:
		if not my_flag_parallel:
			print 'c Start computing features ...'
			scf.computing_features(sparkle_global_help.feature_data_csv_path, 1)
			print 'c Feature data file ' + sparkle_global_help.feature_data_csv_path + ' has been updated!'
			print 'c Computing features done!'
		else:
			num_job_in_parallel = sparkle_experiments_related_help.num_job_in_parallel
			scfp.computing_features_parallel(sparkle_global_help.feature_data_csv_path, num_job_in_parallel, 1)
			print 'c Computing features in parallel ...'

	if not my_flag_run_solver_later:
		if not my_flag_parallel:
			print 'c Start running solvers ...'
			srs.running_solvers(sparkle_global_help.performance_data_csv_path, 1)
			print 'c Performance data file ' + sparkle_global_help.performance_data_csv_path + ' has been updated!'
			print 'c Running solvers done!'
		else:
			num_job_in_parallel = sparkle_experiments_related_help.num_job_in_parallel
			srsp.running_solvers_parallel(sparkle_global_help.performance_data_csv_path, num_job_in_parallel, 1)
			print 'c Running solvers in parallel ...'
			

