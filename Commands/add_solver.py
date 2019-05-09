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
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_run_solvers_parallel_help as srsp
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_experiments_related_help
from sparkle_help import sparkle_job_parallel_help
from sparkle_help import sparkle_add_configured_solver_help as sacsh

if __name__ == r'__main__':

	
	my_flag_run_solver_later = False
	my_flag_nickname = False
	my_flag_parallel = False
	my_flag_deterministic = False
	deterministic = '0'
	nickname_str = r''
	solver_source = r''

	len_argv = len(sys.argv)
	i = 1
	while i<len_argv:
		if sys.argv[i] == r'-run-solver-later':
			my_flag_run_solver_later = True
		elif sys.argv[i] == r'-nickname':
			my_flag_nickname = True
			i += 1
			nickname_str = sys.argv[i]
		elif sys.argv[i] == r'-parallel':
			my_flag_parallel = True
		elif sys.argv[i] == r'-deterministic':
			i += 1
			if sys.argv[i] == r'0':
				my_flag_deterministic = True
				deterministic = r'0'
			elif sys.argv[i] == r'1':
				my_flag_deterministic = True
				deterministic = r'1'
			else:
				print(r'c Arguments Error!')
				print(r'c Usage: ' + sys.argv[0] + r' [-run-solver-later] [-nickname <nickname>] [-parallel] -deterministic {0, 1} <solver_source_directory>')
				sys.exit()
		else:
			solver_source = sys.argv[i]
		i += 1

	if not os.path.exists(solver_source):
		print r'c Solver path ' + "\'" + solver_source + "\'" + r' does not exist!'
		print r'c Usage: ' + sys.argv[0] + r' [-run-solver-later] [-nickname <nickname>] [-parallel] -deterministic {0, 1} <solver_source_directory>'
		sys.exit()
	
	if not my_flag_deterministic:
		print(r'c Please specify the deterministic property of the adding solver!')
		print(r'c Usage: ' + sys.argv[0] + r' [-run-solver-later] [-nickname <nickname>] [-parallel] -deterministic {0, 1} <solver_source_directory>')
		sys.exit()

	last_level_directory = r''
	last_level_directory = sfh.get_last_level_directory_name(solver_source)

	solver_diretory = r'Solvers/' + last_level_directory
	if not os.path.exists(solver_diretory): os.mkdir(solver_diretory)
	else:
		print r'c Solver ' + sfh.get_last_level_directory_name(solver_diretory) + r' already exists!'
		print r'c Do not add solver ' + sfh.get_last_level_directory_name(solver_diretory)
		sys.exit()

	os.system(r'cp -r ' + solver_source + r'/* ' + solver_diretory)

	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)
	performance_data_csv.add_column(solver_diretory)
	performance_data_csv.update_csv()

	sparkle_global_help.solver_list.append(solver_diretory)
	sfh.add_new_solver_into_file(solver_diretory, deterministic)
	
	print 'c Adding solver ' + sfh.get_last_level_directory_name(solver_diretory) + ' done!'
	
	if sacsh.check_adding_solver_contain_pcs_file(solver_diretory):
		pcs_file_name = sacsh.get_pcs_file_from_solver_directory(solver_diretory)
		smac_scenario_dir = sparkle_global_help.smac_dir + r'/' + r'example_scenarios/'
		command_line = r'cp -r ' + solver_diretory + r' ' + smac_scenario_dir
		os.system(command_line)
		smac_solver_dir = smac_scenario_dir + r'/' + sfh.get_last_level_directory_name(solver_source) + r'/'
		sacsh.create_necessary_files_for_configured_solver(smac_solver_dir)
		print('c pcs file detected, this is a configured solver')
		print('c solver added to SMAC')
	
	if os.path.exists(sparkle_global_help.sparkle_portfolio_selector_path):
		command_line = r'rm -f ' + sparkle_global_help.sparkle_portfolio_selector_path
		os.system(command_line)
		print 'c Removing Sparkle portfolio selector ' + sparkle_global_help.sparkle_portfolio_selector_path + ' done!'
	
	if os.path.exists(sparkle_global_help.sparkle_report_path):
		command_line = r'rm -f ' + sparkle_global_help.sparkle_report_path
		os.system(command_line)
		print 'c Removing Sparkle report ' + sparkle_global_help.sparkle_report_path + ' done!'
	
	if my_flag_nickname:
		sparkle_global_help.solver_nickname_mapping[nickname_str] = solver_diretory
		sfh.add_new_solver_nickname_into_file(nickname_str, solver_diretory)
		pass

	if not my_flag_run_solver_later:
		if not my_flag_parallel:
			print 'c Start running solvers ...'
			srs.running_solvers(sparkle_global_help.performance_data_csv_path, 1)
			print 'c Performance data file ' + sparkle_global_help.performance_data_csv_path + ' has been updated!'
			print 'c Running solvers done!'
		else:
			num_job_in_parallel = sparkle_experiments_related_help.num_job_in_parallel
			run_solvers_parallel_jobid = srsp.running_solvers_parallel(sparkle_global_help.performance_data_csv_path, num_job_in_parallel, 1)
			print 'c Running solvers in parallel ...'
			dependency_jobid_list = []
			if run_solvers_parallel_jobid:
				dependency_jobid_list.append(run_solvers_parallel_jobid)
			job_script = 'Commands/construct_sparkle_portfolio_selector.py'
			run_job_parallel_jobid = sparkle_job_parallel_help.running_job_parallel(job_script, dependency_jobid_list)
		
			if run_job_parallel_jobid:
				dependency_jobid_list.append(run_job_parallel_jobid)
			job_script = 'Commands/generate_report.py'
			run_job_parallel_jobid = sparkle_job_parallel_help.running_job_parallel(job_script, dependency_jobid_list)


