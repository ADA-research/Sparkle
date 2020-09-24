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
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_logging as sl


if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	if len(sys.argv) != 1:
		print(r'c Command error!')
		print(r'c Usage: ' + sys.argv[0])
		sys.exit()

	my_suffix = sparkle_basic_help.get_time_pid_random_string()
	my_record_filename = "Records/My_Record_" + my_suffix + '.zip'

	sparkle_record_help.save_current_sparkle_platform(my_record_filename)

	print(r'c Record file ' + my_record_filename + r' saved successfully!')

