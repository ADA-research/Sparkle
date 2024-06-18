#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#Sparkle SMAC wrapper VRP_heuristic_Jan_MkII_Sparkle

import time
import sys
import subprocess
from pathlib import Path
from tools.slurm_parsing import parse_commandline_dict

# Convert the argument of the target_algorithm script to dictionary
args = parse_commandline_dict(sys.argv[1:])

# Extract and delete data that needs specific formatting
solver_dir = Path(args["solver_dir"])
instance = args["instance"]
specifics = args["specifics"]
cutoff_time = int(args["cutoff_time"])+1
# run_length = args["run_length"]
seed = args["seed"]

del args["solver_dir"]
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
solver_exec = f"{solver_dir / solver_binary}" if solver_dir != Path(".") else "./" + solver_binary
solver_cmd = [solver_exec,
              "-inst", str(instance),
              "-seed", str(seed)]

instance_name = Path(instance).name
solver_name = Path(solver_binary).name

solver_call = subprocess.run(solver_cmd + params,
                             capture_output=True)

output_str = solver_call.stdout.decode()
output_list = output_str.splitlines()

quality=1000000000000
status = r'SUCCESS'#always ok, code checks per iteration whether cutoff time is exceeded

if len(output_list) > 0:
    quality = output_list[-1].strip()

if specifics == 'rawres':
    tmp_directory = Path("tmp/")
    time_stamp = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
    rawres_file_name = Path(f"{solver_name}_{instance_name}_{time_stamp}.rawres_solver")
    if Path.cwd().name != tmp_directory.name:
        tmp_directory.mkdir(exist_ok=True)
        raw_result_path = tmp_directory / rawres_file_name
    else:
        raw_result_path = rawres_file_name
    raw_result_path.parent.mkdir(parents=True, exist_ok=True)
    with raw_result_path.open('w') as outfile:
        outfile.write(str(solver_cmd + params) + "\n" + output_str)

outdir = {"status": status,
		  "quality": quality,
          "solver_call": solver_cmd + params}

print(outdir)
