#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import time
import sys
import ast
import subprocess
from pathlib import Path

# Convert the argument of the target_algorithm script to dictionairy
# Join the argv to ensure we can work with broken up arguments
args = ast.literal_eval(" ".join(sys.argv[1:]))

# Extract and delete data that needs specific formatting
solver_dir = Path(args["solver_dir"])
instance = Path(args["instance"])
specifics = args["specifics"]
seed = args["seed"]

del args["solver_dir"]
del args["instance"]
del args["cutoff_time"]
del args["seed"]
del args["specifics"]
del args["run_length"]

solver_name = "PbO-CCSAT"
solver_exec = f"{solver_dir / solver_name}" if solver_dir != Path(".") else "./" + solver_name
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

status = r'CRASHED'
for line in output_str.splitlines():
    line = line.strip()
    if (line == r's SATISFIABLE') or (line == r's UNSATISFIABLE'):
        status = r'SUCCESS'
        break
    elif line == r's UNKNOWN':
        status = r'TIMEOUT'
        break

if specifics == 'rawres':
    tmp_directory = Path("tmp/")
    rawres_file_name = Path(f"{solver_name}_{instance.name}_"\
                       f"{time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))}.rawres")
    if Path.cwd().name != tmp_directory.name:
        tmp_directory.mkdir(exist_ok=True)
        raw_result_path = tmp_directory / rawres_file_name
    else:
        raw_result_path = rawres_file_name
    with raw_result_path.open('w') as outfile:
        outfile.write(output_str)

outdir = {"status": status,
          "quality": 0,
          "solver_call": solver_cmd + params}

print(outdir)
