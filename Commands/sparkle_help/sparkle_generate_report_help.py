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
import sparkle_global_help
import sparkle_file_help as sfh
import sparkle_feature_data_csv_help as sfdcsv
import sparkle_performance_data_csv_help as spdcsv
import sparkle_experiments_related_help
import sparkle_compute_marginal_contribution_help

def get_customCommands():
	str_value = r''
	return str_value

def get_sparkle():
	str_value = r'\emph{Sparkle}'
	return str_value

def get_sparkleVersion():
	str_value = r'Sparkle_SAT_Challenge_2018'
	return str_value

def get_numSolvers():
	num_solvers = len(sparkle_global_help.solver_list)
	str_value = str(num_solvers)
	return str_value

def get_solverList():
	str_value = r''
	solver_list = sparkle_global_help.solver_list
	for solver_path in solver_list:
		solver_name = sfh.get_file_name(solver_path)
		str_value += r'\item \textbf{' + solver_name + r'}' + '\n'
	return str_value

def get_numFeatureExtractors():
	num_feature_extractors = len(sparkle_global_help.extractor_list)
	str_value = str(num_feature_extractors)
	return str_value

def get_featureExtractorList():
	str_value = r''
	extractor_list = sparkle_global_help.extractor_list
	for extractor_path in extractor_list:
		extractor_name = sfh.get_file_name(extractor_path)
		str_value += r'\item \textbf{' + extractor_name + r'}' + '\n'
	return str_value

def get_numTotalInstances():
	num_total_instances = len(sparkle_global_help.instance_list)
	str_value = str(num_total_instances)
	return str_value

def get_numInstanceClasses():
	list_instance_class = []
	instance_list = sparkle_global_help.instance_list
	for instance_path in instance_list:
		instance_class = sfh.get_current_directory_name(instance_path)
		if not (instance_class in list_instance_class):
			list_instance_class.append(instance_class)
	str_value = str(len(list_instance_class))
	return str_value

def get_instanceClassList():
	str_value = r''
	list_instance_class = []
	dict_number_of_instances_in_instance_class = {}
	instance_list = sparkle_global_help.instance_list
	for instance_path in instance_list:
		instance_class = sfh.get_current_directory_name(instance_path)
		if not (instance_class in list_instance_class):
			list_instance_class.append(instance_class)
			dict_number_of_instances_in_instance_class[instance_class] = 1
		else:
			dict_number_of_instances_in_instance_class[instance_class] += 1
			
	for instance_class in list_instance_class:
		str_value += r'\item \textbf{' + instance_class + r'}, number of instances: ' + str(dict_number_of_instances_in_instance_class[instance_class]) + '\n'
	
	return str_value

def get_featureComputationCutoffTime():
	str_value = str(sparkle_experiments_related_help.cutoff_time_total_extractor_run_on_one_instance)
	return str_value

def get_featureComputationMemoryLimit():
	str_value = str(sparkle_experiments_related_help.memory_limit_each_extractor_run)
	return str_value

def get_performanceComputationCutoffTime():
	str_value = str(sparkle_experiments_related_help.cutoff_time_each_run)
	return str_value

def get_performanceComputationMemoryLimit():
	str_value = str(sparkle_experiments_related_help.memory_limit_each_solver_run)
	return str_value

'''
def get_solverPerfectRankingList():
	str_value = r''
	command = r'Commands/compute_marginal_contribution.py -perfect'
	output = os.popen(command).readlines()
	for myline in output:
		mylist = myline.strip().split()
		if len(mylist) == 5:
			if mylist[0] == r'c' and mylist[1][0] == r'#' and mylist[3] == r'Rel_Margi_Contr:':
				solver = mylist[2]
				marginal_contribution = mylist[4]
				str_value += r'\item \textbf{' + solver + r'}, relative marginal contribution: ' + marginal_contribution + '\n'
	return str_value
'''

'''
def get_solverActualRankingList():
	str_value = r''
	command = r'Commands/compute_marginal_contribution.py -actual'
	output = os.popen(command).readlines()
	for myline in output:
		mylist = myline.strip().split()
		if len(mylist) == 5:
			if mylist[0] == r'c' and mylist[1][0] == r'#' and mylist[3] == r'Rel_Margi_Contr:':
				solver = mylist[2]
				marginal_contribution = mylist[4]
				str_value += r'\item \textbf{' + solver + r'}, relative marginal contribution: ' + marginal_contribution + '\n'
	return str_value
'''

