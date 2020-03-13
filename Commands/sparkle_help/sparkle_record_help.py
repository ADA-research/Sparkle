#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import os
import time
import random
import sys
import shutil
import fcntl
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_global_help


global record_log_file_path
record_log_file_path = sparkle_global_help.sparkle_log_path

def detect_current_sparkle_platform_exists():
	my_flag_anyone = False
	if os.path.exists(r'Instances/'): my_flag_anyone = True
	if os.path.exists(r'Solvers/'): my_flag_anyone = True
	if os.path.exists(r'Extractors/'): my_flag_anyone = True	
	if os.path.exists(r'Feature_Data/'): my_flag_anyone = True
	if os.path.exists(r'Performance_Data/'): my_flag_anyone = True
	if os.path.exists(r'Reference_Lists/'): my_flag_anyone = True
	if os.path.exists(r'Sparkle_Portfolio_Selector/'): my_flag_anyone = True
	return my_flag_anyone


def save_current_sparkle_platform(my_record_filename):
	my_flag_instances = False
	my_flag_solvers = False
	my_flag_extractors = False
	my_flag_feature_data = False
	my_flag_performance_data = False
	my_flag_reference_lists = False
	my_flag_sparkle_portfolio_selector = False
	
	if os.path.exists(r'Instances/'): my_flag_instances = True
	if os.path.exists(r'Solvers/'): my_flag_solvers = True
	if os.path.exists(r'Extractors/'): my_flag_extractors = True
	if os.path.exists(r'Feature_Data/'): my_flag_feature_data = True
	if os.path.exists(r'Performance_Data/'): my_flag_performance_data = True
	if os.path.exists(r'Reference_Lists/'): my_flag_reference_lists = True
	if os.path.exists(r'Sparkle_Portfolio_Selector/'): my_flag_sparkle_portfolio_selector = True
	
	if not os.path.exists(r'TMP/'):
		output = os.mkdir(r'TMP/')
	
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
	
	os.system(r'rm -f ' + record_log_file_path)
	return
	

def cleanup_current_sparkle_platform():
	if os.path.exists(r'Instances/'): shutil.rmtree(r'Instances/')
	if os.path.exists(r'Solvers/'): shutil.rmtree(r'Solvers/')
	if os.path.exists(r'Extractors/'): shutil.rmtree(r'Extractors/')
	if os.path.exists(r'Feature_Data/'): shutil.rmtree(r'Feature_Data/')
	if os.path.exists(r'Performance_Data/'): shutil.rmtree(r'Performance_Data/')
	if os.path.exists(r'Reference_Lists/'): shutil.rmtree(r'Reference_Lists/')
	if os.path.exists(r'Sparkle_Portfolio_Selector'): shutil.rmtree(r'Sparkle_Portfolio_Selector/')
	return


def extract_sparkle_record(my_record_filename):
	if not os.path.exists(my_record_filename):
		sys.exit()
	
	my_suffix = sparkle_basic_help.get_time_pid_random_string()
	my_tmp_directory = r'tmp_directory_' + my_suffix
	
	if not os.path.exists(r'TMP/'):
		output = os.mkdir(r'TMP/')
	
	os.system(r'unzip -o ' + my_record_filename + r' -d ' + my_tmp_directory + " >> " + record_log_file_path)
	os.system(r'cp -r ' + my_tmp_directory + '/* ' + './')
	shutil.rmtree(my_tmp_directory)
	os.system(r'rm -f ' + record_log_file_path)
	return




