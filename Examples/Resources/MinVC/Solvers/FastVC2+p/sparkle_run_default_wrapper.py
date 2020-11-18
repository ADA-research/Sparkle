#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import argparse

# Problem specific imports
import fcntl
import sys


# Print a command line call for the target algorithm with a given instance file
def print_command(instance_file):
	executable_name = 'fastvc2+p'
	param_str = "-cand_count '198'"

	# TODO: Add optional seed and cutoff time to print_command function?
	#seed_str = '1'
	#cutoff_time_str = sys.argv[3]
	#command_line = executable_name + ' -inst ' + instance_file + ' -seed ' + seed_str + ' -cutoff_time ' + cutoff_time_str + ' -opt 0 ' + param_str
	command_line = executable_name + ' -inst ' + instance_file + ' -opt 0 ' + param_str

	print(command_line)


# Parse problem specific output and print it for Sparkle; or ask Sparkle to use it's own parser (SAT only)
def print_output(output_file):
	# Read solution quality from file
	infile = open(output_file, 'r')
	fcntl.flock(infile.fileno(), fcntl.LOCK_EX)

	solution_quality = sys.maxsize
	lines = infile.readlines()

	for line in lines:
		words = line.strip().split()
		if len(words) <= 0:
			continue
		if len(words) >=4 and words[1] == 'c' and words[2] == 'vertex_cover:':
			temp_solution_quality = int(words[3])
			if solution_quality < 0 or temp_solution_quality < solution_quality:
				solution_quality = temp_solution_quality

	infile.close()

	# Print keyword 'quality' followed by a space and the solution quality
	print('quality ' + str(solution_quality))


### No editing needed for your own wrapper below this line ###


if __name__ == '__main__':
	# Define command line arguments
	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--print-command', metavar='INSTANCE_FILE', type=str, help='print command line call to the target algorithm to stdout given an instance file')
	group.add_argument('--print-output', metavar='OUTPUT_FILE', type=str, help='print target algorithm output in Sparkle format given an output file')

	# Process command line arguments
	args = parser.parse_args()
	instance_file = args.print_command
	output_file = args.print_output

	# Call function based on arguments
	if(instance_file is not None):
		print_command(instance_file)
	elif(output_file is not None):
		print_output(output_file)

