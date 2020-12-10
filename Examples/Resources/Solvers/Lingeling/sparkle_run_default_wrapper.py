#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import argparse


# Print a command line call for the target algorithm with a given instance file
def print_command(instance_file, seed_str: str, cutoff_time_str: str):
	executable_name = 'lingeling'

	command_line = executable_name + ' ' + instance_file + ' ' + seed_str

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
	parser.add_argument('--seed', metavar='VALUE', type=str, help='required with --print-command; seed for the target algorithm to use')
	parser.add_argument('--cutoff-time', metavar='VALUE', type=str, help='optional with --print-command; cutoff time in seconds for the target algorithm')

	# Process command line arguments
	args = parser.parse_args()
	if args.print_command and args.seed is None:
		parser.error('--print-command requires --seed')
	instance_file = args.print_command
	output_file = args.print_output
	seed_str = args.seed
	cutoff_time_str = args.cutoff_time

	# Call function based on arguments
	if(instance_file is not None):
		print_command(instance_file, seed_str, cutoff_time_str)
	elif(output_file is not None):
		print_output(output_file)

