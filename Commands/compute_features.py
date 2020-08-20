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
from sparkle_help import sparkle_compute_features_help as scf
from sparkle_help import sparkle_compute_features_parallel_help as scfp
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_experiments_related_help
from sparkle_help import sparkle_logging as sl


def compute_features_parallel(my_flag_recompute):
	num_job_in_parallel = sparkle_experiments_related_help.num_job_in_parallel

	if my_flag_recompute:
		feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(sparkle_global_help.feature_data_csv_path)
		feature_data_csv.clean_csv()
		scfp.computing_features_parallel(sparkle_global_help.feature_data_csv_path, num_job_in_parallel, 2)
	else: 
		scfp.computing_features_parallel(sparkle_global_help.feature_data_csv_path, num_job_in_parallel, 1)

	print('c Computing features in parallel ...')
	
	return


if __name__ == r'__main__':
	# Log command call
	sl.log_command(sys.argv)

	# Define command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--recompute', action='store_true', help='re-run feature extractor for instances with previously computed features')
	parser.add_argument('--parallel', action='store_true', help='run the feature extractor on multiple instances in parallel')

	# Process command line arguments
	args = parser.parse_args()
	my_flag_recompute = args.recompute
	my_flag_parallel = args.parallel

	# Start compute features
	print('c Start computing features ...')

	if not my_flag_parallel:
		if my_flag_recompute:
			feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(sparkle_global_help.feature_data_csv_path)
			feature_data_csv.clean_csv()
			scf.computing_features(sparkle_global_help.feature_data_csv_path, 2)
		else: 
			scf.computing_features(sparkle_global_help.feature_data_csv_path, 1)
	
		print('c Feature data file ' + sparkle_global_help.feature_data_csv_path + ' has been updated!')
		print('c Computing features done!')
	else:
		compute_features_parallel(my_flag_recompute)

