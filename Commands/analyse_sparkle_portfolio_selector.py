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
from sparkle_help import sparkle_construct_portfolio_selector_help as scps
from sparkle_help import sparkle_construct_portfolio_selector_parallel_help as scpsp
from sparkle_help import sparkle_compute_marginal_contribution_help as scmc
from sparkle_help import sparkle_job_help
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_experiments_related_help
from sparkle_help import sparkle_analyse_portfolio_selector_parallel_help


if __name__ == r'__main__':
	
	if len(sys.argv) != 1:
		print('c Arguments error!')
		print('c Usage: ' + sys.argv[0])
		sys.exit()
	
	portfolio_selector_path_basis = sparkle_global_help.sparkle_portfolio_selector_path
	num_job_in_parallel = sparkle_experiments_related_help.num_job_in_parallel
	performance_data_csv_path = sparkle_global_help.performance_data_csv_path
	feature_data_csv_path = sparkle_global_help.feature_data_csv_path
	cutoff_time_each_run = sparkle_experiments_related_help.cutoff_time_each_run
	par_num = sparkle_experiments_related_help.par_num 
	
	sparkle_analyse_portfolio_selector_parallel_help.analysing_portfolio_selector_parallel(portfolio_selector_path_basis, num_job_in_parallel, performance_data_csv_path, feature_data_csv_path, cutoff_time_each_run, par_num)
	
		
