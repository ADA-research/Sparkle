#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import argparse


# Print a command line call for the target algorithm with a given instance file
def print_command(instance_file):
	executable_name = 'CSCCSat'
	param_str = '1'
	
	command_line = executable_name + ' ' + instance_file + ' ' + param_str
	
	print(command_line)


# Parse problem specific output and print it for Sparkle; or ask Sparkle to use it's own parser (SAT only)
def print_output(output_file):
	print('Use Sparkle SAT parser')


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

