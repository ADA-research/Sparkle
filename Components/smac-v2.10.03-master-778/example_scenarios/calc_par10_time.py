#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-

import os
import sys

#global sum_par10_time
#global num_sol_instance
#global num_all_instance

def get_file_directory(filepath):
	if os.path.isdir(filepath):
		if filepath[-1] != r'/':
			filedir = filepath + r'/'
		else:
			filedir = filepath
		return filedir
	right_index = filepath.rfind(r'/')
	if right_index<0: filedir = r'./'
	else: filedir = filepath[:right_index+1]
	return filedir

def get_file_name(filepath):
	right_index = filepath.rfind(r'/')
	filename = filepath
	if right_index<0: pass
	else: filename = filepath[right_index+1:]
	return filename

def get_file_least_extension(filepath):
	filename = get_file_name(filepath)
	file_extension = r''
	right_index = filename.rfind(r'.')
	if right_index<0: pass
	else: file_extension = filename[right_index+1:]
	return file_extension

def get_file_key_str(filepath, solver_name):
	file_key_str = r''
	file_key_dir = get_file_directory(filepath)
	index = file_key_dir.find(r'results/')
	file_key_dir = file_key_dir[index+len(r'results/'):]
	file_key_str = file_key_dir
	
	file_key_name = get_file_name(filepath)
	index = file_key_name.find(solver_name)
	file_key_name = file_key_name[index+len(solver_name)+1:]
	index = file_key_name.rfind(r'_1.res')
	file_key_name = file_key_name[:index]

	file_key_str += file_key_name
	
	return file_key_str


def visit_all_res_files_recursive(path, cutoff):
	global sum_par10_time
	global num_sol_instance
	global num_all_instance
	
	if os.path.isfile(path):
		file_extension = get_file_least_extension(path)
		if file_extension == r'res':
			fin = open(path, 'r')
			while True:
				myline = fin.readline()
				if myline:
					mylist = myline.strip().split()
					if len(mylist) <=1 :
						continue
					if mylist[1] == r's':
						run_time = float(mylist[0].split(r'/')[0])
						if(run_time > cutoff):
							continue
						if mylist[2] == r'SATISFIABLE':
							num_sol_instance += 1
							num_all_instance += 1
							sum_par10_time += run_time
							break
						elif mylist[2] == r'UNSATISFIABLE':
							num_sol_instance += 1
							num_all_instance += 1
							sum_par10_time += run_time
							break	
				else:
					run_time = cutoff * 10
					num_all_instance += 1
					sum_par10_time += run_time
					break
		return
	
	elif os.path.isdir(path):
		if path[-1] != r'/':
			this_path = path + r'/'
		else:
			this_path = path
		list_all_items = os.listdir(this_path)
		for item in list_all_items:
			visit_all_res_files_recursive(this_path+item, cutoff)
	return

def get_key(item):
	return item[0]

if __name__ == r'__main__':

	if len(sys.argv) != 3:
		print r'c Command error!'
		print r'c Usage: ' + sys.argv[0] + r' <path> <cutoff>'
		sys.exit()
	
	path = sys.argv[1]
	cutoff = int(sys.argv[2])

	global sum_par10_time
	global num_sol_instance
	global num_all_instance
	
	sum_par10_time = 0
	num_sol_instance = 0
	num_all_instance = 0
	visit_all_res_files_recursive(path, cutoff)
	
	print('avg_par10_time = %f' % (float(sum_par10_time)/num_all_instance))
	print('num_sol_instance = %d' % (num_sol_instance))
	print('num_all_instance = %d' % (num_all_instance))
	
	#print('cutoff = %d' % (cutoff))
	#print('num_sol = %d' % (len(list_sol_res_files)))

	#list_data_files.sort(key=get_key)
	#for item in list_data_files:
	#	print('%s %s' % (item[0], str(item[1])))	
	
