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

if __name__ == r'__main__':

	
	my_flag_run_solver_later = False
	my_flag_nickname = False
	my_flag_parallel = False
	my_flag_incomplete = False
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
		elif sys.argv[i] == r'-incomplete':
			my_flag_incomplete = True
		else:
			solver_source = sys.argv[i]
		i += 1

	if not os.path.exists(solver_source):
		print r'c Solver path ' + "\'" + solver_source + "\'" + r' does not exist!'
		print r'c Usage: ' + sys.argv[0] + r' [-run-solver-later] [-nickname] [<nickname>] [-incomplete] [-parallel] <solver_source_directory>'
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
	if my_flag_incomplete:
		sfh.add_new_solver_into_file(solver_diretory, 'incomplete')
		sparkle_global_help.solver_complete_type_mapping[solver_diretory] = 'incomplete'
	else:
		sfh.add_new_solver_into_file(solver_diretory)
		sparkle_global_help.solver_complete_type_mapping[solver_diretory] = 'complete'
		
	print 'c Adding solver ' + sfh.get_last_level_directory_name(solver_diretory) + ' done!'
	
	if os.path.exists(sparkle_global_help.sparkle_portfolio_selector_path):
		command_line = r'rm -f ' + sparkle_global_help.sparkle_portfolio_selector_path
		os.system(command_line)
		command_line = r'rm -f ' + sparkle_global_help.sparkle_portfolio_selector_path + '*'
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


