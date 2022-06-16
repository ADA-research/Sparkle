#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
from pathlib import Path

from sparkle_help import sparkle_basic_help as sbh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_file_help as sfh


global record_log_file_path
record_log_file_path = sgh.sparkle_err_path

def detect_current_sparkle_platform_exists():
	my_flag_anyone = False
	if os.path.exists(r'Instances/'): my_flag_anyone = True
	if os.path.exists(r'Solvers/'): my_flag_anyone = True
	if os.path.exists(r'Extractors/'): my_flag_anyone = True	
	if os.path.exists(r'Feature_Data/'): my_flag_anyone = True
	if os.path.exists(r'Performance_Data/'): my_flag_anyone = True
	if os.path.exists(r'Reference_Lists/'): my_flag_anyone = True
	if os.path.exists(r'Sparkle_Portfolio_Selector/'): my_flag_anyone = True
	if sgh.sparkle_parallel_portfolio_dir.exists():
		my_flag_anyone = True

	return my_flag_anyone


def save_current_sparkle_platform(my_record_filename):
	my_flag_instances = False
	my_flag_solvers = False
	my_flag_extractors = False
	my_flag_feature_data = False
	my_flag_performance_data = False
	my_flag_reference_lists = False
	my_flag_sparkle_portfolio_selector = False
	my_flag_sparkle_parallel_portfolio = False
	
	if os.path.exists(r'Instances/'): my_flag_instances = True
	if os.path.exists(r'Solvers/'): my_flag_solvers = True
	if os.path.exists(r'Extractors/'): my_flag_extractors = True
	if os.path.exists(r'Feature_Data/'): my_flag_feature_data = True
	if os.path.exists(r'Performance_Data/'): my_flag_performance_data = True
	if os.path.exists(r'Reference_Lists/'): my_flag_reference_lists = True
	if os.path.exists(r'Sparkle_Portfolio_Selector/'): my_flag_sparkle_portfolio_selector = True
	if sgh.sparkle_parallel_portfolio_dir.exists():
		my_flag_sparkle_parallel_portfolio = True
	
	if not os.path.exists(r'Tmp/'):
		output = os.mkdir(r'Tmp/')
	
	my_record_filename_exist = os.path.exists(my_record_filename)
	if not my_record_filename_exist:
		if my_flag_instances:
			my_record_filename_exist = True
			print(r'c Now recording current Sparkle platform in file ' + my_record_filename + r' ...')
			output = os.system(r'zip -r ' + my_record_filename + r' Instances/' + " >> " + record_log_file_path)
	else:
		if my_flag_instances:
			output = os.system(r'zip -g -r ' + my_record_filename + r' Instances/' + " >> " + record_log_file_path)
	
	if not my_record_filename_exist:
		if my_flag_solvers:
			my_record_filename_exist = True
			print(r'c Now recording current Sparkle platform in file ' + my_record_filename + r' ...')
			output = os.system(r'zip -r ' + my_record_filename + r' Solvers/' + " >> " + record_log_file_path)
	else:
		if my_flag_solvers:
			output = os.system(r'zip -g -r ' + my_record_filename + r' Solvers/' + " >> " + record_log_file_path)
			
	if not my_record_filename_exist:
		if my_flag_extractors:
			my_record_filename_exist = True
			print(r'c Now recording current Sparkle platform in file ' + my_record_filename + r' ...')
			output = os.system(r'zip -r ' + my_record_filename + r' Extractors/' + " >> " + record_log_file_path)
	else:
		if my_flag_extractors:
			output = os.system(r'zip -g -r ' + my_record_filename + r' Extractors/' + " >> " + record_log_file_path)
	
	if not my_record_filename_exist:
		if my_flag_feature_data:
			my_record_filename_exist = True
			print(r'c Now recording current Sparkle platform in file ' + my_record_filename + r' ...')
			output = os.system(r'zip -r ' + my_record_filename + r' Feature_Data/' + " >> " + record_log_file_path)
	else:
		if my_flag_feature_data:
			output = os.system(r'zip -g -r ' + my_record_filename + r' Feature_Data/' + " >> " + record_log_file_path)
	
	if not my_record_filename_exist:
		if my_flag_performance_data:
			my_record_filename_exist = True
			print(r'c Now recording current Sparkle platform in file ' + my_record_filename + r' ...')
			output = os.system(r'zip -r ' + my_record_filename + r' Performance_Data/' + " >> " + record_log_file_path)
	else:
		if my_flag_performance_data:
			output = os.system(r'zip -g -r ' + my_record_filename + r' Performance_Data/' + " >> " + record_log_file_path)
	
	if not my_record_filename_exist:
		if my_flag_reference_lists:
			my_record_filename_exist = True
			print(r'c Now recording current Sparkle platform in file ' + my_record_filename + r' ...')
			output = os.system(r'zip -r ' + my_record_filename + r' Reference_Lists/' + " >> " + record_log_file_path)
	else:
		if my_flag_reference_lists:
			output = os.system(r'zip -g -r ' + my_record_filename + r' Reference_Lists/' + " >> " + record_log_file_path)
	
	if not my_record_filename_exist:
		if my_flag_sparkle_portfolio_selector:
			my_record_filename_exist = True
			print(r'c Now recording current Sparkle platform in file ' + my_record_filename + r' ...')
			output = os.system(r'zip -r ' + my_record_filename + r' Sparkle_Portfolio_Selector/' + " >> " + record_log_file_path)
	else:
		if my_flag_sparkle_portfolio_selector:
			output = os.system(r'zip -g -r ' + my_record_filename + r' Sparkle_Portfolio_Selector/' + " >> " + record_log_file_path)
	
	if not my_record_filename_exist:
		if my_flag_sparkle_parallel_portfolio:
			my_record_filename_exist = True
			print(f'c Now recording current Sparkle platform in file {my_record_filename} ...')
			output = os.system(f'zip -r {my_record_filename} '
				f'{sgh.sparkle_parallel_portfolio_dir}/ >> {record_log_file_path}')
	else:
		if my_flag_sparkle_parallel_portfolio:
			output = os.system(f'zip -g -r {my_record_filename} '
				f'{sgh.sparkle_parallel_portfolio_dir}/ >> {record_log_file_path}')

	os.system(r'rm -f ' + record_log_file_path)

	return
	