def get_parNum():
	par_num = sparkle_experiments_related_help.par_num
	return str(par_num)

def get_PenaltyTimeRankingList():
	str_value = r''
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path + '_validate.csv')
	cutoff_time_each_run = sparkle_experiments_related_help.cutoff_time_each_run
	par_num = sparkle_experiments_related_help.par_num
	
	solver_penalty_time_ranking_list = performance_data_csv.get_solver_penalty_time_ranking_list(cutoff_time_each_run, par_num)
	
	rank_num = 1
	for solver, this_penalty_time in solver_penalty_time_ranking_list:
		#str_value += r'\item \textbf{' + sfh.get_file_name(solver) + '}, PAR%d: ' % (par_num) + str(this_penalty_time) + '\n'
		str_value += '%d & %s & %.6f' % (rank_num, sfh.get_file_name(solver), float(this_penalty_time)) + '\\\\' + '\n'
		rank_num += 1
	
	return str_value

'''
def get_VBSPenaltyTime():
	str_value = r''
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)
	cutoff_time_each_run = sparkle_experiments_related_help.cutoff_time_each_run
	par_num = sparkle_experiments_related_help.par_num
	vbs_penalty_time = performance_data_csv.calc_vbs_penalty_time(cutoff_time_each_run, par_num)
	
	str_value = str(vbs_penalty_time)
	return str_value
'''

'''
def get_actualPenaltyTime():
	str_value = r''
	actual_penalty_time = 0.0
	actual_count = 0
	
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)
	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(sparkle_global_help.feature_data_csv_path)
	actual_portfolio_selector_path = sparkle_global_help.sparkle_portfolio_selector_path
	cutoff_time_each_run = sparkle_experiments_related_help.cutoff_time_each_run
	par_num = sparkle_experiments_related_help.par_num
	penalty_time_each_run = cutoff_time_each_run * par_num
	
	for instance in performance_data_csv.list_rows():
		list_predict_schedule = sparkle_compute_marginal_contribution_help.get_list_predict_schedule(actual_portfolio_selector_path, feature_data_csv, instance)
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
			actual_penalty_time = actual_penalty_time + used_time_for_this_instance
		else:
			actual_penalty_time = actual_penalty_time + penalty_time_each_run
		actual_count += 1
	
	actual_penalty_time = actual_penalty_time / actual_count
	str_value = str(actual_penalty_time)
	return str_value
'''

def get_dict_sbs_penalty_time_on_each_instance():
	mydict = {}
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path + '_validate.csv')
	cutoff_time_each_run = sparkle_experiments_related_help.cutoff_time_each_run
	par_num = sparkle_experiments_related_help.par_num
	penalty_time_each_run = cutoff_time_each_run * par_num
	
	solver_penalty_time_ranking_list = performance_data_csv.get_solver_penalty_time_ranking_list(cutoff_time_each_run, par_num)
	sbs_solver = solver_penalty_time_ranking_list[0][0]
	
	for instance in performance_data_csv.list_rows():
		this_run_time = performance_data_csv.get_value(instance, sbs_solver)
		if this_run_time <= cutoff_time_each_run:
			mydict[instance] = this_run_time
		else:
			mydict[instance] = penalty_time_each_run
	return mydict


def get_dict_vbs_penalty_time_on_each_instance():
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path + '_validate.csv')
	mydict = performance_data_csv.get_dict_vbs_penalty_time_on_each_instance()
	return mydict


