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
import math
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_experiments_related_help
from sparkle_help import sparkle_compute_marginal_contribution_help
from sparkle_help import sparkle_configure_solver_help as scsh
from sparkle_help import sparkle_run_ablation_help as sah

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
	list_instance = sfh.get_list_all_filename(ori_instance_dir)
	str_value = str(len(list_instance))
	return str_value

def get_numInstanceInInstanceSet_smacDir(instance_set_name):
	str_value = ''
	instance_dir = sgh.smac_dir + '/example_scenarios/' + 'instances/' + instance_set_name + '/'
	list_instance = sfh.get_list_all_filename(instance_dir)
	str_value = str(len(list_instance))
	return str_value

def get_PAR10_performance(results_file, cutoff):
	list_instance_and_par10 = construct_list_instance_and_performance(results_file, cutoff)
	
	sum_par10 = 0.0
	num_instances = 0
	
	for item in list_instance_and_par10:
		num_instances += 1
		sum_par10 += float(item[1])

	mean_par10 = float(sum_par10 / num_instances)

	return mean_par10

def get_optimisedConfigurationTestingPerformancePAR10(solver_name, instance_set_name, smac_each_run_cutoff_time):
	str_value = ''
	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + '/'
	configured_results_dir = smac_solver_dir + 'results/' + sgh.sparkle_run_configured_wrapper + '_' + instance_set_name + '/'
	script_calc_par10_time_path = sgh.smac_dir + '/example_scenarios/' + 'calc_par10_time.py'
	command_line = script_calc_par10_time_path + ' ' + configured_results_dir + ' ' + str(smac_each_run_cutoff_time)
	output = os.popen(command_line).readlines()
	str_value = output[0].strip().split()[2]
	return str_value

def get_defaultConfigurationTestingPerformancePAR10(solver_name, instance_set_name, smac_each_run_cutoff_time):
	str_value = ''
	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + '/'
	default_results_dir = smac_solver_dir + 'results/' + sgh.sparkle_run_default_wrapper + '_' + instance_set_name + '/'
	script_calc_par10_time_path = sgh.smac_dir + '/example_scenarios/' + 'calc_par10_time.py'
	command_line = script_calc_par10_time_path + ' ' + default_results_dir + ' ' + str(smac_each_run_cutoff_time)
	output = os.popen(command_line).readlines()
	str_value = output[0].strip().split()[2]
	return str_value
	

def get_optimisedConfigurationTrainingPerformancePAR10(solver_name, instance_set_name, smac_each_run_cutoff_time):
	str_value = ''
	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + '/'
	configured_results_dir = smac_solver_dir + 'results_train/' + sgh.sparkle_run_configured_wrapper + '_' + instance_set_name + '/'
	script_calc_par10_time_path = sgh.smac_dir + '/example_scenarios/' + 'calc_par10_time.py'
	command_line = script_calc_par10_time_path + ' ' + configured_results_dir + ' ' + str(smac_each_run_cutoff_time)
	output = os.popen(command_line).readlines()
	str_value = output[0].strip().split()[2]
	return str_value

def get_defaultConfigurationTrainingPerformancePAR10(solver_name, instance_set_name, smac_each_run_cutoff_time):
	str_value = ''
	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + '/'
	default_results_dir = smac_solver_dir + 'results_train/' + sgh.sparkle_run_default_wrapper + '_' + instance_set_name + '/'
	script_calc_par10_time_path = sgh.smac_dir + '/example_scenarios/' + 'calc_par10_time.py'
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
						# Minimum runtime. Is lower than this not accurate?
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

# Retrieve instances and corresponding performance values from smac validation objective matrix
def construct_list_instance_and_performance(result_file, cutoff):
	list_instance_and_performance = []

	fin = open(result_file, 'r')
	fin.readline() # Skip column titles

	while True:
		myline = fin.readline()

		if not myline.strip():
			break

		mylist = myline.split(r',')
		instance_path = mylist[0].strip('\"')
		instance = instance_path.split('/')[-1]
		performance = float(mylist[2].replace('"', ''))

		# If the objective is runtime, compute the PAR10 score; otherwise don't modify the value
		smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run_str, num_of_smac_run_in_parallel_str = scsh.get_smac_settings()
		if smac_run_obj == 'RUNTIME':
			if performance < 0.01001: # Minimum runtime. Is lower than this not accurate?
				performance = 0.01001
			elif performance >= float(cutoff):
				performance = float(cutoff) * 10

		list_instance_and_performance.append([instance, performance])

	return list_instance_and_performance

