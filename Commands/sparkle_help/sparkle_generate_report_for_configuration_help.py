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
import sparkle_global_help
import sparkle_file_help as sfh
import sparkle_feature_data_csv_help as sfdcsv
import sparkle_performance_data_csv_help as spdcsv
import sparkle_experiments_related_help
import sparkle_compute_marginal_contribution_help
import sparkle_configure_solver_help as scsh

def get_customCommands():
	str_value = r''
	return str_value

def get_sparkle():
	str_value = r'\emph{Sparkle}'
	return str_value

def get_sparkleVersion():
	str_value = r'1.0.0'
	return str_value

def get_numInstanceInInstanceSet(instance_set_name):
	str_value = ''
	ori_instance_dir = 'Instances/' + instance_set_name + '/'
	list_instance = sfh.get_list_all_cnf_filename(ori_instance_dir)
	str_value = str(len(list_instance))
	return str_value

def get_numInstanceInTrainingInstanceSet(instance_set_name):
	str_value = ''
	train_instance_dir = sparkle_global_help.smac_dir + '/example_scenarios/' + 'instances/' + instance_set_name + '/'
	list_train_instance = sfh.get_list_all_cnf_filename(train_instance_dir)
	str_value = str(len(list_train_instance))
	return str_value

def get_numInstanceInTestingInstanceSet(instance_set_name):
	str_value = ''
	test_instance_dir = sparkle_global_help.smac_dir + '/example_scenarios/' + 'instances_test/' + instance_set_name + '/'
	list_test_instance = sfh.get_list_all_cnf_filename(test_instance_dir)
	str_value = str(len(list_test_instance))
	return str_value

def get_optimisedConfigurationTestingPerformancePAR10(solver_name, instance_set_name, smac_each_run_cutoff_time):
	str_value = ''
	smac_solver_dir = sparkle_global_help.smac_dir + '/example_scenarios/' + solver_name + '/'
	configured_results_dir = smac_solver_dir + 'results/' + sparkle_global_help.sparkle_run_configured_wrapper + '_' + instance_set_name + '/'
	script_calc_par10_time_path = sparkle_global_help.smac_dir + '/example_scenarios/' + 'calc_par10_time.py'
	command_line = script_calc_par10_time_path + ' ' + configured_results_dir + ' ' + str(smac_each_run_cutoff_time)
	output = os.popen(command_line).readlines()
	str_value = output[0].strip().split()[2]
	return str_value

def get_defaultConfigurationTestingPerformancePAR10(solver_name, instance_set_name, smac_each_run_cutoff_time):
	str_value = ''
	smac_solver_dir = sparkle_global_help.smac_dir + '/example_scenarios/' + solver_name + '/'
	default_results_dir = smac_solver_dir + 'results/' + sparkle_global_help.sparkle_run_default_wrapper + '_' + instance_set_name + '/'
	script_calc_par10_time_path = sparkle_global_help.smac_dir + '/example_scenarios/' + 'calc_par10_time.py'
	command_line = script_calc_par10_time_path + ' ' + default_results_dir + ' ' + str(smac_each_run_cutoff_time)
	output = os.popen(command_line).readlines()
	str_value = output[0].strip().split()[2]
	return str_value
	

def get_optimisedConfigurationTrainingPerformancePAR10(solver_name, instance_set_name, smac_each_run_cutoff_time):
	str_value = ''
	smac_solver_dir = sparkle_global_help.smac_dir + '/example_scenarios/' + solver_name + '/'
	configured_results_dir = smac_solver_dir + 'results_train/' + sparkle_global_help.sparkle_run_configured_wrapper + '_' + instance_set_name + '/'
	script_calc_par10_time_path = sparkle_global_help.smac_dir + '/example_scenarios/' + 'calc_par10_time.py'
	command_line = script_calc_par10_time_path + ' ' + configured_results_dir + ' ' + str(smac_each_run_cutoff_time)
	output = os.popen(command_line).readlines()
	str_value = output[0].strip().split()[2]
	return str_value

