#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""TCA Solver wrapper."""
import sys
import subprocess
from pathlib import Path
from sparkle.types import SolverStatus
from sparkle.tools.solver_wrapper_parsing import parse_solver_wrapper_args, \
    get_solver_call_params


# Parse the arguments of the solver wrapper
args_dict = parse_solver_wrapper_args(sys.argv[1:])

# Extract certain args from the above dict for use further below
solver_dir = Path(args_dict["solver_dir"])
seed = args_dict["seed"]

cutoff_time = args_dict["cutoff_time"]

# TODO Why is the constraint file not used?
# We deal with multi-file instances, but only use the .model files
instance_names = args_dict["instance"]
instance = next((inst for inst in instance_names if ".model" in inst), None)

# Construct the base solver call
solver_name = "TCA"
if solver_dir != Path("."):
    solver_exec = f"{solver_dir / solver_name}"
else:
    f"./{solver_name}"
solver_cmd = [solver_exec,
              str(instance),
              str(cutoff_time - 3),
              str(seed)]

# Get further params for the solver call
params = get_solver_call_params(args_dict)

try:
    solver_call = subprocess.run(solver_cmd + params,
                                 capture_output=True)
except Exception as ex:
    print(f"Solver call failed with exception:\n{ex}")

# Convert Solver output to dictionary for configurator target algorithm script
output_str = solver_call.stdout.decode()
print(output_str)  # Print original output so it can be verified

solution_quality = sys.maxsize
status = SolverStatus.CRASHED

for line in output_str.splitlines():
    words = line.strip().split()
    if len(words) <= 0:
        continue
    if status != SolverStatus.SUCCESS and len(words) == 18 and words[1] == 'We' and \
       words[2] == 'recommend':
        # First output line is normal, probably no crash
        # If no actual solution is found, we probably reach the cutoff time before
        # finding a solution
        status = SolverStatus.TIMEOUT
    # Make sure words consists of [time, array_size, step]
    if len(words) == 3 and words[0].replace('.', '', 1).isdigit() and words[1]\
       .replace('.', '', 1).isdigit() and words[2].replace('.', '', 1).isdigit():
        temp_solution_quality = int(words[1])
        if temp_solution_quality < solution_quality:
            solution_quality = temp_solution_quality
            status = SolverStatus.SUCCESS

outdir = {"status": status.value,
          "quality": solution_quality,
          "solver_call": solver_cmd + params}

print(outdir)
