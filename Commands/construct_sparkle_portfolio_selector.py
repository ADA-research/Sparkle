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
import argparse
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_construct_portfolio_selector_help as scps
import compute_marginal_contribution as cmc
from sparkle_help import sparkle_job_help
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings
from sparkle_help.sparkle_settings import PerformanceMeasure
from sparkle_help.sparkle_settings import SettingState
from sparkle_help import argparse_custom as ac


def judge_exist_remaining_jobs(feature_data_csv_path, performance_data_csv_path):
	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
	list_feature_computation_job = feature_data_csv.get_list_remaining_feature_computation_job()
	total_job_num = sparkle_job_help.get_num_of_total_job_from_list(list_feature_computation_job)

	if total_job_num > 0:
		return True

	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	list_performance_computation_job = performance_data_csv.get_list_remaining_performance_computation_job()
	total_job_num = sparkle_job_help.get_num_of_total_job_from_list(list_performance_computation_job)

	if total_job_num > 0:
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
	# Initialise settings
	global settings
	sgh.settings = sparkle_settings.Settings()

	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--recompute-portfolio-selector', action='store_true', help='force the construction of a new portfolio selector even when it already exists for the current feature and performance data. NOTE: This will also result in the computation of the marginal contributions of solvers to the new portfolio selector.')
	parser.add_argument('--recompute-marginal-contribution', action='store_true', help='force marginal contribution to be recomputed even when it already exists in file for the current selector')
	parser.add_argument('--performance-measure', choices=PerformanceMeasure.__members__, default=sgh.settings.DEFAULT_general_performance_measure, action=ac.SetByUser, help='the performance measure, e.g. runtime')

	# Process command line arguments
	args = parser.parse_args()
	flag_recompute_portfolio = args.recompute_portfolio_selector
	flag_recompute_marg_cont = args.recompute_marginal_contribution
	if ac.set_by_user(args, 'performance_measure'): sgh.settings.set_general_performance_measure(PerformanceMeasure.from_str(args.performance_measure), SettingState.CMD_LINE)

	print('c Start constructing Sparkle portfolio selector ...')

	generate_task_run_status()

	flag_judge_exist_remaining_jobs = judge_exist_remaining_jobs(sgh.feature_data_csv_path, sgh.performance_data_csv_path)

	if flag_judge_exist_remaining_jobs:
		print(r'c There remain unperformed feature computation jobs or performance computation jobs!')
		print(r'c Please first execute all unperformed jobs before constructing Sparkle portfolio selecotr')
		print(r'c Sparkle portfolio selector is not successfully constructed!')
		delete_task_run_status()
		sys.exit()

	delete_log_files() # Make sure no old log files remain
	success = scps.construct_sparkle_portfolio_selector(sgh.sparkle_portfolio_selector_path, sgh.performance_data_csv_path, sgh.feature_data_csv_path, flag_recompute_portfolio)

	if success:
		print('c Sparkle portfolio selector constructed!')
		print('c Sparkle portfolio selector located at ' + sgh.sparkle_portfolio_selector_path)

		# Compute and print marginal contributions of the perfect and actual portfolio selectors
		cmc.compute_perfect(flag_recompute_marg_cont)
		cmc.compute_actual(flag_recompute_marg_cont)

		delete_task_run_status()
		delete_log_files()

	# Write used settings to file
	sgh.settings.write_used_settings()

