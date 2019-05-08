#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

from math import log

import os
import sys
import fcntl
import sparkle_basic_help
import sparkle_record_help
import sparkle_file_help as sfh
import sparkle_global_help
import sparkle_feature_data_csv_help as sfdcsv
import sparkle_performance_data_csv_help as spdcsv
import sparkle_run_solvers_help as srs
import sparkle_construct_portfolio_selector_help as scps ##
import sparkle_run_portfolio_selector_help as srps ##
import sparkle_experiments_related_help as serh ##


def compute_perfect_selector_marginal_contribution(performance_data_csv_path = sparkle_global_help.performance_data_csv_path, cutoff_time_each_run = srs.cutoff_time_each_run, mode=1):
	par_num = serh.par_num
	print 'c In this calculation, cutoff time for each run is ' + str(cutoff_time_each_run) + ' seconds, and PAR factor is ' + str(par_num)
	
	rank_list = []
	solver_amc_list = []
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	num_instances = performance_data_csv.get_row_size()
	num_solvers = performance_data_csv.get_column_size()
	
	#print 'c Computing virtual best performance for portfolio selector with all solvers ...'
	#virtual_best_performance = performance_data_csv.calc_virtual_best_performance_of_portfolio(cutoff_time_each_run, num_instances, num_solvers)
	#print 'c Virtual best performance for portfolio selector with all solvers is ' + str(virtual_best_performance)
	#print 'c Computing done!'
	
	print('c Computing perfect PAR%d value for portfolio selector with all solvers ...' % par_num)
	virtual_best_penalty_time = performance_data_csv.calc_vbs_penalty_time(cutoff_time_each_run, par_num)
	print('c Perfect PAR%d value for portfolio selector with all solvers is %f' % (par_num, virtual_best_penalty_time))
	print('c Computing done!')
	
	dict_tmp_virtual_best_penalty_time = {}
	
	for solver in performance_data_csv.list_columns():
		#print 'c Computing virtual best performance for portfolio selector excluding solver ' + sfh.get_last_level_directory_name(solver) + ' ...'
		print('c Computing perfect PAR%d value for portfolio selector excluding solver %s ...' % (par_num, sfh.get_last_level_directory_name(solver)))
		tmp_performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
		tmp_performance_data_csv.delete_column(solver)
		
		#tmp_virtual_best_performance = tmp_performance_data_csv.calc_virtual_best_performance_of_portfolio(cutoff_time_each_run, num_instances, num_solvers)
		#print 'c Virtual best performance for portfolio selector excluding solver ' + sfh.get_last_level_directory_name(solver) + ' is ' + str(tmp_virtual_best_performance)
		#print 'c Computing done!'
		#marginal_contribution = virtual_best_performance - tmp_virtual_best_performance
		
		
		tmp_virtual_best_penalty_time = tmp_performance_data_csv.calc_vbs_penalty_time(cutoff_time_each_run, par_num)
		dict_tmp_virtual_best_penalty_time[solver] = tmp_virtual_best_penalty_time
		print('c Perfect PAR%d value for portfolio selector excluding solver %s is %f' % (par_num, sfh.get_last_level_directory_name(solver), tmp_virtual_best_penalty_time))
		
		#absolute_marginal_contribution = tmp_virtual_best_penalty_time/virtual_best_penalty_time
		#if absolute_marginal_contribution <=1:
		#	absolute_marginal_contribution = 0
		
		absolute_marginal_contribution = 0
		if tmp_virtual_best_penalty_time > virtual_best_penalty_time:
			absolute_marginal_contribution = log(tmp_virtual_best_penalty_time/virtual_best_penalty_time, 10)
		else:
			absolute_marginal_contribution = 0
		
		solver_tuple = (solver, absolute_marginal_contribution)
		#rank_list.append(solver_tuple)
		solver_amc_list.append(solver_tuple)
		#print 'c Marginal contribution (to Perfect Selector) for solver ' + sfh.get_last_level_directory_name(solver) + ' is ' + str(marginal_contribution)
		print('c Absolute marginal contribution (to Perfect Selector) for solver ' + sfh.get_last_level_directory_name(solver) + ' is ' + str(absolute_marginal_contribution))
	
	print('c Computing relative marginal contribution ...')
	
	sum_absolute_marginal_contribution = 0
	for solver, absolute_marginal_contribution in solver_amc_list:
		sum_absolute_marginal_contribution += absolute_marginal_contribution
	
	rank_list = []
	for solver, absolute_marginal_contribution in solver_amc_list:
		if sum_absolute_marginal_contribution == 0:
			relative_marginal_contribution = 0
		else:
			relative_marginal_contribution = absolute_marginal_contribution/sum_absolute_marginal_contribution
			
		if mode==1:
			solver_tuple = (solver, relative_marginal_contribution)
		else:
			solver_tuple = (solver, relative_marginal_contribution, absolute_marginal_contribution, dict_tmp_virtual_best_penalty_time[solver])
			
		rank_list.append(solver_tuple)
		print('c Relative marginal contribution (to Perfect Selector) for solver ' + sfh.get_last_level_directory_name(solver) + ' is ' + str(relative_marginal_contribution))
	
	rank_list.sort(key=lambda marginal_contribution: marginal_contribution[1], reverse=True)
	return rank_list


