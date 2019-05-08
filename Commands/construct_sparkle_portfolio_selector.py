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
import random
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_csv_help as scsv
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_construct_portfolio_selector_help as scps
from sparkle_help import sparkle_construct_portfolio_selector_parallel_help as scpsp
from sparkle_help import sparkle_compute_marginal_contribution_help as scmc
from sparkle_help import sparkle_job_help
from sparkle_help import sparkle_csv_merge_help
from sparkle_help import sparkle_experiments_related_help
from sparkle_help import sparkle_job_parallel_help

def judge_exist_remaining_jobs(feature_data_csv_path, performance_data_csv_path):
	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
	list_feature_computation_job = feature_data_csv.get_list_remaining_feature_computation_job()
	total_job_num = sparkle_job_help.get_num_of_total_job_from_list(list_feature_computation_job)
	if total_job_num>0:
		return True
	
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	list_performance_computation_job = performance_data_csv.get_list_remaining_performance_computation_job()
	total_job_num = sparkle_job_help.get_num_of_total_job_from_list(list_performance_computation_job)
	if total_job_num>0:
		return True
	
	return False

def split_feature_csv_and_performance_csv(feature_data_csv_path, performance_data_csv_path, mode=1, train_ratio=0.8, seed = 1):
	if mode==1:
		feature_data_csv_path_train = feature_data_csv_path + '_train.csv'
		feature_data_csv_path_validate = feature_data_csv_path + '_validate.csv'
		performance_data_csv_path_train = performance_data_csv_path + '_train.csv'
		performance_data_csv_path_validate = performance_data_csv_path + '_validate.csv'
		
		os.system('cp %s %s' % (feature_data_csv_path, feature_data_csv_path_train))
		os.system('cp %s %s' % (feature_data_csv_path, feature_data_csv_path_validate))
		os.system('cp %s %s' % (performance_data_csv_path, performance_data_csv_path_train))
		os.system('cp %s %s' % (performance_data_csv_path, performance_data_csv_path_validate))
		
		return feature_data_csv_path_train, feature_data_csv_path_validate, performance_data_csv_path_train, performance_data_csv_path_validate
	
	elif mode==2:
		random.seed(seed)
		feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
		performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
		
		num_instances = len(feature_data_csv.list_rows())
		
		list_instance_family = []
		dict_instance_family_to_instance_list = {}
		
		for instance_path in feature_data_csv.list_rows():
			instance_family = sfh.get_all_level_directory(instance_path)
			if not instance_family in list_instance_family:
				list_instance_family.append(instance_family)
				dict_instance_family_to_instance_list[instance_family] = []
				dict_instance_family_to_instance_list[instance_family].append(instance_path)
			else:
				dict_instance_family_to_instance_list[instance_family].append(instance_path)
		
		print(len(list_instance_family))
		#for instance_family in list_instance_family:
		#	print("%s %d" % (instance_family, len(dict_instance_family_to_instance_list[instance_family])))
		
		list_instance_train = []
		list_instance_validate = []
		
		for instance_family in list_instance_family:
			list_instance_current = dict_instance_family_to_instance_list[instance_family]
			length_list_instance_current = len(list_instance_current)
			length_list_instance_current_train = length_list_instance_current / 3
			if length_list_instance_current_train <= 0:
				length_list_instance_current_train = min(length_list_instance_current, 1)
			length_list_instance_current_test = length_list_instance_current - length_list_instance_current_train
			
			tmp_list_instance_current = []
			for instance_path in list_instance_current:
				tmp_list_instance_current.append(instance_path)
			length_tmp_list_instance_current = len(tmp_list_instance_current)
			i=0
			
			while True:
				if i >= length_list_instance_current_train:
					break
				selected_index = random.randint(0, length_tmp_list_instance_current-1)
				selected_value = tmp_list_instance_current[selected_index]
				list_instance_train.append(selected_value)
				
				tmp_value = tmp_list_instance_current[selected_index]
				tmp_list_instance_current[selected_index] = tmp_list_instance_current[length_tmp_list_instance_current-1]
				tmp_list_instance_current[length_tmp_list_instance_current-1] = tmp_value
				
				length_tmp_list_instance_current -= 1
				i += 1
			
			for instance_path in list_instance_current:
				if not instance_path in list_instance_train:
					list_instance_validate.append(instance_path)
			
			print("%s %d %d %d" % (instance_family, len(dict_instance_family_to_instance_list[instance_family]), length_list_instance_current_train, length_list_instance_current_test))
			
		list_instance_train.sort()
		list_instance_validate.sort()
		
		feature_data_csv_path_train = feature_data_csv_path + '_train.csv'
		feature_data_csv_path_validate = feature_data_csv_path + '_validate.csv'
		performance_data_csv_path_train = performance_data_csv_path + '_train.csv'
		performance_data_csv_path_validate = performance_data_csv_path + '_validate.csv'
	
		feature_data_csv_train = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
		feature_data_csv_validate = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
		performance_data_csv_train = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
		performance_data_csv_validate = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	
		for i in range(0, num_instances):
			row_name_i = feature_data_csv.get_row_name(i)
		
			if not row_name_i in list_instance_train:
				feature_data_csv_train.delete_row(row_name_i)
				performance_data_csv_train.delete_row(row_name_i)
			
			if not row_name_i in list_instance_validate:
				feature_data_csv_validate.delete_row(row_name_i)
				performance_data_csv_validate.delete_row(row_name_i)
	
		feature_data_csv_train.save_csv(feature_data_csv_path_train)
		feature_data_csv_validate.save_csv(feature_data_csv_path_validate)
		performance_data_csv_train.save_csv(performance_data_csv_path_train)
		performance_data_csv_validate.save_csv(performance_data_csv_path_validate)
		
		return feature_data_csv_path_train, feature_data_csv_path_validate, performance_data_csv_path_train, performance_data_csv_path_validate	
	
	elif mode==3:
		random.seed(seed)
	
		feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
		performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	
		num_instances = len(feature_data_csv.list_rows())
		num_instances_train = num_instances * train_ratio
		num_instances_validate = num_instances - num_instances_train
	
		list_instances_train = []
		list_instances_validate = []
	
		list_num = []
		for i in range(0, num_instances):
			list_num.append(i)
	
		tmp_num_instances = num_instances
		i = 0
		while True:
			if i >= num_instances_train:
				break
		
			selected_index = random.randint(0, tmp_num_instances-1)
			selected_value = list_num[selected_index]
			list_instances_train.append(selected_value)
		
			tmp_value = list_num[selected_index]
			list_num[selected_index] = list_num[tmp_num_instances-1]
			list_num[tmp_num_instances-1] = tmp_value
		
			tmp_num_instances -= 1
			i += 1
	
		list_instances_train.sort()
	
		for i in range(0, num_instances):
			if not i in list_instances_train:
				list_instances_validate.append(i)
	
		feature_data_csv_path_train = feature_data_csv_path + '_train.csv'
		feature_data_csv_path_validate = feature_data_csv_path + '_validate.csv'
		performance_data_csv_path_train = performance_data_csv_path + '_train.csv'
		performance_data_csv_path_validate = performance_data_csv_path + '_validate.csv'
	
		feature_data_csv_train = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
		feature_data_csv_validate = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
		performance_data_csv_train = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
		performance_data_csv_validate = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	
		for i in range(0, num_instances):
			row_name_i = feature_data_csv.get_row_name(i)
		
			if not i in list_instances_train:
				feature_data_csv_train.delete_row(row_name_i)
				performance_data_csv_train.delete_row(row_name_i)
			
			if not i in list_instances_validate:
				feature_data_csv_validate.delete_row(row_name_i)
				performance_data_csv_validate.delete_row(row_name_i)
	
		feature_data_csv_train.save_csv(feature_data_csv_path_train)
		feature_data_csv_validate.save_csv(feature_data_csv_path_validate)
		performance_data_csv_train.save_csv(performance_data_csv_path_train)
		performance_data_csv_validate.save_csv(performance_data_csv_path_validate)
	
		return feature_data_csv_path_train, feature_data_csv_path_validate, performance_data_csv_path_train, performance_data_csv_path_validate
	
	elif mode==4:
		random.seed(seed)
		feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
		performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
		
		num_instances = len(feature_data_csv.list_rows())
		
		list_instance_family = []
		dict_instance_family_to_instance_list = {}
		
		for instance_path in feature_data_csv.list_rows():
			instance_family = sfh.get_all_level_directory(instance_path)
			if not instance_family in list_instance_family:
				list_instance_family.append(instance_family)
				dict_instance_family_to_instance_list[instance_family] = []
				dict_instance_family_to_instance_list[instance_family].append(instance_path)
			else:
				dict_instance_family_to_instance_list[instance_family].append(instance_path)
		
		print(len(list_instance_family))
		
		list_instance_train = []
		list_instance_validate = []
		
		train_instance_family_ratio = 0.6
		num_instance_family = len(list_instance_family)
		num_instance_family_train = int(num_instance_family * train_instance_family_ratio)
		if num_instance_family_train <= 0: num_instance_family_train = min(num_instance_family, 1)
		num_instance_family_validate = num_instance_family - num_instance_family_train
		
		#tmp_list_instance_family = list_instance_family.copy()
		tmp_list_instance_family = []
		for instance_family in list_instance_family:
			tmp_list_instance_family.append(instance_family)
		
		length_tmp_list_instance_family = len(tmp_list_instance_family)
		i = 0
		while True:
			if i >= num_instance_family_train: break
			
			selected_index = random.randint(0, length_tmp_list_instance_family-1)
			selected_value = tmp_list_instance_family[selected_index]
			selected_list_instance_current = dict_instance_family_to_instance_list[selected_value]
			for instance_path in selected_list_instance_current:
				list_instance_train.append(instance_path)
			
			tmp_value = tmp_list_instance_family[selected_index]
			tmp_list_instance_family[selected_index] = tmp_list_instance_family[length_tmp_list_instance_family-1]
			tmp_list_instance_family[length_tmp_list_instance_family-1] = tmp_value
			
			length_tmp_list_instance_family -= 1
			i += 1
			
		for instance_path in feature_data_csv.list_rows():
			if not instance_path in list_instance_train:
				list_instance_validate.append(instance_path)
		
		list_instance_train.sort()
		list_instance_validate.sort()
		
		feature_data_csv_path_train = feature_data_csv_path + '_train.csv'
		feature_data_csv_path_validate = feature_data_csv_path + '_validate.csv'
		performance_data_csv_path_train = performance_data_csv_path + '_train.csv'
		performance_data_csv_path_validate = performance_data_csv_path + '_validate.csv'
		
		feature_data_csv_train = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
		feature_data_csv_validate = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
		performance_data_csv_train = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
		performance_data_csv_validate = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
		
		for i in range(0, num_instances):
			row_name_i = feature_data_csv.get_row_name(i)
		
			if not row_name_i in list_instance_train:
				feature_data_csv_train.delete_row(row_name_i)
				performance_data_csv_train.delete_row(row_name_i)
			
			if not row_name_i in list_instance_validate:
				feature_data_csv_validate.delete_row(row_name_i)
				performance_data_csv_validate.delete_row(row_name_i)
		
		feature_data_csv_train.save_csv(feature_data_csv_path_train)
		feature_data_csv_validate.save_csv(feature_data_csv_path_validate)
		performance_data_csv_train.save_csv(performance_data_csv_path_train)
		performance_data_csv_validate.save_csv(performance_data_csv_path_validate)
		
		return feature_data_csv_path_train, feature_data_csv_path_validate, performance_data_csv_path_train, performance_data_csv_path_validate
		
		
	
