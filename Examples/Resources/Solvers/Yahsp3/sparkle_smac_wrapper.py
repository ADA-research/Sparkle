#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import time
import random
import sys
# DONE: Add imports required by your changes
import re
from subprocess import Popen, PIPE


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


# Process SMAC arguments
instance = sys.argv[1]
specifics = sys.argv[2]
cutoff_time = int(float(sys.argv[3]) + 1)
run_length = int(sys.argv[4])
seed = int(sys.argv[5])

params = sys.argv[6:]

relative_path = r'./'
runsolver_binary = relative_path + r'runsolver'
# DONE: Change solver name
solver_binary = relative_path + r'cpt_yahsp'

tmp_directory = relative_path + r'tmp/'
if not os.path.exists(tmp_directory):
	os.system(r'mkdir -p ' + tmp_directory)

instance_name = get_last_level_directory_name(instance)
solver_name = get_last_level_directory_name(solver_binary)
runsolver_watch_data_path = tmp_directory + solver_name + r'_' + instance_name + r'_' + get_time_pid_random_string() + r'.log'

# Process parameters
# DONE: Make sure parameters are processed correctly for your solver
len_argv = len(sys.argv)
i = 6
param_str = ''
while i<len_argv:
	param_str += r' ' + sys.argv[i]
	i += 1
	param_str += r' ' + sys.argv[i]
	i += 1

# DONE: Change call to solver
# Generate domain file (problem specific)
domain_file = 'domain_' + str(get_time_pid_random_string()) + '.pddl'
command = 'python generate_domain_file.py 5 ' + param_str + ' > ' + domain_file
process = Popen(command, shell=True, stdout=PIPE)
stdout = process.communicate()
# Call solver
command = runsolver_binary + r' -w ' + runsolver_watch_data_path + r' -W ' + str(cutoff_time) + r' ' + solver_binary + r' -y 1 -o ' + domain_file + ' -f ' + instance

#print(command)

# Execute and measure time
start_time = time.time()
output_list = os.popen(command).readlines()
end_time = time.time()
run_time = end_time - start_time
if run_time > cutoff_time: run_time = cutoff_time

# Cleanup
os.system(r'rm -f ' + runsolver_watch_data_path)
# DONE: Any problem specific cleanup
os.system(r'rm -f ' + domain_file)

#print output_list

# Process run status
# DONE: Change checks for status for your specific problem output
status = r'CRASHED'
quality = 0

if run_time == cutoff_time:
	status = r'TIMEOUT'
else:
	count = 0
	for line in output_list:
		line = line.strip()
		if re.match("[0-9]:", line):
			count += 1
	if count > 0:
		quality = 0-float(run_time)
		status = r'SUCCESS'

print(r'Result for SMAC: ' + status + r', ' + str(run_time) + r', ' + str(run_length) + r', ' + str(quality) + ', ' + str(seed))