def get_list_predict_schedule(actual_portfolio_selector_path, feature_data_csv, instance):
	list_predict_schedule = []
	python_executable = sparkle_global_help.python_executable
	if not os.path.exists(r'TMP/'): os.mkdir(r'TMP/')
	feature_vector_string = feature_data_csv.get_feature_vector_string(instance)
	predict_schedule_result_path = r'TMP/predict_schedule_' + sparkle_basic_help.get_time_pid_random_string() + r'.predres'
	
	command_line = python_executable + r' ' + sparkle_global_help.autofolio_path + r' --load ' + actual_portfolio_selector_path + r' --feature_vec' + r' ' + feature_vector_string + r' 1> ' + predict_schedule_result_path + r' 2> ' + sparkle_global_help.sparkle_log_path
	
	#print 'c ' + command_line
	os.system(command_line)
	
	list_predict_schedule = srps.get_list_predict_schedule_from_file(predict_schedule_result_path)
	
	#print r'c for solving instance ' + instance + r', ' + r'list_predict_schedule = ' + str(list_predict_schedule)
	
	os.system(r'rm -f ' + predict_schedule_result_path)
	os.system(r'rm -f ' + sparkle_global_help.sparkle_log_path)
	return list_predict_schedule

'''
def compute_actual_selector_performance(actual_portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, num_instances, num_solvers):
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
	
	actual_selector_performance = 0
	
	for instance in performance_data_csv.list_rows():
		list_predict_schedule = get_list_predict_schedule(actual_portfolio_selector_path, feature_data_csv, instance)
		#print 'c instance = ' + instance + ', schedule: ' + str(list_predict_schedule)
		used_time_for_this_instance = 0
		flag_successfully_solving = False
		for i in range(0, len(list_predict_schedule)):
			if used_time_for_this_instance >= cutoff_time_each_run:
				flag_successfully_solving = False
				break
			solver = list_predict_schedule[i][0]
			scheduled_cutoff_time_this_run = list_predict_schedule[i][1]
			required_time_this_run = performance_data_csv.get_value(instance, solver)
			#print 'c required_time_this_run = ' + str(required_time_this_run)
			if required_time_this_run <= scheduled_cutoff_time_this_run:
				used_time_for_this_instance = used_time_for_this_instance + required_time_this_run
				if used_time_for_this_instance > cutoff_time_each_run:
					flag_successfully_solving = False
				else: flag_successfully_solving = True
				break
			else:
				used_time_for_this_instance = used_time_for_this_instance + scheduled_cutoff_time_this_run
				continue
		#print 'c instace = ' + instance + ', used_time_for_this_instance =' + str(used_time_for_this_instance) + ', flag_successfully_solving = ' + str(flag_successfully_solving)
		if flag_successfully_solving:
			score_this_instance = 1 + (cutoff_time_each_run - used_time_for_this_instance) / (num_instances*cutoff_time_each_run*num_solvers+1)
		else:
			score_this_instance = 0
		#print 'c instance = ' + instance + ', score_this_instance = ' + str(score_this_instance)
		
		actual_selector_performance = actual_selector_performance + score_this_instance
			
	return actual_selector_performance
'''

