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
instance = Path(args["instance"])
specifics = args["specifics"]
seed = args["seed"]

del args["instance"]
del args["cutoff_time"]
del args["seed"]
del args["specifics"]
del args["run_length"]

solver_name = "PbO-CCSAT"

tmp_directory = Path("tmp/")
tmp_directory.mkdir(exist_ok=True)

rawres_file = tmp_directory / (solver_name + "_" + instance.name + "_" + get_time_pid_random_string() + ".rawres")

solver_cmd = ["./" + solver_name,
              "-inst", instance,
              "-seed", str(seed)]

# Construct call from args dictionary
params = []
for key in args:
    if args[key] is not None:
        params.extend(["-" + str(key), str(args[key])])

solver_call = subprocess.run(solver_cmd + params,
                             capture_output=True)

# Convert Solver output to dictionary for configurator target algorithm script
output_list = solver_call.stdout.decode().splitlines()

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
    raw_result_path = Path(rawres_file)
    with raw_result_path.open('w') as outfile:
        for line in output_list:
            outfile.write(line)

outdir = {"status": status,
          "quality": 0,
          "solver_call": solver_cmd + params,
          "raw_output": output_list}

print(outdir)