def get_dict_actual_portfolio_selector_penalty_time_on_each_instance():
	portfolio_selector_penalty_time_on_each_instance_path = sparkle_global_help.sparkle_portfolio_selector_path + '_penalty_time_on_each_instance.txt'
	if os.path.exists(portfolio_selector_penalty_time_on_each_instance_path) and os.path.isfile(portfolio_selector_penalty_time_on_each_instance_path):
		mydict = {}
		fin = open(portfolio_selector_penalty_time_on_each_instance_path, 'r')
		while True:
			myline = fin.readline()
			if not myline: break
			mylist = myline.strip().split()
			instance = mylist[0]
			runtime = float(mylist[1])
			mydict[instance] = runtime
		fin.close()
		return mydict
	
	
	mydict = {}
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path + '_validate.csv')
	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(sparkle_global_help.feature_data_csv_path)
	actual_portfolio_selector_path = sparkle_global_help.sparkle_portfolio_selector_path
	cutoff_time_each_run = sparkle_experiments_related_help.cutoff_time_each_run
	par_num = sparkle_experiments_related_help.par_num
	penalty_time_each_run = cutoff_time_each_run * par_num
	
	for instance in performance_data_csv.list_rows():
		list_predict_schedule = sparkle_compute_marginal_contribution_help.get_list_predict_schedule(actual_portfolio_selector_path, feature_data_csv, instance)
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


def get_figure_portfolio_selector_sparkle_vs_sbs(dict_actual_portfolio_selector_penalty_time_on_each_instance):
	str_value = r''
	dict_sbs_penalty_time_on_each_instance = get_dict_sbs_penalty_time_on_each_instance()
	#dict_actual_portfolio_selector_penalty_time_on_each_instance = get_dict_actual_portfolio_selector_penalty_time_on_each_instance()
	cutoff_time_each_run = sparkle_experiments_related_help.cutoff_time_each_run
	par_num = sparkle_experiments_related_help.par_num
	penalty_time_each_run = cutoff_time_each_run * par_num
	
	latex_directory_path = r'Components/Sparkle-latex-generator/'
	figure_portfolio_selector_sparkle_vs_sbs_filename = r'figure_portfolio_selector_sparkle_vs_sbs'
	data_portfolio_selector_sparkle_vs_sbs_filename = r'data_portfolio_selector_sparkle_vs_sbs_filename.dat'
	data_portfolio_selector_sparkle_vs_sbs_filepath = latex_directory_path + data_portfolio_selector_sparkle_vs_sbs_filename
	
	fout = open(data_portfolio_selector_sparkle_vs_sbs_filepath, 'w+')
	for instance in dict_sbs_penalty_time_on_each_instance:
		sbs_penalty_time = dict_sbs_penalty_time_on_each_instance[instance]
		sparkle_penalty_time = dict_actual_portfolio_selector_penalty_time_on_each_instance[instance]
		fout.write(str(sbs_penalty_time) + r' ' + str(sparkle_penalty_time) + '\n')
	fout.close()
	
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path + '_validate.csv')
	cutoff_time_each_run = sparkle_experiments_related_help.cutoff_time_each_run
	solver_penalty_time_ranking_list = performance_data_csv.get_solver_penalty_time_ranking_list(cutoff_time_each_run, par_num)
	sbs_solver = solver_penalty_time_ranking_list[0][0]
	
	gnuplot_command = r'cd ' + latex_directory_path + r'; python auto_gen_plot.py ' + data_portfolio_selector_sparkle_vs_sbs_filename + r' ' + str(penalty_time_each_run) + r' ' + '\'SBS (' + sfh.get_file_name(sbs_solver) + ')\' ' + r'Sparkle_Selector' + r' ' + figure_portfolio_selector_sparkle_vs_sbs_filename + r' ' + str(par_num)
	
	#print(gnuplot_command)
	
	os.system(gnuplot_command)
	
	str_value = '\\includegraphics[width=0.6\\textwidth]{%s}' % (figure_portfolio_selector_sparkle_vs_sbs_filename)
	return str_value


