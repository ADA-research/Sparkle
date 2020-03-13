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
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_experiments_related_help
from sparkle_help import sparkle_compute_marginal_contribution_help

def get_customCommands():
	str_value = r''
	return str_value

def get_sparkle():
	str_value = r'\emph{Sparkle}'
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

def get_performanceComputationCutoffTime():
	str_value = str(sparkle_experiments_related_help.cutoff_time_each_run)
	return str_value

def get_solverPerfectRankingList():
	str_value = r''
	command = r'Commands/compute_marginal_contribution.py -perfect'
	output = os.popen(command).readlines()
	for myline in output:
		mylist = myline.strip().split()
		if len(mylist) == 5:
			if mylist[0] == r'c' and mylist[1][0] == r'#' and mylist[3] == r'Margi_Contr:':
				solver = mylist[2]
				marginal_contribution = mylist[4]
				str_value += r'\item \textbf{' + solver + r'}, marginal contribution: ' + marginal_contribution + '\n'
	return str_value

def get_solverActualRankingList():
	str_value = r''
	command = r'Commands/compute_marginal_contribution.py -actual'
	output = os.popen(command).readlines()
	for myline in output:
		mylist = myline.strip().split()
		if len(mylist) == 5:
			if mylist[0] == r'c' and mylist[1][0] == r'#' and mylist[3] == r'Margi_Contr:':
				solver = mylist[2]
				marginal_contribution = mylist[4]
				str_value += r'\item \textbf{' + solver + r'}, marginal contribution: ' + marginal_contribution + '\n'
	return str_value

def get_PAR10RankingList():
	str_value = r''
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)
	cutoff_time_each_run = sparkle_experiments_related_help.cutoff_time_each_run
	
	solver_penalty_time_ranking_list = performance_data_csv.get_solver_penalty_time_ranking_list(cutoff_time_each_run)
	
	for solver, this_penalty_time in solver_penalty_time_ranking_list:
		str_value += r'\item \textbf{' + solver + r'}, PAR10: ' + str(this_penalty_time) + '\n'
	
	return str_value


def get_VBSPAR10():
	str_value = r''
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)
	cutoff_time_each_run = sparkle_experiments_related_help.cutoff_time_each_run
	vbs_penalty_time = performance_data_csv.calc_vbs_penaltry_time(cutoff_time_each_run, 10)
	
	str_value = str(vbs_penalty_time)
	return str_value


def get_actualPAR10():
	str_value = r''
	actual_penalty_time = 0.0
	actual_count = 0
	
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)
	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(sparkle_global_help.feature_data_csv_path)
	actual_portfolio_selector_path = sparkle_global_help.sparkle_portfolio_selector_path
	cutoff_time_each_run = sparkle_experiments_related_help.cutoff_time_each_run
	penalty_time_each_run = sparkle_experiments_related_help.penalty_time
	
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
			actual_penalty_time = actual_penalty_time + used_time_for_this_instance
		else:
			actual_penalty_time = actual_penalty_time + penalty_time_each_run
		actual_count += 1
	
	actual_penalty_time = actual_penalty_time / actual_count
	str_value = str(actual_penalty_time)
	return str_value


def get_dict_sbs_penalty_time_on_each_instance():
	mydict = {}
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)
	cutoff_time_each_run = sparkle_experiments_related_help.cutoff_time_each_run
	
	solver_penalty_time_ranking_list = performance_data_csv.get_solver_penalty_time_ranking_list(cutoff_time_each_run)
	sbs_solver = solver_penalty_time_ranking_list[0][0]
	
	for instance in performance_data_csv.list_rows():
		this_run_time = performance_data_csv.get_value(instance, sbs_solver)
		if this_run_time <= cutoff_time_each_run:
			mydict[instance] = this_run_time
		else:
			mydict[instance] = sparkle_experiments_related_help.penalty_time
	return mydict


def get_dict_vbs_penalty_time_on_each_instance():
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)
	mydict = performance_data_csv.get_dict_vbs_penalty_time_on_each_instance()
	return mydict

