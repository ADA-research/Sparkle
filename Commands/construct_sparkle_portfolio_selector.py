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
import argparse
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_construct_portfolio_selector_help as scps
from sparkle_help import sparkle_compute_marginal_contribution_help as scmc
from sparkle_help import sparkle_job_help
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_logging as sl


def judge_exist_remaining_jobs(feature_data_csv_path, performance_data_csv_path):
	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
	list_feature_computation_job = feature_data_csv.get_list_remaining_feature_computation_job()
	total_job_num = sparkle_job_help.get_num_of_total_job_from_list(list_feature_computation_job)
	if total_job_num>0:
		return True
	
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	list_performance_computation_job = performance_data_csv.get_list_remaining_performance_computation_job()
	total_job_num = sparkle_job_help.get_num_of_total_job_from_list(list_performance_computation_job)
	if total_job_num>0:
		return True
	
	return False


def generate_task_run_status():
	key_str = 'construct_sparkle_portfolio_selector'
	task_run_status_path = r'Tmp/SBATCH_Portfolio_Jobs/' + key_str + r'.statusinfo'
	status_info_str = 'Status: Running\n'
	sfh.write_string_to_file(task_run_status_path, status_info_str)
	return


def delete_task_run_status():
	key_str = 'construct_sparkle_portfolio_selector'
	task_run_status_path = r'Tmp/SBATCH_Portfolio_Jobs/' + key_str + r'.statusinfo'
	os.system(r'rm -rf ' + task_run_status_path)
	return


def delete_log_files():
	os.system(r'rm -f ' + sgh.sparkle_log_path)
	os.system(r'rm -f ' + sgh.sparkle_err_path)
	return


def print_log_paths():
	print('c Consider investigating the log files:')
	print('c stdout: ' + sgh.sparkle_log_path)
	print('c stderr: ' + sgh.sparkle_err_path)
	return


if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()

	# Process command line arguments
	args = parser.parse_args()

	print('c Start constructing Sparkle portfolio selector ...')
	
	generate_task_run_status()
	
	flag_judge_exist_remaining_jobs = judge_exist_remaining_jobs(sgh.feature_data_csv_path, sgh.performance_data_csv_path)
	
	if flag_judge_exist_remaining_jobs:
		print(r'c There remain unperformed feature computation jobs or performance computation jobs!')
		print(r'c Please first execute all unperformed jobs before constructing Sparkle portfolio selecotr')
		print(r'c Sparkle portfolio selector is not successfully constructed!')
		delete_task_run_status()
		sys.exit()
	
	cutoff_time_each_run = scps.get_cutoff_time_each_run_from_cutoff_time_information_txt_path()

	delete_log_files() # Make sure no old log files remain
	scps.construct_sparkle_portfolio_selector(sgh.sparkle_portfolio_selector_path, sgh.performance_data_csv_path, sgh.feature_data_csv_path, cutoff_time_each_run)
	
	if not os.path.exists(sgh.sparkle_portfolio_selector_path):
		print('c Sparkle portfolio selector is not successfully constructed!')
		print('c There might be some errors!')
		print_log_paths()
		delete_task_run_status()
		sys.exit()
	else:
		print('c Sparkle portfolio selector constructed!')
		print('c Sparkle portfolio selector located at ' + sgh.sparkle_portfolio_selector_path)
		
		print(r"c Start computing each solver's marginal contribution to perfect selector ...")
		rank_list = scmc.compute_perfect_selector_marginal_contribution(cutoff_time_each_run = cutoff_time_each_run)
		scmc.print_rank_list(rank_list, 1)
		print(r'c Marginal contribution (perfect selector) computing done!')
	
		
		print(r"c Start computing each solver's marginal contribution to actual selector ...")
		rank_list = scmc.compute_actual_selector_marginal_contribution(cutoff_time_each_run = cutoff_time_each_run)
		scmc.print_rank_list(rank_list, 2)
		print(r'c Marginal contribution (actual selector) computing done!')
		delete_task_run_status()
		delete_log_files()