def get_figure_portfolio_selector_sparkle_vs_vbs(dict_actual_portfolio_selector_penalty_time_on_each_instance):
	str_value = r''
	dict_vbs_penalty_time_on_each_instance = get_dict_vbs_penalty_time_on_each_instance()
	#dict_actual_portfolio_selector_penalty_time_on_each_instance = get_dict_actual_portfolio_selector_penalty_time_on_each_instance()
	cutoff_time_each_run = sparkle_experiments_related_help.cutoff_time_each_run
	par_num = sparkle_experiments_related_help.par_num
	penalty_time_each_run = cutoff_time_each_run * par_num
	
	latex_directory_path = r'Components/Sparkle-latex-generator/'
	figure_portfolio_selector_sparkle_vs_vbs_filename = r'figure_portfolio_selector_sparkle_vs_vbs'
	data_portfolio_selector_sparkle_vs_vbs_filename = r'data_portfolio_selector_sparkle_vs_vbs_filename.dat'
	data_portfolio_selector_sparkle_vs_vbs_filepath = latex_directory_path + data_portfolio_selector_sparkle_vs_vbs_filename
	
	fout = open(data_portfolio_selector_sparkle_vs_vbs_filepath, 'w+')
	for instance in dict_vbs_penalty_time_on_each_instance:
		vbs_penalty_time = dict_vbs_penalty_time_on_each_instance[instance]
		sparkle_penalty_time = dict_actual_portfolio_selector_penalty_time_on_each_instance[instance]
		fout.write(str(vbs_penalty_time) + r' ' + str(sparkle_penalty_time) + '\n')
	fout.close()
	
	gnuplot_command = r'cd ' + latex_directory_path + r'; python auto_gen_plot.py ' + data_portfolio_selector_sparkle_vs_vbs_filename + r' ' + str(penalty_time_each_run) + r' ' + r'VBS' + r' ' + r'Sparkle_Selector' + r' ' + figure_portfolio_selector_sparkle_vs_vbs_filename + r' ' + str(par_num)
	
	os.system(gnuplot_command)
	
	str_value = '\\includegraphics[width=0.6\\textwidth]{%s}' % (figure_portfolio_selector_sparkle_vs_vbs_filename)
	return str_value


def get_perfect_selector_related_information():
	str_value_solverPerfectRankingList = ''
	str_value_VBSPenaltyTime = ''
	str_value_perfectPortfolioPenaltyTimeList = ''
	
	par_num = sparkle_experiments_related_help.par_num
	par_num_str = 'PAR' + str(par_num)
	
	dict_amc = {}
	
	command = r'Commands/compute_marginal_contribution.py -perfect'
	output = os.popen(command).readlines()
	
	solver_rank = 1
	list_perfectPortfolioPenaltyTimeList = []
	
	for myline in output:
		mylist = myline.strip().split()
		
		if len(mylist) == 12:
			if mylist[0] == 'c' and mylist[1] == 'Perfect' and mylist[2] == par_num_str and mylist[3] == 'value' and mylist[4] == 'for' and mylist[5] == 'portfolio' and mylist[6] == 'selector' and mylist[7] == 'with' and mylist[8] == 'all' and mylist[9] == 'solvers' and mylist[10] == 'is':
				str_value_VBSPenaltyTime = '%.6f' % (float(mylist[11]))
				continue
		
		if len(mylist) == 12:
			if mylist[0] == 'c' and mylist[1] == 'Perfect' and mylist[2] == par_num_str and mylist[3] == 'value' and mylist[4] == 'for' and mylist[5] == 'portfolio' and mylist[6] == 'selector' and mylist[7] == 'excluding' and mylist[8] == 'solver' and mylist[10] == 'is':
				solver = mylist[9]
				penalty_time = mylist[11]
				#str_value_perfectPortfolioPenaltyTimeList += r'\item \textbf{Perfect Portfolio Selector excluding ' + solver + '}, ' + par_num_str + ': ' + penalty_time + '\n'
				#str_value_perfectPortfolioPenaltyTimeList += 'Perfect Portfolio Selector excluding \\emph{%s} & %.6f \\\\ \n' % (solver, float(penalty_time))
				list_perfectPortfolioPenaltyTimeList.append([solver, float(penalty_time)])
				continue
		
		if len(mylist) == 12:
			if mylist[0] == 'c' and mylist[1] == 'Absolute' and mylist[2] == 'marginal' and mylist[3] == 'contribution' and mylist[4] == '(to' and mylist[5] == 'Perfect' and mylist[6] == 'Selector)' and mylist[7] == 'for' and mylist[8] == 'solver' and mylist[10] == 'is':
				solver = mylist[9]
				solver_amc = mylist[11]
				dict_amc[solver] = solver_amc
				continue
		
		if len(mylist) == 5:
			if mylist[0] == r'c' and mylist[1][0] == r'#' and mylist[3] == r'Rel_Margi_Contr:':
				solver = mylist[2]
				solver_rmc = mylist[4]
				#str_value_solverPerfectRankingList += r'\item \textbf{' + solver + r'}, Rel_Margi_Contr: ' + solver_rmc + ', Abs_Margi_Contr: ' + dict_amc[solver] + '\n'
				str_value_solverPerfectRankingList += '%d & %s & %.6f & %.6f \\\\ \n' % (solver_rank, solver, float(solver_rmc), float(dict_amc[solver]))
				solver_rank += 1
	
	list_perfectPortfolioPenaltyTimeList.sort(key=lambda item: item[1])
	
	for solver, penalty_time_value in list_perfectPortfolioPenaltyTimeList:
		str_value_perfectPortfolioPenaltyTimeList += 'Perfect Portfolio Selector excluding \\emph{%s} & %.6f \\\\ \n' % (solver, penalty_time_value)
	
	return str_value_solverPerfectRankingList, str_value_VBSPenaltyTime, str_value_perfectPortfolioPenaltyTimeList


