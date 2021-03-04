#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import sys
import argparse

from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_job_help as sjh
from sparkle_help.sparkle_command_help import CommandName


if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group()
	group.add_argument('--job-id', required=False, type=str, default=None, help='job ID to wait for')
	group.add_argument('--command', required=False, choices=CommandName.__members__, default=None, help='command you want to run, Sparkl will wait for the dependencies of this command to be completed')

	# Process command line arguments
	args = parser.parse_args()
	job_id = args.job_id
	command = CommandName.from_str(args.command)

	if job_id is not None:
		sjh.wait_for_job(job_id)
	elif command is not None:
		sjh.wait_for_dependencies(command)
	else:
		wait_for_all_jobs()

