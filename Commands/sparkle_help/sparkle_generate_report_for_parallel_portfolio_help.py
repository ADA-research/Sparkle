#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_compute_marginal_contribution_help as scmch
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_generate_report_help as sgrh
from sparkle_help.sparkle_settings import PerformanceMeasure
import compute_marginal_contribution as cmc


def get_numSolvers(parallel_portfolio_path: str):
	solver_list = sfh.get_solver_list_from_parallel_portfolio(parallel_portfolio_path)
	num_solvers = len(solver_list)
	str_value = str(num_solvers)

	if int(str_value) < 1:
		print('ERROR: No solvers found, report generation failed!')
		sys.exit()

	return str_value

def get_solverList(parallel_portfolio_path: str):
	str_value = r''
	solver_list = sfh.get_solver_list_from_parallel_portfolio(parallel_portfolio_path)
	for solver_path in solver_list:
		solver_name = sfh.get_file_name(solver_path)
		if solver_name == "": solver_name = sfh.get_last_level_directory_name(solver_path)
		x = solver_name.rfind("_")
		if str(x) != '-1':solver_name = solver_name[:x] + '\\' + solver_name[x:]
		str_value += r'\item \textbf{' + solver_name + r'}' + '\n'
		print(str_value)
	return str_value

def get_numInstanceClasses(instances: list):
	list_instance_class = []
	instance_list = instances
	for instance_path in instance_list:
		instance_class = sfh.get_current_directory_name(instance_path)
		if not (instance_class in list_instance_class):
			list_instance_class.append(instance_class)
	str_value = str(len(list_instance_class))

	if int(str_value) < 1:
		print('ERROR: No instance sets found, report generation failed!')
		sys.exit()

	return str_value


def get_instanceClassList(instances: list):
	str_value = r''
	list_instance_class = []
	dict_number_of_instances_in_instance_class = {}
	instance_list = instances
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

def get_results():
	
	solutions_dir  = r'Performance_Data/Tmp_PaP/'
	results = sfh.get_list_all_result_filename(solutions_dir)
	# TODO functionality for multiple results.
	result_path = solutions_dir + str(results[0])
	with open(result_path, "r") as result:
		lines = result.readlines()
		
	result_lines = []
	for i in lines:
		result_lines.append(i.strip())

	return result_lines


def get_solversWithSolution():
	
	result_lines = get_results()
	str_value = ""
	instance = sfh.get_file_name(result_lines[0])
	solver = sfh.get_file_name(result_lines[1])
	duration = result_lines[2]
	#TODO #URGENT rewrite this function for multiple instances
	if sgh.settings.get_general_performance_measure() == PerformanceMeasure.QUALITY_ABSOLUTE:
		str_value += r'\item \textbf{' + instance + r'}, was scored by: ' + r'\textbf{' + solver + r'} with a score of ' + duration
	else:
		str_value += r'\item Solver \textbf{' + solver + r'}, was the best solver on ' + r'\textbf{' + '1' + r'} instance(s)'

	return str_value

def get_dict_sbs_penalty_time_on_each_instance(instances: list):
	mydict = {}

	cutoff_time = sgh.settings.get_general_target_cutoff_time()
	results = get_results()

	for instance in instances:
		#TODO Create this for multiple instances.!! SBS so get_results doesnt work anymore since it finds only the PaP results.
		this_run_time = results[2]
		if float(this_run_time) <= cutoff_time:
			mydict[instance] = this_run_time
		else:
			mydict[instance] = sgh.settings.get_penalised_time()	
	
	return mydict

# def get_dict_vbs_penalty_time_on_each_instance():
# 	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sgh.performance_data_csv_path)
# 	mydict = performance_data_csv.get_dict_vbs_penalty_time_on_each_instance()
# 	return mydict

