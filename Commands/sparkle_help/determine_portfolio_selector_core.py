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
import numpy as np
import sparkle_basic_help
import sparkle_global_help
import sparkle_file_help as sfh
import sparkle_construct_portfolio_selector_help as scps
import sparkle_feature_data_csv_help as sfdcsv
import sparkle_performance_data_csv_help as spdcsv
import sparkle_compute_marginal_contribution_help

def generate_task_run_status(excluded_solver=''):
	if excluded_solver == '':
		key_str = 'construct_sparkle_portfolio_selector'
	else:
		key_str = 'construct_sparkle_portfolio_selector' + '_' + sfh.get_last_level_directory_name(excluded_solver)
	task_run_status_path = r'TMP/SBATCH_Portfolio_Jobs/' + key_str + r'.statusinfo'
	status_info_str = 'Status: Running\n'
	sfh.write_string_to_file(task_run_status_path, status_info_str)
	return

def delete_task_run_status(excluded_solver=''):
	if excluded_solver == '':
		key_str = 'construct_sparkle_portfolio_selector'
	else:
		key_str = 'construct_sparkle_portfolio_selector' + '_' + sfh.get_last_level_directory_name(excluded_solver)
	task_run_status_path = r'TMP/SBATCH_Portfolio_Jobs/' + key_str + r'.statusinfo'
	os.system(r'rm -rf ' + task_run_status_path)
	return

def calc_par2_value_for_file(tmp_portfolio_selector_penalty_time_on_each_instance_path, cutoff_time_each_run, par_num):
	par2_value_sum = 0
	instance_count = 0
	penalty_time_each_run = cutoff_time_each_run * par_num
	par2_value_average = penalty_time_each_run
	
	fin = open(tmp_portfolio_selector_penalty_time_on_each_instance_path, 'r')
	while True:
		myline = fin.readline()
		if not myline: break
		mylist = myline.strip().split()
		runtime = float(mylist[-1])
		if runtime <= cutoff_time_each_run:
			par2_value_sum += runtime
		else:
			par2_value_sum += penalty_time_each_run
		instance_count += 1
	fin.close()
	
	try:
		par2_value_average = par2_value_sum/instance_count
	except:
		par2_value_average = penalty_time_each_run
	
	return par2_value_average

def calc_averaged_scheduling_length_for_file(tmp_portfolio_selector_predict_schedule_path):
	total_scheduling_length = 0
	instance_count = 0
	
	fin = open(tmp_portfolio_selector_predict_schedule_path, 'r')
	while True:
		instance_str = fin.readline()
		if not instance_str: break
		scheduling_list_str = fin.readline()
		if not scheduling_list_str: break
		scheduling_list = eval(scheduling_list_str)
		scheduling_length = len(scheduling_list)
		total_scheduling_length += scheduling_length
		instance_count += 1
	fin.close()
	
	try:
		averaged_scheduling_length = total_scheduling_length/instance_count
	except:
		averaged_scheduling_length = -2
		
	return averaged_scheduling_length

