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
from typing import List
from typing import Tuple

from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_compute_marginal_contribution_help as scmc
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings


def compute_perfect(flag_recompute: bool = False) -> List[Tuple[str, float]]:
	print(r"c Start computing each solver's marginal contribution to perfect selector ...")
	rank_list = scmc.compute_perfect_selector_marginal_contribution(flag_recompute=flag_recompute)
	scmc.print_rank_list(rank_list, 1)
	print(r'c Marginal contribution (perfect selector) computing done!')

	return rank_list


def compute_actual(flag_recompute: bool = False) -> List[Tuple[str, float]]:
	print(r"c Start computing each solver's marginal contribution to actual selector ...")
	rank_list = scmc.compute_actual_selector_marginal_contribution(flag_recompute=flag_recompute)
	scmc.print_rank_list(rank_list, 2)
	print(r'c Marginal contribution (actual selector) computing done!')

	return rank_list


def compute_marginal_contribution(flag_compute_perfect: bool, flag_compute_actual: bool, flag_recompute: bool):
	if flag_compute_perfect:
		compute_perfect(flag_recompute)
	elif flag_compute_actual:
		compute_actual(flag_recompute)
	else:
		print(r'c ERROR: compute_marginal_contribution called without a flag set to True, stopping execution')
		sys.exit()


if __name__ == r'__main__':
	# Initialise settings
	global settings
	sgh.settings = sparkle_settings.Settings()

	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--perfect', action='store_true', help='compute the marginal contribution for the perfect selector')
	group.add_argument('--actual', action='store_true', help='compute the marginal contribution for the actual selector')
	parser.add_argument('--recompute', action='store_true', help='force marginal contribution to be recomputed even when it already exists in file for for the current selector')

	# Process command line arguments
	args = parser.parse_args()
	flag_compute_perfect = args.perfect
	flag_compute_actual = args.actual
	flag_recompute = args.recompute

	compute_marginal_contribution(flag_compute_perfect, flag_compute_actual, flag_recompute)

