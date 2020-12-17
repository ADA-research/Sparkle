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
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_construct_portfolio_selector_help as scps ##
from sparkle_help import sparkle_run_portfolio_selector_help as srps ##
from sparkle_help import sparkle_logging as sl


def compute_perfect_selector_marginal_contribution(performance_data_csv_path = sgh.performance_data_csv_path):
	cutoff_time_str = str(sgh.settings.get_general_target_cutoff_time())
	print('c In this calculation, cutoff time for each run is ' + cutoff_time_str + ' seconds')
	
	rank_list = []
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	num_instances = performance_data_csv.get_row_size()
	num_solvers = performance_data_csv.get_column_size()
	
	print('c Computing virtual best performance for portfolio selector with all solvers ...')
	virtual_best_performance = performance_data_csv.calc_virtual_best_performance_of_portfolio(num_instances, num_solvers)
	print('c Virtual best performance for portfolio selector with all solvers is ' + str(virtual_best_performance))
	print('c Computing done!')
	
	for solver in performance_data_csv.list_columns():
		print('c Computing virtual best performance for portfolio selector excluding solver ' + sfh.get_last_level_directory_name(solver) + ' ...')
		tmp_performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
		tmp_performance_data_csv.delete_column(solver)
		tmp_virtual_best_performance = tmp_performance_data_csv.calc_virtual_best_performance_of_portfolio(num_instances, num_solvers)
		print('c Virtual best performance for portfolio selector excluding solver ' + sfh.get_last_level_directory_name(solver) + ' is ' + str(tmp_virtual_best_performance))
		print('c Computing done!')
		marginal_contribution = virtual_best_performance - tmp_virtual_best_performance
		solver_tuple = (solver, marginal_contribution)
		rank_list.append(solver_tuple)
		print('c Marginal contribution (to Perfect Selector) for solver ' + sfh.get_last_level_directory_name(solver) + ' is ' + str(marginal_contribution))
		
	rank_list.sort(key=lambda marginal_contribution: marginal_contribution[1], reverse=True)
	return rank_list


def get_list_predict_schedule(actual_portfolio_selector_path, feature_data_csv, instance):
	list_predict_schedule = []
	python_executable = sgh.python_executable
	if not os.path.exists(r'Tmp/'): os.mkdir(r'Tmp/')
	feature_vector_string = feature_data_csv.get_feature_vector_string(instance)
	predict_schedule_result_path = r'Tmp/predict_schedule_' + sparkle_basic_help.get_time_pid_random_string() + r'.predres'
	
	command_line = python_executable + r' ' + sgh.autofolio_path + r' --load ' + actual_portfolio_selector_path + r' --feature_vec' + r' ' + feature_vector_string + r' 1> ' + predict_schedule_result_path + r' 2> ' + sgh.sparkle_err_path
	
	#print 'c ' + command_line
	os.system(command_line)
	
	list_predict_schedule = srps.get_list_predict_schedule_from_file(predict_schedule_result_path)

	#print r'c for solving instance ' + instance + r', ' + r'list_predict_schedule = ' + str(list_predict_schedule)

	# If there is error output log temporary files for analsysis, otherwise remove them
	with open(sgh.sparkle_err_path) as file_content:
		lines = file_content.read().splitlines()
	if len(lines) > 1 or lines[0] != 'INFO:AutoFolio:Predict on Test':
		sl.add_output(predict_schedule_result_path, 'Predicted portfolio schedule')
		sl.add_output(sgh.sparkle_err_path, 'Predicted portfolio schedule error output')
	else:
		os.system(r'rm -f ' + predict_schedule_result_path)
		os.system(r'rm -f ' + sgh.sparkle_err_path)

	return list_predict_schedule


def compute_actual_selector_performance(actual_portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, num_instances, num_solvers):
	cutoff_time = sgh.settings.get_general_target_cutoff_time()
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
	
	actual_selector_performance = 0
	
	for instance in performance_data_csv.list_rows():
		list_predict_schedule = get_list_predict_schedule(actual_portfolio_selector_path, feature_data_csv, instance)
		#print 'c instance = ' + instance + ', schedule: ' + str(list_predict_schedule)
		used_time_for_this_instance = 0
		flag_successfully_solving = False
		for i in range(0, len(list_predict_schedule)):
			if used_time_for_this_instance >= cutoff_time:
				flag_successfully_solving = False
				break
			solver = list_predict_schedule[i][0]
			scheduled_cutoff_time_this_run = list_predict_schedule[i][1]
			required_time_this_run = performance_data_csv.get_value(instance, solver)
			#print 'c required_time_this_run = ' + str(required_time_this_run)
			if required_time_this_run <= scheduled_cutoff_time_this_run:
				used_time_for_this_instance = used_time_for_this_instance + required_time_this_run
				if used_time_for_this_instance > cutoff_time:
					flag_successfully_solving = False
				else: flag_successfully_solving = True
				break
			else:
				used_time_for_this_instance = used_time_for_this_instance + scheduled_cutoff_time_this_run
				continue
		#print 'c instace = ' + instance + ', used_time_for_this_instance =' + str(used_time_for_this_instance) + ', flag_successfully_solving = ' + str(flag_successfully_solving)
		if flag_successfully_solving:
			score_this_instance = 1 + (cutoff_time - used_time_for_this_instance) / (num_instances * cutoff_time * num_solvers + 1)
		else:
			score_this_instance = 0
		#print 'c instance = ' + instance + ', score_this_instance = ' + str(score_this_instance)
		
		actual_selector_performance = actual_selector_performance + score_this_instance
			
	return actual_selector_performance