def compute_actual_selector_penalty_time(actual_portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, num_instances, num_solvers):
	par_num = serh.par_num
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
	
	actual_selector_penalty_time = 0
	count = 0
	
	for instance in performance_data_csv.list_rows():
		count += 1
		list_predict_schedule = get_list_predict_schedule(actual_portfolio_selector_path, feature_data_csv, instance)
		#print 'c instance = ' + instance + ', schedule: ' + str(list_predict_schedule)
		used_time_for_this_instance = 0
		flag_successfully_solving = False
		for i in range(0, len(list_predict_schedule)):
			if used_time_for_this_instance >= cutoff_time_each_run:
				flag_successfully_solving = False
				break
			solver = list_predict_schedule[i][0]
			scheduled_cutoff_time_this_run = list_predict_schedule[i][1]
			required_time_this_run = performance_data_csv.get_value(instance, solver)
			#print 'c required_time_this_run = ' + str(required_time_this_run)
			if required_time_this_run <= scheduled_cutoff_time_this_run:
				used_time_for_this_instance = used_time_for_this_instance + required_time_this_run
				if used_time_for_this_instance > cutoff_time_each_run:
					flag_successfully_solving = False
				else: flag_successfully_solving = True
				break
			else:
				used_time_for_this_instance = used_time_for_this_instance + scheduled_cutoff_time_this_run
				continue
		#print 'c instace = ' + instance + ', used_time_for_this_instance =' + str(used_time_for_this_instance) + ', flag_successfully_solving = ' + str(flag_successfully_solving)
		if flag_successfully_solving:
			penalty_time_on_this_instance = used_time_for_this_instance
		else:
			penalty_time_on_this_instance = cutoff_time_each_run * par_num
		#print 'c instance = ' + instance + ', score_this_instance = ' + str(score_this_instance)
		
		actual_selector_penalty_time += penalty_time_on_this_instance
	
	actual_selector_penalty_time = actual_selector_penalty_time / count		
	return actual_selector_penalty_time


