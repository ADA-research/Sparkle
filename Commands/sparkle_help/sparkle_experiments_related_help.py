#!/usr/bin/env python2.7
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
import fcntl
import sparkle_global_help
import sparkle_basic_help
import sparkle_file_help as sfh
import sparkle_performance_data_csv_help as spdcsv


def init():
	global num_job_in_parallel
	global cutoff_time_each_run
	global par_num
	global penalty_time
	global sleep_time_after_each_solver_run
	global sleep_time_after_each_extractor_run
	#global cutoff_time_each_extractor_run
	global cutoff_time_total_extractor_run_on_one_instance

	#default settings
	num_job_in_parallel = 32
	cutoff_time_each_run = 3600 #90
	par_num = 10
	cutoff_time_total_extractor_run_on_one_instance = 90 #as SATzilla does


	sparkle_default_settings_path = sparkle_global_help.sparkle_default_settings_path
	if os.path.exists(sparkle_default_settings_path):
		fin = open(sparkle_default_settings_path, 'r+')
		fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
		while True:
			myline = fin.readline().strip()
			if not myline:
				break
			mylist = myline.split()
			if mylist[0] == r'num_job_in_parallel':
				num_job_in_parallel = int(mylist[2])
			elif mylist[0] == r'cutoff_time_each_performance_computation':
				cutoff_time_each_run = int(mylist[2])
			elif mylist[0] == r'penalty_number':
				par_num = int(mylist[2])
			elif mylist[0] == r'cutoff_time_each_feature_computation':
				cutoff_time_total_extractor_run_on_one_instance = int(mylist[2])
		fin.close()
	
	'''
	cutoff_time_information_txt_path = sparkle_global_help.cutoff_time_information_txt_path
	if os.path.exists(cutoff_time_information_txt_path):
		fo = open(cutoff_time_information_txt_path, 'r+')
		fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
		myline = fo.readline().strip()
		mylist = myline.split()
		cutoff_time_each_run = int(mylist[2])
		
		myline = fo.readline().strip()
		mylist = myline.split()
		par_num = int(mylist[2])
		fo.close()
	else:
		#default settings
		cutoff_time_each_run = 3600 #90 #default setting
		par_num = 10
	'''
	
	penalty_time = cutoff_time_each_run * par_num
	sleep_time_after_each_solver_run = 1 #add at version 1.0.2
	sleep_time_after_each_extractor_run = 1 #add at version 1.0.2
	
	#cutoff_time_each_extractor_run = 90 #as SATzilla does
	#cutoff_time_total_extractor_run_on_one_instance = 90 #as SATzilla does
	
	#print r'c cutoff_time_each_run = ' + str(cutoff_time_each_run)
	#print r'c par_num = ' + str(par_num)
	
	return

init()


	