def judge_complete_analysing_all_portfolio_selectors():
	portfolio_selector_path = sparkle_global_help.sparkle_portfolio_selector_path
	portfolio_selector_penalty_time_on_each_instance_path = portfolio_selector_path + '_penalty_time_on_each_instance.txt'
	if (not os.path.exists(portfolio_selector_penalty_time_on_each_instance_path)) or (not os.path.isfile(portfolio_selector_penalty_time_on_each_instance_path)):
		return False
	
	performance_data_csv_path = sparkle_global_help.performance_data_csv_path + '_validate.csv'
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	
	for excluded_solver in performance_data_csv.list_columns():	
		portfolio_selector_path = sparkle_global_help.sparkle_portfolio_selector_path + '_excluding_' + sfh.get_last_level_directory_name(excluded_solver)
		portfolio_selector_penalty_time_on_each_instance_path = portfolio_selector_path + '_penalty_time_on_each_instance.txt'
		if (not os.path.exists(portfolio_selector_penalty_time_on_each_instance_path)) or (not os.path.isfile(portfolio_selector_penalty_time_on_each_instance_path)):
			return False
	
	return True
		
def get_actualPenaltyTime_from_exisiting_analysis_file(portfolio_selector_penalty_time_on_each_instance_path):
	cutoff_time_each_run = sparkle_experiments_related_help.cutoff_time_each_run
	par_num = sparkle_experiments_related_help.par_num
	penalty_time_each_run = cutoff_time_each_run * par_num
	
	actualPenaltyTime = 0
	instance_count = 0
	
	fin = open(portfolio_selector_penalty_time_on_each_instance_path, 'r')
	while True:
		myline = fin.readline()
		if not myline: break
		mylist = myline.strip().split()
		instance = mylist[0]
		runtime = float(mylist[1])
		if runtime > cutoff_time_each_run:
			runtime = penalty_time_each_run
		actualPenaltyTime += runtime
		instance_count += 1
	fin.close()
	
	actualPenaltyTime = actualPenaltyTime / instance_count
	return actualPenaltyTime


