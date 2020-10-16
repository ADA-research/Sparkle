#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import os
import sys
import fcntl
import argparse
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_construct_portfolio_selector_help as scps ##
from sparkle_help import sparkle_run_portfolio_selector_help as srps ##
from sparkle_help import sparkle_compute_marginal_contribution_help as scmc
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_logging as sl


def compute_perfect():
	cutoff_time_each_run = scps.get_cutoff_time_each_run_from_cutoff_time_information_txt_path()

	print(r"c Start computing each solver's marginal contribution to perfect selector ...")
	rank_list = scmc.compute_perfect_selector_marginal_contribution(cutoff_time_each_run = cutoff_time_each_run)
	scmc.print_rank_list(rank_list, 1)
	print(r'c Marginal contribution (perfect selector) computing done!')

	return rank_list


def compute_actual():
	cutoff_time_each_run = scps.get_cutoff_time_each_run_from_cutoff_time_information_txt_path()

	print(r"c Start computing each solver's marginal contribution to actual selector ...")
	rank_list = scmc.compute_actual_selector_marginal_contribution(cutoff_time_each_run = cutoff_time_each_run)
	scmc.print_rank_list(rank_list, 2)
	print(r'c Marginal contribution (actual selector) computing done!')

	return rank_list


def compute_marginal_contribution(flag_compute_perfect, flag_compute_actual):
	if flag_compute_perfect:
		compute_perfect()
	elif flag_compute_actual:
		compute_actual()
	else:
		print(r'c ERROR: compute_marginal_contribution called without a flag set to True, stopping execution')
		sys.exit()


if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group()
	group.add_argument('perfect', action='store_true', help='compute the marginal contribution for the perfect selector')
	group.add_argument('actual', action='store_true', help='compute the marginal contribution for the actual selector')

	# Process command line arguments
	args = parser.parse_args()
	flag_compute_perfect = args.perfect
	flag_compute_actual = args.actual

	compute_marginal_contribution(flag_compute_perfect, flag_compute_actual)

