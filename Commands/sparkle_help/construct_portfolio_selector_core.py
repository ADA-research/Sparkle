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
		key_str = 'construct_sparkle_portfolio_selector'
	else:
		key_str = 'construct_sparkle_portfolio_selector' + '_' + sfh.get_last_level_directory_name(excluded_solver)
	task_run_status_path = r'TMP/SBATCH_Portfolio_Jobs/' + key_str + r'.statusinfo'
	status_info_str = 'Status: Running\n'
	sfh.write_string_to_file(task_run_status_path, status_info_str)
	return

def delete_task_run_status(excluded_solver=''):
	if excluded_solver == '':
		key_str = 'construct_sparkle_portfolio_selector'
	else:
		key_str = 'construct_sparkle_portfolio_selector' + '_' + sfh.get_last_level_directory_name(excluded_solver)
	task_run_status_path = r'TMP/SBATCH_Portfolio_Jobs/' + key_str + r'.statusinfo'
	os.system(r'rm -rf ' + task_run_status_path)
	return

def generate_file_predict_schedule_for_each_instance(portfolio_selector_path, feature_data_csv_path, file_predict_schedule_path):
	autofolio_predict_features_for_csv_path = 'Components/AutoFolio-master_predict_features_for_csv/scripts/autofolio'
	command_line = 'python3 %s --load %s --feature_csv %s > %s' % (autofolio_predict_features_for_csv_path, portfolio_selector_path, feature_data_csv_path, file_predict_schedule_path)
	os.system(command_line)
	return

def get_dict_predict_schedule_for_each_instance(file_predict_schedule_path):
	dict_predict_schedule_for_each_instance = {}
	fin = open(file_predict_schedule_path, 'r')
	while True:
		myline = fin.readline()
		if not myline: break
		instance = myline.strip()
		
		myline = fin.readline()
		if not myline: break
		list_predict_schedule = eval(myline.strip())
		
		dict_predict_schedule_for_each_instance[instance] = list_predict_schedule
	fin.close()
	return dict_predict_schedule_for_each_instance

def get_dict_sparkle_portfolio_selector_penalty_time_on_each_instance(portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, par_num):
	mydict = {}
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
	penalty_time_each_run = cutoff_time_each_run * par_num
	
	## generate_file_predict_schedule_for_each_instance
	file_predict_schedule_path = portfolio_selector_path + '_predict_schedule_for_each_instance.txt'
	generate_file_predict_schedule_for_each_instance(portfolio_selector_path, feature_data_csv_path, file_predict_schedule_path)
	dict_predict_schedule_for_each_instance = get_dict_predict_schedule_for_each_instance(file_predict_schedule_path)
	
	for instance in performance_data_csv.list_rows():
		#list_predict_schedule = sparkle_compute_marginal_contribution_help.get_list_predict_schedule(portfolio_selector_path, feature_data_csv, instance)
		list_predict_schedule = dict_predict_schedule_for_each_instance[instance]
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
	
	os.system('rm -f %s' % (file_predict_schedule_path))
	
	return mydict

def to_file_dict_sparkle_portfolio_selector_penalty_time_on_each_instance(dict_sparkle_portfolio_selector_penalty_time_on_each_instance, portfolio_selector_penalty_time_on_each_instance_path): #directly copy from analyse_portfolio_selector_core.py
	fout = open(portfolio_selector_penalty_time_on_each_instance_path, 'w+')
	for instance in dict_sparkle_portfolio_selector_penalty_time_on_each_instance:
		fout.write('%s %f\n' % (instance, dict_sparkle_portfolio_selector_penalty_time_on_each_instance[instance]))
	fout.close()
	return

def calc_par2_value_for_dict(mydict, cutoff_time_each_run, par_num):
	par2_value_sum = 0
	instance_count = 0
	par2_value_average = 0
	penalty_time_each_run = cutoff_time_each_run * par_num
	
	for instance in mydict:
		runtime = float(mydict[instance])
		if runtime <= cutoff_time_each_run:
			par2_value_sum += runtime
		else:
			par2_value_sum += penalty_time_each_run
		instance_count += 1
	
	try:
		par2_value_average = par2_value_sum / instance_count
	except:
		par2_value_average = 0
	
	return par2_value_average