def get_actual_selector_related_information_from_existing_analysis_files():
	str_value_solverActualRankingList = ''
	str_value_actualPenaltyTime = ''
	str_value_actualPortfolioPenaltyTimeList = ''
	
	portfolio_selector_path_basis = sparkle_global_help.sparkle_portfolio_selector_path
	portfolio_selector_path = portfolio_selector_path_basis
	portfolio_selector_penalty_time_on_each_instance_path = portfolio_selector_path + '_penalty_time_on_each_instance.txt'
	actual_portfolio_selector_penalty_time_value = get_actualPenaltyTime_from_exisiting_analysis_file(portfolio_selector_penalty_time_on_each_instance_path)
	str_value_actualPenaltyTime = '%.6f' % (actual_portfolio_selector_penalty_time_value)
	
	list_actualPortfolioPenaltyTimeList = []
	performance_data_csv_path = sparkle_global_help.performance_data_csv_path + '_validate.csv'
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	for excluded_solver in performance_data_csv.list_columns():	
		portfolio_selector_path = portfolio_selector_path_basis + '_excluding_' + sfh.get_last_level_directory_name(excluded_solver)
		portfolio_selector_penalty_time_on_each_instance_path = portfolio_selector_path + '_penalty_time_on_each_instance.txt'
		solver = sfh.get_last_level_directory_name(excluded_solver)
		penalty_time_value = get_actualPenaltyTime_from_exisiting_analysis_file(portfolio_selector_penalty_time_on_each_instance_path)
		list_actualPortfolioPenaltyTimeList.append([solver, penalty_time_value])
	
	list_actualPortfolioPenaltyTimeList.sort(key=lambda item: item[1])
	
	for solver, penalty_time_value in list_actualPortfolioPenaltyTimeList:
		str_value_actualPortfolioPenaltyTimeList += 'Actual Portfolio Selector excluding \\emph{%s} & %.6f \\\\ \n' % (solver, penalty_time_value)
	
	list_solverActualRankingList = []
	amc_value_sum = 0
	for solver, penalty_time_value in list_actualPortfolioPenaltyTimeList:
		if penalty_time_value > actual_portfolio_selector_penalty_time_value:
			solver_amc_value = log(penalty_time_value/actual_portfolio_selector_penalty_time_value, 10)
		else:
			solver_amc_value = 0
		amc_value_sum += solver_amc_value
		list_solverActualRankingList.append([solver, solver_amc_value])
	
	for i in range(0, len(list_solverActualRankingList)):
		solver_amc_value = list_solverActualRankingList[i][1]
		solver_rmc_value = 0
		try:
			solver_rmc_value = solver_amc_value/amc_value_sum
		except:
			solver_rmc_value = 0
		list_solverActualRankingList[i].append(solver_rmc_value)
	
	list_solverActualRankingList.sort(key=lambda item: item[2], reverse=True)
	solver_rank = 1
	for i in range(0, len(list_solverActualRankingList)):
		solver = list_solverActualRankingList[i][0]
		solver_amc_value = list_solverActualRankingList[i][1]
		solver_rmc_value = list_solverActualRankingList[i][2]
		str_value_solverActualRankingList += '%d & %s & %.6f & %.6f \\\\ \n' % (solver_rank, solver, solver_rmc_value, solver_amc_value)
		solver_rank += 1
	
	return str_value_solverActualRankingList, str_value_actualPenaltyTime, str_value_actualPortfolioPenaltyTimeList