def get_defaultConfigurationTrainingPerformancePAR10(solver_name, instance_set_name, smac_each_run_cutoff_time):
	str_value = ''
	smac_solver_dir = sparkle_global_help.smac_dir + '/example_scenarios/' + solver_name + '/'
	default_results_dir = smac_solver_dir + 'results_train/' + sparkle_global_help.sparkle_run_default_wrapper + '_' + instance_set_name + '/'
	script_calc_par10_time_path = sparkle_global_help.smac_dir + '/example_scenarios/' + 'calc_par10_time.py'
	command_line = script_calc_par10_time_path + ' ' + default_results_dir + ' ' + str(smac_each_run_cutoff_time)
	output = os.popen(command_line).readlines()
	str_value = output[0].strip().split()[2]
	return str_value


def get_instance_path_from_path(results_dir, path):
	if results_dir[-1] != r'/':
		results_dir += r'/'
	instance_path = path.replace(results_dir, r'')
	pos_right_slash = instance_path.rfind(r'/')
	instance_path_1 = instance_path[:pos_right_slash+1]
	instance_path_2 = instance_path[pos_right_slash+1:]
	
	key_str_wrapper = r'wrapper'
	pos_wrapper = instance_path_2.find(key_str_wrapper)
	instance_path_2 = instance_path_2[pos_wrapper+1:]
	pos_underscore_first = instance_path_2.find('_')
	instance_path_2 = instance_path_2[pos_underscore_first+1:]
	pos_underscore_last = instance_path_2.rfind('_')
	instance_path_2 = instance_path_2[:pos_underscore_last]
	instance_path = instance_path_1 + instance_path_2
	return instance_path

def construct_list_instance_and_par10_recursive(list_instance_and_par10, path, cutoff):
	if os.path.isfile(path):
		file_extension = sfh.get_file_least_extension(path)
		if file_extension == r'res':
			fin = open(path, 'r')
			while True:
				myline = fin.readline()
				if myline:
					mylist = myline.strip().split()
					if len(mylist) <= 1:
						continue
					if mylist[1] == r's':
						run_time = float(mylist[0].split(r'/')[0])
						if run_time < 0.01001:
							run_time = 0.01001
						if run_time > cutoff:
							continue
						if mylist[2] == r'SATISFIABLE':
							list_instance_and_par10.append([path, run_time])
							break
						elif mylist[2] == r'UNSATISFIABLE':
							list_instance_and_par10.append([path, run_time])
							break
				else:
					run_time = cutoff * 10
					list_instance_and_par10.append([path, run_time])
					break
		return
		
	elif os.path.isdir(path):
		if path[-1] != r'/':
			this_path = path + r'/'
		else:
			this_path = path
		list_all_items = os.listdir(this_path)
		for item in list_all_items:
			construct_list_instance_and_par10_recursive(list_instance_and_par10, this_path + item, cutoff)
	return 
	

def get_dict_instance_to_par10(results_dir, cutoff):
	list_instance_and_par10 = []
	construct_list_instance_and_par10_recursive(list_instance_and_par10, results_dir, cutoff)
	
	dict_instance_to_par10 = {}
	
	for item in list_instance_and_par10:
		instance = get_instance_path_from_path(results_dir, item[0])
		par10_value = item[1]
		dict_instance_to_par10[instance] = par10_value
		#print('%s %f' % (instance, par10_value))
	
	return dict_instance_to_par10