# Return a dictionary of instance names and their performance
def get_dict_instance_to_performance(results_file, cutoff):
	list_instance_and_performance = construct_list_instance_and_performance(results_file, float(cutoff))
	
	dict_instance_to_performance = {}
	
	for item in list_instance_and_performance:
		instance = get_instance_path_from_path(results_file, item[0])
		performance_value = item[1]
		dict_instance_to_performance[instance] = performance_value
		#print('%s %f' % (instance, performance_value))
	
	return dict_instance_to_performance


def get_performance_measure():
	performance_measure = ''

	smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run_str, num_of_smac_run_in_parallel_str = scsh.get_smac_settings()

	if smac_run_obj == 'RUNTIME':
		performance_measure = 'PAR10'
	elif smac_run_obj == 'QUALITY':
		performance_measure = 'performance'

	return performance_measure


def get_runtimeBool():
	runtime_bool = ''

	smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run_str, num_of_smac_run_in_parallel_str = scsh.get_smac_settings()

	if smac_run_obj == 'RUNTIME':
		runtime_bool = r'\runtimetrue'
	elif smac_run_obj == r'QUALITY':
		runtime_bool = r'\runtimefalse'

	return runtime_bool

def get_ablationBool(solver_name, instance_train_name, instance_test_name):
	ablation_bool = ''

	if sah.check_for_ablation(solver_name, instance_train_name, instance_test_name):
		ablation_bool = r'\ablationtrue'
	else:
		ablation_bool = r'\ablationfalse'

	return ablation_bool

def get_figure_configured_vs_default_on_test_instance_set(solver_name, instance_set_train_name, instance_set_test_name, smac_each_run_cutoff_time):
	str_value = r''
	configured_results_file = 'validationObjectiveMatrix-configuration_for_validation-walltime.csv'
	default_results_file = 'validationObjectiveMatrix-cli-1-walltime.csv'
	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + '/'
	configured_results_dir = smac_solver_dir + 'outdir_test_configured/' + configured_results_file
	default_results_dir = smac_solver_dir + 'outdir_test_default/' + default_results_file
	dict_instance_to_par10_configured = get_dict_instance_to_performance(configured_results_dir, smac_each_run_cutoff_time)
	dict_instance_to_par10_default = get_dict_instance_to_performance(default_results_dir, smac_each_run_cutoff_time)
	
	configuration_reports_directory = r'Configuration_Reports/' + solver_name + '_' + instance_set_train_name + '_' + instance_set_test_name + '/'
	latex_directory_path = configuration_reports_directory + r'Sparkle-latex-generator-for-configuration/'
	data_plot_configured_vs_default_on_test_instance_set_filename = 'data_' + solver_name + '_configured_vs_default_on_' + instance_set_test_name + '_test'
	data_plot_configured_vs_default_on_test_instance_set_path = latex_directory_path + data_plot_configured_vs_default_on_test_instance_set_filename + '.dat'
	fout = open(data_plot_configured_vs_default_on_test_instance_set_path, 'w+')
	min_value = sgh.sparkle_maximum_int
	max_value = sgh.sparkle_minimum_int
	for instance in dict_instance_to_par10_configured:
		configured_par10_value = dict_instance_to_par10_configured[instance]
		default_par10_value = dict_instance_to_par10_default[instance]
		fout.write(str(default_par10_value) + ' ' + str(configured_par10_value) + '\n')
		if configured_par10_value < min_value: min_value = configured_par10_value
		if default_par10_value < min_value: min_value = default_par10_value
		if configured_par10_value > max_value: max_value = configured_par10_value
		if default_par10_value > max_value: max_value = default_par10_value
	fout.close()
	
	performance_measure = get_performance_measure()
	gnuplot_command = 'cd \'%s\' ; python auto_gen_plot.py \'%s\' %d \'%s\' \'%s\' \'%s\' \'%s\'' % (latex_directory_path, data_plot_configured_vs_default_on_test_instance_set_filename + '.dat', int(float(smac_each_run_cutoff_time)*10), solver_name + ' (default)', solver_name + ' (configured)', data_plot_configured_vs_default_on_test_instance_set_filename, performance_measure)

	# For QUALITY performance givethe desired bounds for the plot
	if performance_measure != 'PAR10':
		lower_bound = 10**math.floor(math.log10(min_value))
		upper_bound = 10**math.ceil(math.log10(max_value))
		gnuplot_command = gnuplot_command + ' %d %d' % (lower_bound, upper_bound)

	os.system(gnuplot_command)

	str_value = '\\includegraphics[width=0.6\\textwidth]{%s}' % (data_plot_configured_vs_default_on_test_instance_set_filename)
	return str_value