def get_actual_selector_related_information():
	str_value_solverActualRankingList = ''
	str_value_actualPenaltyTime = ''
	str_value_actualPortfolioPenaltyTimeList = ''
	
	if judge_complete_analysing_all_portfolio_selectors():
		str_value_solverActualRankingList, str_value_actualPenaltyTime, str_value_actualPortfolioPenaltyTimeList = get_actual_selector_related_information_from_existing_analysis_files()
		return str_value_solverActualRankingList, str_value_actualPenaltyTime, str_value_actualPortfolioPenaltyTimeList
	
	par_num = sparkle_experiments_related_help.par_num
	par_num_str = 'PAR' + str(par_num)
	
	dict_amc = {}
	
	command = r'Commands/compute_marginal_contribution.py -actual'
	output = os.popen(command).readlines()
	
	solver_rank = 1
	list_actualPortfolioPenaltyTimeList = []
	
	for myline in output:
		mylist = myline.strip().split()
		
		if len(mylist) == 12:
			if mylist[0] == 'c' and mylist[1] == 'Actual' and mylist[2] == par_num_str and mylist[3] == 'value' and mylist[4] == 'for' and mylist[5] == 'portfolio' and mylist[6] == 'selector' and mylist[7] == 'with' and mylist[8] == 'all' and mylist[9] == 'solvers' and mylist[10] == 'is':
				str_value_actualPenaltyTime = '%.6f' % (float(mylist[11]))
				continue
		
		if len(mylist) == 12:
			if mylist[0] == 'c' and mylist[1] == 'Actual' and mylist[2] == par_num_str and mylist[3] == 'value' and mylist[4] == 'for' and mylist[5] == 'portfolio' and mylist[6] == 'selector' and mylist[7] == 'excluding' and mylist[8] == 'solver' and mylist[10] == 'is':
				solver = mylist[9]
				penalty_time = mylist[11]
				#str_value_actualPortfolioPenaltyTimeList += r'\item \textbf{Actual Portfolio Selector excluding ' + solver + '}, ' + par_num_str + ': ' + penalty_time + '\n'
				#str_value_actualPortfolioPenaltyTimeList += 'Actual Portfolio Selector excluding \\emph{%s} & %.6f \\\\ \n' % (solver, float(penalty_time))
				list_actualPortfolioPenaltyTimeList.append([solver, float(penalty_time)])
				continue
		
		if len(mylist) == 12:
			if mylist[0] == 'c' and mylist[1] == 'Absolute' and mylist[2] == 'marginal' and mylist[3] == 'contribution' and mylist[4] == '(to' and mylist[5] == 'Actual' and mylist[6] == 'Selector)' and mylist[7] == 'for' and mylist[8] == 'solver' and mylist[10] == 'is':
				solver = mylist[9]
				solver_amc = mylist[11]
				dict_amc[solver] = solver_amc
				continue
		
		if len(mylist) == 5:
			if mylist[0] == r'c' and mylist[1][0] == r'#' and mylist[3] == r'Rel_Margi_Contr:':
				solver = mylist[2]
				solver_rmc = mylist[4]
				#str_value_solverActualRankingList += r'\item \textbf{' + solver + r'}, Rel_Margi_Contr: ' + solver_rmc + ', Abs_Margi_Contr: ' + dict_amc[solver] + '\n'
				str_value_solverActualRankingList += '%d & %s & %.6f & %.6f \\\\ \n' % (solver_rank, solver, float(solver_rmc), float(dict_amc[solver]))
				solver_rank += 1
				
	list_actualPortfolioPenaltyTimeList.sort(key=lambda item: item[1])
	
	for solver, penalty_time_value in list_actualPortfolioPenaltyTimeList:
		str_value_actualPortfolioPenaltyTimeList += 'Actual Portfolio Selector excluding \\emph{%s} & %.6f \\\\ \n' % (solver, penalty_time_value)
				
	return str_value_solverActualRankingList, str_value_actualPenaltyTime, str_value_actualPortfolioPenaltyTimeList



