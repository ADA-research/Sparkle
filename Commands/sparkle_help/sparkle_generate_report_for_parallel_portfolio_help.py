#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
from datetime import datetime, timedelta
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
	# If a solver contains multiple solver_variations.
	for solver in solver_list:
		if ' ' in solver:
			num_solvers += int(solver[solver.rfind(' ')+1:]) - 1
	
	str_value = str(num_solvers)

	if int(str_value) < 1:
		print('ERROR: No solvers found, report generation failed!')
		sys.exit()

	return str_value

def get_solverList(parallel_portfolio_path: str):
	str_value = r''
	
	solver_list = sfh.get_solver_list_from_parallel_portfolio(parallel_portfolio_path)
	for solver_path in solver_list:
		solver_variations = 0
		if ' ' in solver_path:
			solver_variations = int(solver_path[solver_path.rfind(' ')+1:])
			solver_path = solver_path[:solver_path.rfind(' ')]
		solver_name = sfh.get_file_name(solver_path)
		if solver_name == "": solver_name = sfh.get_last_level_directory_name(solver_path)
		x = solver_name.rfind("_")
		if str(x) != '-1':solver_name = solver_name[:x] + '\\' + solver_name[x:]
		str_value += r'\item \textbf{' + sgrh.underscore_for_latex(solver_name) + r'}' + '\n'
		if solver_variations > 1:
			seed_number = r''
			for instances in range(1,solver_variations+1):
				seed_number += str(instances) 
				if instances != solver_variations: seed_number += r','
			str_value += r'\item[] With seeds: ' + seed_number + '\n'
		print(str_value)
	return str_value

def get_numInstanceClasses(instances: list):
	list_instance_class = []
	instance_list = eval(str(instances[0]))
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
	nr_of_instances = 0
	list_instance_class = []
	dict_number_of_instances_in_instance_class = {}
	instance_list = eval(str(instances[0]))
	for instance_path in instance_list:
		instance_class = sfh.get_current_directory_name(instance_path)
		if not (instance_class in list_instance_class):
			list_instance_class.append(instance_class)
			dict_number_of_instances_in_instance_class[instance_class] = 1
		else:
			dict_number_of_instances_in_instance_class[instance_class] += 1

	for instance_class in list_instance_class:
		str_value += r'\item \textbf{' + sgrh.underscore_for_latex(instance_class) + r'}, number of instances: ' + str(dict_number_of_instances_in_instance_class[instance_class]) + '\n'
		nr_of_instances += int(dict_number_of_instances_in_instance_class[instance_class])
	return str_value, str(nr_of_instances)

def get_results():
	# TODO add check if instance and solver listed in the result are part of the job
	solutions_dir  = r'Performance_Data/Tmp_PaP/'
	results = sfh.get_list_all_result_filename(solutions_dir)
	results_dict = dict()
	for result in results:
		result_path = solutions_dir + str(result)
		with open(result_path, "r") as result_file:
			lines = result_file.readlines()
			
		result_lines = []
		for i in lines:
			result_lines.append(i.strip())
		if len(result_lines) == 3:
			instance = sfh.get_last_level_directory_name(result_lines[0])
			if instance in results_dict:
				if float(results_dict[instance][1]) > float(result_lines[2]):
					results_dict[instance][0] = result_lines[1]
					results_dict[instance][1] = result_lines[2]
			else:
				results_dict[instance] = [result_lines[1],result_lines[2]]
	
	return results_dict


