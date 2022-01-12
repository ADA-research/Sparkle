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
import pickle
import numpy as np
from shutil import which
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


def get_numSolvers():
	num_solvers = len(sgh.solver_list)
	str_value = str(num_solvers)

	if int(str_value) < 1:
		print('ERROR: No solvers found, report generation failed!')
		sys.exit()

	return str_value


def get_solverList():
	str_value = r''
	solver_list = sgh.solver_list
	for solver_path in solver_list:
		solver_name = sfh.get_file_name(solver_path)
		str_value += r'\item \textbf{' + solver_name + r'}' + '\n'
	return str_value


def get_numFeatureExtractors():
	num_feature_extractors = len(sgh.extractor_list)
	str_value = str(num_feature_extractors)

	if int(str_value) < 1:
		print('ERROR: No feature extractors found, report generation failed!')
		sys.exit()

	return str_value


def get_featureExtractorList():
	str_value = r''
	extractor_list = sgh.extractor_list
	for extractor_path in extractor_list:
		extractor_name = sfh.get_file_name(extractor_path)
		str_value += r'\item \textbf{' + extractor_name + r'}' + '\n'
	return str_value


def get_numInstanceClasses():
	list_instance_class = []
	instance_list = sgh.instance_list
	for instance_path in instance_list:
		instance_class = sfh.get_current_directory_name(instance_path)
		if not (instance_class in list_instance_class):
			list_instance_class.append(instance_class)
	str_value = str(len(list_instance_class))

	if int(str_value) < 1:
		print('ERROR: No instance sets found, report generation failed!')
		sys.exit()

	return str_value


def get_instanceClassList():
	str_value = r''
	list_instance_class = []
	dict_number_of_instances_in_instance_class = {}
	instance_list = sgh.instance_list
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
	str_value = str(sgh.settings.get_general_extractor_cutoff_time())
	return str_value


def get_performanceComputationCutoffTime():
	str_value = str(sgh.settings.get_general_target_cutoff_time())
	return str_value


def get_solverPerfectRankingList():
	rank_list = cmc.compute_perfect()
	str_value = r''

	for i in range(0, len(rank_list)):
		solver = rank_list[i][0]
		solver = sfh.get_file_name(solver)
		marginal_contribution = str(rank_list[i][1])
		str_value += r'\item \textbf{' + solver + r'}, marginal contribution: ' + marginal_contribution + '\n'
	return str_value


def get_solverActualRankingList():
	rank_list = cmc.compute_actual()
	str_value = r''

	for i in range(0, len(rank_list)):
		solver = rank_list[i][0]
		solver = sfh.get_file_name(solver)
		marginal_contribution = str(rank_list[i][1])
		str_value += r'\item \textbf{' + solver + r'}, marginal contribution: ' + marginal_contribution + '\n'
	return str_value


def get_PAR10RankingList():
	str_value = r''
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sgh.performance_data_csv_path)

	solver_penalty_time_ranking_list = performance_data_csv.get_solver_penalty_time_ranking_list()
	
	for solver, this_penalty_time in solver_penalty_time_ranking_list:
		solver = sfh.get_file_name(solver)
		str_value += r'\item \textbf{' + solver + r'}, PAR10: ' + str(this_penalty_time) + '\n'
	
	return str_value


def get_VBSPAR10():
	str_value = r''
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sgh.performance_data_csv_path)
	vbs_penalty_time = performance_data_csv.calc_vbs_penalty_time()
	
	str_value = str(vbs_penalty_time)
	return str_value


def get_actualPAR10():
	performance_dict = get_dict_actual_portfolio_selector_penalty_time_on_each_instance()
	mean_performance = sum(performance_dict.values()) / len(performance_dict)
	return str(mean_performance)


