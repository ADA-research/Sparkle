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
import compute_features as cf
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings


if __name__ == r'__main__':
	# Initialise settings
	global settings
	sgh.settings = sparkle_settings.Settings()

	# Log command call
	sl.log_command(sys.argv)

	parser = argparse.ArgumentParser()
	parser.add_argument('--recompute', action='store_true', help='re-run feature extractor for instances with previously computed features')

	# Process command line arguments
	args = parser.parse_args()
	my_flag_recompute = args.recompute

	# Start compute features parallel
	print('c Start computing features ...')

	cf.compute_features_parallel(my_flag_recompute)