def determine_portfolio_selector_via_PAR(actual_portfolio_selector_path, cutoff_time_each_run, par_num, round_count, portfolio_selector_basis=''):
	best_par2_value = -1
	actual_portfolio_selector_penalty_time_on_each_instance_path = actual_portfolio_selector_path + '_penalty_time_on_each_instance.txt'
	actual_portfolio_selector_predict_schedule_path = actual_portfolio_selector_path + '_predict_schedule_for_each_instance.txt'
	
	if portfolio_selector_basis != '':
		overall_actual_portfolio_selector_path = portfolio_selector_basis
		overall_actual_portfolio_selector_penalty_time_on_each_instance_path = overall_actual_portfolio_selector_path + '_penalty_time_on_each_instance.txt'
		overall_actual_portfolio_selector_predict_schedule_path = overall_actual_portfolio_selector_path + '_predict_schedule_for_each_instance.txt'
		overall_best_par2_value = calc_par2_value_for_file(overall_actual_portfolio_selector_penalty_time_on_each_instance_path, cutoff_time_each_run, par_num)
	
	for i in range(0, round_count):
		run_id_str = str(i)
		tmp_portfolio_selector_path = actual_portfolio_selector_path + '_' + run_id_str
		tmp_portfolio_selector_penalty_time_on_each_instance_path = tmp_portfolio_selector_path + '_penalty_time_on_each_instance.txt'
		tmp_portfolio_selector_predict_schedule_path = tmp_portfolio_selector_path + '_predict_schedule_for_each_instance.txt'
		
		if os.path.exists(tmp_portfolio_selector_path) and os.path.isfile(tmp_portfolio_selector_path) and os.path.exists(tmp_portfolio_selector_penalty_time_on_each_instance_path) and os.path.isfile(tmp_portfolio_selector_penalty_time_on_each_instance_path):
			try:
				tmp_par2_value = calc_par2_value_for_file(tmp_portfolio_selector_penalty_time_on_each_instance_path, cutoff_time_each_run, par_num)
		
				print('c %s %f' % (tmp_portfolio_selector_path, tmp_par2_value))
		
				bool_updated = False
				if best_par2_value < 0 or tmp_par2_value < best_par2_value:
					bool_updated = True
					best_par2_value = tmp_par2_value
					#os.system('mv %s %s' % (tmp_portfolio_selector_path, actual_portfolio_selector_path))
					#os.system('mv %s %s' % (tmp_portfolio_selector_penalty_time_on_each_instance_path, actual_portfolio_selector_penalty_time_on_each_instance_path))
					#os.system('mv %s %s' % (tmp_portfolio_selector_predict_schedule_path, actual_portfolio_selector_predict_schedule_path))
					os.system('cp %s %s' % (tmp_portfolio_selector_path, actual_portfolio_selector_path))
					os.system('cp %s %s' % (tmp_portfolio_selector_penalty_time_on_each_instance_path, actual_portfolio_selector_penalty_time_on_each_instance_path))
					os.system('cp %s %s' % (tmp_portfolio_selector_predict_schedule_path, actual_portfolio_selector_predict_schedule_path))
					
					pass
				
				if portfolio_selector_basis != '':
					if tmp_par2_value < overall_best_par2_value:
						os.system('cp %s %s' % (tmp_portfolio_selector_path, overall_actual_portfolio_selector_path))
						os.system('cp %s %s' % (tmp_portfolio_selector_penalty_time_on_each_instance_path, overall_actual_portfolio_selector_penalty_time_on_each_instance_path))
						os.system('cp %s %s' % (tmp_portfolio_selector_predict_schedule_path, overall_actual_portfolio_selector_predict_schedule_path))
		
				if not bool_updated:
					#os.system('rm -f %s' % (tmp_portfolio_selector_path))
					#os.system('rm -f %s' % (tmp_portfolio_selector_penalty_time_on_each_instance_path))
					#os.system('rm -f %s' % (tmp_portfolio_selector_predict_schedule_path))
					pass
			except:
				#os.system('rm -f %s' % (tmp_portfolio_selector_path))
				#os.system('rm -f %s' % (tmp_portfolio_selector_penalty_time_on_each_instance_path))
				#os.system('rm -f %s' % (tmp_portfolio_selector_predict_schedule_path))
				pass
		else:
			#os.system('rm -f %s' % (tmp_portfolio_selector_path))
			#os.system('rm -f %s' % (tmp_portfolio_selector_penalty_time_on_each_instance_path))
			#os.system('rm -f %s' % (tmp_portfolio_selector_predict_schedule_path))
			pass
	return

