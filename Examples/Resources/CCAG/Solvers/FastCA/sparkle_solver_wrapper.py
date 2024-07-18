#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""FastCA Solver wrapper."""

import time
import sys
import subprocess
from pathlib import Path
from sparkle.tools.slurm_parsing import parse_commandline_dict

# Convert the arguments to a dictionary
args = parse_commandline_dict(sys.argv[1:])

# Extract and delete data that needs specific formatting
solver_dir = Path(args["solver_dir"])
# We deal with multi-file instances, but only use the .model files
instance = ""
for instance_file in args["instance"]:
    if Path(instance_file).suffix == ".model":
        instance = Path(instance_file)
        break
specifics = args["specifics"]
seed = args["seed"]

del args["solver_dir"]
del args["instance"]
del args["cutoff_time"]
del args["seed"]
del args["specifics"]
del args["run_length"]

solver_name = "FastCA"
if solver_dir != Path("."):
    solver_exec = f"{solver_dir / solver_name}"
else:
    f"./{solver_name}"
solver_cmd = [solver_exec,
              "-inst", str(instance),
              "-seed", str(seed)]

# Construct call from args dictionary
params = []
for key in args:
    if args[key] is not None:
        params.extend(["-" + str(key), str(args[key])])

try:
    solver_call = subprocess.run(solver_cmd + params,
                                 capture_output=True)
except Exception as ex:
    print(f"Solver call failed with exception:\n{ex}")

# Convert Solver output to dictionary for configurator target algorithm script
output_str = solver_call.stdout.decode()

solution_quality = sys.maxsize
status = 'CRASHED'

for line in output_str.splitlines():
    words = line.strip().split()
    if len(words) <= 0:
        continue
    if status != "SUCCESS" and len(words) == 18 and words[1] == 'We' and words[2] == 'recommend':
        # First output line is normal, probably no crash
        # If no actual solution is found, we probably reach the cutoff time before finding a solution
        status = 'TIMEOUT'
    words[1].replace('.','',1).isdigit()
    if len(words) == 4 and words[1].replace('.','',1).isdigit() and words[2].replace('.','',1).isdigit() and words[3].replace('.','',1).isdigit():
        temp_solution_quality = int(words[2])
        if temp_solution_quality < solution_quality:
            solution_quality = temp_solution_quality
            status = 'SUCCESS'

if specifics == "rawres":
    tmp_directory = Path("tmp/")
    timestamp = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(time.time()))
    rawres_file_name = Path(f"{solver_name}_{instance.name}_{timestamp}.rawres_solver")
    if tmp_directory not in Path.cwd():
        tmp_directory.mkdir(exist_ok=True)
        raw_result_path = tmp_directory / rawres_file_name
    else:
        raw_result_path = rawres_file_name
    with raw_result_path.open("w") as outfile:
        outfile.write(output_str)

outdir = {"status": status,
          "quality": solution_quality,
          "solver_call": solver_cmd + params}

print(outdir)
