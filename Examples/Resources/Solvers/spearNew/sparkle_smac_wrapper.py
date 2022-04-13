#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import time
import random
import sys
import re
import logging
from pathlib import Path
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile


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


def float_regex(self):
	return '[+-]?\d+(?:\.\d+)?(?:[eE][+-]\d+)?'


instance = sys.argv[1]
specifics = sys.argv[2]
cutoff_time = int(float(sys.argv[3]) + 1)
run_length = int(sys.argv[4])
seed = int(sys.argv[5])

params = sys.argv[6:]

relative_path = r'./'
runsolver_binary = relative_path + r'runsolver'
solver_binary = relative_path + r'Spear-32_1.2.1'

tmp_directory = relative_path + r'tmp/'
if not os.path.exists(tmp_directory):
	os.system(r'mkdir -p ' + tmp_directory)

instance_name = get_last_level_directory_name(instance)
solver_name = get_last_level_directory_name(solver_binary)
runsolver_watch_data_path = tmp_directory + solver_name + r'_' + instance_name + r'_' + get_time_pid_random_string() + r'.log'

# command = runsolver_binary + r' -w ' + runsolver_watch_data_path + r' -W ' + str(cutoff_time) + r' ' + solver_binary + r' -inst ' + instance + r' -seed ' + str(seed)
# command = solver_binary + r' --seed ' + str(seed) + r' --model-stdout' + r' --dimacs ' + instance 
# cmd = "%s --seed %d --model-stdout --dimacs %s" %(solver_binary, runargs["seed"], runargs["instance"]) + rest
command = "%s --seed %d --model-stdout --dimacs %s" %(solver_binary, seed, instance)

random_id = get_time_pid_random_string()
watcher_file = NamedTemporaryFile(
	suffix=".log", prefix="watcher-%s-" % (random_id), dir=tmp_directory, delete=False)
solver_file = NamedTemporaryFile(
	suffix=".log", prefix="solver-%s-" % (random_id), dir=tmp_directory, delete=False)

len_argv = len(sys.argv)
i = 6
while i<len_argv:
	command += r' -' + sys.argv[i]
	i += 1
	command += r' ' + sys.argv[i]
	i += 1

runsolver_cmd = [runsolver_binary, "-C", cutoff_time,
					"-w", "\"%s\"" % (watcher_file.name),
					"-o", "\"%s\"" % (solver_file.name)]

runsolver_cmd = " ".join(map(str, runsolver_cmd)) + " " + command

#print(command)

subprocesses = []
start_time = time.time()
# output_list = os.popen(call_target(command)).readlines()
io = Popen(runsolver_cmd, shell=True,
			preexec_fn=os.setpgrp, universal_newlines=True)
subprocesses.append(io)
io.wait()
subprocesses.remove(io)
if io.stdout:
	io.stdout.flush()
solver_file.seek(0)
watcher_file.seek(0)
end_time = time.time()
run_time = end_time - start_time
if run_time > cutoff_time: run_time = cutoff_time

os.system(r'rm -f ' + runsolver_watch_data_path)

#print output_list



logger = logging.getLogger("GenericWrapper")
logger.setLevel(logging.DEBUG)
additional = ""

try:
	data = str(watcher_file.read().decode("utf8"))
	if (re.search('runsolver_max_cpu_time_exceeded', data) or re.search('Maximum CPU time exceeded', data)):
		status = "TIMEOUT"

	if (re.search('runsolver_max_memory_limit_exceeded', data) or re.search('Maximum VSize exceeded', data)):
		status = "TIMEOUT"
		additional += " memory limit was exceeded"

	cpu_pattern1 = re.compile('^runsolver_cputime: (%s)' % (
		float_regex()), re.MULTILINE)
	cpu_match1 = re.search(cpu_pattern1, data)

	cpu_pattern2 = re.compile('^CPU time \\(s\\): (%s)' % (
		float_regex()), re.MULTILINE)
	cpu_match2 = re.search(cpu_pattern2, data)

	if (cpu_match1):
		time = float(cpu_match1.group(1))
	if (cpu_match2):
		time = float(cpu_match2.group(1))

	exitcode_pattern = re.compile('Child status: ([0-9]+)')
	exitcode_match = re.search(exitcode_pattern, data)

	if (exitcode_match):
		exit_code = int(exitcode_match.group(1))
except:
	# due to the common, rare runsolver bug,
	# the watcher file can be corrupted and can fail to be read
	exit_code = 0
	logger.warning(
		"Failed to read runsolver's watcher file---trust own wc-time measurment")



print("reading solver results from %s" % (solver_file.name))
data = solver_file.read()
try:
    data = str(data.decode("utf8"))
except AttributeError:
    print("AttributeError when reading solver results from file")
    pass    

status = 'CRASHED'
print(data)
if re.search('UNSATISFIABLE', data) or re.search('SATISFIABLE', data):
    status = 'SUCCESS'
elif re.search('s UNKNOWN', data) or re.search('INDETERMINATE', data):
    status = 'TIMEOUT'


print('Result for SMAC: ' + status + ', ' + str(run_time) + ', 0, 0, ' + str(seed))

if specifics == 'rawres':
	raw_result_path = Path(runsolver_watch_data_path.replace('.log', '.rawres'))

	with raw_result_path.open('w') as outfile:
		for line in data:
			outfile.write(line)