def get_solversWithSolution():
	
	results_on_instances = get_results()
	str_value = ""
	if sgh.settings.get_general_performance_measure() != PerformanceMeasure.QUALITY_ABSOLUTE:
		solver_dict = dict()
		unsolved_instances = 0
		for instances in results_on_instances:
			solver_name = sfh.get_file_name(results_on_instances[instances][0])
			cutoff_time = str(sgh.settings.get_general_target_cutoff_time() * 10)

			if results_on_instances[instances][1] != cutoff_time:
				if '_seed_' in solver_name:
					solver_name = solver_name[:solver_name.rfind('_seed_')+7]
				if solver_name in solver_dict:
					solver_dict[solver_name] = solver_dict[solver_name] + 1
				else: 
					solver_dict[solver_name] = 1
			else:
				unsolved_instances += 1

	if sgh.settings.get_general_performance_measure() == PerformanceMeasure.QUALITY_ABSOLUTE:
		for instances in results_on_instances:
			str_value += r'\item \textbf{' + sgrh.underscore_for_latex(instances) + r'}, was scored by: ' + r'\textbf{' + sgrh.underscore_for_latex(sfh.get_last_level_directory_name(results_on_instances[instances][0])) + r'} with a score of ' + str(results_on_instances[instances][1])
	else:
		for solver in solver_dict:
			str_value += r'\item Solver \textbf{' + sgrh.underscore_for_latex(solver) + r'}, was the best solver on ' + r'\textbf{' + str(solver_dict[solver]) + r'} instance(s)'
		if unsolved_instances:
			str_value += r'\item \textbf{' + str(unsolved_instances) + r'} instance(s) remained unsolved'

	return str_value, solver_dict, unsolved_instances

def get_dict_sbs_penalty_time_on_each_instance(parallel_portfolio_path: str, instances: list):
	mydict = {}
	# This is for the single best solver!! so count everything for every solver!!
	cutoff_time = sgh.settings.get_general_target_cutoff_time()
	results = get_results()
	solver_list = sfh.get_solver_list_from_parallel_portfolio(parallel_portfolio_path)
	for lines in solver_list:
		full_solver_list = []
		if ' ' in lines:
			for solver_variations in range(1,int(lines[lines.rfind(' ')+1:])+1):
				solver_path = lines[:lines.rfind(' ')]
				solver_variation = sfh.get_last_level_directory_name(solver_path)
				if '/' in solver_variation: solver_variation = solver_variation[:solver_variation.rfind('/')]
				solver_variation = r'Tmp/' + solver_variation + r'_seed_' + str(solver_variations)
				full_solver_list.append(solver_variation)
		else: 
			full_solver_list.append(lines)

	# Find single best solver
	instance_list = eval(str(instances[0]))
	for instance in instance_list:
		instance_name = sfh.get_last_level_directory_name(instance)
		if instance_name in results:
			this_run_time = results[instance_name][1]
			if float(this_run_time) <= cutoff_time:
				for solver in full_solver_list:
					# in because the solver name contains the instance name aswell
					if solver in results[instance_name][0]:
						if solver in mydict:
							mydict[solver] += float(this_run_time)
						else:
							mydict[solver] = float(this_run_time)
					else:
						if solver in mydict:
							mydict[solver] += float(sgh.settings.get_penalised_time())
						else:
							mydict[solver] = float(sgh.settings.get_penalised_time())
			else:
				for solver in full_solver_list:
					if solver in mydict:
						mydict[solver] += float(sgh.settings.get_penalised_time())
					else:
						mydict[solver] = float(sgh.settings.get_penalised_time())
		else:
			for solver in full_solver_list:
				if solver in mydict:
					mydict[solver] += float(sgh.settings.get_penalised_time())
				else:
					mydict[solver] = float(sgh.settings.get_penalised_time())
	sbs_name = min(mydict, key=mydict.get)
	sbs_name = sfh.get_last_level_directory_name(sbs_name)
	sbs_dict = {}
	for instance in instance_list:
		instance_name = sfh.get_last_level_directory_name(instance)
		if sbs_name in results[instance_name][0]:
			sbs_dict[instance_name] = results[instance_name][1]
		else:
			sbs_dict[instance_name] = sgh.settings.get_penalised_time()
	print(sbs_dict)
	return sbs_dict,sbs_name, mydict

