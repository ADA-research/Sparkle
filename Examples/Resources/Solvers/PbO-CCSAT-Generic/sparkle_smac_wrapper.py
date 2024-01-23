#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import time
import random
import sys
from pathlib import Path


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
solver_binary = relative_path + r'PbO-CCSAT'

tmp_directory = relative_path + r'tmp/'
if not os.path.exists(tmp_directory):
    os.system(r'mkdir -p ' + tmp_directory)

inputlog = Path(tmp_directory + "inputlog.txt")
with inputlog.open("w+") as f:
    instr = " ".join(sys.argv)
    f.write(instr)

instance_name = get_last_level_directory_name(instance)
solver_name = get_last_level_directory_name(solver_binary)
runsolver_watch_data_path = tmp_directory + solver_name + r'_' + instance_name + r'_' + get_time_pid_random_string() + r'.log'

command = runsolver_binary + r' -w ' + runsolver_watch_data_path + r' --cpu-limit ' + str(cutoff_time) + r' ' + solver_binary + r' -inst ' + instance + r' -seed ' + str(seed)

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

status = r'CRASHED'
for line in output_list:
    line = line.strip()
    if (line == r's SATISFIABLE') or (line == r's UNSATISFIABLE'):
        status = r'SUCCESS'
        break
    elif line == r's UNKNOWN':
        status = r'TIMEOUT'
        break

print(r'Result for SMAC: ' + status + r', ' + str(run_time) + r', 0, 0, ' + str(seed))

if specifics == 'rawres':
    raw_result_path = Path(runsolver_watch_data_path.replace('.log', '.rawres'))

    with raw_result_path.open('w') as outfile:
        for line in output_list:
            outfile.write(line)