def get_dict_sbs_penalty_time_on_each_instance():
	mydict = {}
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sgh.performance_data_csv_path)
	cutoff_time = sgh.settings.get_general_target_cutoff_time()
	
	solver_penalty_time_ranking_list = performance_data_csv.get_solver_penalty_time_ranking_list()
	sbs_solver = solver_penalty_time_ranking_list[0][0]
	
	for instance in performance_data_csv.list_rows():
		this_run_time = performance_data_csv.get_value(instance, sbs_solver)
		if this_run_time <= cutoff_time:
			mydict[instance] = this_run_time
		else:
			mydict[instance] = sgh.settings.get_penalised_time()
	return mydict


def get_dict_vbs_penalty_time_on_each_instance():
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sgh.performance_data_csv_path)
	mydict = performance_data_csv.get_dict_vbs_penalty_time_on_each_instance()
	return mydict


def get_dict_actual_portfolio_selector_penalty_time_on_each_instance():
	# FOR DEBUGGING
	if os.path.isfile("cache.pickle"):
		try:
			fh = open("cache.pickle", "rb")
			mydict = pickle.load(fh)
			fh.close()
			return mydict
		except:
			pass

	mydict = {}
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sgh.performance_data_csv_path)
	actual_portfolio_selector_path = sgh.sparkle_portfolio_selector_path

	for instance in performance_data_csv.list_rows():
		used_time_for_this_instance, flag_successfully_solving = scmch.compute_actual_used_time_for_instance(actual_portfolio_selector_path, instance, sgh.feature_data_csv_path, performance_data_csv)

		if flag_successfully_solving:
			mydict[instance] = used_time_for_this_instance
		else:
			mydict[instance] = sgh.settings.get_penalised_time()

	# FOR DEBUGGING
	fh = open("cache.pickle", "wb")
	pickle.dump(mydict, fh)
	fh.close()

	return mydict


def get_figure_portfolio_selector_sparkle_vs_sbs():
	dict_sbs_penalty_time_on_each_instance = get_dict_sbs_penalty_time_on_each_instance()
	dict_actual_portfolio_selector_penalty_time_on_each_instance = get_dict_actual_portfolio_selector_penalty_time_on_each_instance()

	instances = dict_sbs_penalty_time_on_each_instance.keys() & dict_actual_portfolio_selector_penalty_time_on_each_instance.keys()
	assert (len(dict_sbs_penalty_time_on_each_instance) == len(instances))
	points = []
	for instance in instances:
		point = [dict_sbs_penalty_time_on_each_instance[instance], dict_actual_portfolio_selector_penalty_time_on_each_instance[instance]]
		points.append(point)

	latex_directory_path = r'Components/Sparkle-latex-generator/'
	figure_portfolio_selector_sparkle_vs_sbs_filename = r'figure_portfolio_selector_sparkle_vs_sbs'
	
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sgh.performance_data_csv_path)
	solver_penalty_time_ranking_list = performance_data_csv.get_solver_penalty_time_ranking_list()
	sbs_solver = solver_penalty_time_ranking_list[0][0]
	sbs_solver = sfh.get_file_name(sbs_solver)

	generate_comparison_plot(points,
							 figure_portfolio_selector_sparkle_vs_sbs_filename,
							 xlabel=f"SBS ({sbs_solver}) [PAR10]",
							 ylabel="Sparkle Selector [PAR10]",
							 limit="magnitude",
							 limit_min=0.25,
							 limit_max=0.25,
							 penalty_time=sgh.settings.get_penalised_time(),
							 cwd=latex_directory_path)
	str_value = '\\includegraphics[width=0.6\\textwidth]{%s}' % (figure_portfolio_selector_sparkle_vs_sbs_filename)
	return str_value