def determine_portfolio_selector_via_averaged_scheduling_length(actual_portfolio_selector_path, round_count, portfolio_selector_basis=''):
	best_averaged_scheduling_length = -1
	actual_portfolio_selector_penalty_time_on_each_instance_path = actual_portfolio_selector_path + '_penalty_time_on_each_instance.txt'
	actual_portfolio_selector_predict_schedule_path = actual_portfolio_selector_path + '_predict_schedule_for_each_instance.txt'

	for i in range(0, round_count):
		run_id_str = str(i)
		tmp_portfolio_selector_path = actual_portfolio_selector_path + '_' + run_id_str
		tmp_portfolio_selector_penalty_time_on_each_instance_path = tmp_portfolio_selector_path + '_penalty_time_on_each_instance.txt'
		tmp_portfolio_selector_predict_schedule_path = tmp_portfolio_selector_path + '_predict_schedule_for_each_instance.txt'
		if os.path.exists(tmp_portfolio_selector_path) and os.path.isfile(tmp_portfolio_selector_path) and os.path.exists(tmp_portfolio_selector_predict_schedule_path) and os.path.isfile(tmp_portfolio_selector_predict_schedule_path):
			try:
				tmp_averaged_scheduling_length = calc_averaged_scheduling_length_for_file(tmp_portfolio_selector_predict_schedule_path)
				print('c %s %f' % (tmp_portfolio_selector_path, tmp_averaged_scheduling_length))
				
				bool_updated = False
				if best_averaged_scheduling_length < 0 or (tmp_averaged_scheduling_length>=0 and tmp_averaged_scheduling_length > best_averaged_scheduling_length):
					bool_updated = True
					best_averaged_scheduling_length = tmp_averaged_scheduling_length
					os.system('cp %s %s' % (tmp_portfolio_selector_path, actual_portfolio_selector_path))
					os.system('cp %s %s' % (tmp_portfolio_selector_penalty_time_on_each_instance_path, actual_portfolio_selector_penalty_time_on_each_instance_path))
					os.system('cp %s %s' % (tmp_portfolio_selector_predict_schedule_path, actual_portfolio_selector_predict_schedule_path))
					pass
				
				if not bool_updated:
					#os.system('rm -f %s' % (tmp_portfolio_selector_path))
					#os.system('rm -f %s' % (tmp_portfolio_selector_penalty_time_on_each_instance_path))
					#os.system('rm -f %s' % (tmp_portfolio_selector_predict_schedule_path))
					pass
			except:
				#os.system('rm -f %s' % (tmp_portfolio_selector_path))
				#os.system('rm -f %s' % (tmp_portfolio_selector_penalty_time_on_each_instance_path))
				#os.system('rm -f %s' % (tmp_portfolio_selector_predict_schedule_path))
				pass
		else:
			#os.system('rm -f %s' % (tmp_portfolio_selector_path))
			#os.system('rm -f %s' % (tmp_portfolio_selector_penalty_time_on_each_instance_path))
			#os.system('rm -f %s' % (tmp_portfolio_selector_predict_schedule_path))
			pass
	return


def determine_portfolio_selector_via_PAR_and_averaged_scheduling_length(actual_portfolio_selector_path, cutoff_time_each_run, par_num, round_count, portfolio_selector_basis=''):
	actual_portfolio_selector_penalty_time_on_each_instance_path = actual_portfolio_selector_path + '_penalty_time_on_each_instance.txt'
	actual_portfolio_selector_predict_schedule_path = actual_portfolio_selector_path + '_predict_schedule_for_each_instance.txt'
	
	list_candidate_item = []
	
	for i in range(0, round_count):
		run_id_str = str(i)
		tmp_portfolio_selector_path = actual_portfolio_selector_path + '_' + run_id_str
		tmp_portfolio_selector_penalty_time_on_each_instance_path = tmp_portfolio_selector_path + '_penalty_time_on_each_instance.txt'
		tmp_portfolio_selector_predict_schedule_path = tmp_portfolio_selector_path + '_predict_schedule_for_each_instance.txt'
		if os.path.exists(tmp_portfolio_selector_path) and os.path.isfile(tmp_portfolio_selector_path) and os.path.exists(tmp_portfolio_selector_penalty_time_on_each_instance_path) and os.path.isfile(tmp_portfolio_selector_penalty_time_on_each_instance_path) and os.path.exists(tmp_portfolio_selector_predict_schedule_path) and os.path.isfile(tmp_portfolio_selector_predict_schedule_path):
			try:
				tmp_par2_value = calc_par2_value_for_file(tmp_portfolio_selector_penalty_time_on_each_instance_path, cutoff_time_each_run, par_num)
				tmp_averaged_scheduling_length = calc_averaged_scheduling_length_for_file(tmp_portfolio_selector_predict_schedule_path)
				candidate_item = [tmp_portfolio_selector_path, tmp_portfolio_selector_penalty_time_on_each_instance_path, tmp_portfolio_selector_predict_schedule_path, tmp_par2_value, tmp_averaged_scheduling_length]
				list_candidate_item.append(candidate_item)
			except:
				pass
	
	list_candidate_item.sort(key=lambda candidate_item: candidate_item[3])
	
	valid_size = len(list_candidate_item)/4
	if valid_size<=0: valid_size = len(list_candidate_item)
	
	best_averaged_scheduling_length = -1
	best_index = -1
	for i in range(0, valid_size):
		candidate_item = list_candidate_item[i]
		tmp_averaged_scheduling_length = candidate_item[4]
		if best_averaged_scheduling_length == -1 or (tmp_averaged_scheduling_length>=0 and tmp_averaged_scheduling_length > best_averaged_scheduling_length):
			best_averaged_scheduling_length = tmp_averaged_scheduling_length
			best_index = i
	
	candidate_item = list_candidate_item[best_index]
	tmp_portfolio_selector_path = candidate_item[0]
	tmp_portfolio_selector_penalty_time_on_each_instance_path = candidate_item[1]
	tmp_portfolio_selector_predict_schedule_path = candidate_item[2]
	
	print('c %d %s %f %d' % (best_index, tmp_portfolio_selector_path, candidate_item[3], candidate_item[4]))
	
	os.system('cp %s %s' % (tmp_portfolio_selector_path, actual_portfolio_selector_path))
	os.system('cp %s %s' % (tmp_portfolio_selector_penalty_time_on_each_instance_path, actual_portfolio_selector_penalty_time_on_each_instance_path))
	os.system('cp %s %s' % (tmp_portfolio_selector_predict_schedule_path, actual_portfolio_selector_predict_schedule_path))
	return

