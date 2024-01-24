#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import time
import random
import sys
import ast
import subprocess
from pathlib import Path


def get_time_pid_random_string():
    my_time_str = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
    my_pid = os.getpid()
    my_pid_str = str(my_pid)
    my_random = random.randint(1, sys.maxsize)
    my_random_str = str(my_random)
    my_time_pid_random_str = my_time_str + '_' + my_pid_str + '_' + my_random_str
    return my_time_pid_random_str

# Convert the argument of the target_algorithm script to dictionary
args = ast.literal_eval(sys.argv[1])

# Extract and delete data that needs specific formatting
instance = args["instance"]
specifics = args["specifics"]
cutoff_time = int(args["cutoff_time"])+1
# run_length = args["run_length"]
seed = args["seed"]

del args["instance"]
del args["cutoff_time"]
del args["seed"]
del args["specifics"]
del args["run_length"]

runsolver_binary = "./runsolver"
solver_binary = "./PbO-CCSAT"

tmp_directory = Path("tmp/")
tmp_directory.mkdir(exist_ok=True)
#if not os.path.exists(tmp_directory):
#    os.system(r'mkdir -p ' + tmp_directory)

instance_name = Path(instance).name
solver_name = Path(solver_binary).name
runsolver_watch_data_path = tmp_directory / (solver_name + "_" + instance_name + "_" + get_time_pid_random_string() + ".log")

runsolver_call = [runsolver_binary,
                  "-w", str(runsolver_watch_data_path),
                  "--cpu-limit", str(cutoff_time),
                  solver_binary,
                  "-inst", instance,
                  "-seed", str(seed)]

params = []
for key in args:
    if args[key] is not None:
        params.extend(["-" + str(key), str(args[key])])

solver_call = subprocess.run(runsolver_call + params,
                             capture_output=True)

output_list = solver_call.stdout.decode().splitlines()

Path(runsolver_watch_data_path).unlink(missing_ok=True)

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

outdir = {"status": status,
          "solver_call": runsolver_call + params,
          "raw_output": output_list}

print(outdir)