def get_figure_portfolio_selector_sparkle_vs_vbs():
	dict_vbs_penalty_time_on_each_instance = get_dict_vbs_penalty_time_on_each_instance()
	dict_actual_portfolio_selector_penalty_time_on_each_instance = get_dict_actual_portfolio_selector_penalty_time_on_each_instance()

	instances = dict_vbs_penalty_time_on_each_instance.keys() & dict_actual_portfolio_selector_penalty_time_on_each_instance.keys()
	assert (len(dict_vbs_penalty_time_on_each_instance) == len(instances))
	points = []
	for instance in instances:
		point = [dict_vbs_penalty_time_on_each_instance[instance],
				 dict_actual_portfolio_selector_penalty_time_on_each_instance[instance]]
		points.append(point)
	
	latex_directory_path = r'Components/Sparkle-latex-generator/'
	figure_portfolio_selector_sparkle_vs_vbs_filename = r'figure_portfolio_selector_sparkle_vs_vbs'

	generate_comparison_plot(points,
							 figure_portfolio_selector_sparkle_vs_vbs_filename,
							 xlabel=f"VBS [PAR10]",
							 ylabel="Sparkle Selector [PAR10]",
							 limit="magnitude",
							 limit_min=0.25,
							 limit_max=0.25,
							 penalty_time=sgh.settings.get_penalised_time(),
							 cwd=latex_directory_path)

	str_value = '\\includegraphics[width=0.6\\textwidth]{%s}' % (figure_portfolio_selector_sparkle_vs_vbs_filename)
	return str_value


def get_testInstanceClass(test_case_directory: str):
	str_value = sfh.get_last_level_directory_name(test_case_directory)
	str_value = r'\textbf{' + str_value + r'}'
	return str_value


def get_numInstanceInTestInstanceClass(test_case_directory: str):
	str_value = r''
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(test_case_directory + r'sparkle_performance_data.csv')
	str_value = str(len(performance_data_csv.list_rows()))
	return str_value


def get_testActualPAR10(test_case_directory: str):
	str_value = r''
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(test_case_directory + r'sparkle_performance_data.csv')
	solver = performance_data_csv.list_columns()[0]
	
	cutoff_time_each_run = sgh.settings.get_general_target_cutoff_time()
	
	sparkle_penalty_time = 0.0
	sparkle_penalty_time_count = 0
	
	for instance in performance_data_csv.list_rows():
		this_run_time = performance_data_csv.get_value(instance, solver)
		sparkle_penalty_time_count += 1
		if this_run_time <= cutoff_time_each_run:
			sparkle_penalty_time += this_run_time
		else:
			sparkle_penalty_time += sgh.settings.get_penalised_time()
	
	sparkle_penalty_time = sparkle_penalty_time / sparkle_penalty_time_count
	str_value = str(sparkle_penalty_time)
	return str_value


def get_dict_variable_to_value(test_case_directory: str = None):
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

	variable = r'PAR10RankingList'
	str_value = get_PAR10RankingList()
	mydict[variable] = str_value

	variable = r'VBSPAR10'
	str_value = get_VBSPAR10()
	mydict[variable] = str_value

	variable = r'actualPAR10'
	str_value = get_actualPAR10()
	mydict[variable] = str_value

	variable = r'figure-portfolio-selector-sparkle-vs-sbs'
	str_value = get_figure_portfolio_selector_sparkle_vs_sbs()
	mydict[variable] = str_value

	variable = r'figure-portfolio-selector-sparkle-vs-vbs'
	str_value = get_figure_portfolio_selector_sparkle_vs_vbs()
	mydict[variable] = str_value

	variable = r'testBool'
	str_value = r'\testfalse'
	mydict[variable] = str_value

	# Train and test
	if test_case_directory is not None:
		variable = r'testInstanceClass'
		str_value = get_testInstanceClass(test_case_directory)
		mydict[variable] = str_value
	
		variable = r'numInstanceInTestInstanceClass'
		str_value = get_numInstanceInTestInstanceClass(test_case_directory)
		mydict[variable] = str_value
	
		variable = r'testActualPAR10'
		str_value = get_testActualPAR10(test_case_directory)
		mydict[variable] = str_value

		variable = r'testBool'
		str_value = r'\testtrue'
		mydict[variable] = str_value

	return mydict