def get_dict_actual_portfolio_selector_penalty_time_on_each_instance():
	mydict = {}
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)
	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(sparkle_global_help.feature_data_csv_path)
	actual_portfolio_selector_path = sparkle_global_help.sparkle_portfolio_selector_path
	cutoff_time_each_run = sparkle_experiments_related_help.cutoff_time_each_run
	
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
			mydict[instance] = sparkle_experiments_related_help.penalty_time
	return mydict

def get_figure_portfolio_selector_sparkle_vs_sbs():
	str_value = r''
	dict_sbs_penalty_time_on_each_instance = get_dict_sbs_penalty_time_on_each_instance()
	dict_actual_portfolio_selector_penalty_time_on_each_instance = get_dict_actual_portfolio_selector_penalty_time_on_each_instance()
	
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
	
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)
	cutoff_time_each_run = sparkle_experiments_related_help.cutoff_time_each_run
	solver_penalty_time_ranking_list = performance_data_csv.get_solver_penalty_time_ranking_list(cutoff_time_each_run)
	sbs_solver = solver_penalty_time_ranking_list[0][0]
	
	gnuplot_command = r'cd ' + latex_directory_path + r'; python auto_gen_plot.py ' + data_portfolio_selector_sparkle_vs_sbs_filename + r' ' + str(sparkle_experiments_related_help.penalty_time) + r' ' + '\'SBS (' + sbs_solver + ')\' ' + r'Sparkle_Selector' + r' ' + figure_portfolio_selector_sparkle_vs_sbs_filename
	
	#print(gnuplot_command)
	
	os.system(gnuplot_command)
	
	str_value = '\\includegraphics[width=0.6\\textwidth]{%s}' % (figure_portfolio_selector_sparkle_vs_sbs_filename)
	return str_value


def get_figure_portfolio_selector_sparkle_vs_vbs():
	str_value = r''
	dict_vbs_penalty_time_on_each_instance = get_dict_vbs_penalty_time_on_each_instance()
	dict_actual_portfolio_selector_penalty_time_on_each_instance = get_dict_actual_portfolio_selector_penalty_time_on_each_instance()
	
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
	
	gnuplot_command = r'cd ' + latex_directory_path + r'; python auto_gen_plot.py ' + data_portfolio_selector_sparkle_vs_vbs_filename + r' ' + str(sparkle_experiments_related_help.penalty_time) + r' ' + r'VBS' + r' ' + r'Sparkle_Selector' + r' ' + figure_portfolio_selector_sparkle_vs_vbs_filename
	
	os.system(gnuplot_command)
	
	str_value = '\\includegraphics[width=0.6\\textwidth]{%s}' % (figure_portfolio_selector_sparkle_vs_vbs_filename)
	return str_value



def get_dict_variable_to_value():
	mydict = {}
	
	variable = r'customCommands'
	str_value = get_customCommands()
	mydict[variable] = str_value
	
	variable = r'sparkle'
	str_value = get_sparkle()
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
	
	variable = r'numInstanceClasses'
	str_value = get_numInstanceClasses()
	mydict[variable] = str_value
	
	variable = r'instanceClassList'
	str_value = get_instanceClassList()
	mydict[variable] = str_value
	
	variable = r'featureComputationCutoffTime'
	str_value = get_featureComputationCutoffTime()
	mydict[variable] = str_value
	
	variable = r'performanceComputationCutoffTime'
	str_value = get_performanceComputationCutoffTime()
	mydict[variable] = str_value
	
	variable = r'solverPerfectRankingList'
	str_value = get_solverPerfectRankingList()
	mydict[variable] = str_value
	
	variable = r'solverActualRankingList'
	str_value = get_solverActualRankingList()
	mydict[variable] = str_value
	
	variable = r'figure-portfolio-selector-sparkle-vs-sbs'
	str_value = get_figure_portfolio_selector_sparkle_vs_sbs()
	mydict[variable] = str_value
	
	variable = r'figure-portfolio-selector-sparkle-vs-vbs'
	str_value = get_figure_portfolio_selector_sparkle_vs_vbs()
	mydict[variable] = str_value
	
	variable = r'PAR10RankingList'
	str_value = get_PAR10RankingList()
	mydict[variable] = str_value
	
	variable = r'VBSPAR10'
	str_value = get_VBSPAR10()
	mydict[variable] = str_value
	
	variable = r'actualPAR10'
	str_value = get_actualPAR10()
	mydict[variable] = str_value
	
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
	