def get_dict_actual_portfolio_selector_penalty_time_on_each_instance(parallel_portfolio_path: str, instances: str):
	mydict = {}

	cutoff_time = sgh.settings.get_general_target_cutoff_time()
	results = get_results()

	for instance in instances:
		#TODO Create this for multiple instances.!! SBS so get_results doesnt work anymore since it finds only the PaP results.
		this_run_time = results[2]
		if float(this_run_time) <= cutoff_time:
			mydict[instance] = this_run_time
		else:
			mydict[instance] = sgh.settings.get_penalised_time()	
	

	return mydict

def get_figure_parallel_portfolio_sparkle_vs_sbs(parallel_portfolio_path: str, instances: list):
	str_value = r''
	dict_sbs_penalty_time_on_each_instance = get_dict_sbs_penalty_time_on_each_instance(instances)

	print(dict_sbs_penalty_time_on_each_instance)
	dict_actual_portfolio_selector_penalty_time_on_each_instance = get_dict_actual_portfolio_selector_penalty_time_on_each_instance(parallel_portfolio_path, instances)

	latex_directory_path = r'Components/Sparkle-latex-generator-for-parallel-portfolio/'
	figure_portfolio_selector_sparkle_vs_sbs_filename = r'figure_parallel_portfolio_sparkle_vs_sbs'
	data_portfolio_selector_sparkle_vs_sbs_filename = r'data_parallel_portfolio_sparkle_vs_sbs_filename.dat'
	data_portfolio_selector_sparkle_vs_sbs_filepath = latex_directory_path + data_portfolio_selector_sparkle_vs_sbs_filename
	
	fout = open(data_portfolio_selector_sparkle_vs_sbs_filepath, 'w+')
	for instance in dict_sbs_penalty_time_on_each_instance:
		sbs_penalty_time = dict_sbs_penalty_time_on_each_instance[instance]
		sparkle_penalty_time = dict_actual_portfolio_selector_penalty_time_on_each_instance[instance]
		fout.write(str(sbs_penalty_time) + r' ' + str(sparkle_penalty_time) + '\n')
	fout.close()

	#TODO change this for multiple instances.
	result_lines = get_results()
	sbs_solver = sfh.get_file_name(result_lines[1])

	penalised_time_str = str(sgh.settings.get_penalised_time())

	gnuplot_command = r'cd ' + latex_directory_path + r'; python auto_gen_plot.py ' + data_portfolio_selector_sparkle_vs_sbs_filename + r' ' + penalised_time_str + r' ' + '\'SBS (' + sbs_solver + ')\' ' + r'Parallel-Portfolio' + r' ' + figure_portfolio_selector_sparkle_vs_sbs_filename

	#print(gnuplot_command)
	
	os.system(gnuplot_command)
	
	str_value = '\\includegraphics[width=0.6\\textwidth]{%s}' % (figure_portfolio_selector_sparkle_vs_sbs_filename)
	return str_value


# def get_figure_parallel_portfolio_sparkle_vs_vbs(parallel_portfolio_path: str):
# 	str_value = r''
# 	dict_vbs_penalty_time_on_each_instance = get_dict_vbs_penalty_time_on_each_instance()
# 	dict_actual_portfolio_selector_penalty_time_on_each_instance = get_dict_actual_portfolio_selector_penalty_time_on_each_instance(parallel_portfolio_path)
	
# 	latex_directory_path = r'Components/Sparkle-latex-generator-for-parallel-portfolio/'
# 	figure_portfolio_selector_sparkle_vs_vbs_filename = r'figure_parallel_portfolio_sparkle_vs_vbs'
# 	data_portfolio_selector_sparkle_vs_vbs_filename = r'data_parallel_portfolio_sparkle_vs_vbs_filename.dat'
# 	data_portfolio_selector_sparkle_vs_vbs_filepath = latex_directory_path + data_portfolio_selector_sparkle_vs_vbs_filename
	
# 	fout = open(data_portfolio_selector_sparkle_vs_vbs_filepath, 'w+')
# 	for instance in dict_vbs_penalty_time_on_each_instance:
# 		vbs_penalty_time = dict_vbs_penalty_time_on_each_instance[instance]
# 		sparkle_penalty_time = dict_actual_portfolio_selector_penalty_time_on_each_instance[instance]
# 		fout.write(str(vbs_penalty_time) + r' ' + str(sparkle_penalty_time) + '\n')
# 	fout.close()