def get_dict_actual_portfolio_selector_penalty_time_on_each_instance(instances: str):
	mydict = {}

	cutoff_time = sgh.settings.get_general_target_cutoff_time()
	results = get_results()
	instance_list = eval(str(instances[0]))
	for instance in instance_list:
		instance_name = sfh.get_last_level_directory_name(instance)
		if instance_name in results:
			if float(results[instance_name][1]) <= cutoff_time:
				mydict[instance_name] = float(results[instance_name][1])
			else:
				mydict[instance_name] = sgh.settings.get_penalised_time()
		else:
			mydict[instance_name] = sgh.settings.get_penalised_time()	
	
	return mydict

def get_figure_parallel_portfolio_sparkle_vs_sbs(parallel_portfolio_path: str, instances: list):
	str_value = r''
	dict_sbs_penalty_time_on_each_instance, sbs_solver, dict_all_solvers = get_dict_sbs_penalty_time_on_each_instance(parallel_portfolio_path, instances)
	dict_actual_portfolio_selector_penalty_time_on_each_instance = get_dict_actual_portfolio_selector_penalty_time_on_each_instance(instances)

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

	penalised_time_str = str(sgh.settings.get_penalised_time())

	gnuplot_command = r'cd ' + latex_directory_path + r'; python auto_gen_plot.py ' + data_portfolio_selector_sparkle_vs_sbs_filename + r' ' + penalised_time_str + r' ' + '\'SBS (' + sgrh.underscore_for_latex(sbs_solver) + ')\' ' + r'Parallel-Portfolio' + r' ' + figure_portfolio_selector_sparkle_vs_sbs_filename

	#print(gnuplot_command)
	
	os.system(gnuplot_command)
	
	str_value = '\\includegraphics[width=0.6\\textwidth]{%s}' % (figure_portfolio_selector_sparkle_vs_sbs_filename)
	return str_value, dict_all_solvers, dict_actual_portfolio_selector_penalty_time_on_each_instance

def get_wallclock_time(portfolio_path: str):
	logging_file = str(portfolio_path) + '/logging.txt'
	with open(logging_file, "r") as result_file:
		lines = result_file.readlines()
	start_time = r''
	end_time = r''
	for line in lines:
		if "starting time of portfolio" in line.strip():
			start_time = line[line.rfind(' ')+1:].strip()
		if "ending time of portfolio" in line.strip():
			end_time = line[line.rfind(' ')+1:].strip()
	if start_time and end_time:
		FMT = '%H:%M:%S'
		time_difference = datetime.strptime(end_time, FMT) - datetime.strptime(start_time, FMT)
		if time_difference.days < 0:
			time_difference = timedelta(days=0,seconds=time_difference.seconds,microseconds=time_difference.microseconds)
	return str(time_difference)

def get_runtime(portfolio_path: str, nr_of_jobs: int):
	logging_file = str(portfolio_path) + '/logging2.txt'
	with open(logging_file, "r") as result_file:
		lines = result_file.readlines()
	runtime_jobs = {}
	cutoff_time = sgh.settings.get_general_target_cutoff_time()
	for line in lines:
		line = line.strip()
		if ':' in line:
			job_nr = line[:line.rfind(':')]
			job_runtime = int(line[line.rfind(':')+1:])
			if job_nr in runtime_jobs:
				if int(runtime_jobs[job_nr]) > job_runtime:
					runtime_jobs[job_nr] = job_runtime
			else:
				if int(job_runtime) > int(cutoff_time):
					job_runtime = cutoff_time
				runtime_jobs[job_nr] = job_runtime
	total_runtime = 0
	for job in runtime_jobs:
		total_runtime += runtime_jobs[job]
	if len(runtime_jobs) < nr_of_jobs:
		total_runtime += cutoff_time * (nr_of_jobs - len(runtime_jobs))
	str_total_runtime = str(timedelta(seconds=int(total_runtime)))
	
	return str_total_runtime

