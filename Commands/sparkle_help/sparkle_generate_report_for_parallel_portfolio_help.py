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
import compute_marginal_contribution as cmc


def get_customCommands():
	str_value = r''
	return str_value

def get_sparkle():
	str_value = r'\emph{Sparkle}'
	return str_value

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
		str_value += r'\item \textbf{' + solver_name + r'}' + '\n'
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


def get_cutoffTime():
	str_value = str(sgh.settings.get_general_target_cutoff_time())
	return str_value


def get_results():
	# TODO Change the directory
	solutions_dir  = r'Performance_Data/Tmp/'
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
	str_value += r'\item \textbf{' + instance + r'}, was solved by: ' + r'\textbf{' + solver + r'} in ' + duration + ' seconds \n'


	return str_value

def get_figure_parallel_portfolio_vs_average_sequential(parallel_portfolio_path: str):
	str_value = r''
	
	latex_directory_path = r'Components/Sparkle-latex-generator-for-parallel-portfolio/'
	figure_best_solvers_vs_average_solver_order_filename = r'figure_best_solvers_vs_average_solver'
	data_best_solvers_vs_average_solver_order_filename = r'data_best_solvers_vs_average_solver.dat'
	data_best_solvers_vs_average_solver_order_filepath = latex_directory_path + data_best_solvers_vs_average_solver_order_filename
	
	fout = open(data_best_solvers_vs_average_solver_order_filepath, 'w+')
	result_lines = get_results()
	best_solver_time = result_lines[2]
	nr_of_solvers = get_numSolvers(parallel_portfolio_path)
	cutoff_time = get_cutoffTime()
	max_sequential_time = (int(nr_of_solvers) - 1) * int(cutoff_time) + float(best_solver_time)
	average_sequential_time = (int(nr_of_solvers) - 1)/2 * int(cutoff_time) + float(best_solver_time)
	fout.write("best_solver_time" + r' ' + str(best_solver_time) + '\n')
	fout.write("worst_case_sequential_time" + r' ' + str(max_sequential_time) + '\n')
	fout.write("average_case_sequential_time" + r' ' + str(average_sequential_time) + '\n')
	fout.close()

	gnuplot_command = r'cd ' + latex_directory_path + r'; python auto_gen_plot.py ' + data_best_solvers_vs_average_solver_order_filename + r' ' + figure_best_solvers_vs_average_solver_order_filename
	
	#print(gnuplot_command)
	print('DEBUG gnuplot_command will now be executed')
	print(gnuplot_command)
	os.system(gnuplot_command)
	print('DEBUG after gnuplot_command is executed')
	str_value = '\\includegraphics[width=0.6\\textwidth]{%s}' % (figure_best_solvers_vs_average_solver_order_filename)
	return str_value




def get_dict_variable_to_value(parallel_portfolio_path: str, instances: list):
	mydict = {}

	variable = r'customCommands'
	str_value = get_customCommands()
	mydict[variable] = str_value

	variable = r'sparkle'
	str_value = get_sparkle()
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
	str_value = get_cutoffTime()
	mydict[variable] = str_value

	variable = r'solversWithSolution'
	str_value = get_solversWithSolution()
	mydict[variable] = str_value

	variable = r'figureComputationComparison'
	str_value = get_figure_parallel_portfolio_vs_average_sequential(parallel_portfolio_path)
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