def get_list_total_instance_from_file(actual_portfolio_selector_penalty_time_on_each_instance_path):
	list_total_instance = []
	
	fin = open(actual_portfolio_selector_penalty_time_on_each_instance_path, 'r')
	while True:
		myline = fin.readline()
		if not myline: break
		mylist = myline.strip().split()
		instance_path = mylist[0]
		list_total_instance.append(instance_path)
	
	return list_total_instance
		
def divide_instance_list_into_families(list_total_instance):
	list_instance_family = []
	dict_instance_family_to_instance_list = {}
	
	for instance_path in list_total_instance:
		instance_family = sfh.get_all_level_directory(instance_path)
		if not instance_family in list_instance_family:
			list_instance_family.append(instance_family)
			dict_instance_family_to_instance_list[instance_family] = []
			dict_instance_family_to_instance_list[instance_family].append(instance_path)
		else:
			dict_instance_family_to_instance_list[instance_family].append(instance_path)
	
	return list_instance_family, dict_instance_family_to_instance_list

def calc_portfolio_selector_variance_over_instance_family(candidate_item, list_instance_family, dict_instance_family_to_instance_list):
	tmp_portfolio_selector_penalty_time_on_each_instance_path = candidate_item[1]
	
	dict_instance_to_par_value = {}
	
	fin = open(tmp_portfolio_selector_penalty_time_on_each_instance_path, 'r')
	while True:
		myline = fin.readline()
		if not myline: break
		mylist = myline.strip().split()
		instance_path = mylist[0]
		par_value = float(mylist[1])
		dict_instance_to_par_value[instance_path] = par_value
	
	list_par_value_over_instance_family = []
	for instance_family in list_instance_family:
		list_instance_current = dict_instance_family_to_instance_list[instance_family]
		par_value_sum = 0
		instance_count = 0
		for instance in list_instance_current:
			par_value_tmp = dict_instance_to_par_value[instance]
			par_value_sum += par_value_tmp
			instance_count += 1
		
		if instance_count > 0:
			list_par_value_over_instance_family.append(par_value_sum/instance_count)
	
	par_value_std_over_insance_family = np.std(list_par_value_over_instance_family)
	#print(list_par_value_over_instance_family)
	#print(par_value_std_over_insance_family)
	return par_value_std_over_insance_family



