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
	parser.add_argument('--job-id', required=False, type=str, default=None, help='job ID to wait for')

	# Process command line arguments
	args = parser.parse_args()
	job_id = args.job_id

	if job_id is not None:
		sjh.wait_for_job(job_id)
	else:
		wait_for_all_jobs()

