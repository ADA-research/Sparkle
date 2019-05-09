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
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_compute_features_help as scf
from sparkle_help import sparkle_compute_features_parallel_help as scfp
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_experiments_related_help

if __name__ == r'__main__':

	
	my_flag_run_extractor_later = False
	my_flag_nickname = False
	my_flag_parallel = False
	nickname_str = r''
	extractor_source = r''

	len_argv = len(sys.argv)
	i = 1
	while i<len_argv:
		if sys.argv[i] == r'-run-extractor-later':
			my_flag_run_extractor_later = True
		elif sys.argv[i] == r'-nickname':
			my_flag_nickname = True
			i += 1
			nickname_str = sys.argv[i]
		elif sys.argv[i] == r'-parallel':
			my_flag_parallel = True
		else:
			extractor_source = sys.argv[i]
		i += 1

	if not os.path.exists(extractor_source):
		print r'c Feature extractor path ' + "\'" + extractor_source + "\'" + r' does not exist!'
		print r'c Usage: ' + sys.argv[0] + r' [-run-extractor-later] [-nickname] [<nickname>] [-parallel] <feature_extractor_source_directory>'
		sys.exit()

	last_level_directory = r''
	last_level_directory = sfh.get_last_level_directory_name(extractor_source)

	extractor_diretory = r'Extractors/' + last_level_directory
	if not os.path.exists(extractor_diretory): os.mkdir(extractor_diretory)
	else:
		print r'c Feature extractor ' + sfh.get_last_level_directory_name(extractor_diretory) + r' already exists!'
		print r'c Do not add feature extractor ' + sfh.get_last_level_directory_name(extractor_diretory)
		sys.exit()

	os.system(r'cp -r ' + extractor_source + r'/* ' + extractor_diretory)

	sparkle_global_help.extractor_list.append(extractor_diretory)
	sfh.add_new_extractor_into_file(extractor_diretory)
	
	##pre-run the feature extractor on a testing instance, to obtain the feature names
	extractor_path = extractor_diretory
	instance_path = extractor_path + r'/' + r'sparkle_test_instance.cnf'
	result_path = r'TMP/' + sfh.get_last_level_directory_name(extractor_path) + r'_' + sfh.get_last_level_directory_name(instance_path) + r'_' + sparkle_basic_help.get_time_pid_random_string() + r'.rawres'
	command_line = extractor_path + r'/' + sparkle_global_help.sparkle_run_default_wrapper + r' ' + extractor_path + r'/' + r' ' + instance_path + r' ' + result_path
	os.system(command_line)

	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(sparkle_global_help.feature_data_csv_path)

	tmp_fdcsv = sfdcsv.Sparkle_Feature_Data_CSV(result_path)
	list_columns = tmp_fdcsv.list_columns()
	for column_name in list_columns:
		feature_data_csv.add_column(column_name)

	feature_data_csv.update_csv()
	
	sparkle_global_help.extractor_feature_vector_size_mapping[extractor_diretory] = len(list_columns)
	sfh.add_new_extractor_feature_vector_size_into_file(extractor_diretory, len(list_columns))

	command_line = r'rm -f ' + result_path
	os.system(command_line)
	
	print 'c Adding feature extractor ' + sfh.get_last_level_directory_name(extractor_diretory) + ' done!'

	if os.path.exists(sparkle_global_help.sparkle_portfolio_selector_path):
		command_line = r'rm -f ' + sparkle_global_help.sparkle_portfolio_selector_path
		os.system(command_line)
		print 'c Removing Sparkle portfolio selector ' + sparkle_global_help.sparkle_portfolio_selector_path + ' done!'

	if os.path.exists(sparkle_global_help.sparkle_report_path):
		command_line = r'rm -f ' + sparkle_global_help.sparkle_report_path
		os.system(command_line)
		print 'c Removing Sparkle report ' + sparkle_global_help.sparkle_report_path + ' done!'

	if my_flag_nickname:
		sparkle_global_help.extractor_nickname_mapping[nickname_str] = extractor_diretory
		sfh.add_new_extractor_nickname_into_file(nickname_str, extractor_diretory)
		pass

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


