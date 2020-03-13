#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import os
import time
import random
import sys
import fcntl
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_experiments_related_help as ser

'''
def csv_load_combine_update(feature_data_csv_path, second_sfdcsv):
	fo = open(feature_data_csv_path, 'r+')
	fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
	try:
		feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
		feature_data_csv.combine(second_sfdcsv)
		feature_data_csv.update_csv()
	except:
		fo.close()
		return
	fo.close()
	return
'''

def feature_data_csv_merge():
	try:
		feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(sparkle_global_help.feature_data_csv_path)
		tmp_feature_data_csv_directory = r'Feature_Data/TMP/'
		csv_list = sfh.get_list_all_csv_filename(tmp_feature_data_csv_directory)
	except:
		return
	
	for i in range(0, len(csv_list)):
		csv_name = csv_list[i]
		csv_path = tmp_feature_data_csv_directory + csv_name
		try:
			tmp_feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(csv_path)
			feature_data_csv.combine(tmp_feature_data_csv)
			feature_data_csv.update_csv()
			os.system(r'rm -f ' + csv_path)
		except:
			continue
	return


def performance_data_csv_merge():
	try:
		performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)
		tmp_performance_data_result_directory = r'Performance_Data/TMP/'
		result_list = sfh.get_list_all_result_filename(tmp_performance_data_result_directory)
	except:
		return
	
	wrong_solver_list = []
	
	for i in range(0, len(result_list)):
		result_name = result_list[i]
		result_path = tmp_performance_data_result_directory + result_name
		try:
			fin = open(result_path, 'r+')
			fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
			instance_path = fin.readline().strip()
			if not instance_path: continue
			solver_path = fin.readline().strip()
			if not solver_path: continue
			verify_string = fin.readline().strip()
			if not verify_string: continue
			runtime_str = fin.readline().strip()
			if not runtime_str: continue
			runtime = float(runtime_str)
			
			if verify_string == r'SAT':
				if runtime > ser.cutoff_time_each_run: runtime = ser.penalty_time
				performance_data_csv.set_value(instance_path, solver_path, runtime)
				if sparkle_global_help.instance_reference_mapping[instance_path] != r'SAT':
					sparkle_global_help.instance_reference_mapping[instance_path] = r'SAT'
					sfh.write_instance_reference_mapping()
			elif verify_string == r'UNSAT':
				if runtime > ser.cutoff_time_each_run: runtime = ser.penalty_time
				performance_data_csv.set_value(instance_path, solver_path, runtime)
				if sparkle_global_help.instance_reference_mapping[instance_path] != r'UNSAT':
					sparkle_global_help.instance_reference_mapping[instance_path] = r'UNSAT'
					sfh.write_instance_reference_mapping()
			elif verify_string == r'UNKNOWN':
				runtime = ser.penalty_time
				performance_data_csv.set_value(instance_path, solver_path, runtime)
			elif verify_string == r'WRONG':
				wrong_solver_list.append(solver_path)
			else:
				verify_string = r'UNKNOWN'
				runtime = ser.penalty_time
				performance_data_csv.set_value(instance_path, solver_path, runtime)
			fin.close()
			performance_data_csv.update_csv()
			os.system(r'rm -f ' + result_path)
		except:
			continue
	
	for i in range(0, len(wrong_solver_list)):
		wrong_solver_path = wrong_solver_list[i]
		performance_data_csv.delete_column(wrong_solver_path)
		performance_data_csv.update_csv()
		sparkle_global_help.solver_list.remove(wrong_solver_path)
		output = sparkle_global_help.solver_nickname_mapping.pop(wrong_solver_path)
		sfh.write_solver_list()
		sfh.write_solver_nickname_mapping()
	
	return


feature_data_csv_merge()
performance_data_csv_merge()




	
