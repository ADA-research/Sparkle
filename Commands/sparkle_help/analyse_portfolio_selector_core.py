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
import sparkle_basic_help
import sparkle_file_help as sfh
import sparkle_construct_portfolio_selector_help as scps
import sparkle_feature_data_csv_help as sfdcsv
import sparkle_performance_data_csv_help as spdcsv
import sparkle_compute_marginal_contribution_help

def generate_task_run_status(excluded_solver=''):
	if excluded_solver == '':
		key_str = 'analyse_sparkle_portfolio_selector'
	else:
		key_str = 'analyse_sparkle_portfolio_selector' + '_' + sfh.get_last_level_directory_name(excluded_solver)
	task_run_status_path = r'TMP/SBATCH_Report_Jobs/' + key_str + r'.statusinfo'
	status_info_str = 'Status: Running\n'
	sfh.write_string_to_file(task_run_status_path, status_info_str)
	return

def delete_task_run_status(excluded_solver=''):
	if excluded_solver == '':
		key_str = 'analyse_sparkle_portfolio_selector'
	else:
		key_str = 'analyse_sparkle_portfolio_selector' + '_' + sfh.get_last_level_directory_name(excluded_solver)
	task_run_status_path = r'TMP/SBATCH_Report_Jobs/' + key_str + r'.statusinfo'
	os.system(r'rm -rf ' + task_run_status_path)
	return

def get_dict_sparkle_portfolio_selector_penalty_time_on_each_instance(portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, par_num, excluded_solver=''):
	mydict = {}
	if excluded_solver == '':
		performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	else:
		portfolio_selector_path = portfolio_selector_path + '_excluding_' + sfh.get_last_level_directory_name(excluded_solver)
		performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
		performance_data_csv.delete_column(excluded_solver)
	
	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
	penalty_time_each_run = cutoff_time_each_run * par_num
	
	for instance in performance_data_csv.list_rows():
		list_predict_schedule = sparkle_compute_marginal_contribution_help.get_list_predict_schedule(portfolio_selector_path, feature_data_csv, instance)
		used_time_for_this_instance = 0
		flag_successfully_solving = False
		for i in range(0, len(list_predict_schedule)):
			if used_time_for_this_instance >= cutoff_time_each_run:
				flag_successfully_solving = False
				break
			solver = list_predict_schedule[i][0]
			scheduled_cutoff_time_this_run = list_predict_schedule[i][1]
			required_time_this_run = performance_data_csv.get_value(instance, solver)
			if required_time_this_run <= scheduled_cutoff_time_this_run:
				used_time_for_this_instance = used_time_for_this_instance + required_time_this_run
				if used_time_for_this_instance > cutoff_time_each_run:
					flag_successfully_solving = False
				else: flag_successfully_solving = True
				break
			else:
				used_time_for_this_instance = used_time_for_this_instance + scheduled_cutoff_time_this_run
				continue
		if flag_successfully_solving:
			mydict[instance] = used_time_for_this_instance
		else:
			mydict[instance] = penalty_time_each_run
	return mydict

def to_file_dict_sparkle_portfolio_selector_penalty_time_on_each_instance(dict_sparkle_portfolio_selector_penalty_time_on_each_instance, portfolio_selector_penalty_time_on_each_instance_path):
	fout = open(portfolio_selector_penalty_time_on_each_instance_path, 'w+')
	for instance in dict_sparkle_portfolio_selector_penalty_time_on_each_instance:
		fout.write('%s %f\n' % (instance, dict_sparkle_portfolio_selector_penalty_time_on_each_instance[instance]))
	fout.close()
	return

if __name__ == '__main__':
	excluded_solver = ''
	if len(sys.argv) >=6:
		portfolio_selector_path = sys.argv[1]
		performance_data_csv_path = sys.argv[2]
		feature_data_csv_path = sys.argv[3]
		cutoff_time_each_run = int(sys.argv[4])
		par_num = int(sys.argv[5])
		if len(sys.argv) >=7:
			excluded_solver = sys.argv[6]
			if len(excluded_solver) >=1 and excluded_solver[-1] == '/':
				excluded_solver = excluded_solver[:-1]
	else:
		print('c Arguments Error!')
		sys.exit(-1)
	
	generate_task_run_status(excluded_solver)	
	
	dict_sparkle_portfolio_selector_penalty_time_on_each_instance = get_dict_sparkle_portfolio_selector_penalty_time_on_each_instance(portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, par_num, excluded_solver)
	
	if excluded_solver == '':
		portfolio_selector_penalty_time_on_each_instance_path = portfolio_selector_path + '_penalty_time_on_each_instance.txt'
	else:
		portfolio_selector_penalty_time_on_each_instance_path = portfolio_selector_path + '_excluding_' + sfh.get_last_level_directory_name(excluded_solver) + '_penalty_time_on_each_instance.txt'
	
	to_file_dict_sparkle_portfolio_selector_penalty_time_on_each_instance(dict_sparkle_portfolio_selector_penalty_time_on_each_instance, portfolio_selector_penalty_time_on_each_instance_path)
	
	delete_task_run_status(excluded_solver)


