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
from sparkle_help import sparkle_logging as sl


if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('record_file_path', metavar='record-file-path', type=str, help='path to the record file')

	# Process command line arguments
	args = parser.parse_args()
	record_file_name = args.record_file_path
	if not os.path.exists(record_file_name):
		print(r'c Record file ' + record_file_name + r' does not exist!')
		sys.exit()
	
	print(r'c Removing record file ' + record_file_name + ' ...')
	command_line = r'rm -rf ' + record_file_name
	os.system(command_line)
	print(r'c Record file ' + record_file_name + r' removed!')

