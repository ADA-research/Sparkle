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
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_system_status_help
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_run_status_help
from sparkle_help import sparkle_generate_report_help
from sparkle_help import sparkle_file_help as sfh

def generate_task_run_status():
	key_str = 'generate_report'
	task_run_status_path = r'TMP/SBATCH_Report_Jobs/' + key_str + r'.statusinfo'
	status_info_str = 'Status: Running\n'
	sfh.write_string_to_file(task_run_status_path, status_info_str)
	return

def delete_task_run_status():
	key_str = 'generate_report'
	task_run_status_path = r'TMP/SBATCH_Report_Jobs/' + key_str + r'.statusinfo'
	os.system(r'rm -rf ' + task_run_status_path)
	return


if __name__ == r'__main__':
	
	if len(sys.argv) != 1:
		print r'c Command error!'
		print r'c Usage: ' + sys.argv[0]
		sys.exit()
	
	if not os.path.isfile(sparkle_global_help.sparkle_portfolio_selector_path):
		print(r'c Before generating Sparkle report, please first construct Sparkle portfolio selector!')
		print(r'c Do not generate Sparkle report. Exit!')
		sys.exit()
	
	print r'c Generating report ...'
	generate_task_run_status()
	sparkle_generate_report_help.generate_report()
	delete_task_run_status()
	print r'c Report generated ...'
	