def get_figure_configured_vs_default_on_test_instance_set(solver_name, instance_set_name, smac_each_run_cutoff_time):
	str_value = r''
	smac_solver_dir = sparkle_global_help.smac_dir + '/example_scenarios/' + solver_name + '/'
	configured_results_dir = smac_solver_dir + 'results/' + sparkle_global_help.sparkle_run_configured_wrapper + '_' + instance_set_name + '/'
	default_results_dir = smac_solver_dir + 'results/' + sparkle_global_help.sparkle_run_default_wrapper + '_' + instance_set_name + '/'
	dict_instance_to_par10_configured = get_dict_instance_to_par10(configured_results_dir, smac_each_run_cutoff_time)
	dict_instance_to_par10_default = get_dict_instance_to_par10(default_results_dir, smac_each_run_cutoff_time)
	
	configuration_reports_directory = r'Configuration_Reports/' + solver_name + '_' + instance_set_name + '/'
	latex_directory_path = configuration_reports_directory + r'Sparkle-latex-generator-for-configuration/'
	data_plot_configured_vs_default_on_test_instance_set_filename = 'data_' + solver_name + '_configured_vs_default_on_' + instance_set_name + '_test'
	data_plot_configured_vs_default_on_test_instance_set_path = latex_directory_path + data_plot_configured_vs_default_on_test_instance_set_filename + '.dat'
	fout = open(data_plot_configured_vs_default_on_test_instance_set_path, 'w+')
	for instance in dict_instance_to_par10_configured:
		configured_par10_value = dict_instance_to_par10_configured[instance]
		default_par10_value = dict_instance_to_par10_default[instance]
		fout.write(str(default_par10_value) + ' ' + str(configured_par10_value) + '\n')
	fout.close()
	
	gnuplot_command = 'cd \'%s\' ; python auto_gen_plot.py \'%s\' %d \'%s\' \'%s\' \'%s\'' % (latex_directory_path, data_plot_configured_vs_default_on_test_instance_set_filename + '.dat', int(float(smac_each_run_cutoff_time)*10), solver_name + ' (default)', solver_name + ' (configured)', data_plot_configured_vs_default_on_test_instance_set_filename) 
	
	os.system(gnuplot_command)
	
	str_value = '\\includegraphics[width=0.6\\textwidth]{%s}' % (data_plot_configured_vs_default_on_test_instance_set_filename)
	return str_value


def get_figure_configured_vs_default_on_train_instance_set(solver_name, instance_set_name, smac_each_run_cutoff_time):
	str_value = r''
	smac_solver_dir = sparkle_global_help.smac_dir + '/example_scenarios/' + solver_name + '/'
	configured_results_dir = smac_solver_dir + 'results_train/' + sparkle_global_help.sparkle_run_configured_wrapper + '_' + instance_set_name + '/'
	default_results_dir = smac_solver_dir + 'results_train/' + sparkle_global_help.sparkle_run_default_wrapper + '_' + instance_set_name + '/'
	dict_instance_to_par10_configured = get_dict_instance_to_par10(configured_results_dir, smac_each_run_cutoff_time)
	dict_instance_to_par10_default = get_dict_instance_to_par10(default_results_dir, smac_each_run_cutoff_time)
	
	configuration_reports_directory = r'Configuration_Reports/' + solver_name + '_' + instance_set_name + '/'
	latex_directory_path = configuration_reports_directory + r'Sparkle-latex-generator-for-configuration/'
	data_plot_configured_vs_default_on_train_instance_set_filename = 'data_' + solver_name + '_configured_vs_default_on_' + instance_set_name + '_train'
	data_plot_configured_vs_default_on_train_instance_set_path = latex_directory_path + data_plot_configured_vs_default_on_train_instance_set_filename + '.dat'
	fout = open(data_plot_configured_vs_default_on_train_instance_set_path, 'w+')
	for instance in dict_instance_to_par10_configured:
		configured_par10_value = dict_instance_to_par10_configured[instance]
		default_par10_value = dict_instance_to_par10_default[instance]
		fout.write(str(default_par10_value) + ' ' + str(configured_par10_value) + '\n')
	fout.close()
	
	gnuplot_command = 'cd \'%s\' ; python auto_gen_plot.py \'%s\' %d \'%s\' \'%s\' \'%s\'' % (latex_directory_path, data_plot_configured_vs_default_on_train_instance_set_filename + '.dat', int(float(smac_each_run_cutoff_time)*10), solver_name + ' (default)', solver_name + ' (configured)', data_plot_configured_vs_default_on_train_instance_set_filename) 
	
	os.system(gnuplot_command)
	
	str_value = '\\includegraphics[width=0.6\\textwidth]{%s}' % (data_plot_configured_vs_default_on_train_instance_set_filename)
	return str_value


