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

# Keep track of which command called Sparkle
global caller
caller = 'unknown'

# Current caller file path
global caller_file_path
caller_file_path = 'not set'

def update_caller(argv):
	global caller
	caller = Path(argv[0]).stem

# Create a new file path for the caller with the given timestamp
def update_caller_file_path(timestamp):
	caller_file = caller + '_' + timestamp + '.txt'
	global caller_file_path
	caller_file_path = sgh.sparkle_global_log_dir + 'Output_details/' + caller_file

	# Create needed directories if they don't exists
	caller_dir = Path(caller_file_path).parents[0]
	caller_dir.mkdir(parents=True, exist_ok=True)

	# If the caller output file does not exist yet, write the header
	if not Path(caller_file_path).is_file():
		output_header = '     Timestamp		  					Path		  					Description\n'
		with open(caller_file_path, "a") as output_file:
			output_file.write(output_header)

	return

def add_output(output_path, description):
	# Prepare logging information
	timestamp = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
	output_str = timestamp + '   ' + output_path + '   ' + description + '\n'

	# Write output path and description to caller file
	with open(caller_file_path, "a") as output_file:
		output_file.write(output_str)

# Write to file which command was executed when, with which arguments, and
# where details about it's output are stored (if any)
def log_command(argv):
	# Determine caller
	update_caller(argv)

	# Prepare logging information
	timestamp = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
	update_caller_file_path(timestamp)
	output_file = caller_file_path
	args = ' '.join(argv[0:])
	log_str = timestamp + '   ' + args + '   ' + output_file + '\n'

	# Make sure directory exists
	log_dir = Path(sgh.sparkle_global_log_dir)
	log_dir.mkdir(parents=True, exist_ok=True)

	# If the log file does not exist yet, write the header
	log_path = sgh.sparkle_global_log_path
	if not Path(log_path).is_file():
		log_header = '     Timestamp		  					Command		  					Output details\n'
		with open(log_path, "a") as log_file:
			log_file.write(log_header)

	# Write to log file
	with open(log_path, "a") as log_file:
		log_file.write(log_str)

	return

