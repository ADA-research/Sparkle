#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Sparkle SMAC wrapper template."""

import os
import time
import random
import sys
import Path
# TODO: Add imports required by your changes


def get_time_pid_random_string():
    """Return a combination of time, PID, and random str."""
    my_time_str = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
    my_pid = os.getpid()
    my_pid_str = str(my_pid)
    my_random = random.randint(1, sys.maxsize)
    my_random_str = str(my_random)
    my_time_pid_random_str = my_time_str + '_' + my_pid_str + '_' + my_random_str
    return my_time_pid_random_str


def get_last_level_directory_name(filepath):
    """Return the final path component for a given string; similar to Path.name."""
    if filepath[-1] == '/':
        filepath = filepath[0:-1]
    right_index = filepath.rfind('/')
    if right_index < 0:
        pass
    else:
        filepath = filepath[right_index + 1:]
    return filepath


# Process SMAC arguments
instance = sys.argv[1]
specifics = sys.argv[2]
cutoff_time = int(float(sys.argv[3]) + 1)
run_length = int(sys.argv[4])
seed = int(sys.argv[5])

params = sys.argv[6:]

relative_path = './'
runsolver_binary = relative_path + 'runsolver'
# TODO: Change solver name
solver_binary = relative_path + 'PbO-CCSAT'

tmp_directory = relative_path + 'tmp/'
if not os.path.exists(tmp_directory):
    os.system('mkdir -p ' + tmp_directory)

instance_name = get_last_level_directory_name(instance)
solver_name = get_last_level_directory_name(solver_binary)
runsolver_watch_data_path = (tmp_directory + solver_name + '_' + instance_name + '_'
                             + get_time_pid_random_string() + '.log')

# Process parameters
# TODO: Make sure parameters are processed correctly for your solver
len_argv = len(sys.argv)
i = 6
param_str = ''

while i < len_argv:
    param_str += ' ' + sys.argv[i]
    i += 1
    param_str += ' ' + sys.argv[i]
    i += 1

# TODO: Change call to solver
command = (f'{runsolver_binary} -w {runsolver_watch_data_path} --cpu-limit '
           f'{str(cutoff_time)} {solver_binary} -inst {instance} -seed {str(seed)}'
           f'{param_str}')

# Execute and measure time
start_time = time.time()
output_list = os.popen(command).readlines()
end_time = time.time()
run_time = end_time - start_time
if run_time > cutoff_time:
    run_time = cutoff_time

# Cleanup
os.system('rm -f ' + runsolver_watch_data_path)
# TODO: Any problem specific cleanup

# Process run status
# TODO: Change checks for status for your specific problem output
status = 'CRASHED'
run_length = 0
quality = 0
for line in output_list:
    line = line.strip()
    if (line == 's SATISFIABLE') or (line == 's UNSATISFIABLE'):
        status = 'SUCCESS'
        break
    elif line == 's UNKNOWN':
        status = 'TIMEOUT'
        break

# Output results in the format SMAC requires
print(f'Result for SMAC: {status}, {str(run_time)}, {str(run_length)}, {str(quality)}, '
      f'{str(seed)}')

# Write raw solver output to file for Sparkle when calling run_configured_solver.py
if specifics == 'rawres':
    raw_result_path = Path(runsolver_watch_data_path.replace('.log', '.rawres'))

    with raw_result_path.open('w') as outfile:
        for line in output_list:
            outfile.write(line)
