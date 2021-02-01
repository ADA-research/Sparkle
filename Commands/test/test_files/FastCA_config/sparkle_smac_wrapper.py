#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

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


def _is_a_number(input_str : str):
	try:
		input_val = eval(input_str)
		if (type(input_val) == float) or (type(input_val) == int):
			return True
		else:
			return False
	except:
		return False


# Parse problem specific output and return it
def parse_output(output_list) -> (str, float):
	# Read solution quality from output_list
	solution_quality = sys.maxsize
	status = 'UNKNOWN'
	lines = output_list

	for line in lines:
		words = line.strip().split()
		if len(words) <= 0:
			continue
		if len(words) == 17 and words[0] == 'We' and words[1] == 'recommend':
			# First output line is normal, probably no crash
			solution_quality = sys.maxsize - 1
			# If no actual solution is found, we probably reach the cutoff time before finding a solution
			status = 'TIMEOUT'
		if len(words) == 3 and _is_a_number(words[0]) and _is_a_number(words[1]) and _is_a_number(words[2]):
			temp_solution_quality = int(words[1])
			if temp_solution_quality < solution_quality:
				solution_quality = temp_solution_quality
				status = 'SUCCESS'

	if solution_quality == sys.maxsize:
		status = 'CRASHED'

	return status, solution_quality


instance = sys.argv[1]
inst_list = instance.split()
inst_model = inst_list[0]
inst_constr = inst_list[1]
specifics = sys.argv[2]
cutoff_time = int(float(sys.argv[3]) + 1)
run_length = int(sys.argv[4])
seed = int(sys.argv[5])

params = sys.argv[6:]

relative_path = r'./'
runsolver_binary = relative_path + 'runsolver'
solver_binary = relative_path + 'FastCA'

tmp_directory = relative_path + 'tmp/'
if not os.path.exists(tmp_directory):
	os.system(r'mkdir -p ' + tmp_directory)

instance_model_name = get_last_level_directory_name(inst_model)
instance_constr_name = get_last_level_directory_name(inst_constr)
solver_name = get_last_level_directory_name(solver_binary)
runsolver_watch_data_path = tmp_directory + solver_name + '_' + instance_model_name + '_' + get_time_pid_random_string() + '.log'

command = runsolver_binary + ' -w ' + runsolver_watch_data_path + ' -W ' + str(cutoff_time) + r' ' + solver_binary + ' ' + inst_model + ' ' + inst_constr + ' ' + str(cutoff_time)

i = 6 # Start with first argument after 'seed'
while i < len(sys.argv):
	# Skip the parameter name for positional parameters
	i += 1
	command += r' ' + sys.argv[i]
	i += 1

# TODO: Replace with runtime from runsolver
start_time = time.time()
output_list = os.popen(command).readlines()
end_time = time.time()
run_time = end_time - start_time
if run_time > cutoff_time: run_time = cutoff_time

os.system(r'rm -f ' + runsolver_watch_data_path)

status, quality = parse_output(output_list)

print('Result for SMAC: ' + status + ', ' + str(run_time) + ', 0, ' + str(quality) + ', ' + str(seed))