def get_figure_configured_vs_default_on_train_instance_set(solver_name, instance_set_train_name, configuration_reports_directory, smac_each_run_cutoff_time):
	str_value = r''
	optimised_configuration_str, optimised_configuration_performance_par10, optimised_configuration_seed = scsh.get_optimised_configuration(solver_name, instance_set_train_name)
	configured_results_file = 'validationObjectiveMatrix-traj-run-' + optimised_configuration_seed + '-walltime.csv'
	default_results_file = 'validationObjectiveMatrix-cli-1-walltime.csv'
	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + '/'
	configured_results_dir = smac_solver_dir + 'outdir_train_configuration/' + solver_name + '_' + instance_set_train_name + '_scenario/' + configured_results_file
	default_results_dir = smac_solver_dir + 'outdir_train_default/' + default_results_file
	dict_instance_to_par10_configured = get_dict_instance_to_performance(configured_results_dir, smac_each_run_cutoff_time)
	dict_instance_to_par10_default = get_dict_instance_to_performance(default_results_dir, smac_each_run_cutoff_time)
	
	latex_directory_path = configuration_reports_directory + r'Sparkle-latex-generator-for-configuration/'
	data_plot_configured_vs_default_on_train_instance_set_filename = 'data_' + solver_name + '_configured_vs_default_on_' + instance_set_train_name + '_train'
	data_plot_configured_vs_default_on_train_instance_set_path = latex_directory_path + data_plot_configured_vs_default_on_train_instance_set_filename + '.dat'
	fout = open(data_plot_configured_vs_default_on_train_instance_set_path, 'w+')
	# Write PAR10 values for configured and default to file
	min_value = sgh.sparkle_maximum_int
	max_value = sgh.sparkle_minimum_int
	for instance in dict_instance_to_par10_configured:
		configured_par10_value = dict_instance_to_par10_configured[instance]
		default_par10_value = dict_instance_to_par10_default[instance]
		fout.write(str(default_par10_value) + ' ' + str(configured_par10_value) + '\n')
		if configured_par10_value < min_value: min_value = configured_par10_value
		if default_par10_value < min_value: min_value = default_par10_value
		if configured_par10_value > max_value: max_value = configured_par10_value
		if default_par10_value > max_value: max_value = default_par10_value
	fout.close()

	performance_measure = get_performance_measure()
	gnuplot_command = 'cd \'%s\' ; python auto_gen_plot.py \'%s\' %d \'%s\' \'%s\' \'%s\' \'%s\'' % (latex_directory_path, data_plot_configured_vs_default_on_train_instance_set_filename + '.dat', int(float(smac_each_run_cutoff_time)*10), solver_name + ' (default)', solver_name + ' (configured)', data_plot_configured_vs_default_on_train_instance_set_filename, performance_measure)

	# For QUALITY performance givethe desired bounds for the plot
	if performance_measure != 'PAR10':
		lower_bound = 10**math.floor(math.log10(min_value))
		upper_bound = 10**math.ceil(math.log10(max_value))
		gnuplot_command = gnuplot_command + ' %d %d' % (lower_bound, upper_bound)

	os.system(gnuplot_command)
	
	str_value = '\\includegraphics[width=0.6\\textwidth]{%s}' % (data_plot_configured_vs_default_on_train_instance_set_filename)
	return str_value


