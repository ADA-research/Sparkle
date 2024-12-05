#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Sparkle SMAC wrapper VRP_heuristic_Jan_MkII_Sparkle
import sys
import subprocess
from pathlib import Path
from sparkle.tools.solver_wrapper_parsing import parse_solver_wrapper_args, \
    get_solver_call_params

# Parse the arguments of the solver wrapper
args_dict = parse_solver_wrapper_args(sys.argv[1:])

# Extract certain args from the above dict for use further below
solver_dir = args_dict["solver_dir"]
instance = args_dict["instance"]
seed = args_dict["seed"]
seed = args_dict["seed"]

# Construct the base solver call
solver_binary = "VRP_SISRs"
solver_exec = f"{solver_dir / solver_binary}" if solver_dir != Path(".") else "./" \
    + solver_binary
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

output_str = solver_call.stdout.decode()
print(output_str)  # Print original output so it can be verified
output_list = output_str.splitlines()

quality = 1000000000000
status = r'SUCCESS'  # always ok, code checks per iteration if cutoff time is exceeded

if len(output_list) > 0:
    quality = output_list[-1].strip()

outdir = {"status": status,
          "quality": quality,
          "solver_call": solver_cmd + params}

print(outdir)
