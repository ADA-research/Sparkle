#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import time
import random
import sys
from argparse import Namespace
from pathlib import Path


def get_time_pid_random_string():
    my_time_str = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
    my_pid = os.getpid()
    my_pid_str = str(my_pid)
    my_random = random.randint(1, sys.maxsize)
    my_random_str = str(my_random)
    my_time_pid_random_str = my_time_str + '_' + my_pid_str + '_' + my_random_str
    return my_time_pid_random_str


args = eval(sys.argv[1])

# instance = sys.argv[1]
specifics = args.specifics
cutoff_time = args.cutoff_time
# run_length = int(sys.argv[4])
seed = args.seed

# params = sys.argv[6:]

relative_path = r'./'
runsolver_binary = relative_path + r'runsolver'
solver_binary = relative_path + r'PbO-CCSAT'

tmp_directory = relative_path + r'tmp/'
if not os.path.exists(tmp_directory):
    os.system(r'mkdir -p ' + tmp_directory)

instance_name = Path(args.instance).name
solver_name = Path(solver_binary).name
runsolver_watch_data_path = tmp_directory + solver_name + r'_' + instance_name + r'_' + get_time_pid_random_string() + r'.log'

command = runsolver_binary + r' -w ' + runsolver_watch_data_path + r' --cpu-limit ' + str(cutoff_time) + r' ' + solver_binary + r' -inst ' + args.instance + r' -seed ' + str(args.seed)
del args.instance
del args.cutoff_time
del args.seed
del args.specifics
del args.run_length
for k in args.__dict__:
    if args.__dict__[k] is not None:
        command += r' ' + str(k) + " " + str(args.__dict__[k])

output_list = os.popen(command).readlines()

Path(runsolver_watch_data_path).unlink()

status = r'CRASHED'
for line in output_list:
    line = line.strip()
    if (line == r's SATISFIABLE') or (line == r's UNSATISFIABLE'):
        status = r'SUCCESS'
        break
    elif line == r's UNKNOWN':
        status = r'TIMEOUT'
        break

if specifics == 'rawres':
    raw_result_path = Path(runsolver_watch_data_path.replace('.log', '.rawres'))

    with raw_result_path.open('w') as outfile:
        for line in output_list:
            outfile.write(line)

#print(r'Result for SMAC: ' + status + r', ' + str(run_time) + r', 0, 0, ' + str(seed))

outdir = {"status": status,
          "raw_output": output_list}
print(str(outdir))