def get_timeouts_test(solver_name, instance_set_name, cutoff):
	configured_timeouts = 0
	default_timeouts = 0
	overlapping_timeouts = 0

	# Retrieve instances and PAR10 values
	configured_results_file = 'validationObjectiveMatrix-configuration_for_validation-walltime.csv'
	default_results_file = 'validationObjectiveMatrix-cli-1-walltime.csv'
	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + '/'
	configured_results_dir = smac_solver_dir + 'outdir_test_configured/' + configured_results_file
	default_results_dir = smac_solver_dir + 'outdir_test_default/' + default_results_file
	dict_instance_to_par10_configured = get_dict_instance_to_performance(configured_results_dir, cutoff)
	dict_instance_to_par10_default = get_dict_instance_to_performance(default_results_dir, cutoff)

	# Count default timeouts, configured timeouts, and overlapping timeouts
	timeout_value = cutoff * 10

	for instance in dict_instance_to_par10_configured:
		configured_par10_value = dict_instance_to_par10_configured[instance]
		default_par10_value = dict_instance_to_par10_default[instance]
		#print('%f %f %f' % (timeout_value, configured_par10_value, default_par10_value))
		if configured_par10_value == timeout_value:
			configured_timeouts += 1
		if default_par10_value == timeout_value:
			default_timeouts += 1
		if configured_par10_value == timeout_value and default_par10_value == timeout_value:
			overlapping_timeouts += 1

	#print('%d %d %d' % (configured_timeouts, default_timeouts, overlapping_timeouts))
	return configured_timeouts, default_timeouts, overlapping_timeouts


def get_timeouts_train(solver_name, instance_set_name, cutoff):
	configured_timeouts = 0
	default_timeouts = 0
	overlapping_timeouts = 0

	# Retrieve instances and PAR10 values
	optimised_configuration_str, optimised_configuration_performance_par10, optimised_configuration_seed = scsh.get_optimised_configuration(solver_name, instance_set_name)
	configured_results_file = 'validationObjectiveMatrix-traj-run-' + optimised_configuration_seed + '-walltime.csv'
	default_results_file = 'validationObjectiveMatrix-cli-1-walltime.csv'
	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + '/'
	configured_results_dir = smac_solver_dir + 'outdir_train_configuration/' + solver_name + '_' + instance_set_name + '_scenario/' + configured_results_file
	default_results_dir = smac_solver_dir + 'outdir_train_default/' + default_results_file
	dict_instance_to_par10_configured = get_dict_instance_to_performance(configured_results_dir, cutoff)
	dict_instance_to_par10_default = get_dict_instance_to_performance(default_results_dir, cutoff)

	# Count default timeouts, configured timeouts, and overlapping timeouts
	timeout_value = cutoff * 10

	for instance in dict_instance_to_par10_configured:
		configured_par10_value = dict_instance_to_par10_configured[instance]
		default_par10_value = dict_instance_to_par10_default[instance]
		#print('%f %f %f' % (timeout_value, configured_par10_value, default_par10_value))
		if configured_par10_value == timeout_value:
			configured_timeouts += 1
		if default_par10_value == timeout_value:
			default_timeouts += 1
		if configured_par10_value == timeout_value and default_par10_value == timeout_value:
			overlapping_timeouts += 1

	#print('%d %d %d' % (configured_timeouts, default_timeouts, overlapping_timeouts))
	return configured_timeouts, default_timeouts, overlapping_timeouts

def get_ablation_table(solver_name, instance_set_train_name, instance_set_test_name=None):
	results = sah.get_ablation_table(solver_name, instance_set_train_name, instance_set_test_name)
	table_string = "\\begin{tabular}{rrrrr}"
	for i,line in enumerate(results):
		if i == 0:
			line = ["\\textbf{{{0}}}".format(word) for word in line]
		table_string += " & ".join(line) + " \\\\ "
		if i == 0:
			table_string += "\\hline "
	table_string += "\\end{tabular}"

	return table_string

