#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#Sparkle SMAC wrapper VRP_heuristic_Jan_MkII_Sparkle

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


# Construct call from args dictionary
params = []
for key in args:
    if args[key] is not None:
        params.extend(["-" + str(key), str(args[key])])

solver_binary = "VRP_SISRs"
solver_cmd = ["./" + solver_binary,
              "-inst", str(instance),
              "-seed", str(seed)]



instance_name = Path(instance).name
solver_name = Path(solver_binary).name

solver_call = subprocess.run(solver_cmd + params,
                             capture_output=True)

output_list = solver_call.stdout.decode().splitlines()

quality=1000000000000
status = r'SUCCESS'#always ok, code checks per iteration whether cutoff time is exceeded

if len(output_list) > 0:
    quality = output_list[-1].strip()

"""if specifics == 'rawres':
	raw_result_path = Path(runsolver_watch_data_path.replace('.log', '.rawres'))

	with raw_result_path.open('w') as outfile:
		for line in output_list:
			outfile.write(line)"""

outdir = {"status": status,
		  "quality": quality,
          "solver_call": solver_cmd + params}

print(outdir)