def get_resultsTable(dict_all_solvers: dict, parallel_portfolio_path: str, dict_portfolio: dict, solver_with_solutions: dict, unsolved_instances: str, instances: str):
	portfolio_PAR10 = 0.0
	for instance in dict_portfolio:
		portfolio_PAR10 += dict_portfolio[instance]
	results = dict_all_solvers
	# Table 1: Portfolio results
	table_string = "\\caption *{\\textbf{Portfolio results}} \\label{tab:portfolio_results} "
	table_string += "\\begin{tabular}{rrrrr}"
	table_string += "\\textbf{Portfolio nickname} & \\textbf{PAR10} & \\textbf{\\#Timeouts} & \\textbf{\\#Cancelled} & \\textbf{\\#Best solver} \\\\ \\hline "
	table_string += sgrh.underscore_for_latex(sfh.get_last_level_directory_name(parallel_portfolio_path)) + " & " + str(round(portfolio_PAR10,2)) + " & " + str(unsolved_instances) + " & 0" + " & " + str(int(instances)-int(unsolved_instances)) + " \\\\ "
	table_string += "\\end{tabular}"
	table_string += "\\bigskip"
	# Table 2: Solver results
	table_string += "\\caption *{\\textbf{Solver results}} \\label{tab:solver_results} "
	table_string += "\\begin{tabular}{rrrrr}"
	for i,line in enumerate(results):
		solver_name = sfh.get_last_level_directory_name(line)
		if i == 0:
			table_string += "\\textbf{Solver} & \\textbf{PAR10} & \\textbf{\\#Timeouts} & \\textbf{\\#Cancelled} & \\textbf{\\#Best solver} \\\\ \\hline "
		if solver_name not in solver_with_solutions:
			cancelled = int(instances) - int(unsolved_instances)
			table_string += sgrh.underscore_for_latex(solver_name) + " & " + str(round(results[line], 2)) + " & " + str(unsolved_instances) + " & " + str(cancelled) + " & 0 " + " \\\\ "
		else:
			cancelled = int(instances) - int(unsolved_instances) - int(solver_with_solutions[solver_name])
			table_string += sgrh.underscore_for_latex(solver_name) + " & " + str(round(results[line], 2)) + " & " + str(unsolved_instances) + " & " + str(cancelled) + " & " + str(solver_with_solutions[solver_name]) + " \\\\ "
	table_string += "\\end{tabular}"
	# Table 3: Process duration results
	table_string += "\\caption *{\\textbf{Process duration results}} \\label{tab:process_duration_results} "
	table_string += "\\begin{tabular}{rr}"
	table_string += "\\textbf{Variations} & \\textbf{Duration} \\\\ \\hline "
	table_string += "Total runtime & " + str(get_runtime(parallel_portfolio_path, (int(instances)*len(results)))) + "\\\\"
	table_string += "Wallclock time & " + str(get_wallclock_time(parallel_portfolio_path)) + "\\\\"
	table_string += "\\end{tabular}"
	return table_string


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
	str_value, nr_of_instances = get_instanceClassList(instances)
	mydict[variable] = str_value
	
	variable = r'cutoffTime'
	str_value = str(sgh.settings.get_general_target_cutoff_time())
	mydict[variable] = str_value
	
	variable = r'solversWithSolution'
	str_value, solvers_with_solution, unsolved_instances = get_solversWithSolution()
	mydict[variable] = str_value

	variable = r'figure-parallel-portfolio-sparkle-vs-sbs'
	str_value, dict_all_solvers, dict_actual_portfolio_selector_penalty_time_on_each_instance = get_figure_parallel_portfolio_sparkle_vs_sbs(parallel_portfolio_path, instances)
	mydict[variable] = str_value

	variable = r'resultsTable'
	str_value = get_resultsTable(dict_all_solvers, parallel_portfolio_path, dict_actual_portfolio_selector_penalty_time_on_each_instance, solvers_with_solution, unsolved_instances, nr_of_instances)
	mydict[variable] = str_value

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