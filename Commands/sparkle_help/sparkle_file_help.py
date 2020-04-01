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
import time
import random
import fcntl
from sparkle_help import sparkle_global_help


def create_new_empty_file(filepath):
	fo = open(filepath, "w+")
	fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
	fo.close()
	return

def get_current_directory_name(filepath):
	if filepath[-1] == r'/': filepath = filepath[0:-1]
	right_index = filepath.rfind(r'/')
	if right_index<0: pass
	else:
		filepath = filepath[0:right_index]
		filepath = get_last_level_directory_name(filepath)
	return filepath

def get_last_level_directory_name(filepath):
	if filepath[-1] == r'/': filepath = filepath[0:-1]
	right_index = filepath.rfind(r'/')
	if right_index<0: pass
	else: filepath = filepath[right_index+1:]
	return filepath


def get_file_name(filepath):
	right_index = filepath.rfind(r'/')
	filename = filepath
	if right_index<0: pass
	else: filename = filepath[right_index+1:]
	return filename

def get_directory(filepath):
	right_index = filepath.rfind(r'/')
	if right_index<0:
		directory = r'./'
	else:
		directory = filepath[:right_index+1]
	return directory

def get_file_full_extension(filepath):
	filename = get_file_name(filepath)
	file_extension = r''
	left_index = filename.find(r'.')
	if left_index<0: pass
	else: file_extension = filename[left_index+1:]
	return file_extension


def get_file_least_extension(filepath):
	filename = get_file_name(filepath)
	file_extension = r''
	right_index = filename.rfind(r'.')
	if right_index<0: pass
	else: file_extension = filename[right_index+1:]
	return file_extension


def get_list_all_cnf_filename_recursive(path, list_all_cnf_filename):
	if os.path.isfile(path):
		file_extension = get_file_least_extension(path)
		if file_extension == r'cnf':
			filename = get_file_name(path)
			list_all_cnf_filename.append(filename)
		return
	elif os.path.isdir(path):
		if path[-1]!=r'/':
			this_path = path + '/'
		else:
			this_path = path
		list_all_items = os.listdir(this_path)
		for item in list_all_items:
			get_list_all_cnf_filename_recursive(this_path+item, list_all_cnf_filename)
	return

def get_list_all_cnf_filename(filepath):
	list_all_cnf_filename = []
	get_list_all_cnf_filename_recursive(filepath, list_all_cnf_filename)
	return list_all_cnf_filename

def get_list_all_filename_recursive(path, list_all_filename):
	if os.path.isfile(path):
		filename = get_file_name(path)
		list_all_filename.append(filename)
		return
	elif os.path.isdir(path):
		if path[-1]!=r'/':
			this_path = path + '/'
		else:
			this_path = path
		list_all_items = os.listdir(this_path)
		for item in list_all_items:
			get_list_all_filename_recursive(this_path+item, list_all_filename)
	return

def get_list_all_filename(filepath):
	list_all_filename = []
	get_list_all_filename_recursive(filepath, list_all_filename)
	return list_all_filename

def get_list_all_directory_recursive(path, list_all_directory):
	if os.path.isfile(path):
		directory = get_directory(path)
		list_all_directory.append(directory)
		return
	elif os.path.isdir(path):
		if path[-1]!=r'/':
			this_path = path + '/'
		else:
			this_path = path
		list_all_items = os.listdir(this_path)
		for item in list_all_items:
			get_list_all_directory_recursive(this_path+item, list_all_directory)
	return

def get_list_all_directory(filepath):
	list_all_directory = []
	get_list_all_directory_recursive(filepath, list_all_directory)
	return list_all_directory

'''
def get_list_all_cnf_filename(filepath):
	if not os.path.exists(filepath):
		print r'c Directory ' + filepath + r' does not exist!'
		sys.exit()
	list_all_items = os.listdir(filepath)
	list_all_cnf_filename = []
	for i in range(0, len(list_all_items)):
		file_extension = get_file_least_extension(list_all_items[i])
		if file_extension == r'cnf':
			list_all_cnf_filename.append(list_all_items[i])
	return list_all_cnf_filename
'''

def get_list_all_csv_filename(filepath):
	csv_list = []
	if not os.path.exists(filepath):
		return csv_list
	
	list_all_items = os.listdir(filepath)
	for i in range(0, len(list_all_items)):
		file_extension = get_file_least_extension(list_all_items[i])
		if file_extension == r'csv':
			csv_list.append(list_all_items[i])
	return csv_list

def get_list_all_result_filename(filepath):
	result_list = []
	if not os.path.exists(filepath):
		return result_list
	
	list_all_items = os.listdir(filepath)
	for i in range(0, len(list_all_items)):
		file_extension = get_file_least_extension(list_all_items[i])
		if file_extension == r'result':
			result_list.append(list_all_items[i])
	return result_list

def get_list_all_jobinfo_filename(filepath):
	jobinfo_list = []
	if not os.path.exists(filepath):
		return jobinfo_list
	
	list_all_items = os.listdir(filepath)
	for i in range(0, len(list_all_items)):
		file_extension = get_file_least_extension(list_all_items[i])
		if file_extension == r'jobinfo':
			jobinfo_list.append(list_all_items[i])
	return jobinfo_list