def compute_actual_selector_marginal_contribution(performance_data_csv_path = sparkle_global_help.performance_data_csv_path, feature_data_csv_path = sparkle_global_help.feature_data_csv_path, cutoff_time_each_run = srs.cutoff_time_each_run):
	par_num = serh.par_num
	print 'c In this calculation, cutoff time for each run is ' + str(cutoff_time_each_run) + ' seconds, and PAR factor is ' + str(par_num)

	#print r'c performance_data_csv_path = ' + performance_data_csv_path
	#print r'c feature_data_csv_path = ' + feature_data_csv_path
	rank_list = []
	solver_amc_list = []
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	num_instances = performance_data_csv.get_row_size()
	num_solvers = performance_data_csv.get_column_size()
	
	
	if not os.path.exists(r'TMP/'): os.mkdir(r'TMP/')
	
	print('c Computing actual PAR%d value for portfolio selector with all solvers ...' % par_num)
	if os.path.exists(sparkle_global_help.sparkle_portfolio_selector_path):
		actual_portfolio_selector_path = sparkle_global_help.sparkle_portfolio_selector_path
	else:
		actual_portfolio_selector_path = r'TMP/' + r'actual_portfolio_selector_' + sparkle_basic_help.get_time_pid_random_string()
		scps.construct_sparkle_portfolio_selector(actual_portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run)
	
	if not os.path.exists(actual_portfolio_selector_path):
		print r'c ****** WARNING: ' + actual_portfolio_selector_path + r' does not exist! ******'
		print r'c ****** WARNING: ' + r'AutoFolio constructing the actual portfolio selector with all solvers failed! ******'
		print('c ****** WARNING: ' + r'Using virtual best PAR%d value instead of actual PAR%d value for this portfolio selector! ******' % (par_num, par_num))
		virtual_best_penalty_time = performance_data_csv.calc_vbs_penalty_time(cutoff_time_each_run, par_num)
		actual_selector_penalty_time = virtual_best_penalty_time
	else:
		actual_selector_penalty_time = compute_actual_selector_penalty_time(actual_portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, num_instances, num_solvers)
			
	print('c Actual PAR%d value for portfolio selector with all solvers is ' % (par_num) + str(actual_selector_penalty_time))
	#print 'c actual_selector_performance with all solvers = ' + str(actual_selector_performance)
	print 'c Computing done!'
	
	for solver in performance_data_csv.list_columns():
		print('c Computing actual PAR%d value for portfolio selector excluding solver ' % (par_num) + sfh.get_last_level_directory_name(solver) + ' ...')
		tmp_performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
		tmp_performance_data_csv.delete_column(solver)
		tmp_performance_data_csv_path = r'TMP/' + r'tmp_performance_data_csv_' + sparkle_basic_help.get_time_pid_random_string() + r'.csv'
		tmp_performance_data_csv.save_csv(tmp_performance_data_csv_path)
		#tmp_actual_portfolio_selector_path = r'TMP/' + r'tmp_actual_portfolio_selector_' + sparkle_basic_help.get_time_pid_random_string()
		
		tmp_actual_portfolio_selector_path = sparkle_global_help.sparkle_portfolio_selector_path + '_excluding_' + sfh.get_last_level_directory_name(solver)
		
		if not os.path.exists(tmp_actual_portfolio_selector_path):
			if len(tmp_performance_data_csv.list_columns()) >= 1:
				scps.construct_sparkle_portfolio_selector(tmp_actual_portfolio_selector_path, tmp_performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run)
			else:
				print(r'c ****** WARNING: ' + r'No solver exists ! ******')
		
		if not os.path.exists(tmp_actual_portfolio_selector_path):
			print r'c ****** WARNING: ' + tmp_actual_portfolio_selector_path + r' does not exist! ******'
			print r'c ****** WARNING: ' + r'AutoFolio constructing the actual portfolio selector excluding solver ' + sfh.get_last_level_directory_name(solver) + r' failed! ******'
			print('c ****** WARNING: ' + r'Using virtual best PAR%d value instead of actual PAR%d value for this portfolio selector! ******' % (par_num, par_num))
			tmp_virtual_best_penalty_time = tmp_performance_data_csv.calc_vbs_penalty_time(cutoff_time_each_run, par_num)
			tmp_actual_selector_penalty_time = tmp_virtual_best_penalty_time
		else:
			tmp_actual_selector_penalty_time = compute_actual_selector_penalty_time(tmp_actual_portfolio_selector_path, tmp_performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, num_instances, num_solvers)
		
		print('c Actual PAR%d value for portfolio selector excluding solver ' % (par_num) + sfh.get_last_level_directory_name(solver) + ' is ' + str(tmp_actual_selector_penalty_time))
		#print 'c tmp_actual_selector_performance excluding ' + solver + ' = ' + str(tmp_actual_selector_performance)
		os.system(r'rm -f ' + tmp_performance_data_csv_path)
		#os.system(r'rm -f ' + tmp_actual_portfolio_selector_path)
		#print 'c Computing done!'
		
		#absolute_marginal_contribution = tmp_actual_selector_penalty_time / actual_selector_penalty_time
		#if absolute_marginal_contribution <=1:
		#	absolute_marginal_contribution = 0
		
		absolute_marginal_contribution = 0
		if tmp_actual_selector_penalty_time > actual_selector_penalty_time:
			absolute_marginal_contribution = log(tmp_actual_selector_penalty_time/actual_selector_penalty_time, 10)
		else:
			absolute_marginal_contribution = 0
		
		solver_tuple = (solver, absolute_marginal_contribution)
		#rank_list.append(solver_tuple)
		solver_amc_list.append(solver_tuple)
		print('c Absolute marginal contribution (to Actual Selector) for solver ' + sfh.get_last_level_directory_name(solver) + ' is ' + str(absolute_marginal_contribution))
	
	print('c Computing relative marginal contribution ...')
	
	sum_absolute_marginal_contribution = 0
	for solver, absolute_marginal_contribution in solver_amc_list:
		sum_absolute_marginal_contribution += absolute_marginal_contribution
	
	rank_list = []
	for solver, absolute_marginal_contribution in solver_amc_list:
		if sum_absolute_marginal_contribution == 0:
			relative_marginal_contribution = 0
		else:
			relative_marginal_contribution = absolute_marginal_contribution/sum_absolute_marginal_contribution
		solver_tuple = (solver, relative_marginal_contribution)
		rank_list.append(solver_tuple)
		print('c Relative marginal contribution (to Actual Selector) for solver ' + sfh.get_last_level_directory_name(solver) + ' is ' + str(relative_marginal_contribution))
	
	rank_list.sort(key=lambda marginal_contribution: marginal_contribution[1], reverse=True)
	
	if actual_portfolio_selector_path != sparkle_global_help.sparkle_portfolio_selector_path:
		os.system(r'rm -f ' + actual_portfolio_selector_path)
	return rank_list

def print_rank_list(rank_list, mode):
	my_string = r''
	if mode == 1: my_string = r'perfect selector'
	elif mode == 2: my_string = r'actual selector'
	else: pass
	print r'c ******'
	print r"c Solver ranking list via relative marginal contribution (Rel_Margi_Contr) with regards to " + my_string
	for i in range(0, len(rank_list)):
		solver = rank_list[i][0]
		marginal_contribution = rank_list[i][1]
		print r'c #' + str(i+1) + r': ' + sfh.get_last_level_directory_name(solver) + '\t Rel_Margi_Contr: ' + str(marginal_contribution)
	print r'c ******'
	return


