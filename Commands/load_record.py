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

	if len(sys.argv) != 2:
		print r'c Command error!'
		print r'c Usage: ' + sys.argv[0] + r' <record_file_name>'
		sys.exit()

	record_file_name = sys.argv[1]
	if not os.path.exists(record_file_name):
		print r'c Record file ' + record_file_name + r' does not exist!'
		print r'c Nothing Changed!'
		sys.exit()
	
	print r'c Cleaning existing Sparkle platform ...'
	sparkle_record_help.cleanup_current_sparkle_platform()
	print r'c Existing Sparkle platform cleaned!'

	print r'c Loading record file ' + record_file_name + ' ...'
	sparkle_record_help.extract_sparkle_record(record_file_name)
	print r'c Record file ' + record_file_name + r' loaded successfully!'
	
