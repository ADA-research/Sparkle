#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import time
import sys
import subprocess
from pathlib import Path
from sparkle.types import SolverStatus
from sparkle.tools.solver_wrapper_parsing import *


# Parse the arguments of the solver wrapper
args_dict = parse_solver_wrapper_args(sys.argv[1:])

# Extract certain args from the above dict for use further below
solver_dir = args_dict["solver_dir"]
instance = args_dict["instance"]
seed = args_dict["seed"]
specifics = args_dict["specifics"]

# Construct the base solver call
solver_name = "PbO-CCSAT"
solver_exec = f"{solver_dir / solver_name}" if solver_dir != Path(".") else "./" + \
    solver_name
solver_cmd = [solver_exec,
              "-inst", str(instance),
              "-seed", str(seed)]

# Get further params for the solver call
params = get_solver_call_params(args_dict)

# Execute the solver call
try:
    solver_call = subprocess.run(solver_cmd + params,
                                 capture_output=True)
except Exception as ex:
    print(f"Solver call failed with exception:\n{ex}")

# Convert Solver output to dictionary for configurator target algorithm script
output_str = solver_call.stdout.decode()

status = SolverStatus.CRASHED
for line in output_str.splitlines():
    line = line.strip()
    if (line == r's SATISFIABLE') or (line == r's UNSATISFIABLE'):
        status = SolverStatus.SUCCESS
        break
    elif line == r's UNKNOWN':
        status = SolverStatus.TIMEOUT
        break

if specifics == 'rawres':
    tmp_directory = Path("tmp/")
    cur_time_str = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
    rawres_file_name = Path(f"{solver_name}_{instance.name}_" + cur_time_str
                            + ".rawres_solver")
    if Path.cwd().name != tmp_directory.name:
        tmp_directory.mkdir(exist_ok=True)
        raw_result_path = tmp_directory / rawres_file_name
    else:
        raw_result_path = rawres_file_name
    raw_result_path.parent.mkdir(parents=True, exist_ok=True)
    with raw_result_path.open('w') as outfile:
        outfile.write(str(solver_cmd + params) + "\n" + output_str)

outdir = {"status": status.value,
          "quality": 0,
          "solver_call": solver_cmd + params}

print(outdir)
