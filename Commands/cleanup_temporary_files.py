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
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_csv_merge_help

if __name__ == r'__main__':

	if len(sys.argv) != 1:
		print r'c Command error!'
		print r'c Usage: ' + sys.argv[0]
		sys.exit()

	print r'c Cleaning temporary files ...'
	command_line = r'rm -rf Commands/sparkle_help/*.pyc'
	os.system(command_line)
	command_line = r'rm -rf TMP/*'
	os.system(command_line)
	command_line = r'rm -rf TMP/SBATCH_Extractor_Jobs/*'
	os.system(command_line)
	command_line = r'rm -rf TMP/SBATCH_Solver_Jobs/*'
	os.system(command_line)
	command_line = r'rm -rf TMP/SBATCH_Portfolio_Jobs/*'
	os.system(command_line)
	command_line = r'rm -rf TMP/SBATCH_Report_Jobs/*'
	os.system(command_line)
	command_line = r'rm -rf Feature_Data/TMP/*'
	os.system(command_line)
	command_line = r'rm -rf Performance_Data/TMP/*'
	os.system(command_line)
	command_line = r'rm -rf LOG/*'
	os.system(command_line)
	command_line = r'rm -f slurm-*'
	os.system(command_line)
	print r'c Temporary files cleaned!'