def get_list_all_statusinfo_filename(filepath):
	statusinfo_list = []
	if not os.path.exists(filepath):
		return statusinfo_list
	
	list_all_items = os.listdir(filepath)
	for i in range(0, len(list_all_items)):
		file_extension = get_file_least_extension(list_all_items[i])
		if file_extension == r'statusinfo':
			statusinfo_list.append(list_all_items[i])
	return statusinfo_list

def add_new_instance_into_file(filepath):
	fo = open(sparkle_global_help.instance_list_path, 'a+')
	fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
	fo.write(filepath + '\n')
	fo.close()
	return


def add_new_instance_reference_into_file(filepath, status):
	fo = open(sparkle_global_help.instance_reference_list_path, 'a+')
	fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
	fo.write(filepath + r' ' + status + '\n')
	fo.close()
	return


def add_new_solver_into_file(filepath, deterministic='0'):
	fo = open(sparkle_global_help.solver_list_path, 'a+')
	fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
	fo.write(filepath + r' ' + deterministic + '\n')
	fo.close()
	return


def add_new_solver_nickname_into_file(nickname, filepath):
	fo = open(sparkle_global_help.solver_nickname_list_path, 'a+')
	fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
	fo.write(nickname + r' ' + filepath + '\n')
	fo.close()
	return


def add_new_extractor_into_file(filepath):
	fo = open(sparkle_global_help.extractor_list_path, 'a+')
	fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
	fo.write(filepath + '\n')
	fo.close()
	return

def add_new_extractor_feature_vector_size_into_file(filepath, feature_vector_size):
	fo = open(sparkle_global_help.extractor_feature_vector_size_list_path, 'a+')
	fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
	fo.write(filepath + r' ' + str(feature_vector_size) + '\n')
	fo.close()
	return
	
def add_new_extractor_nickname_into_file(nickname, filepath):
	fo = open(sparkle_global_help.extractor_nickname_list_path, 'a+')
	fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
	fo.write(nickname + r' ' + filepath + '\n')
	fo.close()
	return	
	
	

def write_solver_list():
	fout = open(sparkle_global_help.solver_list_path, 'w+')
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
	for i in range(0, len(sparkle_global_help.solver_list)):
		fout.write(sparkle_global_help.solver_list[i] + '\n')
	fout.close()
	return

def write_solver_nickname_mapping():
	fout = open(sparkle_global_help.solver_nickname_list_path, 'w+')
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
	for key in sparkle_global_help.solver_nickname_mapping:
		fout.write(key + r' ' + sparkle_global_help.solver_nickname_mapping[key] + '\n')
	fout.close()
	return

def write_extractor_list():
	fout = open(sparkle_global_help.extractor_list_path, 'w+')
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
	for i in range(0, len(sparkle_global_help.extractor_list)):
		fout.write(sparkle_global_help.extractor_list[i] + '\n')
	fout.close()
	return

def write_extractor_feature_vector_size_mapping():
	fout = open(sparkle_global_help.extractor_feature_vector_size_list_path, 'w+')
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
	for key in sparkle_global_help.extractor_feature_vector_size_mapping:
		fout.write(key + r' ' + str(sparkle_global_help.extractor_feature_vector_size_mapping[key]) + '\n')
	fout.close()
	return

def write_extractor_nickname_mapping():
	fout = open(sparkle_global_help.extractor_nickname_list_path, 'w+')
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
	for key in sparkle_global_help.extractor_nickname_mapping:
		fout.write(key + r' ' + sparkle_global_help.extractor_nickname_mapping[key] + '\n')
	fout.close()
	return

def write_instance_list():
	fout = open(sparkle_global_help.instance_list_path, 'w+')
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
	for i in range(0, len(sparkle_global_help.instance_list)):
		fout.write(sparkle_global_help.instance_list[i] + '\n')
	fout.close()
	return

def write_instance_reference_mapping():
	fout = open(sparkle_global_help.instance_reference_list_path, 'w+')
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
	for key in sparkle_global_help.instance_reference_mapping:
		fout.write(key + r' ' + sparkle_global_help.instance_reference_mapping[key] + '\n')	
	fout.close()
	return

def write_string_to_file(file_path, string_value):
	fout = open(file_path, 'w+')
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
	fout.write(string_value.strip()+'\n')
	fout.close()
	return

def append_string_to_file(file_path, string_value):
	fout = open(file_path, 'a+')
	while True:
		try:
			fcntl.flock(fout.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
			fout.write(string_value.strip()+'\n')
			#fcntl.flock(fout.fileno(), fcntl.LOCK_UN)
			fout.close()
			break
		except:
			time.sleep(random.randint(1, 5))
	'''
	fout = open(file_path, 'a+')
	fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
	fout.write(string_value.strip()+'\n')
	fout.close()
	'''
	return

def get_cutoff_time_information():
	fin = open(sparkle_global_help.cutoff_time_information_txt_path, 'r+')
	fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
	myline = fin.readline().strip()
	mylist = myline.split()
	cutoff_time_each_run = float(mylist[2])
	myline = fin.readline().strip()
	mylist = myline.split()
	par_num = float(mylist[2])
	penalty_time = cutoff_time_each_run * par_num
	fin.close()
	return [cutoff_time_each_run, par_num, penalty_time]