def generate_report(test_case_directory: str = None):
	# Include results on the test set if a test case directory is given
	if test_case_directory is not None:
		if not os.path.exists(test_case_directory):
			print('ERROR: The given directory', test_case_directory, 'does not exist!')
			sys.exit(-1)

		if test_case_directory[-1] != r'/':
			test_case_directory += r'/'

		latex_report_filename = r'Sparkle_Report_for_Test'
		dict_variable_to_value = get_dict_variable_to_value(test_case_directory)
	# Only look at the training instance set(s)
	else:
		latex_report_filename = r'Sparkle_Report'
		dict_variable_to_value = get_dict_variable_to_value()

	latex_directory_path = r'Components/Sparkle-latex-generator/'
	latex_template_filename = r'template-Sparkle.tex'

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

	compile_command = r'cd ' + latex_directory_path + r'; pdflatex -interaction=nonstopmode ' + latex_report_filename + r'.tex 1> /dev/null 2>&1'
	os.system(compile_command)
	os.system(compile_command)

	compile_command = r'cd ' + latex_directory_path + r'; bibtex ' + latex_report_filename + r'.aux 1> /dev/null 2>&1'
	os.system(compile_command)
	os.system(compile_command)

	compile_command = r'cd ' + latex_directory_path + r'; pdflatex -interaction=nonstopmode ' + latex_report_filename + r'.tex 1> /dev/null 2>&1'
	os.system(compile_command)
	os.system(compile_command)

	report_path = latex_directory_path + latex_report_filename + r'.pdf'
	print(r'Report is placed at: ' + report_path)
	sl.add_output(report_path, 'Sparkle portfolio selector report')

	return