def determine_portfolio_selector_via_PAR_and_variance(actual_portfolio_selector_path, cutoff_time_each_run, par_num, round_count, portfolio_selector_basis=''):
	actual_portfolio_selector_penalty_time_on_each_instance_path = actual_portfolio_selector_path + '_penalty_time_on_each_instance.txt'
	actual_portfolio_selector_predict_schedule_path = actual_portfolio_selector_path + '_predict_schedule_for_each_instance.txt'
	
	list_candidate_item = []
	
	for i in range(0, round_count):
		run_id_str = str(i)
		tmp_portfolio_selector_path = actual_portfolio_selector_path + '_' + run_id_str
		tmp_portfolio_selector_penalty_time_on_each_instance_path = tmp_portfolio_selector_path + '_penalty_time_on_each_instance.txt'
		tmp_portfolio_selector_predict_schedule_path = tmp_portfolio_selector_path + '_predict_schedule_for_each_instance.txt'
		if os.path.exists(tmp_portfolio_selector_path) and os.path.isfile(tmp_portfolio_selector_path) and os.path.exists(tmp_portfolio_selector_penalty_time_on_each_instance_path) and os.path.isfile(tmp_portfolio_selector_penalty_time_on_each_instance_path) and os.path.exists(tmp_portfolio_selector_predict_schedule_path) and os.path.isfile(tmp_portfolio_selector_predict_schedule_path):
			try:
				tmp_par2_value = calc_par2_value_for_file(tmp_portfolio_selector_penalty_time_on_each_instance_path, cutoff_time_each_run, par_num)
				tmp_averaged_scheduling_length = calc_averaged_scheduling_length_for_file(tmp_portfolio_selector_predict_schedule_path)
				candidate_item = [tmp_portfolio_selector_path, tmp_portfolio_selector_penalty_time_on_each_instance_path, tmp_portfolio_selector_predict_schedule_path, tmp_par2_value, tmp_averaged_scheduling_length]
				list_candidate_item.append(candidate_item)
			except:
				pass

	list_candidate_item.sort(key=lambda candidate_item: candidate_item[3])
	
	valid_size = len(list_candidate_item)/4
	if valid_size<=0: valid_size = len(list_candidate_item)
	
	
	performance_data_csv_path_validate = sparkle_global_help.performance_data_csv_path + '_validate.csv'
	performance_data_csv_validate = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path_validate)
	list_total_instance = performance_data_csv_validate.list_rows()
	list_instance_family, dict_instance_family_to_instance_list = divide_instance_list_into_families(list_total_instance)
	
	best_index = -1
	smallest_par_value_std = -1
	for i in range(0, valid_size):
		candidate_item = list_candidate_item[i]
		par_value_std_over_insance_family = calc_portfolio_selector_variance_over_instance_family(candidate_item, list_instance_family, dict_instance_family_to_instance_list)
		if smallest_par_value_std < 0 or par_value_std_over_insance_family < smallest_par_value_std:
			smallest_par_value_std = par_value_std_over_insance_family
			best_index = i
	
	selected_portfolio_selector_path = list_candidate_item[best_index][0]
	selected_portfolio_selector_penalty_time_on_each_instance_path = list_candidate_item[best_index][1]
	selected_portfolio_selector_predict_schedule_path = list_candidate_item[best_index][2]
	
	print('c %d %s %f' % (best_index, selected_portfolio_selector_path, smallest_par_value_std))
	
	os.system('cp %s %s' % (selected_portfolio_selector_path, actual_portfolio_selector_path))
	os.system('cp %s %s' % (selected_portfolio_selector_penalty_time_on_each_instance_path, actual_portfolio_selector_penalty_time_on_each_instance_path))
	os.system('cp %s %s' % (selected_portfolio_selector_predict_schedule_path, actual_portfolio_selector_predict_schedule_path))
	return


def determine_portfolio_selector(actual_portfolio_selector_path, cutoff_time_each_run, par_num, round_count, portfolio_selector_basis, mode=1):
	if mode==1:
		determine_portfolio_selector_via_PAR(actual_portfolio_selector_path, cutoff_time_each_run, par_num, round_count, portfolio_selector_basis)
	elif mode==2:
		determine_portfolio_selector_via_averaged_scheduling_length(actual_portfolio_selector_path, round_count, portfolio_selector_basis)
	elif mode==3:
		determine_portfolio_selector_via_PAR_and_averaged_scheduling_length(actual_portfolio_selector_path, cutoff_time_each_run, par_num, round_count, portfolio_selector_basis)
	elif mode==4:
		determine_portfolio_selector_via_PAR_and_variance(actual_portfolio_selector_path, cutoff_time_each_run, par_num, round_count, portfolio_selector_basis='')
	else:
		determine_portfolio_selector_via_PAR(actual_portfolio_selector_path, cutoff_time_each_run, par_num, round_count, portfolio_selector_basis)
	return
					

if __name__ == '__main__':
	if len(sys.argv) >= 6:
		portfolio_selector_basis = sys.argv[1]
		performance_data_csv_path = sys.argv[2]
		cutoff_time_each_run = int(sys.argv[3])
		par_num = int(sys.argv[4])
		round_count = int(sys.argv[5])
		if len(sys.argv) >= 7:
			mode = int(sys.argv[6])
		else:
			mode = 1 #default
	else:
		print('c Arguments Error!')
		sys.exit(-1)
	
	generate_task_run_status()	
	
	determine_portfolio_selector(portfolio_selector_basis, cutoff_time_each_run, par_num, round_count, '', mode)
	
	performance_data_csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)
	
	for excluded_solver in performance_data_csv.list_columns():
		actual_portfolio_selector_path = portfolio_selector_basis + '_excluding_' + sfh.get_last_level_directory_name(excluded_solver)
		determine_portfolio_selector(actual_portfolio_selector_path, cutoff_time_each_run, par_num, round_count, portfolio_selector_basis, mode)
	
	delete_task_run_status()