def construct_sparkle_portfolio_selector_with_all_solvers(portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, par_num, round_count=1):
	best_par2_value = -1
	portfolio_selector_penalty_time_on_each_instance_path = portfolio_selector_path + '_penalty_time_on_each_instance.txt'
	
	for i in range(0, round_count):
		bool_updated = False
		tmp_portfolio_selector_path = portfolio_selector_path + '_' + str(i)
		scps.construct_sparkle_portfolio_selector(tmp_portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run)
		tmp_dict = get_dict_sparkle_portfolio_selector_penalty_time_on_each_instance(tmp_portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, par_num)
		tmp_par2_value = calc_par2_value_for_dict(tmp_dict, cutoff_time_each_run, par_num)
		
		print('c %s %f' % (tmp_portfolio_selector_path, tmp_par2_value))
		
		if best_par2_value < 0 or tmp_par2_value < best_par2_value:
			bool_updated = True
			best_par2_value = tmp_par2_value
			os.system('mv %s %s' % (tmp_portfolio_selector_path, portfolio_selector_path))
			to_file_dict_sparkle_portfolio_selector_penalty_time_on_each_instance(tmp_dict, portfolio_selector_penalty_time_on_each_instance_path)
	
		if not bool_updated:
			os.system('rm -f %s' % (tmp_portfolio_selector_path))
		
	return

def construct_sparkle_portfolio_selector_excluding_one_solver(portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, par_num, excluded_solver, round_count=1):
	tmp_performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	tmp_performance_data_csv.delete_column(excluded_solver)
	tmp_performance_data_csv_path = r'TMP/' + r'tmp_performance_data_csv_' + sparkle_basic_help.get_time_pid_random_string() + r'.csv'
	tmp_performance_data_csv.save_csv(tmp_performance_data_csv_path)
	tmp_actual_portfolio_selector_path = portfolio_selector_path + '_excluding_' + sfh.get_last_level_directory_name(excluded_solver)
	tmp_portfolio_selector_penalty_time_on_each_instance_path = portfolio_selector_path + '_excluding_' + sfh.get_last_level_directory_name(excluded_solver) + '_penalty_time_on_each_instance.txt'
	
	if len(tmp_performance_data_csv.list_columns()) >= 1:
		best_par2_value = -1
		for i in range(0, round_count):
			bool_updated = False
			tmp_portfolio_selector_path = tmp_actual_portfolio_selector_path + '_' + str(i)
			scps.construct_sparkle_portfolio_selector(tmp_portfolio_selector_path, tmp_performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run)
			tmp_dict = get_dict_sparkle_portfolio_selector_penalty_time_on_each_instance(tmp_portfolio_selector_path, tmp_performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, par_num)
			tmp_par2_value = calc_par2_value_for_dict(tmp_dict, cutoff_time_each_run, par_num)
			
			print('c %s %f' % (tmp_portfolio_selector_path, tmp_par2_value))
			
			if best_par2_value < 0 or tmp_par2_value < best_par2_value:
				bool_updated = True
				best_par2_value = tmp_par2_value
				os.system('mv %s %s' % (tmp_portfolio_selector_path, tmp_actual_portfolio_selector_path))
				to_file_dict_sparkle_portfolio_selector_penalty_time_on_each_instance(tmp_dict, tmp_portfolio_selector_penalty_time_on_each_instance_path)
			
			if not bool_updated:
				os.system('rm -f %s' % (tmp_portfolio_selector_path))
			
	else:
		print(r'c ****** WARNING: ' + r'No solver exists ! ******')
	
	return


if __name__ == '__main__':
	excluded_solver = ''
	if len(sys.argv) >= 6:
		portfolio_selector_path = sys.argv[1]
		performance_data_csv_path = sys.argv[2]
		feature_data_csv_path = sys.argv[3]
		cutoff_time_each_run = int(sys.argv[4])
		par_num = int(sys.argv[5])
		if len(sys.argv) >= 7:
			excluded_solver = sys.argv[6]
			if len(excluded_solver) >=1 and excluded_solver[-1] == '/':
				excluded_solver = excluded_solver[:-1]
	else:
		print('c Arguments Error!')
		sys.exit(-1)
	
	generate_task_run_status(excluded_solver)	
	
	round_count = 5
	
	if excluded_solver == '':
		construct_sparkle_portfolio_selector_with_all_solvers(portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, par_num, round_count)
	else:
		construct_sparkle_portfolio_selector_excluding_one_solver(portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, par_num, excluded_solver, round_count)
	
	delete_task_run_status(excluded_solver)


