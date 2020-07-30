#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import time
from pathlib import Path

from sparkle_help import sparkle_global_help as sgh

# Write to file which command was executed when, with which arguments, and
# where details about it's output are stored (if any)
def log_command(argv, output_file=None):
	# Prepare logging information
	timestamp = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
	if output_file is None:
		output_file = 'N/A'
	args = ' '.join(argv[0:])
	log_str = timestamp + '   ' + args + '   ' + output_file + '\n'

	# Make sure directory exists
	log_path = sgh.sparkle_global_log
	log_dir = Path(log_path).parents[0]
	log_dir.mkdir(parents=True, exist_ok=True)

	# If the log file does not exist yet, write the header
	if not Path(log_path).is_file():
		log_header = '     Timestamp		  					Command		  					Output details\n'
		with open(log_path, "a") as log_file:
			log_file.write(log_header)

	# Write to log file
	with open(log_path, "a") as log_file:
		log_file.write(log_str)

	return