def get_dict_variable_to_value(solver_name, instance_set_train_name, instance_set_test_name=None, ablation=True):
	full_dict = {}

	if instance_set_test_name is not None:
		configuration_reports_directory = r'Configuration_Reports/' + solver_name + '_' + instance_set_train_name + '_' + instance_set_test_name + '/'
	else:
		configuration_reports_directory = r'Configuration_Reports/' + solver_name + '_' + instance_set_train_name + '/'

	common_dict = get_dict_variable_to_value_common(solver_name, instance_set_train_name, configuration_reports_directory)
	full_dict.update(common_dict)

	variable = r'testBool'

	if instance_set_test_name is not None:
		test_dict = get_dict_variable_to_value_test(solver_name, instance_set_train_name, instance_set_test_name)
		full_dict.update(test_dict)
		str_value = r'\testtrue'
	else:
		str_value = r'\testfalse'
	full_dict[variable] = str_value

	if not ablation:
		full_dict["ablationBool"] = r'\ablationfalse'

	return full_dict


# Retrieve variables relevant to all configuration reports
def get_dict_variable_to_value_common(solver_name, instance_set_train_name, configuration_reports_directory):
	common_dict = {}

	variable = r'performanceMeasure'
	str_value = get_performance_measure()
	common_dict[variable] = str_value

	variable = r'runtimeBool'
	str_value = get_runtimeBool()
	common_dict[variable] = str_value

	variable = r'customCommands'
	str_value = get_customCommands()
	common_dict[variable] = str_value
	
	variable = r'sparkle'
	str_value = get_sparkle()
	common_dict[variable] = str_value
	
	variable = r'solver'
	str_value = solver_name
	common_dict[variable] = str_value

	variable = r'instanceSetTrain'
	str_value = instance_set_train_name
	common_dict[variable] = str_value
	
	variable = r'sparkleVersion' 
	str_value = get_sparkleVersion()
	common_dict[variable] = str_value
	
	variable = r'numInstanceInTrainingInstanceSet'
	str_value = get_numInstanceInInstanceSet_smacDir(instance_set_train_name)
	common_dict[variable] = str_value
	
	smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run_str, num_of_smac_run_in_parallel_str = scsh.get_smac_settings()
	
	variable = r'numSmacRuns'
	common_dict[variable] = str(num_of_smac_run_str)
	
	variable = r'smacObjective'
	common_dict[variable] = str(smac_run_obj)
	
	variable = r'smacWholeTimeBudget'
	common_dict[variable] = str(smac_whole_time_budget)
	
	variable = r'smacEachRunCutoffTime'
	common_dict[variable] = str(smac_each_run_cutoff_time)
	
	optimised_configuration_str, optimised_configuration_performance_par10, optimised_configuration_seed = scsh.get_optimised_configuration(solver_name, instance_set_train_name)
	
	variable = r'optimisedConfiguration'
	common_dict[variable] = str(optimised_configuration_str)
	
	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + '/'

	variable = r'optimisedConfigurationTrainingPerformancePAR10'
	optimised_configuration_str, optimised_configuration_performance_par10, optimised_configuration_seed = scsh.get_optimised_configuration(solver_name, instance_set_train_name)
	configured_results_train_file = 'validationObjectiveMatrix-traj-run-' + str(optimised_configuration_seed) + '-walltime.csv'
	configured_results_train_dir = smac_solver_dir + 'outdir_train_configuration/' + solver_name + '_' + instance_set_train_name + '_scenario/' + configured_results_train_file
	str_value = get_PAR10_performance(configured_results_train_dir, smac_each_run_cutoff_time)
	common_dict[variable] = str(str_value)
	
	variable = r'defaultConfigurationTrainingPerformancePAR10'
	default_results_train_file = 'validationObjectiveMatrix-cli-1-walltime.csv'
	default_results_train_dir = smac_solver_dir + 'outdir_train_default/' + default_results_train_file
	str_value = get_PAR10_performance(default_results_train_dir, smac_each_run_cutoff_time)
	common_dict[variable] = str(str_value)
	
	variable = r'figure-configured-vs-default-train'
	str_value = get_figure_configured_vs_default_on_train_instance_set(solver_name, instance_set_train_name, configuration_reports_directory, float(smac_each_run_cutoff_time))
	common_dict[variable] = str_value
	
	# Retrieve timeout numbers for the training instances
	configured_timeouts_train, default_timeouts_train, overlapping_timeouts_train = get_timeouts_train(solver_name, instance_set_train_name, float(smac_each_run_cutoff_time))

	variable = r'timeoutsTrainDefault'
	common_dict[variable] = str(default_timeouts_train)

	variable = r'timeoutsTrainConfigured'
	common_dict[variable] = str(configured_timeouts_train)

	variable = r'timeoutsTrainOverlap'
	common_dict[variable] = str(overlapping_timeouts_train)

	variable = r'ablationBool'
	common_dict[variable] = get_ablationBool(solver_name, instance_set_train_name,instance_set_train_name)

	variable = r'ablationPath'
	common_dict[variable] = get_ablation_table(solver_name, instance_set_train_name,instance_set_train_name)

	return common_dict