def compute_actual_selector_marginal_contribution(performance_data_csv_path = sgh.performance_data_csv_path, feature_data_csv_path = sgh.feature_data_csv_path):
	cutoff_time_str = str(sgh.settings.get_general_target_cutoff_time())
	print('c In this calculation, cutoff time for each run is ' + cutoff_time_str + ' seconds')

	#print r'c performance_data_csv_path = ' + performance_data_csv_path
	#print r'c feature_data_csv_path = ' + feature_data_csv_path
	rank_list = []
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	num_instances = performance_data_csv.get_row_size()
	num_solvers = performance_data_csv.get_column_size()
	
	if not os.path.exists(r'Tmp/'): os.mkdir(r'Tmp/')
	
	print('c Computing actual performance for portfolio selector with all solvers ...')
	actual_portfolio_selector_path = r'Tmp/' + r'actual_portfolio_selector_' + sparkle_basic_help.get_time_pid_random_string()
	scps.construct_sparkle_portfolio_selector(actual_portfolio_selector_path, performance_data_csv_path, feature_data_csv_path)

	if not os.path.exists(actual_portfolio_selector_path):
		print(r'c ****** WARNING: ' + actual_portfolio_selector_path + r' does not exist! ******')
		print(r'c ****** WARNING: ' + r'AutoFolio constructing the actual portfolio selector with all solvers failed! ******')
		print(r'c ****** WARNING: ' + r'Using virtual best performance instead of actual performance for this portfolio selector! ******')
		virtual_best_performance = performance_data_csv.calc_virtual_best_performance_of_portfolio(num_instances, num_solvers)
		actual_selector_performance = virtual_best_performance
	else:
		actual_selector_performance = compute_actual_selector_performance(actual_portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, num_instances, num_solvers)
	
	print('c Actual performance for portfolio selector with all solvers is ' + str(actual_selector_performance))
	#print 'c actual_selector_performance with all solvers = ' + str(actual_selector_performance)
	print('c Computing done!')
	
	for solver in performance_data_csv.list_columns():
		print('c Computing actual performance for portfolio selector excluding solver ' + sfh.get_last_level_directory_name(solver) + ' ...')
		tmp_performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
		tmp_performance_data_csv.delete_column(solver)
		tmp_performance_data_csv_path = r'Tmp/' + r'tmp_performance_data_csv_' + sparkle_basic_help.get_time_pid_random_string() + r'.csv'
		tmp_performance_data_csv.save_csv(tmp_performance_data_csv_path)
		tmp_actual_portfolio_selector_path = r'Tmp/' + r'tmp_actual_portfolio_selector_' + sparkle_basic_help.get_time_pid_random_string()
		
		if len(tmp_performance_data_csv.list_columns()) >= 1:
			scps.construct_sparkle_portfolio_selector(tmp_actual_portfolio_selector_path, tmp_performance_data_csv_path, feature_data_csv_path)
		else:
			print(r'c ****** WARNING: ' + r'No solver exists ! ******')
		
		if not os.path.exists(tmp_actual_portfolio_selector_path):
			print(r'c ****** WARNING: ' + tmp_actual_portfolio_selector_path + r' does not exist! ******')
			print(r'c ****** WARNING: ' + r'AutoFolio constructing the actual portfolio selector excluding solver ' + sfh.get_last_level_directory_name(solver) + r' failed! ******')
			print(r'c ****** WARNING: ' + r'Using virtual best performance instead of actual performance for this portfolio selector! ******')
			tmp_virtual_best_performance = tmp_performance_data_csv.calc_virtual_best_performance_of_portfolio(num_instances, num_solvers)
			tmp_actual_selector_performance = tmp_virtual_best_performance
		else:
			tmp_actual_selector_performance = compute_actual_selector_performance(tmp_actual_portfolio_selector_path, tmp_performance_data_csv_path, feature_data_csv_path, num_instances, num_solvers)
		
		print('c Actual performance for portfolio selector excluding solver ' + sfh.get_last_level_directory_name(solver) + ' is ' + str(tmp_actual_selector_performance))
		#print 'c tmp_actual_selector_performance excluding ' + solver + ' = ' + str(tmp_actual_selector_performance)
		os.system(r'rm -f ' + tmp_performance_data_csv_path)
		os.system(r'rm -f ' + tmp_actual_portfolio_selector_path)
		print('c Computing done!')
		
		marginal_contribution = actual_selector_performance - tmp_actual_selector_performance
		
		solver_tuple = (solver, marginal_contribution)
		rank_list.append(solver_tuple)
		print('c Marginal contribution (to Actual Selector) for solver ' + sfh.get_last_level_directory_name(solver) + ' is ' + str(marginal_contribution))

	rank_list.sort(key=lambda marginal_contribution: marginal_contribution[1], reverse=True)
	
	os.system(r'rm -f ' + actual_portfolio_selector_path)
	return rank_list


def print_rank_list(rank_list, mode):
	my_string = r''
	if mode == 1: my_string = r'perfect selector'
	elif mode == 2: my_string = r'actual selector'
	else: pass
	print(r'c ******')
	print(r"c Solver ranking list via marginal contribution (Margi_Contr) with regards to " + my_string)
	for i in range(0, len(rank_list)):
		solver = rank_list[i][0]
		marginal_contribution = rank_list[i][1]
		print(r'c #' + str(i+1) + r': ' + sfh.get_last_level_directory_name(solver) + '\t Margi_Contr: ' + str(marginal_contribution))
	print(r'c ******')
	return

