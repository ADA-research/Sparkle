#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import subprocess
import sys
import random
import time
from pathlib import Path

global sparkle_special_string
sparkle_special_string = r'__@@SPARKLE@@__'

def get_time_pid_random_string():
	my_time_str = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
	my_pid = os.getpid()
	my_pid_str = str(my_pid)
	my_random = random.randint(1, sys.maxsize)
	my_random_str = str(my_random)
	my_time_pid_random_str = my_time_str + '_' + my_pid_str + '_' + my_random_str
	return my_time_pid_random_str

def get_last_level_directory_name(filepath):
	if filepath[-1] == r'/':
		filepath = filepath[0:-1]
	right_index = filepath.rfind(r'/')
	if right_index < 0:
		pass
	else:
		filepath = filepath[right_index+1:]
	return filepath

def deal_raw_result_file(relative_path, cnf_instance_file_name, raw_result_file_name, result_feature_file_name):
	
	#current_directory_path = os.getcwd()
	#current_last_level_directory_name = get_last_level_directory_name(current_directory_path)
	
	extractor_directory_last_level = get_last_level_directory_name(relative_path)
	
	fin = open(raw_result_file_name, 'r')
	fout = open(result_feature_file_name, 'w+')
	while True:
		myline = fin.readline()
		myline = myline.strip()
		if not myline:
			break
		mylist = myline.split()
		if len(mylist) == 0:
			continue
		elif mylist[0] == r'c':
			continue
		else: 
			#fout.write(',' + myline + '\n')
			mylist_comma = myline.split(r',')
			for i in range(0, len(mylist_comma)):
				fout.write(r','+mylist_comma[i] + sparkle_special_string + extractor_directory_last_level)
				#fout.write(r','+mylist_comma[i]+r'_'+current_last_level_directory_name)
			fout.write('\n')
			myline2 = fin.readline()
			myline2 = myline2.strip()
			fout.write(cnf_instance_file_name + ',' + myline2 + '\n')
	fin.close()
	fout.close()
	
	return


executable_name = r'features'

'''
if len(sys.argv) !=4:
	print r'c Command error!'
	print r'c Usage: ' + sys.argv[0] + r' <relative_path> <cnf_instance_file> <result_feature_file>'
	sys.exit()
'''

relative_path = sys.argv[1]
cnf_instance_file_name = sys.argv[2]
result_feature_file_name = sys.argv[3]
#tmp_output = sys.argv[4]

raw_result_file_name = relative_path + r'' + executable_name + r'_' + get_last_level_directory_name(cnf_instance_file_name) + r'_' + get_time_pid_random_string() + r'.rawres'

tmp_output = r'TMP/' + raw_result_file_name

#command_line = relative_path + r'/' + executable_name + r' ' + cnf_instance_file_name + ' ' + tmp_output + r' > ' + raw_result_file_name
command_line = [relative_path + '/' + executable_name, cnf_instance_file_name, tmp_output, '>', raw_result_file_name]
subprocess.run(command_line)
# os.system(command_line)

#print raw_result_file_name

deal_raw_result_file(relative_path, cnf_instance_file_name, raw_result_file_name, result_feature_file_name)

Path(tmp_output).unlink(missing_ok=True)
Path(raw_result_file_name).unlink(missing_ok=True)