def generate_task_run_status():
	key_str = 'construct_sparkle_portfolio_selector'
	task_run_status_path = r'TMP/SBATCH_Portfolio_Jobs/' + key_str + r'.statusinfo'
	status_info_str = 'Status: Running\n'
	sfh.write_string_to_file(task_run_status_path, status_info_str)
	return

def delete_task_run_status():
	key_str = 'construct_sparkle_portfolio_selector'
	task_run_status_path = r'TMP/SBATCH_Portfolio_Jobs/' + key_str + r'.statusinfo'
	os.system(r'rm -rf ' + task_run_status_path)
	return


if __name__ == r'__main__':
	
	if len(sys.argv) != 1 and len(sys.argv) != 2:
		print('c Arguments error!')
		print('c Usage: ' + sys.argv[0])
		print('c or Usage: ' + sys.argv[0] + ' -parallel')
		sys.exit()
	
	flag_judge_exist_remaining_jobs = judge_exist_remaining_jobs(sparkle_global_help.feature_data_csv_path, sparkle_global_help.performance_data_csv_path)
	
	if flag_judge_exist_remaining_jobs:
		print r'c There remain unperformed feature computation jobs or performance computation jobs!'
		print r'c Please first execute all unperformed jobs before constructing Sparkle portfolio selecotr'
		print r'c Sparkle portfolio selector is not successfully constructed!'
		sys.exit()
	
	if len(sys.argv) == 2:
		if sys.argv[1] == '-parallel':
			portfolio_selector_path_basis = sparkle_global_help.sparkle_portfolio_selector_path
			num_job_in_parallel = sparkle_experiments_related_help.num_job_in_parallel
			performance_data_csv_path = sparkle_global_help.performance_data_csv_path
			feature_data_csv_path = sparkle_global_help.feature_data_csv_path
			cutoff_time_each_run = sparkle_experiments_related_help.cutoff_time_each_run
			par_num = sparkle_experiments_related_help.par_num
			round_count = sparkle_experiments_related_help.r_for_constructing_portfolio_selector
			
			feature_data_csv_path_train, feature_data_csv_path_validate, performance_data_csv_path_train, performance_data_csv_path_validate = split_feature_csv_and_performance_csv(feature_data_csv_path, performance_data_csv_path, mode=4, train_ratio=0.6, seed=1)
			
			run_solvers_parallel_jobid = scpsp.constructing_portfolio_selector_parallel(portfolio_selector_path_basis, num_job_in_parallel, performance_data_csv_path_train, performance_data_csv_path_validate, feature_data_csv_path_train, feature_data_csv_path_validate, cutoff_time_each_run, par_num, round_count)
			
			dependency_jobid_list = []
			if run_solvers_parallel_jobid:
				dependency_jobid_list.append(run_solvers_parallel_jobid)
			mode = 1
			job_script = 'Commands/sparkle_help/determine_portfolio_selector_core.py %s %s %d %d %d %d' % (portfolio_selector_path_basis, performance_data_csv_path, int(cutoff_time_each_run), int(par_num), int(round_count), int(mode))
			run_job_parallel_jobid = sparkle_job_parallel_help.running_job_parallel(job_script, dependency_jobid_list)
			
			if run_job_parallel_jobid:
				dependency_jobid_list.append(run_job_parallel_jobid)
			job_script = 'Commands/generate_report.py'
			run_job_parallel_jobid = sparkle_job_parallel_help.running_job_parallel(job_script, dependency_jobid_list)
			
		else:
			print('c Arguments error!')
			print('c Usage: ' + sys.argv[0])
			print('c or Usage: ' + sys.argv[0] + ' -parallel')
		sys.exit()
	
	print 'c Start constructing Sparkle portfolio selector ...'
	
	generate_task_run_status()
	
	cutoff_time_each_run = scps.get_cutoff_time_each_run_from_cutoff_time_information_txt_path()
	
	scps.construct_sparkle_portfolio_selector(sparkle_global_help.sparkle_portfolio_selector_path, sparkle_global_help.performance_data_csv_path, sparkle_global_help.feature_data_csv_path, cutoff_time_each_run)
	
	if not os.path.exists(sparkle_global_help.sparkle_portfolio_selector_path):
		print 'c Sparkle portfolio selector is not successfully constructed!'
		print 'c There might be some errors!'
		delete_task_run_status()
		sys.exit()
	else:
		print 'c Sparkle portfolio selector constructed!'
		print 'c Sparkle portfolio selector located at ' + sparkle_global_help.sparkle_portfolio_selector_path
		
		'''
		print r"c Start computing each solver's marginal contribution to perfect selector ..."
		rank_list = scmc.compute_perfect_selector_marginal_contribution(cutoff_time_each_run = cutoff_time_each_run)
		scmc.print_rank_list(rank_list, 1)
		print r'c Marginal contribution (perfect selector) computing done!'
	
		
		print r"c Start computing each solver's marginal contribution to actual selector ..."
		rank_list = scmc.compute_actual_selector_marginal_contribution(cutoff_time_each_run = cutoff_time_each_run)
		scmc.print_rank_list(rank_list, 2)
		print r'c Marginal contribution (actual selector) computing done!'
		'''
		
	
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)
	
	for solver in performance_data_csv.list_columns():
		print('c Start constructing the actual portfolio selector excluding solver %s ...' % (sfh.get_last_level_directory_name(solver)))
		tmp_performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(sparkle_global_help.performance_data_csv_path)
		tmp_performance_data_csv.delete_column(solver)
		tmp_performance_data_csv_path = r'TMP/' + r'tmp_performance_data_csv_' + sparkle_basic_help.get_time_pid_random_string() + r'.csv'
		tmp_performance_data_csv.save_csv(tmp_performance_data_csv_path)
		tmp_actual_portfolio_selector_path = sparkle_global_help.sparkle_portfolio_selector_path + '_excluding_' + sfh.get_last_level_directory_name(solver)
		
		if len(tmp_performance_data_csv.list_columns()) >= 1:
			scps.construct_sparkle_portfolio_selector(tmp_actual_portfolio_selector_path, tmp_performance_data_csv_path, sparkle_global_help.feature_data_csv_path, cutoff_time_each_run)
		else:
			print(r'c ****** WARNING: ' + r'No solver exists ! ******')
		
		if not os.path.exists(tmp_actual_portfolio_selector_path):
			print('c The actual portfolio selector excluding solver %s is not successfully constructed!' % (sfh.get_last_level_directory_name(solver)))
		else:
			print('c The actual portfolio selector excluding solver %s constructed!' % (sfh.get_last_level_directory_name(solver)))
			print('c The actual portfolio selector excluding solver %s located at %s' % (sfh.get_last_level_directory_name(solver), tmp_actual_portfolio_selector_path))
	
	
	delete_task_run_status()
		
