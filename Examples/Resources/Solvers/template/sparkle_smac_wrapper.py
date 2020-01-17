#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-

import os
import time
import random
import sys
# TODO: Add imports required by your changes

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
# TODO: Change solver name
solver_binary = relative_path + r'PbO-CCSAT'

tmp_directory = relative_path + r'tmp/'
if not os.path.exists(tmp_directory):
	os.system(r'mkdir -p ' + tmp_directory)

instance_name = get_last_level_directory_name(instance)
solver_name = get_last_level_directory_name(solver_binary)
runsolver_watch_data_path = tmp_directory + solver_name + r'_' + instance_name + r'_' + get_time_pid_random_string() + r'.log'

# Process parameters
# TODO: Make sure parameters are processed correctly for your solver
len_argv = len(sys.argv)
i = 6
param_str = ''
while i<len_argv:
	param_str += r' ' + sys.argv[i]
	i += 1
	param_str += r' ' + sys.argv[i]
	i += 1

# TODO: Change call to solver
command = runsolver_binary + r' -w ' + runsolver_watch_data_path + r' -W ' + str(cutoff_time) + r' ' + solver_binary + r' -inst ' + instance + r' -seed ' + str(seed) + param_str

#print(command)

# Execute and measure time
start_time = time.time()
output_list = os.popen(command).readlines()
end_time = time.time()
run_time = end_time - start_time
if run_time > cutoff_time: run_time = cutoff_time

# Cleanup
os.system(r'rm -f ' + runsolver_watch_data_path)
# TODO: Any problem specific cleanup

#print output_list

# Process run status
# TODO: Change checks for status for your specific problem output
status = r'CRASHED'
run_length = 0
quality = 0
for line in output_list:
	line = line.strip()
	if (line == r's SATISFIABLE') or (line == r's UNSATISFIABLE'):
		status = r'SUCCESS'
		break
	elif line == r's UNKNOWN':
		status = r'TIMEOUT'
		break

print(r'Result for SMAC: ' + status + r', ' + str(run_time) + r', ' + str(run_length) + r', ' + str(quality) + ', ' + str(seed))


