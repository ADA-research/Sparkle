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
from sparkle_help import sparkle_job_help


def get_list_running_extractor_jobs():
	list_running_extractor_jobs = []
	
	tmp_directory = r'Tmp/SBATCH_Extractor_Jobs/'
	list_all_statusinfo_filename = sfh.get_list_all_statusinfo_filename(tmp_directory)
	for statusinfo_filename in list_all_statusinfo_filename:
		statusinfo_filepath = tmp_directory + sfh.get_last_level_directory_name(statusinfo_filename)
		try:
			fin = open(statusinfo_filepath, 'r+')
			fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
			mylist1 = fin.readline().strip().split()
			status_str = mylist1[1]
			if not status_str == r'Running':
				fin.close()
				continue
			else:
				mylist2 = fin.readline().strip().split()
				extractor_name = mylist2[1]
				mylist3 = fin.readline().strip().split()
				instance_name = mylist3[1]
				mylist4 = fin.readline().strip().split()
				start_time_str = mylist4[2] + r' ' + mylist4[3]
				fin.readline()
				mylist5 = fin.readline().strip().split()
				cutoff_time_str = mylist5[2]
				fin.close()
				list_running_extractor_jobs.append([status_str, extractor_name, instance_name, start_time_str, cutoff_time_str])
		except:
			continue
	
	return list_running_extractor_jobs


def print_running_extractor_jobs(mode = 1):
	job_list = get_list_running_extractor_jobs()
	print(r'c')
	print(r'c Currently Sparkle has ' + str(len(job_list)) + r' running feature computation jobs:')
	
	if mode == 2:
		current_job_num = 1
		for i in range(0, len(job_list)):
			status_str = job_list[i][0]
			instance_name = job_list[i][1]
			extractor_name = job_list[i][2]
			start_time_str = job_list[i][3]
			cutoff_time_str = job_list[i][4]
			print(r'c [' + str(current_job_num) + r']: Extractor: ' + extractor_name + r', Instance: ' + instance_name + r', Start Time: ' + start_time_str + r', Cutoff Time: ' + cutoff_time_str + r' second(s)' + r', Status: ' + status_str)
			current_job_num += 1
		
	print(r'c')
	return



def get_list_running_solver_jobs():
	list_running_solver_jobs = []
	
	tmp_directory = r'Tmp/SBATCH_Solver_Jobs/'
	list_all_statusinfo_filename = sfh.get_list_all_statusinfo_filename(tmp_directory)
	for statusinfo_filename in list_all_statusinfo_filename:
		statusinfo_filepath = tmp_directory + sfh.get_last_level_directory_name(statusinfo_filename)
		try:
			fin = open(statusinfo_filepath, 'r+')
			fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
			mylist1 = fin.readline().strip().split()
			status_str = mylist1[1]
			if not status_str == r'Running':
				fin.close()
				continue
			else:
				mylist2 = fin.readline().strip().split()
				solver_name = mylist2[1]
				mylist3 = fin.readline().strip().split()
				instance_name = mylist3[1]
				mylist4 = fin.readline().strip().split()
				start_time_str = mylist4[2] + r' ' + mylist4[3]
				fin.readline()
				mylist5 = fin.readline().strip().split()
				cutoff_time_str = mylist5[2]
				fin.close()
				list_running_solver_jobs.append([status_str, solver_name, instance_name, start_time_str, cutoff_time_str])
		except:
			continue
	
	return list_running_solver_jobs


def print_running_solver_jobs(mode = 1):
	job_list = get_list_running_solver_jobs()
	print(r'c')
	print(r'c Currently Sparkle has ' + str(len(job_list)) + r' running performance computation jobs:')
	
	if mode == 2:
		current_job_num = 1
		for i in range(0, len(job_list)):
			status_str = job_list[i][0]
			instance_name = job_list[i][1]
			solver_name = job_list[i][2]
			start_time_str = job_list[i][3]
			cutoff_time_str = job_list[i][4]
			print(r'c [' + str(current_job_num) + r']: Solver: ' + solver_name + r', Instance: ' + instance_name + r', Start Time: ' + start_time_str + r', Cutoff Time: ' + cutoff_time_str + r' second(s)' + r', Status: ' + status_str)
			current_job_num += 1
		
	print(r'c')
	return


def print_running_portfolio_selector_jobs():
	print(r'c')
	key_str = 'construct_sparkle_portfolio_selector'
	task_run_status_path = r'Tmp/SBATCH_Portfolio_Jobs/' + key_str + r'.statusinfo'
	if os.path.isfile(task_run_status_path):
		print(r'c Currently Sparkle portfolio selecotr is constructing ...')
	else:
		print(r'c No currently running Sparkle portfolio selector construction job!')
	print(r'c')
	return


def print_running_report_jobs():
	print(r'c')
	key_str = 'generate_report'
	task_run_status_path = r'Tmp/SBATCH_Report_Jobs/' + key_str + r'.statusinfo'
	if os.path.isfile(task_run_status_path):
		print(r'c Currently Sparkle report is generating ...')
	else:
		print(r'c No currently running Sparkle report generation job!')
	print(r'c')
	return