# 	penalised_time_str = str(sgh.settings.get_penalised_time())
# 	gnuplot_command = r'cd ' + latex_directory_path + r'; python auto_gen_plot.py ' + data_portfolio_selector_sparkle_vs_vbs_filename + r' ' + penalised_time_str + r' ' + r'VBS' + r' ' + r'Sparkle_Selector' + r' ' + figure_portfolio_selector_sparkle_vs_vbs_filename
	
# 	os.system(gnuplot_command)
	
# 	str_value = '\\includegraphics[width=0.6\\textwidth]{%s}' % (figure_portfolio_selector_sparkle_vs_vbs_filename)
# 	return str_value


def get_dict_variable_to_value(parallel_portfolio_path: str, instances: list):
	mydict = {}

	variable = r'customCommands'
	str_value = sgrh.get_customCommands()
	mydict[variable] = str_value

	variable = r'sparkle'
	str_value = sgrh.get_sparkle()
	mydict[variable] = str_value
	
	variable = r'numSolvers'
	str_value = get_numSolvers(parallel_portfolio_path)
	mydict[variable] = str_value
	
	variable = r'solverList'
	str_value = get_solverList(parallel_portfolio_path)
	mydict[variable] = str_value
	
	variable = r'numInstanceClasses'
	str_value = get_numInstanceClasses(instances)
	mydict[variable] = str_value
	
	variable = r'instanceClassList'
	str_value = get_instanceClassList(instances)
	mydict[variable] = str_value
	
	variable = r'cutoffTime'
	str_value = sgrh.get_performanceComputationCutoffTime()
	mydict[variable] = str_value
	
	variable = r'solversWithSolution'
	str_value = get_solversWithSolution()
	mydict[variable] = str_value
	print('DEBUG ' + variable)
	variable = r'figure-parallel-portfolio-sparkle-vs-sbs'
	str_value = get_figure_parallel_portfolio_sparkle_vs_sbs(parallel_portfolio_path, instances)
	mydict[variable] = str_value
	print('DEBUG ' + variable)
	# variable = r'figure-parallel-portfolio-sparkle-vs-vbs'
	# str_value = get_figure_parallel_portfolio_sparkle_vs_vbs(parallel_portfolio_path)
	# mydict[variable] = str_value
	# print('DEBUG ' + variable)
	variable = r'testBool'
	str_value = r'\destrue'
	if sgh.settings.get_general_performance_measure() == PerformanceMeasure.QUALITY_ABSOLUTE:
		str_value = r'\desfalse'
	mydict[variable] = str_value

	return mydict


def generate_report(parallel_portfolio_path: str, instances: list):
	
	latex_report_filename = r'Sparkle_Report'
	dict_variable_to_value = get_dict_variable_to_value(parallel_portfolio_path, instances)

	latex_directory_path = r'Components/Sparkle-latex-generator-for-parallel-portfolio/'
	latex_template_filename = r'template-Sparkle.tex'

	print(dict_variable_to_value)
	
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
		report_content = report_content.replace(variable, str_value)

	#print(report_content)
	latex_report_filepath = latex_directory_path + latex_report_filename + r'.tex'
	fout = open(latex_report_filepath, 'w+')
	fout.write(report_content)
	fout.close()

	compile_command = r'cd ' + latex_directory_path + r'; pdflatex ' + latex_report_filename + r'.tex'
	os.system(compile_command)
	os.system(compile_command)

	compile_command = r'cd ' + latex_directory_path + r'; bibtex ' + latex_report_filename + r'.aux'
	os.system(compile_command)
	os.system(compile_command)

	compile_command = r'cd ' + latex_directory_path + r'; pdflatex ' + latex_report_filename + r'.tex'
	os.system(compile_command)
	os.system(compile_command)

	report_path = latex_directory_path + latex_report_filename + r'.pdf'
	print(r'Report is placed at: ' + report_path)
	sl.add_output(report_path, 'Sparkle parallel portfolio report')

	return