def get_dict_variable_to_value():
	mydict = {}
	
	variable = r'customCommands'
	str_value = get_customCommands()
	mydict[variable] = str_value
	
	variable = r'sparkle'
	str_value = get_sparkle()
	mydict[variable] = str_value
	
	variable = r'sparkleVersion'
	str_value = get_sparkleVersion()
	mydict[variable] = str_value
	
	variable = r'numSolvers'
	str_value = get_numSolvers()
	mydict[variable] = str_value
	
	variable = r'solverList'
	str_value = get_solverList()
	mydict[variable] = str_value
	
	variable = r'numFeatureExtractors'
	str_value = get_numFeatureExtractors()
	mydict[variable] = str_value
	
	variable = r'featureExtractorList'
	str_value = get_featureExtractorList()
	mydict[variable] = str_value
	
	variable = r'numTotalInstances'
	str_value = get_numTotalInstances()
	mydict[variable] = str_value
	
	variable = r'numInstanceClasses'
	str_value = get_numInstanceClasses()
	mydict[variable] = str_value
	
	variable = r'instanceClassList'
	str_value = get_instanceClassList()
	mydict[variable] = str_value
	
	variable = r'featureComputationCutoffTime'
	str_value = get_featureComputationCutoffTime()
	mydict[variable] = str_value
	
	variable = r'featureComputationMemoryLimit'
	str_value = get_featureComputationMemoryLimit()
	mydict[variable] = str_value
	
	variable = r'performanceComputationCutoffTime'
	str_value = get_performanceComputationCutoffTime()
	mydict[variable] = str_value
	
	variable = r'performanceComputationMemoryLimit'
	str_value = get_performanceComputationMemoryLimit()
	mydict[variable] = str_value
	
	#variable = r'solverPerfectRankingList'
	#str_value = get_solverPerfectRankingList()
	#mydict[variable] = str_value
	
	#variable = r'solverActualRankingList'
	#str_value = get_solverActualRankingList()
	#mydict[variable] = str_value
	
	dict_actual_portfolio_selector_penalty_time_on_each_instance = get_dict_actual_portfolio_selector_penalty_time_on_each_instance()
	
	variable = r'figure-portfolio-selector-sparkle-vs-sbs'
	str_value = get_figure_portfolio_selector_sparkle_vs_sbs(dict_actual_portfolio_selector_penalty_time_on_each_instance)
	mydict[variable] = str_value
	
	variable = r'figure-portfolio-selector-sparkle-vs-vbs'
	str_value = get_figure_portfolio_selector_sparkle_vs_vbs(dict_actual_portfolio_selector_penalty_time_on_each_instance)
	mydict[variable] = str_value
	
	variable = r'parNum'
	str_value = get_parNum()
	mydict[variable] = str_value
	
	variable = r'PenaltyTimeRankingList'
	str_value = get_PenaltyTimeRankingList()
	mydict[variable] = str_value
	
	#variable = r'VBSPenaltyTime'
	#str_value = get_VBSPenaltyTime()
	#mydict[variable] = str_value
	
	#variable = r'actualPenaltyTime'
	#str_value = get_actualPenaltyTime()
	#mydict[variable] = str_value
	
	str_value_solverPerfectRankingList, str_value_VBSPenaltyTime, str_value_perfectPortfolioPenaltyTimeList = get_perfect_selector_related_information()
	mydict['solverPerfectRankingList'] = str_value_solverPerfectRankingList
	mydict['VBSPenaltyTime'] = str_value_VBSPenaltyTime
	mydict['perfectPortfolioPenaltyTimeList'] = str_value_perfectPortfolioPenaltyTimeList
	
	str_value_solverActualRankingList, str_value_actualPenaltyTime, str_value_actualPortfolioPenaltyTimeList = get_actual_selector_related_information()
	mydict['solverActualRankingList'] = str_value_solverActualRankingList
	mydict['actualPenaltyTime'] = str_value_actualPenaltyTime
	mydict['actualPortfolioPenaltyTimeList'] = str_value_actualPortfolioPenaltyTimeList
	
	return mydict
	

def generate_report():
	latex_directory_path = r'Components/Sparkle-latex-generator/'
	latex_template_filename = r'template-Sparkle.tex'
	latex_report_filename = r'Sparkle_Report'
	dict_variable_to_value = get_dict_variable_to_value()
	#print(dict_variable_to_value)
	
	latex_template_filepath = latex_directory_path + latex_template_filename
	report_content = r''
	fin = open(latex_template_filepath, 'r')
	while True:
		myline = fin.readline()
		if not myline: break
		report_content += myline
	fin.close()
	
	for variable_key, str_value in dict_variable_to_value.items():
		 variable = r'@@' + variable_key + r'@@'
		 if variable_key != r'figure-portfolio-selector-sparkle-vs-sbs' and variable_key != r'figure-portfolio-selector-sparkle-vs-vbs':
		 	str_value = str_value.replace(r'_', r'\textunderscore ')
		 report_content = report_content.replace(variable, str_value)
	
	#print(report_content)
	
	latex_report_filepath = latex_directory_path + latex_report_filename + r'.tex'
	fout = open(latex_report_filepath, 'w+')
	fout.write(report_content)
	fout.close()
	
	compile_command = r'cd ' + latex_directory_path + r'; pdflatex ' + latex_report_filename + r'.tex 1> /dev/null 2>&1'
	os.system(compile_command)
	os.system(compile_command)
	
	compile_command = r'cd ' + latex_directory_path + r'; bibtex ' + latex_report_filename + r'.aux 1> /dev/null 2>&1'
	os.system(compile_command)
	os.system(compile_command)
	
	compile_command = r'cd ' + latex_directory_path + r'; pdflatex ' + latex_report_filename + r'.tex 1> /dev/null 2>&1'
	os.system(compile_command)
	os.system(compile_command)
	
	print(r'Report is placed at: ' + latex_directory_path + latex_report_filename + r'.pdf')
	
	return
	



