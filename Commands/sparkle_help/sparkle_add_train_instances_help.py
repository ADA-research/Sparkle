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
import random
import pathlib
from sparkle_help import sparkle_file_help as sfh

#DEPRICATED
'''
def get_list_cnf_path_recursive(path, list_cnf_path):
	p = pathlib.Path(path)
	return [f for f in p.rglob("*.cnf") if f.is_file()]

	if os.path.isfile(path):
		file_extension = sfh.get_file_least_extension(path)
		if file_extension == r'cnf':
			list_cnf_path.append(path)
		return
	elif os.path.isdir(path):
		if path[-1]!=r'/':
			this_path = path + '/'
		else:
			this_path = path
		list_all_items = os.listdir(this_path)
		for item in list_all_items:
			get_list_cnf_path_recursive(this_path+item, list_cnf_path)
	return
'''

def get_list_cnf_path(instances_directory):
	path = pathlib.Path(instances_directory)
	return [str(f) for f in path.rglob("*.cnf") if f.is_file()]

	#list_cnf_path = []
	#get_list_cnf_path_recursive(instances_directory, list_cnf_path)
	#return list_cnf_path

#DEPRICATED
'''
def get_list_all_path_recursive(path, list_all_path):
	if os.path.isfile(path):
		list_all_path.append(path)
		return
	elif os.path.isdir(path):
		if path[-1]!=r'/':
			this_path = path + '/'
		else:
			this_path = path
		list_all_items = os.listdir(this_path)
		for item in list_all_items:
			get_list_all_path_recursive(this_path+item, list_all_path)
	return
'''
def get_list_all_path(instances_directory):
	p = pathlib.Path(instances_directory)
	return [str(f) for f in p.rglob("*") if f.is_file()]

	#list_all_path = []
	#get_list_all_path_recursive(instances_directory, list_all_path)
	#return list_all_path

def get_list_train_cnf_index(list_cnf_path):
	num_list_cnf = len(list_cnf_path)
	num_list_train_cnf = num_list_cnf/2
	if num_list_train_cnf <=0: num_list_train_cnf = 1
	elif num_list_train_cnf >=101: num_list_train_cnf = 100
	
	tmp_list_key = []
	for i in range(0, num_list_cnf):
		tmp_list_key.append(i)
	
	list_train_cnf_index = []
	random_valid_limit = num_list_cnf-1
	i=0
	while i<num_list_train_cnf:
		p = random.randint(0, random_valid_limit)
		#print(p, tmp_list_key[p], random_valid_limit, tmp_list_key[:random_valid_limit])
		list_train_cnf_index.append(tmp_list_key[p])
		tmp_value = tmp_list_key[p]
		tmp_list_key[p] = tmp_list_key[random_valid_limit]
		tmp_list_key[random_valid_limit] = tmp_value
		random_valid_limit -= 1
		i+=1
	
	return list_train_cnf_index

def selecting_train_cnf(list_cnf_path, list_train_cnf_index, cnf_dir_prefix, smac_cnf_dir_prefix):
	if cnf_dir_prefix[-1] == r'/':
		cnf_dir_prefix = cnf_dir_prefix[:-1]
	if smac_cnf_dir_prefix == r'/':
		smac_cnf_dir_prefix = smac_cnf_dir_prefix[:-1]
	
	for index in list_train_cnf_index:
		ori_cnf_path = list_cnf_path[index]
		target_cnf_path = ori_cnf_path.replace(cnf_dir_prefix, smac_cnf_dir_prefix, 1)
		target_cnf_dir = sfh.get_directory(target_cnf_path)
		#print(target_cnf_dir)
		if not os.path.exists(target_cnf_dir):
			os.system('mkdir -p ' + target_cnf_dir)
		command_line = 'cp ' + ori_cnf_path + r' ' + target_cnf_path
		#print(command_line)
		os.system(command_line)
	return