def get_dict_variable_to_value(solver_name, instance_set_name):
	mydict = {}
	
	variable = r'customCommands'
	str_value = get_customCommands()
	mydict[variable] = str_value
	
	variable = r'sparkle'
	str_value = get_sparkle()
	mydict[variable] = str_value
	
	variable = r'solver'
	str_value = solver_name
	mydict[variable] = str_value
	
	variable = r'instanceSet'
	str_value = instance_set_name
	mydict[variable] = str_value
	
	variable = r'sparkleVersion'
	str_value = get_sparkleVersion()
	mydict[variable] = str_value
	
	variable = r'numInstanceInInstanceSet'
	str_value = get_numInstanceInInstanceSet(instance_set_name)
	mydict[variable] = str_value
	
	variable = r'numInstanceInTrainingInstanceSet'
	str_value = get_numInstanceInTrainingInstanceSet(instance_set_name)
	mydict[variable] = str_value
	
	variable = r'numInstanceInTestingInstanceSet'
	str_value = get_numInstanceInTestingInstanceSet(instance_set_name)
	mydict[variable] = str_value
	
	smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run_str, num_of_smac_run_in_parallel_str = scsh.get_smac_settings()
	
	variable = r'numSmacRuns'
	mydict[variable] = str(num_of_smac_run_str)
	
	variable = r'smacObjective'
	mydict[variable] = str(smac_run_obj)
	
	variable = r'smacWholeTimeBudget'
	mydict[variable] = str(smac_whole_time_budget)
	
	variable = r'smacEachRunCutoffTime'
	mydict[variable] = str(smac_each_run_cutoff_time)
	
	optimised_configuration_str, optimised_configuration_performance_par10, optimised_configuration_seed = scsh.get_optimised_configuration(solver_name, instance_set_name)
	
	variable = r'optimisedConfiguration'
	mydict[variable] = str(optimised_configuration_str)
	
	variable = r'optimisedConfigurationTestingPerformancePAR10'
	str_value = get_optimisedConfigurationTestingPerformancePAR10(solver_name, instance_set_name, smac_each_run_cutoff_time)
	mydict[variable] = str_value
	
	variable = r'defaultConfigurationTestingPerformancePAR10'
	str_value = get_defaultConfigurationTestingPerformancePAR10(solver_name, instance_set_name, smac_each_run_cutoff_time)
	mydict[variable] = str_value
	
	variable = r'figure-configured-vs-default-test'
	str_value = get_figure_configured_vs_default_on_test_instance_set(solver_name, instance_set_name, float(smac_each_run_cutoff_time))
	mydict[variable] = str_value
	
	
	variable = r'optimisedConfigurationTrainingPerformancePAR10'
	str_value = get_optimisedConfigurationTrainingPerformancePAR10(solver_name, instance_set_name, smac_each_run_cutoff_time)
	mydict[variable] = str_value
	
	variable = r'defaultConfigurationTrainingPerformancePAR10'
	str_value = get_defaultConfigurationTrainingPerformancePAR10(solver_name, instance_set_name, smac_each_run_cutoff_time)
	mydict[variable] = str_value
	
	variable = r'figure-configured-vs-default-train'
	str_value = get_figure_configured_vs_default_on_train_instance_set(solver_name, instance_set_name, float(smac_each_run_cutoff_time))
	mydict[variable] = str_value
	
	return mydict
	

def generate_report_for_configuration(solver_name, instance_set_name):
	configuration_reports_directory = r'Configuration_Reports/' + solver_name + '_' + instance_set_name + '/'
	template_latex_directory_path = r'Components/Sparkle-latex-generator-for-configuration/'
	if not os.path.exists(configuration_reports_directory):
		os.system('mkdir -p ' + configuration_reports_directory)
	os.system(r'cp -r ' + template_latex_directory_path + r' ' + configuration_reports_directory)
	
	latex_directory_path = configuration_reports_directory + r'Sparkle-latex-generator-for-configuration/'
	latex_template_filename = r'template-Sparkle-for-configuration.tex'
	latex_report_filename = r'Sparkle_Report_for_Configuration'
	dict_variable_to_value = get_dict_variable_to_value(solver_name, instance_set_name)
	
	
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
		 if (variable_key != r'figure-configured-vs-default-test') and (variable_key != r'figure-configured-vs-default-train'):
		 	str_value = str_value.replace(r'_', r'\textunderscore ')
		 #str_value = str_value.replace(r'_', r'\textunderscore ')
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
	



