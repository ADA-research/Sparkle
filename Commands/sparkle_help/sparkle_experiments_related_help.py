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
import fcntl

try:
	from sparkle_help import sparkle_global_help as sgh
	from sparkle_help import sparkle_basic_help
	from sparkle_help import sparkle_file_help as sfh
	from sparkle_help import sparkle_performance_data_csv_help as spdcsv
except ImportError:
	import sparkle_global_help as sgh
	import sparkle_basic_help
	import sparkle_file_help as sfh
	import sparkle_performance_data_csv_help as spdcsv


def init():
	global sleep_time_after_each_solver_run
	global sleep_time_after_each_extractor_run
	global cutoff_time_total_extractor_run_on_one_instance

	#default settings
	cutoff_time_total_extractor_run_on_one_instance = 5 #90 #as SATzilla does

	# Read user settings from file
	sparkle_default_settings_path = sgh.sparkle_default_settings_path
	if os.path.exists(sparkle_default_settings_path):
		fin = open(sparkle_default_settings_path, 'r+')
		fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
		while True:
			myline = fin.readline().strip()
			if not myline:
				break
			mylist = myline.split()
			if mylist[0] == r'cutoff_time_each_feature_computation':
				cutoff_time_total_extractor_run_on_one_instance = int(mylist[2])
		fin.close()

	sleep_time_after_each_solver_run = 0 #1 #add at version 1.0.2
	sleep_time_after_each_extractor_run = 0 #1 #add at version 1.0.2

	return

init()

