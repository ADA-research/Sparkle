#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#Sparkle SMAC wrapper VRP_heuristic_Jan_MkII_Sparkle

import os
import time
import random
import sys

def get_time_pid_random_string():
	my_time_str = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
	my_pid = os.getpid()
	my_pid_str = str(my_pid)
	my_random = random.randint(1, sys.maxsize)
	my_random_str = str(my_random)
	my_time_pid_random_str = my_time_str + '_' + my_pid_str + '_' + my_random_str
	return my_time_pid_random_str

def get_last_level_directory_name(filepath):
	if filepath[-1] == r'/': filepath = filepath[0:-1]
	right_index = filepath.rfind(r'/')
	if right_index<0: pass
	else: filepath = filepath[right_index+1:]
	return filepath

instance = sys.argv[1]
specifics = sys.argv[2]
cutoff_time = int(float(sys.argv[3]) + 1)
run_length = int(sys.argv[4])
seed = int(sys.argv[5])

params = sys.argv[6:]

relative_path = r'./'
runsolver_binary = relative_path + r'runsolver'
solver_binary = relative_path + r'VRP_SISRs'

tmp_directory = relative_path + r'tmp/'
if not os.path.exists(tmp_directory):
	os.system(r'mkdir -p ' + tmp_directory)

instance_name = get_last_level_directory_name(instance)
solver_name = get_last_level_directory_name(solver_binary)
runsolver_watch_data_path = tmp_directory + solver_name + r'_' + instance_name + r'_' + get_time_pid_random_string() + r'.log'

command = runsolver_binary + r' -w ' + runsolver_watch_data_path + r' -W ' + str(cutoff_time) + r' ' + solver_binary + r' -inst ' + instance + r' -seed ' + str(seed)
#r: raw string, arguments get passed to algorithm only from solver_binary onwards!
len_argv = len(sys.argv)
i = 6
while i<len_argv:
	command += r' ' + sys.argv[i]
	i += 1
	command += r' ' + sys.argv[i]
	i += 1

#print(command)

start_time = time.time()
output_list = os.popen(command).readlines()
end_time = time.time()
run_time = end_time - start_time
if run_time > cutoff_time: run_time = cutoff_time

os.system(r'rm -f ' + runsolver_watch_data_path)

#print output_list

quality=1000000000000
status = r'SUCCESS'#always ok, code checks per iteration whether cutoff time is exceeded

for line in output_list:
	quality = line.strip()

print(r'Result for SMAC: ' + status + r', ' + str(run_time) + r', 0,'+str(quality) +r', '+ str(seed))
