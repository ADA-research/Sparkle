import os
import sys
import fcntl

from math import log

curDir = os.path.abspath(__file__)
curDir = curDir[:curDir.rfind('/')]
sys.path.append(os.path.join(curDir, '../sparkle_help/'))

from sparkle_csv_help import Sparkle_CSV
from sparkle_feature_data_csv_help import Sparkle_Feature_Data_CSV
from sparkle_performance_data_csv_help import Sparkle_Performance_Data_CSV

import sparkle_global_help
import sparkle_basic_help
import sparkle_file_help as sfh
import sparkle_compute_features_help as scf
import sparkle_compute_features_parallel_help as scfp
import sparkle_run_solvers_help as srs
import sparkle_run_solvers_parallel_help as srsp
import sparkle_experiments_related_help as ser
import sparkle_job_help
import sparkle_compute_marginal_contribution_help as scmc

class Portfolio_Test:
	def __init__(self, test_instance_dir):
		if test_instance_dir[-1] == '/':
			self.test_instance_dir = test_instance_dir
		else:
			self.test_instance_dir = test_instance_dir + '/'
		self.test_case_dir = 'Test_Cases/' + sfh.get_last_level_directory_name(test_instance_dir) + '/'
		self.test_instance_list_file = self.test_case_dir + 'test_instance_list.txt'
		self.test_instance_list = []
		
		self.test_feature_data_dir = self.test_case_dir + 'Feature_Data/'
		self.test_feature_data_csv_path = self.test_feature_data_dir + 'sparkle_feature_data.csv'
		self.test_feature_data_tmp_dir = self.test_feature_data_dir + 'TMP/'
		
		self.test_performance_data_dir = self.test_case_dir + 'Performance_Data/'
		self.test_performance_data_csv_path = self.test_performance_data_dir + 'sparkle_performance_data.csv'
		self.test_performance_data_tmp_dir = self.test_performance_data_dir + 'TMP/'
		
		self.test_tmp_dir = self.test_case_dir + 'TMP/'
		
		self.test_report_dir = self.test_case_dir + 'Sparkle-latex-generator-for-test-cases/'
		
		self.create_test_dir()
		self.init_test_instance()
		self.create_feature_data()
		self.create_performance_data()
		self.create_test_tmp_dir()
		self.create_report_dir()
	
	def create_test_dir(self):
		if not os.path.exists(self.test_case_dir):
			os.system('mkdir -p %s' % (self.test_case_dir))
	
	def init_test_instance(self):
		self.test_instance_list = sfh.get_list_all_cnf_filename(self.test_instance_dir)
		fout = open(self.test_instance_list_file, 'w+')
		for instance_path in self.test_instance_list:
			fout.write(instance_path + '\n')
		fout.close()
	
	def create_feature_data(self):
		if not os.path.exists(self.test_feature_data_dir):
			os.system('mkdir -p %s' % (self.test_feature_data_dir))
		if not os.path.exists(self.test_feature_data_tmp_dir):
			os.system('mkdir -p %s' % (self.test_feature_data_tmp_dir))
		if not os.path.exists(self.test_feature_data_csv_path):
			Sparkle_CSV.create_empty_csv(self.test_feature_data_csv_path)
		
		train_feature_data_csv = Sparkle_Feature_Data_CSV(sparkle_global_help.feature_data_csv_path + '_train.csv')
		feature_data_csv = Sparkle_Feature_Data_CSV(self.test_feature_data_csv_path)
		
		instance_list = self.test_instance_list
		for instance_path in instance_list:
			feature_data_csv.add_row(instance_path)
		
		for column_name in train_feature_data_csv.list_columns():
			feature_data_csv.add_column(column_name)
		
		feature_data_csv.update_csv()
		
		
	def create_performance_data(self):
		if not os.path.exists(self.test_performance_data_dir):
			os.system('mkdir -p %s' % (self.test_performance_data_dir))	
		if not os.path.exists(self.test_performance_data_tmp_dir):
			os.system('mkdir -p %s' % (self.test_performance_data_tmp_dir))
		if not os.path.exists(self.test_performance_data_csv_path):
			Sparkle_CSV.create_empty_csv(self.test_performance_data_csv_path)
		
		performance_data_csv = Sparkle_Performance_Data_CSV(self.test_performance_data_csv_path)
		
		instance_list = self.test_instance_list
		for instance_path in instance_list:
			performance_data_csv.add_row(instance_path)
		
		solver_list = sparkle_global_help.solver_list
		for solver_path in solver_list:
			performance_data_csv.add_column(solver_path)
		
		performance_data_csv.update_csv()
		
	
	def create_test_tmp_dir(self):
		if not os.path.exists(self.test_tmp_dir):
			os.system('mkdir -p %s' % (self.test_tmp_dir))
		
		my_dir = self.test_tmp_dir + 'SBATCH_Extractor_Jobs/'
		if not os.path.exists(my_dir):
			os.system('mkdir -p %s' % (my_dir))
			
		my_dir = self.test_tmp_dir + 'SBATCH_Portfolio_Jobs/'
		if not os.path.exists(my_dir):
			os.system('mkdir -p %s' % (my_dir))
			
		my_dir = self.test_tmp_dir + 'SBATCH_Report_Jobs/'
		if not os.path.exists(my_dir):
			os.system('mkdir -p %s' % (my_dir))
		
		my_dir = self.test_tmp_dir + 'SBATCH_Solver_Jobs/'
		if not os.path.exists(my_dir):
			os.system('mkdir -p %s' % (my_dir))
		
		my_dir = self.test_tmp_dir + 'tmp/'
		if not os.path.exists(my_dir):
			os.system('mkdir -p %s' % (my_dir))
	
	def create_report_dir(self):
		ori_latex_path = r'Components/Sparkle-latex-generator-for-test-cases/'
		if not os.path.exists(self.test_report_dir):
			command_line = 'cp -r %s %s' % (ori_latex_path, self.test_report_dir)
			os.system(command_line)
		return
	
	def generate_computing_features_sbatch_shell_script(self, sbatch_shell_script_path, num_job_in_parallel, feature_data_csv_path, list_jobs, start_index, end_index):
		job_name = sfh.get_file_name(sbatch_shell_script_path)
		num_job_total = end_index - start_index
		if num_job_in_parallel > num_job_total:
			num_job_in_parallel = num_job_total
		command_prefix = r'srun -N1 -n1 --exclusive python2 Commands/sparkle_test_help/compute_features_core.py '
		
		fout = open(sbatch_shell_script_path, 'w+')
		fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
		fout.write(r'#!/bin/bash' + '\n')
		fout.write(r'###' + '\n')
		fout.write(r'#SBATCH --job-name=' + job_name + '\n')
		fout.write(r'#SBATCH --output=' + self.test_tmp_dir + job_name + r'.txt' + '\n')
		fout.write(r'#SBATCH --error=' + self.test_tmp_dir + job_name + r'.err' + '\n')
		fout.write(r'###' + '\n')
		fout.write(r'###' + '\n')
		fout.write(r'#SBATCH --partition=grace30' + '\n')
		fout.write('#SBATCH --mem-per-cpu=%d' % (ser.memory_limit_each_extractor_run) + '\n')
		fout.write(r'#SBATCH --array=0-' + str(num_job_total-1) + r'%' + str(num_job_in_parallel) + '\n')
		fout.write(r'###' + '\n')
		
		fout.write('params=( \\' + '\n')
		
		for i in range(start_index, end_index):
			instance_path = list_jobs[i][0]
			extractor_path = list_jobs[i][1]
			fout.write('\'%s %s\' \\' % (instance_path, extractor_path) + '\n')
		
		fout.write(')' + '\n')
		
		command_line = command_prefix + ' ' + r'${params[$SLURM_ARRAY_TASK_ID]}' + ' ' + feature_data_csv_path + ' ' + self.test_case_dir
		
		fout.write(command_line + '\n')
		fout.close()
		return
	
	def computing_features_parallel(self):
		num_job_in_parallel = ser.num_job_in_parallel
		feature_data_csv = Sparkle_Feature_Data_CSV(self.test_feature_data_csv_path)
		list_feature_computation_job = feature_data_csv.get_list_remaining_feature_computation_job()
		
		runsolver_path = sparkle_global_help.runsolver_path
		if len(sparkle_global_help.extractor_list)==0: cutoff_time_each_extractor_run = ser.cutoff_time_total_extractor_run_on_one_instance + 1
		else: cutoff_time_each_extractor_run = ser.cutoff_time_total_extractor_run_on_one_instance/len(sparkle_global_help.extractor_list) + 1
		cutoff_time_each_run_option = r'-C ' + str(cutoff_time_each_extractor_run)
		
		total_job_num = sparkle_job_help.get_num_of_total_job_from_list(list_feature_computation_job)
		total_job_list = sparkle_job_help.expand_total_job_from_list(list_feature_computation_job)
		
		i = 0
		j = len(total_job_list)
		sbatch_shell_script_path = self.test_tmp_dir + r'computing_features_sbatch_shell_script_' + str(i) + r'_' + str(j) + r'_' + sparkle_basic_help.get_time_pid_random_string() + r'.sh'
		self.generate_computing_features_sbatch_shell_script(sbatch_shell_script_path, num_job_in_parallel, self.test_feature_data_csv_path, total_job_list, i, j)
		os.system(r'chmod a+x ' + sbatch_shell_script_path)
		command_line = r'sbatch ' + sbatch_shell_script_path
		#os.system(command_line)
	
		output_list = os.popen(command_line).readlines()
		if len(output_list) > 0 and len(output_list[0].strip().split())>0:
			jobid = output_list[0].strip().split()[-1]
		else:
			jobid = ''
		return jobid
	
	def generate_running_solvers_sbatch_shell_script(self, sbatch_shell_script_path, num_job_in_parallel, performance_data_csv_path, list_jobs, start_index, end_index):
		job_name = sfh.get_file_name(sbatch_shell_script_path)
		num_job_total = end_index - start_index
		if num_job_in_parallel > num_job_total:
			num_job_in_parallel = num_job_total
		command_prefix = r'srun -N1 -n1 --exclusive python2 Commands/sparkle_test_help/run_solvers_core.py '
	
		fout = open(sbatch_shell_script_path, 'w+')
		fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
		
		fout.write(r'#!/bin/bash' + '\n')
		fout.write(r'###' + '\n')
		fout.write(r'###' + '\n')
		fout.write(r'#SBATCH --job-name=' + job_name + '\n')
		fout.write(r'#SBATCH --output=' + self.test_tmp_dir + job_name + r'.txt' + '\n')
		fout.write(r'#SBATCH --error=' + self.test_tmp_dir + job_name + r'.err' + '\n')
		fout.write(r'###' + '\n')
		fout.write(r'###' + '\n')
		fout.write(r'#SBATCH --partition=grace30' + '\n')
		fout.write('#SBATCH --mem-per-cpu=%d' % (ser.memory_limit_each_solver_run) + '\n')
		fout.write(r'#SBATCH --array=0-' + str(num_job_total-1) + r'%' + str(num_job_in_parallel) + '\n')
		fout.write(r'###' + '\n')
		
		fout.write('params=( \\' + '\n')
		
		for i in range(start_index, end_index):
			instance_path = list_jobs[i][0]
			solver_path = list_jobs[i][1]
			fout.write('\'%s %s\' \\' % (instance_path, solver_path) + '\n')
		
		fout.write(r')' + '\n')
		
		command_line = command_prefix + r' ' + r'${params[$SLURM_ARRAY_TASK_ID]}' + r' ' + performance_data_csv_path + ' ' + self.test_case_dir
		
		fout.write(command_line + '\n')
		fout.close()
		return
	
	def running_solvers_parallel(self):
		num_job_in_parallel = ser.num_job_in_parallel
		performance_data_csv = Sparkle_Performance_Data_CSV(self.test_performance_data_csv_path)
		list_performance_computation_job = performance_data_csv.get_list_remaining_performance_computation_job()
		
		total_job_num = sparkle_job_help.get_num_of_total_job_from_list(list_performance_computation_job)
		total_job_list = sparkle_job_help.expand_total_job_from_list(list_performance_computation_job)
		
		i = 0
		j = len(total_job_list)
		sbatch_shell_script_path = self.test_tmp_dir + r'running_solvers_sbatch_shell_script_' + str(i) + r'_' + str(j) + r'_' + sparkle_basic_help.get_time_pid_random_string() + r'.sh'
		self.generate_running_solvers_sbatch_shell_script(sbatch_shell_script_path, num_job_in_parallel, self.test_performance_data_csv_path, total_job_list, i, j)
		os.system(r'chmod a+x ' + sbatch_shell_script_path)
		command_line = r'sbatch ' + sbatch_shell_script_path
		#os.system(command_line)
	
		output_list = os.popen(command_line).readlines()
		if len(output_list) > 0 and len(output_list[0].strip().split())>0:
			jobid = output_list[0].strip().split()[-1]
		else:
			jobid = ''
		return jobid
	
	def generate_analysing_portfolio_selector_shell_script(self, sbatch_shell_script_path, num_job_in_parallel, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, par_num, list_jobs, start_index, end_index, dependency_jobid_list = []):
		job_name = sfh.get_file_name(sbatch_shell_script_path)
		num_job_total = end_index - start_index
		if num_job_in_parallel > num_job_total:
			num_job_in_parallel = num_job_total
		command_prefix = r'srun -N1 -n1 --exclusive python2 Commands/sparkle_test_help/analyse_portfolio_selector_one_time_core.py '
		
		fout = open(sbatch_shell_script_path, 'w+')
		fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
		
		fout.write(r'#!/bin/bash' + '\n')
		fout.write(r'###' + '\n')
		fout.write(r'#SBATCH --job-name=' + job_name + '\n')
		fout.write(r'#SBATCH --output=' + r'TMP/tmp/%A_%a.txt' + '\n')
		fout.write(r'#SBATCH --error=' + r'TMP/tmp/%A_%a.err' + '\n')
		fout.write(r'###' + '\n')
		fout.write(r'###' + '\n')
		fout.write(r'#SBATCH --partition=grace30' + '\n')
		fout.write('#SBATCH --mem-per-cpu=3000' + '\n')
		dependency_list_str = self.get_dependency_list_str(dependency_jobid_list)
		if dependency_list_str.strip() != '':
			fout.write(r'#SBATCH --dependency=' + dependency_list_str + '\n')
		fout.write(r'#SBATCH --array=0-' + str(num_job_total-1) + r'%' + str(num_job_in_parallel) + '\n')
		fout.write(r'###' + '\n')
		
		fout.write('params=( \\' + '\n')
		
		for i in range(start_index, end_index):
			portfolio_selector_path = list_jobs[i][0]
			excluded_solver = list_jobs[i][1]
			fout.write('\'%s %s %s %d %d %s\'\n' % (portfolio_selector_path, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, par_num, excluded_solver))
		
		fout.write(r')' + '\n')
		command_line = command_prefix + r' ' + r'${params[$SLURM_ARRAY_TASK_ID]}' + ' ' + self.test_case_dir
		fout.write(command_line + '\n')
		fout.close()
		return
	
	def analysing_portfolio_parallel(self, dependency_jobid_list = []):
		portfolio_selector_path_basis = sparkle_global_help.sparkle_portfolio_selector_path
		num_job_in_parallel = ser.num_job_in_parallel
		performance_data_csv_path = self.test_performance_data_csv_path
		feature_data_csv_path = self.test_feature_data_csv_path
		cutoff_time_each_run = ser.cutoff_time_each_run
		par_num = ser.par_num
		
		performance_data_csv = Sparkle_Performance_Data_CSV(performance_data_csv_path)
		total_job_list = []
		
		portfolio_selector_path = portfolio_selector_path_basis
		excluded_solver = ''
		total_job_list.append([portfolio_selector_path, excluded_solver])
		
		for excluded_solver in performance_data_csv.list_columns():
			portfolio_selector_path = portfolio_selector_path_basis
			total_job_list.append([portfolio_selector_path, excluded_solver])
		
		i = 0
		j = len(total_job_list)
		sbatch_shell_script_path = self.test_tmp_dir + r'analysing_portfolio_selector_sbatch_shell_script_' + str(i) + '_' + str(j) + '_' + sparkle_basic_help.get_time_pid_random_string() + r'.sh'
		self.generate_analysing_portfolio_selector_shell_script(sbatch_shell_script_path, num_job_in_parallel, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, par_num, total_job_list, i, j, dependency_jobid_list)
		os.system(r'chmod a+x ' + sbatch_shell_script_path)
		command_line = r'sbatch ' + sbatch_shell_script_path
		#os.system(command_line)
		
		output_list = os.popen(command_line).readlines()
		if len(output_list) > 0 and len(output_list[0].strip().split())>0:
			jobid = output_list[0].strip().split()[-1]
		else:
			jobid = ''
		return jobid
		
	def generating_report(self):
		latex_directory_path = self.test_report_dir
		latex_template_filename = r'template-Sparkle.tex'
		latex_report_filename = r'Sparkle_Report'
		dict_variable_to_value = self.get_dict_variable_to_value()
		
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
			if variable_key != r'figure-portfolio-selector-sparkle-vs-sbs' and variable_key != r'figure-portfolio-selector-sparkle-vs-vbs' and variable_key != r'test-figure-portfolio-selector-sparkle-vs-sbs' and variable_key != r'test-figure-portfolio-selector-sparkle-vs-vbs':
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
	
	def get_dict_variable_to_value(self):
		mydict = {}
		
		variable = r'customCommands'
		str_value = self.get_customCommands()
		mydict[variable] = str_value
		
		variable = r'sparkle'
		str_value = self.get_sparkle()
		mydict[variable] = str_value
		
		variable = r'sparkleVersion'
		str_value = self.get_sparkleVersion()
		mydict[variable] = str_value
		
		variable = r'numSolvers'
		str_value = self.get_numSolvers()
		mydict[variable] = str_value
	
		variable = r'solverList'
		str_value = self.get_solverList()
		mydict[variable] = str_value
		
		variable = r'numFeatureExtractors'
		str_value = self.get_numFeatureExtractors()
		mydict[variable] = str_value
		
		variable = r'featureExtractorList'
		str_value = self.get_featureExtractorList()
		mydict[variable] = str_value
		
		variable = r'numTotalInstances'
		str_value = self.get_numTotalInstances()
		mydict[variable] = str_value
		
		variable = r'numInstanceClasses'
		str_value = self.get_numInstanceClasses()
		mydict[variable] = str_value
		
		variable = r'instanceClassList'
		str_value = self.get_instanceClassList()
		mydict[variable] = str_value
		
		variable = r'featureComputationCutoffTime'
		str_value = self.get_featureComputationCutoffTime()
		mydict[variable] = str_value
		
		variable = r'featureComputationMemoryLimit'
		str_value = self.get_featureComputationMemoryLimit()
		mydict[variable] = str_value
	
		variable = r'performanceComputationCutoffTime'
		str_value = self.get_performanceComputationCutoffTime()
		mydict[variable] = str_value
	
		variable = r'performanceComputationMemoryLimit'
		str_value = self.get_performanceComputationMemoryLimit()
		mydict[variable] = str_value
		
		dict_actual_portfolio_selector_penalty_time_on_each_instance = self.get_dict_actual_portfolio_selector_penalty_time_on_each_instance()
		
		variable = r'figure-portfolio-selector-sparkle-vs-sbs'
		str_value = self.get_figure_portfolio_selector_sparkle_vs_sbs(dict_actual_portfolio_selector_penalty_time_on_each_instance)
		mydict[variable] = str_value
		
		variable = r'figure-portfolio-selector-sparkle-vs-vbs'
		str_value = self.get_figure_portfolio_selector_sparkle_vs_vbs(dict_actual_portfolio_selector_penalty_time_on_each_instance)
		mydict[variable] = str_value
	
		variable = r'parNum'
		str_value = self.get_parNum()
		mydict[variable] = str_value
	
		variable = r'PenaltyTimeRankingList'
		str_value = self.get_PenaltyTimeRankingList()
		mydict[variable] = str_value
		
		str_value_solverPerfectRankingList, str_value_VBSPenaltyTime, str_value_perfectPortfolioPenaltyTimeList = self.get_perfect_selector_related_information()
		mydict['solverPerfectRankingList'] = str_value_solverPerfectRankingList
		mydict['VBSPenaltyTime'] = str_value_VBSPenaltyTime
		mydict['perfectPortfolioPenaltyTimeList'] = str_value_perfectPortfolioPenaltyTimeList
		
		str_value_solverActualRankingList, str_value_actualPenaltyTime, str_value_actualPortfolioPenaltyTimeList = self.get_actual_selector_related_information()
		mydict['solverActualRankingList'] = str_value_solverActualRankingList
		mydict['actualPenaltyTime'] = str_value_actualPenaltyTime
		mydict['actualPortfolioPenaltyTimeList'] = str_value_actualPortfolioPenaltyTimeList
		
		variable = r'numTestTotalInstances'
		str_value = self.get_numTestTotalInstances()
		mydict[variable] = str_value
		
		variable = r'numTestInstanceClasses'
		str_value = self.get_numTestInstanceClasses()
		mydict[variable] = str_value
		
		variable = r'testInstanceClassList'
		str_value = self.get_testInstanceClassList()
		mydict[variable] = str_value
		
		variable = r'testPenaltyTimeRankingList'
		str_value = self.get_testPenaltyTimeRankingList()
		mydict[variable] = str_value
		
		str_value_testSolverPerfectRankingList, str_value_testVBSPenaltyTime, str_value_testPerfectPortfolioPenaltyTimeList = self.get_test_perfect_selector_related_information()
		mydict['testSolverPerfectRankingList'] = str_value_testSolverPerfectRankingList
		mydict['testVBSPenaltyTime'] = str_value_testVBSPenaltyTime
		mydict['testPerfectPortfolioPenaltyTimeList'] = str_value_testPerfectPortfolioPenaltyTimeList
		
		str_value_testSolverActualRankingList, str_value_testActualPenaltyTime, str_value_testActualPortfolioPenaltyTimeList = self.get_test_actual_selector_related_information()
		mydict['testSolverActualRankingList'] = str_value_testSolverActualRankingList
		mydict['testActualPenaltyTime'] = str_value_testActualPenaltyTime
		mydict['testActualPortfolioPenaltyTimeList'] = str_value_testActualPortfolioPenaltyTimeList
		
		dict_test_actual_portfolio_selector_penalty_time_on_each_instance = self.get_dict_test_actual_portfolio_selector_penalty_time_on_each_instance()
		
		variable = r'test-figure-portfolio-selector-sparkle-vs-sbs'
		str_value = self.get_test_figure_portfolio_selector_sparkle_vs_sbs(dict_test_actual_portfolio_selector_penalty_time_on_each_instance)
		mydict[variable] = str_value
		
		variable = r'test-figure-portfolio-selector-sparkle-vs-vbs'
		str_value = self.get_test_figure_portfolio_selector_sparkle_vs_vbs(dict_test_actual_portfolio_selector_penalty_time_on_each_instance)
		mydict[variable] = str_value
	
		variable = r'r_for_constructing_portfolio_selector'
		str_value = str(ser.r_for_constructing_portfolio_selector)
		mydict[variable] = str_value
		
		variable = r'runcount_limit_for_autofolio'
		str_value = str(ser.runcount_limit_for_autofolio)
		mydict[variable] = str_value
		
		variable = r'wallclock_limit_for_autofolio'
		str_value = str(ser.wallclock_limit_for_autofolio)
		mydict[variable] = str_value
		
		return mydict
		
	def get_customCommands(self):
		str_value = r''
		return str_value
	
	def get_sparkle(self):
		str_value = r'\emph{Sparkle}'
		return str_value
	
	def get_sparkleVersion(self):
		str_value = r'Sparkle_SAT_Challenge_2018'
		return str_value
	
	def get_numSolvers(self):
		num_solvers = len(sparkle_global_help.solver_list)
		str_value = str(num_solvers)
		return str_value

	def get_solverList(self):
		str_value = r''
		solver_list = sparkle_global_help.solver_list
		for solver_path in solver_list:
			solver_name = sfh.get_file_name(solver_path)
			str_value += r'\item \textbf{' + solver_name + r'}' + '\n'
		return str_value
	
	def get_numFeatureExtractors(self):
		num_feature_extractors = len(sparkle_global_help.extractor_list)
		str_value = str(num_feature_extractors)
		return str_value
	
	def get_featureExtractorList(self):
		str_value = r''
		extractor_list = sparkle_global_help.extractor_list
		for extractor_path in extractor_list:
			extractor_name = sfh.get_file_name(extractor_path)
			str_value += r'\item \textbf{' + extractor_name + r'}' + '\n'
		return str_value
	
	def get_numTotalInstances(self):
		num_total_instances = len(sparkle_global_help.instance_list)
		str_value = str(num_total_instances)
		return str_value
	
	def get_numInstanceClasses(self):
		list_instance_class = []
		instance_list = sparkle_global_help.instance_list
		for instance_path in instance_list:
			instance_class = sfh.get_current_directory_name(instance_path)
			if not (instance_class in list_instance_class):
				list_instance_class.append(instance_class)
		str_value = str(len(list_instance_class))
		return str_value
	
	def get_instanceClassList(self):
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
	
	def get_featureComputationCutoffTime(self):
		str_value = str(ser.cutoff_time_total_extractor_run_on_one_instance)
		return str_value

	def get_featureComputationMemoryLimit(self):
		str_value = str(ser.memory_limit_each_extractor_run)
		return str_value

	def get_performanceComputationCutoffTime(self):
		str_value = str(ser.cutoff_time_each_run)
		return str_value

	def get_performanceComputationMemoryLimit(self):
		str_value = str(ser.memory_limit_each_solver_run)
		return str_value
	
	def get_dict_actual_portfolio_selector_penalty_time_on_each_instance(self):
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
		else:
			mydict = {}
			return mydict
	
	def get_dict_sbs_penalty_time_on_each_instance(self):
		mydict = {}
		performance_data_csv = Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path + '_validate.csv')
		cutoff_time_each_run = ser.cutoff_time_each_run
		par_num = ser.par_num
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
		
	def get_figure_portfolio_selector_sparkle_vs_sbs(self, dict_actual_portfolio_selector_penalty_time_on_each_instance):
		str_value = r''
		dict_sbs_penalty_time_on_each_instance = self.get_dict_sbs_penalty_time_on_each_instance()
		cutoff_time_each_run = ser.cutoff_time_each_run
		par_num = ser.par_num
		penalty_time_each_run = cutoff_time_each_run * par_num
	
		latex_directory_path = self.test_report_dir
		figure_portfolio_selector_sparkle_vs_sbs_filename = r'figure_portfolio_selector_sparkle_vs_sbs'
		data_portfolio_selector_sparkle_vs_sbs_filename = r'data_portfolio_selector_sparkle_vs_sbs_filename.dat'
		data_portfolio_selector_sparkle_vs_sbs_filepath = latex_directory_path + data_portfolio_selector_sparkle_vs_sbs_filename
	
		fout = open(data_portfolio_selector_sparkle_vs_sbs_filepath, 'w+')
		for instance in dict_sbs_penalty_time_on_each_instance:
			sbs_penalty_time = dict_sbs_penalty_time_on_each_instance[instance]
			sparkle_penalty_time = dict_actual_portfolio_selector_penalty_time_on_each_instance[instance]
			fout.write(str(sbs_penalty_time) + r' ' + str(sparkle_penalty_time) + '\n')
		fout.close()
	
		performance_data_csv = Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path + '_validate.csv')
		cutoff_time_each_run = ser.cutoff_time_each_run
		solver_penalty_time_ranking_list = performance_data_csv.get_solver_penalty_time_ranking_list(cutoff_time_each_run, par_num)
		sbs_solver = solver_penalty_time_ranking_list[0][0]
	
		gnuplot_command = r'cd ' + latex_directory_path + r'; python auto_gen_plot.py ' + data_portfolio_selector_sparkle_vs_sbs_filename + r' ' + str(penalty_time_each_run) + r' ' + '\'SBS (' + sfh.get_file_name(sbs_solver) + ')\' ' + r'Sparkle_Selector' + r' ' + figure_portfolio_selector_sparkle_vs_sbs_filename + r' ' + str(par_num)
	
		#print(gnuplot_command)
	
		os.system(gnuplot_command)
	
		str_value = '\\includegraphics[width=0.6\\textwidth]{%s}' % (figure_portfolio_selector_sparkle_vs_sbs_filename)
		return str_value

	def get_dict_vbs_penalty_time_on_each_instance(self):
		performance_data_csv = Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path + '_validate.csv')
		mydict = performance_data_csv.get_dict_vbs_penalty_time_on_each_instance()
		return mydict


	def get_figure_portfolio_selector_sparkle_vs_vbs(self, dict_actual_portfolio_selector_penalty_time_on_each_instance):
		str_value = r''
		dict_vbs_penalty_time_on_each_instance = self.get_dict_vbs_penalty_time_on_each_instance()
		cutoff_time_each_run = ser.cutoff_time_each_run
		par_num = ser.par_num
		penalty_time_each_run = cutoff_time_each_run * par_num
	
		latex_directory_path = self.test_report_dir
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
	
	def get_parNum(self):
		par_num = ser.par_num
		return str(par_num)
		
	def get_PenaltyTimeRankingList(self):
		str_value = r''
		performance_data_csv = Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path + '_validate.csv')
		cutoff_time_each_run = ser.cutoff_time_each_run
		par_num = ser.par_num
	
		solver_penalty_time_ranking_list = performance_data_csv.get_solver_penalty_time_ranking_list(cutoff_time_each_run, par_num)
	
		rank_num = 1
		for solver, this_penalty_time in solver_penalty_time_ranking_list:
			#str_value += r'\item \textbf{' + sfh.get_file_name(solver) + '}, PAR%d: ' % (par_num) + str(this_penalty_time) + '\n'
			str_value += '%d & %s & %.6f' % (rank_num, sfh.get_file_name(solver), float(this_penalty_time)) + '\\\\' + '\n'
			rank_num += 1
	
		return str_value
	
	def get_perfect_selector_related_information(self):
		str_value_solverPerfectRankingList = ''
		str_value_VBSPenaltyTime = ''
		str_value_perfectPortfolioPenaltyTimeList = ''
	
		par_num = ser.par_num
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
					str_value_solverPerfectRankingList += '%d & %s & %.6f & %.6f \\\\ \n' % (solver_rank, solver, float(solver_rmc), float(dict_amc[solver]))
					solver_rank += 1
	
		list_perfectPortfolioPenaltyTimeList.sort(key=lambda item: item[1])
	
		for solver, penalty_time_value in list_perfectPortfolioPenaltyTimeList:
			str_value_perfectPortfolioPenaltyTimeList += 'Perfect Portfolio Selector excluding \\emph{%s} & %.6f \\\\ \n' % (solver, penalty_time_value)
	
		return str_value_solverPerfectRankingList, str_value_VBSPenaltyTime, str_value_perfectPortfolioPenaltyTimeList
	
	def get_actual_selector_related_information(self):
		str_value_solverActualRankingList = ''
		str_value_actualPenaltyTime = ''
		str_value_actualPortfolioPenaltyTimeList = ''
	
		str_value_solverActualRankingList, str_value_actualPenaltyTime, str_value_actualPortfolioPenaltyTimeList = self.get_actual_selector_related_information_from_existing_analysis_files()
		return str_value_solverActualRankingList, str_value_actualPenaltyTime, str_value_actualPortfolioPenaltyTimeList
	
	def get_actualPenaltyTime_from_exisiting_analysis_file(self, portfolio_selector_penalty_time_on_each_instance_path):
		cutoff_time_each_run = ser.cutoff_time_each_run
		par_num = ser.par_num
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
	
	def get_actual_selector_related_information_from_existing_analysis_files(self):
		str_value_solverActualRankingList = ''
		str_value_actualPenaltyTime = ''
		str_value_actualPortfolioPenaltyTimeList = ''
	
		portfolio_selector_path_basis = sparkle_global_help.sparkle_portfolio_selector_path
		portfolio_selector_path = portfolio_selector_path_basis
		portfolio_selector_penalty_time_on_each_instance_path = portfolio_selector_path + '_penalty_time_on_each_instance.txt'
		actual_portfolio_selector_penalty_time_value = self.get_actualPenaltyTime_from_exisiting_analysis_file(portfolio_selector_penalty_time_on_each_instance_path)
		str_value_actualPenaltyTime = '%.6f' % (actual_portfolio_selector_penalty_time_value)
	
		list_actualPortfolioPenaltyTimeList = []
		performance_data_csv_path = sparkle_global_help.performance_data_csv_path + '_validate.csv'
		performance_data_csv = Sparkle_Performance_Data_CSV(performance_data_csv_path)
		for excluded_solver in performance_data_csv.list_columns():	
			portfolio_selector_path = portfolio_selector_path_basis + '_excluding_' + sfh.get_last_level_directory_name(excluded_solver)
			portfolio_selector_penalty_time_on_each_instance_path = portfolio_selector_path + '_penalty_time_on_each_instance.txt'
			solver = sfh.get_last_level_directory_name(excluded_solver)
			penalty_time_value = self.get_actualPenaltyTime_from_exisiting_analysis_file(portfolio_selector_penalty_time_on_each_instance_path)
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
	
	def get_numTestTotalInstances(self):
		performance_data_csv = Sparkle_Performance_Data_CSV(self.test_performance_data_csv_path)
		num_test_instances = len(performance_data_csv.list_rows())
		str_value = str(num_test_instances)
		return str_value

	def get_numTestInstanceClasses(self):
		performance_data_csv = Sparkle_Performance_Data_CSV(self.test_performance_data_csv_path)
		list_instance_class = []
		instance_list = performance_data_csv.list_rows()
		for instance_path in instance_list:
			instance_class = sfh.get_current_directory_name(instance_path)
			if not (instance_class in list_instance_class):
				list_instance_class.append(instance_class)
		str_value = str(len(list_instance_class))
		return str_value
	
	def get_testInstanceClassList(self):
		performance_data_csv = Sparkle_Performance_Data_CSV(self.test_performance_data_csv_path)
		str_value = r''
		list_instance_class = []
		dict_number_of_instances_in_instance_class = {}
		instance_list = performance_data_csv.list_rows()
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
		
	def get_testPenaltyTimeRankingList(self):
		str_value = r''
		performance_data_csv = Sparkle_Performance_Data_CSV(self.test_performance_data_csv_path)
		cutoff_time_each_run = ser.cutoff_time_each_run
		par_num = ser.par_num
		
		solver_penalty_time_ranking_list = performance_data_csv.get_solver_penalty_time_ranking_list(cutoff_time_each_run, par_num)
		
		rank_num = 1
		for solver, this_penalty_time in solver_penalty_time_ranking_list:
			str_value += '%d & %s & %.6f' % (rank_num, sfh.get_file_name(solver), float(this_penalty_time)) + '\\\\' + '\n'
			rank_num += 1
		return str_value	
				
	def get_test_perfect_selector_related_information(self):
		str_value_testSolverPerfectRankingList = ''
		str_value_testVBSPenaltyTime = '' #
		str_value_testPerfectPortfolioPenaltyTimeList = ''
		
		cutoff_time_each_run = ser.cutoff_time_each_run
		par_num = ser.par_num
		par_num_str = 'PAR' + str(par_num)
		
		performance_data_csv = Sparkle_Performance_Data_CSV(self.test_performance_data_csv_path)
		virtual_best_penalty_time = performance_data_csv.calc_vbs_penalty_time(cutoff_time_each_run, par_num)
		str_value_testVBSPenaltyTime = '%.6f' % float(virtual_best_penalty_time)
		
		rank_list = scmc.compute_perfect_selector_marginal_contribution(self.test_performance_data_csv_path, cutoff_time_each_run, mode = 2)
		solver_rank = 1
		for solver, solver_rmc, solver_amc, tmp_virtual_best_penalty_time in rank_list:
			str_value_testSolverPerfectRankingList += '%d & %s & %.6f & %.6f \\\\ \n' % (solver_rank, sfh.get_last_level_directory_name(solver), float(solver_rmc), float(solver_amc))
		
		list_testPerfectPortfolioPenaltyTimeList = []
		for solver, solver_rmc, solver_amc, tmp_virtual_best_penalty_time in rank_list:
			list_testPerfectPortfolioPenaltyTimeList.append([solver, float(tmp_virtual_best_penalty_time)])
		
		list_testPerfectPortfolioPenaltyTimeList.sort(key=lambda item: item[1])
		
		for solver, penalty_time_value in list_testPerfectPortfolioPenaltyTimeList:
			str_value_testPerfectPortfolioPenaltyTimeList += 'Perfect Portfolio Selector excluding \\emph{%s} & %.6f \\\\ \n' % (sfh.get_last_level_directory_name(solver), penalty_time_value)
		
		return str_value_testSolverPerfectRankingList, str_value_testVBSPenaltyTime, str_value_testPerfectPortfolioPenaltyTimeList
	
	def get_test_actual_selector_related_information(self):
		str_value_testSolverActualRankingList = ''
		str_value_testActualPenaltyTime = ''
		str_value_testActualPortfolioPenaltyTimeList = ''
	
		str_value_testSolverActualRankingList, str_value_testActualPenaltyTime, str_value_testActualPortfolioPenaltyTimeList = self.get_test_actual_selector_related_information_from_existing_analysis_files()
		return str_value_testSolverActualRankingList, str_value_testActualPenaltyTime, str_value_testActualPortfolioPenaltyTimeList
	
	def get_test_actual_selector_related_information_from_existing_analysis_files(self):
		str_value_testSolverActualRankingList = ''
		str_value_testActualPenaltyTime = ''
		str_value_testActualPortfolioPenaltyTimeList = ''
		
		portfolio_selector_path_basis = self.test_case_dir + sfh.get_last_level_directory_name(sparkle_global_help.sparkle_portfolio_selector_path)
		portfolio_selector_path = portfolio_selector_path_basis
		portfolio_selector_penalty_time_on_each_instance_path = portfolio_selector_path + '_penalty_time_on_each_instance.txt'
		actual_portfolio_selector_penalty_time_value = self.get_actualPenaltyTime_from_exisiting_analysis_file(portfolio_selector_penalty_time_on_each_instance_path)
		str_value_testActualPenaltyTime = '%.6f' % (actual_portfolio_selector_penalty_time_value)
		
		list_actualPortfolioPenaltyTimeList = []
		performance_data_csv_path = self.test_performance_data_csv_path
		performance_data_csv = Sparkle_Performance_Data_CSV(performance_data_csv_path)
		for excluded_solver in performance_data_csv.list_columns():	
			portfolio_selector_path = portfolio_selector_path_basis + '_excluding_' + sfh.get_last_level_directory_name(excluded_solver)
			portfolio_selector_penalty_time_on_each_instance_path = portfolio_selector_path + '_penalty_time_on_each_instance.txt'
			solver = sfh.get_last_level_directory_name(excluded_solver)
			penalty_time_value = self.get_actualPenaltyTime_from_exisiting_analysis_file(portfolio_selector_penalty_time_on_each_instance_path)
			list_actualPortfolioPenaltyTimeList.append([solver, penalty_time_value])
		
		list_actualPortfolioPenaltyTimeList.sort(key=lambda item: item[1])
		
		for solver, penalty_time_value in list_actualPortfolioPenaltyTimeList:
			str_value_testActualPortfolioPenaltyTimeList += 'Actual Portfolio Selector excluding \\emph{%s} & %.6f \\\\ \n' % (solver, penalty_time_value)
		
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
			str_value_testSolverActualRankingList += '%d & %s & %.6f & %.6f \\\\ \n' % (solver_rank, solver, solver_rmc_value, solver_amc_value)
			solver_rank += 1
			
		return str_value_testSolverActualRankingList, str_value_testActualPenaltyTime, str_value_testActualPortfolioPenaltyTimeList
		
	def get_dict_test_actual_portfolio_selector_penalty_time_on_each_instance(self):
		portfolio_selector_penalty_time_on_each_instance_path = self.test_case_dir + sfh.get_last_level_directory_name(sparkle_global_help.sparkle_portfolio_selector_path) + '_penalty_time_on_each_instance.txt'
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
		else:
			mydict = {}
			return mydict
	
	def get_dict_test_sbs_penalty_time_on_each_instance(self):
		mydict = {}
		performance_data_csv = Sparkle_Performance_Data_CSV(self.test_performance_data_csv_path)
		cutoff_time_each_run = ser.cutoff_time_each_run
		par_num = ser.par_num
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
		
	def get_test_figure_portfolio_selector_sparkle_vs_sbs(self, dict_test_actual_portfolio_selector_penalty_time_on_each_instance):
		str_value = r''
		dict_sbs_penalty_time_on_each_instance = self.get_dict_test_sbs_penalty_time_on_each_instance()
		cutoff_time_each_run = ser.cutoff_time_each_run
		par_num = ser.par_num
		penalty_time_each_run = cutoff_time_each_run * par_num
		
		latex_directory_path = self.test_report_dir
		figure_portfolio_selector_sparkle_vs_sbs_filename = r'figure_test_portfolio_selector_sparkle_vs_sbs'
		data_portfolio_selector_sparkle_vs_sbs_filename = r'data_test_portfolio_selector_sparkle_vs_sbs_filename.dat'
		data_portfolio_selector_sparkle_vs_sbs_filepath = latex_directory_path + data_portfolio_selector_sparkle_vs_sbs_filename
		
		fout = open(data_portfolio_selector_sparkle_vs_sbs_filepath, 'w+')
		for instance in dict_sbs_penalty_time_on_each_instance:
			sbs_penalty_time = dict_sbs_penalty_time_on_each_instance[instance]
			sparkle_penalty_time = dict_test_actual_portfolio_selector_penalty_time_on_each_instance[instance]
			fout.write(str(sbs_penalty_time) + r' ' + str(sparkle_penalty_time) + '\n')
		fout.close()
		
		performance_data_csv = Sparkle_Performance_Data_CSV(self.test_performance_data_csv_path)
		cutoff_time_each_run = ser.cutoff_time_each_run
		solver_penalty_time_ranking_list = performance_data_csv.get_solver_penalty_time_ranking_list(cutoff_time_each_run, par_num)
		sbs_solver = solver_penalty_time_ranking_list[0][0]
	
		gnuplot_command = r'cd ' + latex_directory_path + r'; python auto_gen_plot.py ' + data_portfolio_selector_sparkle_vs_sbs_filename + r' ' + str(penalty_time_each_run) + r' ' + '\'SBS (' + sfh.get_file_name(sbs_solver) + ')\' ' + r'Sparkle_Selector' + r' ' + figure_portfolio_selector_sparkle_vs_sbs_filename + r' ' + str(par_num)
	
		#print(gnuplot_command)
	
		os.system(gnuplot_command)
	
		str_value = '\\includegraphics[width=0.6\\textwidth]{%s}' % (figure_portfolio_selector_sparkle_vs_sbs_filename)
		return str_value
		
	
	def get_dict_test_vbs_penalty_time_on_each_instance(self):
		performance_data_csv = Sparkle_Performance_Data_CSV(self.test_performance_data_csv_path)
		mydict = performance_data_csv.get_dict_vbs_penalty_time_on_each_instance()
		return mydict
	
	def get_test_figure_portfolio_selector_sparkle_vs_vbs(self, dict_test_actual_portfolio_selector_penalty_time_on_each_instance):
		str_value = r''
		dict_vbs_penalty_time_on_each_instance = self.get_dict_test_vbs_penalty_time_on_each_instance()
		cutoff_time_each_run = ser.cutoff_time_each_run
		par_num = ser.par_num
		penalty_time_each_run = cutoff_time_each_run * par_num
		
		latex_directory_path = self.test_report_dir
		figure_portfolio_selector_sparkle_vs_vbs_filename = r'figure_test_portfolio_selector_sparkle_vs_vbs'
		data_portfolio_selector_sparkle_vs_vbs_filename = r'data_test_portfolio_selector_sparkle_vs_vbs_filename.dat'
		data_portfolio_selector_sparkle_vs_vbs_filepath = latex_directory_path + data_portfolio_selector_sparkle_vs_vbs_filename
		
		fout = open(data_portfolio_selector_sparkle_vs_vbs_filepath, 'w+')
		for instance in dict_vbs_penalty_time_on_each_instance:
			vbs_penalty_time = dict_vbs_penalty_time_on_each_instance[instance]
			sparkle_penalty_time = dict_test_actual_portfolio_selector_penalty_time_on_each_instance[instance]
			fout.write(str(vbs_penalty_time) + r' ' + str(sparkle_penalty_time) + '\n')
		fout.close()
		
		gnuplot_command = r'cd ' + latex_directory_path + r'; python auto_gen_plot.py ' + data_portfolio_selector_sparkle_vs_vbs_filename + r' ' + str(penalty_time_each_run) + r' ' + r'VBS' + r' ' + r'Sparkle_Selector' + r' ' + figure_portfolio_selector_sparkle_vs_vbs_filename + r' ' + str(par_num)
	
		os.system(gnuplot_command)
	
		str_value = '\\includegraphics[width=0.6\\textwidth]{%s}' % (figure_portfolio_selector_sparkle_vs_vbs_filename)
		return str_value
	
	def get_dependency_list_str(self, dependency_jobid_list):
		dependency_list_str = ''
		for dependency_jobid in dependency_jobid_list:
			dependency_list_str += r'afterany:' + dependency_jobid + r','
		dependency_list_str = dependency_list_str[:-1]
		return dependency_list_str
		