def cleanup_current_sparkle_platform():
	if os.path.exists(r'Instances/'): sfh.rmtree(Path(r'Instances/'))
	if os.path.exists(r'Solvers/'): sfh.rmtree(Path(r'Solvers/'))
	if os.path.exists(r'Extractors/'): sfh.rmtree(Path(r'Extractors/'))
	if os.path.exists(r'Feature_Data/'): sfh.rmtree(Path(r'Feature_Data/'))
	if os.path.exists(r'Performance_Data/'): sfh.rmtree(Path(r'Performance_Data/'))
	if os.path.exists(r'Reference_Lists/'): sfh.rmtree(Path(r'Reference_Lists/'))
	if os.path.exists(r'Sparkle_Portfolio_Selector'): sfh.rmtree(Path(r'Sparkle_Portfolio_Selector/'))
	if sgh.sparkle_parallel_portfolio_dir.exists():
		sfh.rmtree(sgh.sparkle_parallel_portfolio_dir)
	ablation_scenario_dir = sgh.ablation_dir + "scenarios/"
	if os.path.exists(ablation_scenario_dir): sfh.rmtree(Path(ablation_scenario_dir))
	return


def extract_sparkle_record(my_record_filename):
	if not os.path.exists(my_record_filename):
		sys.exit()
	
	my_suffix = sbh.get_time_pid_random_string()
	my_tmp_directory = r'tmp_directory_' + my_suffix
	
	if not os.path.exists(r'Tmp/'):
		output = os.mkdir(r'Tmp/')
	
	os.system(r'unzip -o ' + my_record_filename + r' -d ' + my_tmp_directory + " >> " + record_log_file_path)
	os.system(r'cp -r ' + my_tmp_directory + '/* ' + './')
	sfh.rmtree(Path(my_tmp_directory))
	os.system(r'rm -f ' + record_log_file_path)
	return

