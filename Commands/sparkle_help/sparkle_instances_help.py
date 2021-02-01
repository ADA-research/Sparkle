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
from pathlib import Path

from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh


__sparkle_instance_list_file = 'sparkle_instance_list.txt'


#DEPRECATED
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
	path = Path(instances_directory)
	return [str(f) for f in path.rglob("*.cnf") if f.is_file()]

	#list_cnf_path = []
	#get_list_cnf_path_recursive(instances_directory, list_cnf_path)
	#return list_cnf_path

#DEPRECATED
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
	p = Path(instances_directory)
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


def _check_existence_of_instance_list_file(instances_source: str):
	if not os.path.isdir(instances_source):
		return False

	instance_list_file_path = os.path.join(instances_source, __sparkle_instance_list_file)

	if os.path.isfile(instance_list_file_path):
		return True
	else:
		return False


def _get_list_instance(instances_source: str):
	list_instance = []
	instance_list_file_path = os.path.join(instances_source, __sparkle_instance_list_file)
	infile = open(instance_list_file_path)
	lines = infile.readlines()

	for line in lines:
		words = line.strip().split()
		if len(words) <= 0:
			continue
		list_instance.append(line.strip())

	infile.close()

	return list_instance


def _copy_instance_list_to_reference(instances_source: Path):
	instance_list_path = Path(instances_source / Path(__sparkle_instance_list_file))
	target_path = Path(sgh.reference_list_dir / Path(instances_source.name + sgh.instance_list_postfix))
	command_line = 'cp ' + str(instance_list_path) + ' ' + str(target_path)
	os.system(command_line)

	return


def count_instances_in_reference_list(instance_set_name: str) -> int:
	count = 0
	instance_list_path = Path(sgh.reference_list_dir / Path(instance_set_name + sgh.instance_list_postfix))

	# Count instances in instance list file
	with instance_list_path.open('r') as infile:
		for line in infile:
			# If the line does not only contain whitespace, count it
			if line.strip():
				count = count + 1

	return count


def check_existence_of_reference_instance_list(instance_set_name: str) -> bool:
	instance_list_path = Path(sgh.reference_list_dir / Path(instance_set_name + sgh.instance_list_postfix))

	if instance_list_path.is_file():
		return True
	else:
		return False


def remove_reference_instance_list(instance_set_name: str):
	instance_list_path = Path(sgh.reference_list_dir / Path(instance_set_name + sgh.instance_list_postfix))

	sfh.rmfile(instance_list_path)

	return


def copy_reference_instance_list(target_file: Path, instance_set_name: str, path_modifier: str):
	instance_list_path = Path(sgh.reference_list_dir / Path(instance_set_name + sgh.instance_list_postfix))
	outlines = []

	# Add quotes around instances in instance list file
	with instance_list_path.open('r') as infile:
		for line in infile:
			outline = '\"'

			# Modify path for each instance file
			for word in line.strip().split():
				outline = outline + path_modifier + word + ' '

			outline = outline + '\"\n'
			outlines.append(outline)

	# Write quoted instance list to SMAC instance file
	with target_file.open('w') as outfile:
		for line in outlines:
			outfile.write(line)

	return


def _copy_reference_instance_list_to_smac(smac_instance_file: Path, instance_set_name: str):
	path_modifier = '../../instances/' + instance_set_name + '/'
	copy_reference_instance_list(smac_instance_file, instance_set_name, path_modifier)

	return


def copy_instances_to_smac(list_instance_path, instance_dir_prefix: str, smac_instance_dir_prefix: str, train_or_test: str):
	instance_set_name = Path(instance_dir_prefix).name

	file_suffix = ''
	if train_or_test == 'train':
		file_suffix = '_train.txt'
	elif train_or_test == 'test':
		file_suffix = '_test.txt'
	else:
		print('c Invalid function call of \'copy_instances_to_smac\'; aborting execution')
		sys.exit()

	smac_instance_file = Path(smac_instance_dir_prefix + file_suffix)
	smac_instance_dir = Path(sfh.get_directory(smac_instance_dir_prefix))

	# Remove the directory (of this specific instance set) to make sure it is empty
	# and remove the SMAC instance list file to make sure it is empty
	sfh.rmtree(Path(smac_instance_dir_prefix))
	sfh.rmfile(smac_instance_file)

	# (Re)create the path to the SMAC instance directory for this instance set
	if not smac_instance_dir.is_dir():
		smac_instance_dir.mkdir(parents=True, exist_ok=True)

	if instance_dir_prefix[-1] == '/':
		instance_dir_prefix = instance_dir_prefix[:-1]
	if smac_instance_dir_prefix == '/':
		smac_instance_dir_prefix = smac_instance_dir_prefix[:-1]

	fout = smac_instance_file.open('w+')
	for i in range(0, len(list_instance_path)):
		ori_instance_path = list_instance_path[i]
		target_instance_path = ori_instance_path.replace(instance_dir_prefix, smac_instance_dir_prefix, 1)
		target_instance_dir = sfh.get_directory(target_instance_path)
		#print(target_instance_dir)
		if not os.path.exists(target_instance_dir):
			os.system('mkdir -p ' + target_instance_dir)
		command_line = 'cp ' + ori_instance_path + ' ' + target_instance_path
		#print(command_line)
		os.system(command_line)

		# Only do this when no instance_list file exists for this instance set
		if not check_existence_of_reference_instance_list(instance_set_name):
			# Write instance to SMAC instance file
			fout.write(target_instance_path.replace(smac_instance_dir_prefix, '../../instances/' + sfh.get_last_level_directory_name(smac_instance_dir_prefix), 1) + '\n')

	fout.close()

	# If and instance_list file exists for this instance set: Write a version where every line is in double quotes to the SMAC instance file
	if check_existence_of_reference_instance_list(instance_set_name):
		_copy_reference_instance_list_to_smac(smac_instance_file, instance_set_name)

	return

