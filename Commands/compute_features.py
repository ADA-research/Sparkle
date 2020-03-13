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
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_compute_features_help as scf
from sparkle_help import sparkle_compute_features_parallel_help as scfp
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_experiments_related_help

if __name__ == r'__main__':

	
	print('c Start computing features ...')

	my_flag_recompute = False
	my_flag_parallel = False

	len_argv = len(sys.argv)
	i = 1
	while i<len_argv:
		if sys.argv[i] == r'-recompute':
			my_flag_recompute = True
		elif sys.argv[i] == r'-parallel':
			my_flag_parallel = True
		i += 1
	
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
		num_job_in_parallel = sparkle_experiments_related_help.num_job_in_parallel

		if my_flag_recompute:
			feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(sparkle_global_help.feature_data_csv_path)
			feature_data_csv.clean_csv()
			scfp.computing_features_parallel(sparkle_global_help.feature_data_csv_path, num_job_in_parallel, 2)
		else: 
			scfp.computing_features_parallel(sparkle_global_help.feature_data_csv_path, num_job_in_parallel, 1)
	
		print('c Computing features in parallel ...')
	
	
	
	