'''
	Helper function to create comparison plots between two different solvers/portfolios

	Arguments:
	points: list of points which represents with the performance results of (solverA, solverB)
	xlabel: Name of solverA (default: default)
	ylabel: Name of solverB (default: optimised)
	title: Display title in the image (default: None)
	scale: [linear, log] (default: linear)

	limit: Approach of choosing limits for the figure [absolute, relative, magnitude] (default: relative)
		absolute: Takes the absolute value as min/max
		relative: Multiplies the min/max value from the points and divides/multiplies the value with those for min/max
		magnitude: Increases the order of magnitude(10) of the min/max values in the points
	limit_min, limit_max: values used to compute the limits
	output: filepath to save the figure
	penalty_time: Acts a the maximum value the figure takes in consideration for computing the figure limits
	drop_zeros: Remove points with a value of 0
	magnitude_lines: Draw magnitude lines (only supported for log scale)
	cwd: working directory to place the figure 
'''
def generate_comparison_plot(points,
							 output_file,
							 xlabel: str = "default",
							 ylabel: str = "optimised",
							 title: str = "",
							 scale: str = "log",
							 limit: str = "magnitude",
							 limit_min: float = 0.2,
							 limit_max: float = 0.2,
							 penalty_time: float = None,
							 drop_zeros: bool= True,
							 magnitude_lines = sgh.sparkle_maximum_int,
							 cwd=None):

	pwd = os.getcwd()
	if cwd is not None:
		os.chdir(cwd)
		print("Changed cwd to {}".format(os.getcwd()))

	points = np.array(points)
	if drop_zeros:
		zero_runtime = 0.000001 #microsecond
		check_zeros = np.count_nonzero(points <= 0)
		if check_zeros != 0:
			print(f"WARNING: Zero or negative valued performance values detected. Setting these values to {zero_runtime}.")
		points[points == 0] = zero_runtime

	# process labels
	# TODO handle other special characters like $^
	xlabel = xlabel.replace("_", "\\_")  # LaTeX save formatting
	ylabel = ylabel.replace("_", "\\_")  # LaTeX save formatting

	# process range values
	min_point_value = np.min(points)
	max_point_value = np.max(points)
	if penalty_time is not None:
		assert penalty_time >= max_point_value
		max_point_value = penalty_time

	if limit == "absolute":
		min_value = limit_min
		max_value = limit_max
	elif limit == "relative":
		min_value = min_point_value * (1 / limit_min) if min_point_value > 0 else min_point_value * limit_min
		max_value = max_point_value * limit_max if max_point_value > 0 else max_point_value * (1 / limit_max)
	elif limit == "magnitude":
		min_value = 10 ** (np.floor(np.log10(min_point_value))-limit_min)
		max_value = 10 ** (np.ceil(np.log10(max_point_value))+limit_max)

	if scale == "log" and np.min(points) <= 0:
		raise Exception("Cannot plot negative and zero values on a log scales")

	output_data_file = f"{output_file}.dat"
	output_gnuplot_script = f"{output_file}.plt"
	output_eps_file = f"{output_file}.eps"

	# Create data file
	fout = open(output_data_file, 'w')
	for point in points:
		fout.write(" ".join([str(c) for c in point]) + "\n")
	fout.close()

	# Generate plots script
	fout = open(output_gnuplot_script, 'w')
	fout.write(f"set xlabel '{xlabel}'\n")
	fout.write(f"set ylabel '{ylabel}'\n")
	fout.write(f"set title '{title}'\n")
	fout.write("unset key\n")
	fout.write(f"set xrange [{min_value}:{max_value}]\n")
	fout.write(f"set yrange [{min_value}:{max_value}]\n")
	if scale == "log":
		fout.write("set logscale x\n")
		fout.write("set logscale y\n")
	fout.write("set grid lc rgb '#CCCCCC' lw 2\n")
	fout.write("set size square\n")
	fout.write(f"set arrow from {min_value},{min_value} to {max_value},{max_value} nohead lc rgb 'black'\n")
	#TODO magnitude lines for linear scale
	if magnitude_lines > 0 and scale == "log":
		for order in range(magnitude_lines):
			order += 1
			min_shift = min_value * 10 ** order
			max_shift = 10**(np.log10(max_value)-order)

			if min_shift >= max_value: #Outside plot
				break

			fout.write(f"set arrow from {min_value},{min_shift} to {max_shift},{max_value} nohead lc rgb '#CCCCCC' dashtype '-'\n")
			fout.write(f"set arrow from {min_shift},{min_value} to {max_value},{max_shift} nohead lc rgb '#CCCCCC' dashtype '-'\n")

	if penalty_time is not None:
		fout.write(f"set arrow from {min_value},{penalty_time} to {max_value},{penalty_time} nohead lc rgb '#AAAAAA'\n")
		fout.write(f"set arrow from {penalty_time},{min_value} to {penalty_time},{max_value} nohead lc rgb '#AAAAAA'\n")

	# fout.write('set arrow from 0.01,0.01 to %s,%s nohead lc rgb \'black\'' % (penalty_time, penalty_time) + '\n')
	fout.write("set terminal postscript eps color solid linewidth \"Helvetica\" 20\n")
	fout.write(f"set output '{output_eps_file}\n")
	fout.write(f"set style line 1 pt 3 lc rgb 'blue' \n")
	fout.write(f"plot '{output_data_file}' ls 1\n")
	fout.close()

	# Make figure
	cmd = "gnuplot \'%s\'" % (output_gnuplot_script)
	os.system(cmd)

	# Some systems are missing epstopdf so a copy is included
	epsbackup = os.path.join(os.path.abspath(pwd), "Components/epstopdf.pl")
	epstopdf = which("epstopdf") or epsbackup
	os.system(f"{epstopdf} '{output_eps_file}'")

	os.system(f"rm -f '{output_gnuplot_script}'")

	os.chdir(pwd)