# Retrieve variables specific to the testing set
def get_dict_variable_to_value_test(solver_name, instance_set_train_name, instance_set_test_name):
	test_dict = {}
	
	variable = r'instanceSetTest'
	str_value = instance_set_test_name
	test_dict[variable] = str_value
	
	variable = r'numInstanceInTestingInstanceSet'
	str_value = get_numInstanceInInstanceSet_smacDir(instance_set_test_name)
	test_dict[variable] = str_value
	
	smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run_str, num_of_smac_run_in_parallel_str = scsh.get_smac_settings()

	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + '/'

	variable = r'optimisedConfigurationTestingPerformancePAR10'
	configured_results_test_file = 'validationObjectiveMatrix-configuration_for_validation-walltime.csv'
	configured_results_test_dir = smac_solver_dir + 'outdir_test_configured/' + configured_results_test_file
	str_value = get_PAR10_performance(configured_results_test_dir, smac_each_run_cutoff_time)
	test_dict[variable] = str(str_value)
	
	variable = r'defaultConfigurationTestingPerformancePAR10'
	default_results_test_file = 'validationObjectiveMatrix-cli-1-walltime.csv'
	default_results_test_dir = smac_solver_dir + 'outdir_test_default/' + default_results_test_file
	str_value = get_PAR10_performance(default_results_test_dir, smac_each_run_cutoff_time)
	test_dict[variable] = str(str_value)
	
	variable = r'figure-configured-vs-default-test'
	str_value = get_figure_configured_vs_default_on_test_instance_set(solver_name, instance_set_train_name, instance_set_test_name, float(smac_each_run_cutoff_time))
	test_dict[variable] = str_value

	# Retrieve timeout numbers for the testing instances
	configured_timeouts_test, default_timeouts_test, overlapping_timeouts_test = get_timeouts_test(solver_name, instance_set_test_name, float(smac_each_run_cutoff_time))

	variable = r'timeoutsTestDefault'
	test_dict[variable] = str(default_timeouts_test)

	variable = r'timeoutsTestConfigured'
	test_dict[variable] = str(configured_timeouts_test)

	variable = r'timeoutsTestOverlap'
	test_dict[variable] = str(overlapping_timeouts_test)

	variable = r'ablationBool'
	test_dict[variable] = get_ablationBool(solver_name, instance_set_train_name, instance_set_test_name)

	variable = r'ablationPath'
	test_dict[variable] = get_ablation_table(solver_name, instance_set_train_name, instance_set_test_name)

	return test_dict


def check_results_exist(solver_name, instance_set_train_name, instance_set_test_name=None):
	all_good = True
	# Check train instance dir exists
	instance_train_dir = sgh.smac_dir + '/example_scenarios/' + 'instances/' + instance_set_train_name + '/'

	if not os.path.exists(instance_train_dir):
		all_good = False

	# Check train results exist: configured+default
	smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + '/'
	configured_results_train_dir = smac_solver_dir + 'outdir_train_configuration/' + solver_name + '_' + instance_set_train_name + '_scenario/'
	default_results_train_dir = smac_solver_dir + 'outdir_train_default/'

	if not (os.path.exists(configured_results_train_dir) and os.path.exists(default_results_train_dir)):
		all_good = False

	if instance_set_test_name is not None:
		# Check test instance dir exists
		instance_test_dir = sgh.smac_dir + '/example_scenarios/' + 'instances/' + instance_set_test_name + '/'
		if not os.path.exists(instance_test_dir):
			all_good = False

		# Check test results exist: configured+default
		smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + '/'
		configured_results_test_dir = smac_solver_dir + 'outdir_test_configured/'
		default_results_test_dir = smac_solver_dir + 'outdir_test_default/'

		if not (os.path.exists(configured_results_test_dir) and os.path.exists(default_results_test_dir)):
			all_good = False

	if not all_good:
		print('c Error: Results not found for the given solver and instance set(s) combination. Make sure the \'configure_solver\' and \'test_configured_solver_and_default_solver\' commands were correctly executed.')
		sys.exit()

	return


