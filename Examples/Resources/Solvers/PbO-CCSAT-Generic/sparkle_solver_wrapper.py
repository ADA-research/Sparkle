#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
import subprocess
from pathlib import Path
from sparkle.types import SolverStatus
from sparkle.tools.solver_wrapper_parsing import parse_solver_wrapper_args, \
    get_solver_call_params


# Parse the arguments of the solver wrapper
args_dict = parse_solver_wrapper_args(sys.argv[1:])

# Extract certain args from the above dict for use further below
solver_dir = args_dict["solver_dir"]
instance = args_dict["instance"]
seed = args_dict["seed"]

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
print(output_str)  # Print original output so it can be verified

status = SolverStatus.CRASHED
for line in output_str.splitlines():
    line = line.strip()
    if (line == r's SATISFIABLE') or (line == r's UNSATISFIABLE'):
        status = SolverStatus.SUCCESS
        break
    elif line == r's UNKNOWN':
        status = SolverStatus.TIMEOUT
        break

outdir = {"status": status.value,
          "quality": 0,
          "solver_call": solver_cmd + params}

print(outdir)
