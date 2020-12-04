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
from pathlib import PurePath

from sparkle_help import sparkle_global_help as sgh

# Keep track of which command called Sparkle
global caller
caller = 'unknown'

# Current caller file path
global caller_log_path
caller_log_path = 'not set'

global caller_out_dir
caller_out_dir = Path('.')

def update_caller(argv):
	global caller
	caller = Path(argv[0]).stem

# Create a new file path for the caller with the given timestamp
def update_caller_file_path(timestamp: str):
	caller_file = caller + '_main_log.txt'
	caller_dir = Path(caller + '_' + timestamp)
	# Set caller directory for other Sparkle functions to use
	global caller_out_dir
	caller_out_dir = Path(caller_dir)
	global caller_log_path
	caller_log_path = PurePath(sgh.sparkle_global_output_dir / caller_out_dir / caller_file)

	# Create needed directories if they don't exist
	caller_dir = Path(caller_log_path).parents[0]
	caller_dir.mkdir(parents=True, exist_ok=True)

	# If the caller output file does not exist yet, write the header
	if not Path(caller_log_path).is_file():
		output_header = '     Timestamp		  					Path		  					Description\n'
		with open(str(caller_log_path), "a") as output_file:
			output_file.write(output_header)

	return

def add_output(output_path, description):
	# Prepare logging information
	timestamp = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
	output_str = timestamp + '   ' + output_path + '   ' + description + '\n'

	# Write output path and description to caller file
	with open(str(caller_log_path), "a") as output_file:
		output_file.write(output_str)

# Write to file which command was executed when, with which arguments, and
# where details about it's output are stored (if any)
def log_command(argv):
	# Determine caller
	update_caller(argv)

	# Prepare logging information
	timestamp = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
	update_caller_file_path(timestamp)
	output_file = caller_log_path
	args = ' '.join(argv[0:])
	log_str = timestamp + '   ' + args + '   ' + str(output_file) + '\n'

	# Make sure directory exists
	log_dir = Path(sgh.sparkle_global_output_dir)
	log_dir.mkdir(parents=True, exist_ok=True)

	# If the log file does not exist yet, write the header
	log_path = sgh.sparkle_global_log_path
	if not Path(log_path).is_file():
		log_header = '     Timestamp		  					Command		  					Output details\n'
		with open(str(log_path), "a") as log_file:
			log_file.write(log_header)

	# Write to log file
	with open(str(log_path), "a") as log_file:
		log_file.write(log_str)

	return