def get_most_recent_test_run(solver_name):
	instance_set_train = ''
	instance_set_test = ''
	flag_instance_set_train = False
	flag_instance_set_test = False

	# Read most recent run from file
	last_test_file_path = sgh.smac_dir + '/example_scenarios/' + solver_name + '/' + sgh.sparkle_last_test_file_name

	try:
		fin = open(last_test_file_path, 'r')
	except IOError:
		# Report error when file does not exist
		print('c Error: The most recent results do not match the given solver. Please specify which instance sets you want a report for with this solver. Alternatively, make sure the \'test_configured_solver_and_default_solver\' command was executed for this solver.')
		sys.exit()

	while True:
		myline = fin.readline()
		if not myline: break
		words = myline.split()

		if words[0] == 'train':
			instance_set_train = words[1]
			if instance_set_train != '':
				flag_instance_set_train = True
		if words[0] == 'test':
			instance_set_test = words[1]
			if instance_set_test != '':
				flag_instance_set_test = True
	fin.close()

	return instance_set_train, instance_set_test, flag_instance_set_train, flag_instance_set_test


def generate_report_for_configuration_prep(configuration_reports_directory):
	print('c Generating report for configuration ...')

	template_latex_directory_path = r'Components/Sparkle-latex-generator-for-configuration/'
	if not os.path.exists(configuration_reports_directory):
		os.system('mkdir -p ' + configuration_reports_directory)
	os.system(r'cp -r ' + template_latex_directory_path + r' ' + configuration_reports_directory)

	return


def generate_report_for_configuration_train(solver_name, instance_set_train_name, ablation=True):
	configuration_reports_directory = r'Configuration_Reports/' + solver_name + '_' + instance_set_train_name + '/'
	generate_report_for_configuration_prep(configuration_reports_directory)
	dict_variable_to_value = get_dict_variable_to_value(solver_name, instance_set_train_name, ablation=ablation)

	generate_report_for_configuration_common(configuration_reports_directory, dict_variable_to_value)

	return


def generate_report_for_configuration(solver_name, instance_set_train_name, instance_set_test_name, ablation=True):
	configuration_reports_directory = r'Configuration_Reports/' + solver_name + '_' + instance_set_train_name + '_' + instance_set_test_name + '/'
	generate_report_for_configuration_prep(configuration_reports_directory)
	dict_variable_to_value = get_dict_variable_to_value(solver_name, instance_set_train_name, instance_set_test_name, ablation=ablation)

	generate_report_for_configuration_common(configuration_reports_directory, dict_variable_to_value)

	return


def generate_report_for_configuration_common(configuration_reports_directory, dict_variable_to_value):
	latex_directory_path = configuration_reports_directory + r'Sparkle-latex-generator-for-configuration/'
	latex_template_filename = r'template-Sparkle-for-configuration.tex'
	latex_report_filename = r'Sparkle_Report_for_Configuration'
	
	
	# Read in the report template from file
	latex_template_filepath = latex_directory_path + latex_template_filename
	report_content = r''
	fin = open(latex_template_filepath, 'r')
	while True:
		myline = fin.readline()
		if not myline: break
		report_content += myline
	fin.close()
	
	# Replace variables in the report template with their value
	for variable_key, str_value in dict_variable_to_value.items():
		 variable = r'@@' + variable_key + r'@@'
		 if (variable_key != r'figure-configured-vs-default-test') and (variable_key != r'figure-configured-vs-default-train'):
		 	str_value = str_value.replace(r'_', r'\textunderscore ')
		 #str_value = str_value.replace(r'_', r'\textunderscore ')
		 report_content = report_content.replace(variable, str_value)
	
	#print(report_content)
	
	# Write the completed report to a tex file
	latex_report_filepath = latex_directory_path + latex_report_filename + r'.tex'
	fout = open(latex_report_filepath, 'w+')
	fout.write(report_content)
	fout.close()
	
	# Compile the report
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
	print('c Generating report for configuration done!')
	
	return