def get_list_test_cnf_index(list_cnf_path, list_train_cnf_index):
	num_list_cnf = len(list_cnf_path)
	num_list_train_cnf = len(list_train_cnf_index)
	num_list_test_cnf = num_list_cnf - num_list_train_cnf
	
	if num_list_test_cnf <=0: num_list_test_cnf = 1
	elif num_list_test_cnf >=101: num_list_test_cnf = 100
	
	if num_list_cnf == 1 and num_list_train_cnf == 1:
		list_test_cnf_index = [0]
		return list_test_cnf_index
	
	tmp_list_key = []
	for i in range(0, num_list_cnf):
		if not i in list_train_cnf_index:
			tmp_list_key.append(i)
			#print i
	
	#print(len(tmp_list_key), tmp_list_key)
	
	list_test_cnf_index = []
	random_valid_limit = len(tmp_list_key) - 1
	i=0
	while i<num_list_test_cnf:
		p = random.randint(0, random_valid_limit)
		list_test_cnf_index.append(tmp_list_key[p])
		tmp_value = tmp_list_key[p]
		tmp_list_key[p] = tmp_list_key[random_valid_limit]
		tmp_list_key[random_valid_limit] = tmp_value
		random_valid_limit -= 1
		i+=1
	
	return list_test_cnf_index

def selecting_test_cnf(list_cnf_path, list_test_cnf_index, cnf_dir_prefix, smac_cnf_dir_prefix):
	if cnf_dir_prefix[-1] == r'/':
		cnf_dir_prefix = cnf_dir_prefix[:-1]
	if smac_cnf_dir_prefix == r'/':
		smac_cnf_dir_prefix = smac_cnf_dir_prefix[:-1]
	
	for index in list_test_cnf_index:
		ori_cnf_path = list_cnf_path[index]
		target_cnf_path = ori_cnf_path.replace(cnf_dir_prefix, smac_cnf_dir_prefix, 1)
		target_cnf_dir = sfh.get_directory(target_cnf_path)
		#print(target_cnf_dir)
		if not os.path.exists(target_cnf_dir):
			os.system('mkdir -p ' + target_cnf_dir)
		command_line = 'cp ' + ori_cnf_path + r' ' + target_cnf_path
		#print(command_line)
		os.system(command_line)
	return

def copy_instances_to_smac(list_instance_path, instance_dir_prefix, smac_instance_dir_prefix, train_or_test):
	file_suffix = r''
	if train_or_test == r'train':
		file_suffix = r'_train.txt'
	elif train_or_test == r'test':
		file_suffix = r'_test.txt'
	else:
		print(r'c Invalid function call of \'copy_instances_to_smac\'; aborting execution')
		sys.exit()

	file_instance = smac_instance_dir_prefix + file_suffix

	# Make sure the path to file_instance exists
	smac_instance_dir = sfh.get_directory(smac_instance_dir_prefix)
	if not os.path.exists(smac_instance_dir):
		os.system('mkdir -p ' + smac_instance_dir)

	if instance_dir_prefix[-1] == r'/':
		instance_dir_prefix = instance_dir_prefix[:-1]
	if smac_instance_dir_prefix == r'/':
		smac_instance_dir_prefix = smac_instance_dir_prefix[:-1]

	fout = open(file_instance, 'w+')
	for i in range(0, len(list_instance_path)):
		ori_instance_path = list_instance_path[i]
		target_instance_path = ori_instance_path.replace(instance_dir_prefix, smac_instance_dir_prefix, 1)
		target_instance_dir = sfh.get_directory(target_instance_path)
		#print(target_instance_dir)
		if not os.path.exists(target_instance_dir):
			os.system('mkdir -p ' + target_instance_dir)
		command_line = 'cp ' + ori_instance_path + r' ' + target_instance_path
		#print(command_line)
		os.system(command_line)

		fout.write(target_instance_path.replace(smac_instance_dir_prefix, '../../instances/' + sfh.get_last_level_directory_name(smac_instance_dir_prefix), 1) + '\n')
	fout.close()

	return


	
