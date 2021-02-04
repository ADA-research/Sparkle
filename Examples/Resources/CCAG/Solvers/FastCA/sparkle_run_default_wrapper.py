#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import argparse

# Problem specific imports
import fcntl
import sys


# Print a command line call for the target algorithm with a given instance file
def print_command(instance_file, seed_str: str, cutoff_time_str: str):
	executable_name = 'FastCA'
	param_str = " "

	command_line = executable_name + ' ' + instance_file + ' ' + cutoff_time_str + ' ' + seed_str + ' ' + param_str

	print(command_line)

def _is_a_number(input_str : str):
	try:
		input_val = eval(input_str)
		if (type(input_val) == float) or (type(input_val) == int):
			return True
		else:
			return False
	except:
		return False


# Parse problem specific output and print it for Sparkle; or ask Sparkle to use it's own parser (SAT only)
def print_output(terminal_output_file):
	# Read solution quality from file
	infile = open(terminal_output_file, 'r')
	fcntl.flock(infile.fileno(), fcntl.LOCK_EX)

	solution_quality = sys.maxsize
	status = 'UNKNOWN'
	lines = infile.readlines()

	for line in lines:
		words = line.strip().split()
		if len(words) <= 0:
			continue
		if len(words) == 18 and words[1] == 'We' and words[2] == 'recommend':
			# First output line is normal, probably no crash
			solution_quality = sys.maxsize - 1
			# If no actual solution is found, we probably reach the cutoff time before finding a solution
			status = 'TIMEOUT'
		if len(words) == 4 and _is_a_number(words[1]) and _is_a_number(words[2]) and _is_a_number(words[3]):
			temp_solution_quality = int(words[2])
			if temp_solution_quality < solution_quality:
				solution_quality = temp_solution_quality
				status = 'SUCCESS'

	if solution_quality == sys.maxsize:
		status = 'CRASHED'

	infile.close()

	# [required for quality objective] Print keyword 'quality' followed by a space and the solution quality
	print('quality ' + str(solution_quality))
	# [optional] Print keyword 'status' followed by a space and the run status
	print('status ' + status)


### No editing needed for your own wrapper below this line ###


if __name__ == '__main__':
	# Define command line arguments
	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--print-command', metavar='INSTANCE_FILE', type=str, help='print command line call to the target algorithm to stdout given an instance file')
	group.add_argument('--print-output', metavar='TERMINAL_OUTPUT_FILE', type=str, help='print target algorithm output in Sparkle format given an output file containing what the algorithm wrote to the terminal')
	parser.add_argument('--seed', metavar='VALUE', type=str, help='required with --print-command; seed for the target algorithm to use')
	parser.add_argument('--cutoff-time', metavar='VALUE', type=str, help='optional with --print-command; cutoff time in seconds for the target algorithm')

	# Process command line arguments
	args = parser.parse_args()
	if args.print_command and args.seed is None:
		parser.error('--print-command requires --seed')
	instance_file = args.print_command
	terminal_output_file = args.print_output
	seed_str = args.seed
	cutoff_time_str = args.cutoff_time

	# Call function based on arguments
	if(instance_file is not None):
		print_command(instance_file, seed_str, cutoff_time_str)
	elif(terminal_output_file is not None):
		print_output(terminal_output_file)

