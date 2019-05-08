#!/usr/bin/env python2.7
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

if __name__ == r'__main__':
	
	flag_argument_error = False
	flag_compute_perfect = False
	flag_compute_actual = False
	
	len_argv = len(sys.argv)
	if len_argv != 2: flag_argument_error = True
	else:
		if sys.argv[1] == r'-perfect': flag_compute_perfect = True
		elif sys.argv[1] == r'-actual': flag_compute_actual = True
		else: flag_argument_error = True	
	
	if flag_compute_perfect == flag_compute_actual: flag_argument_error = True
	
	if flag_argument_error:
		print r'c Arguments error!'
		print r'c Usage: ' + sys.argv[0] + r' -perfect'
		print r'c Or usage: ' + sys.argv[0] + r' -actual'
		sys.exit()
	else:
		cutoff_time_each_run = scps.get_cutoff_time_each_run_from_cutoff_time_information_txt_path()
	
		if flag_compute_perfect:
			print r"c Start computing each solver's marginal contribution to perfect selector ..."
			rank_list = scmc.compute_perfect_selector_marginal_contribution(performance_data_csv_path = sparkle_global_help.performance_data_csv_path + '_validate.csv', cutoff_time_each_run = cutoff_time_each_run)
			scmc.print_rank_list(rank_list, 1)
			print r'c Marginal contribution (perfect selector) computing done!'
		elif flag_compute_actual:
			print r"c Start computing each solver's marginal contribution to actual selector ..."
			rank_list = scmc.compute_actual_selector_marginal_contribution(performance_data_csv_path = sparkle_global_help.performance_data_csv_path + '_validate.csv', feature_data_csv_path = sparkle_global_help.feature_data_csv_path + '_validate.csv', cutoff_time_each_run = cutoff_time_each_run)
			scmc.print_rank_list(rank_list, 2)
			print r'c Marginal contribution (actual selector) computing done!'
		else:
			sys.exit()
		
	
	
	
	
