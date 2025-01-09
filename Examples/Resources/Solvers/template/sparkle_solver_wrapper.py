#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Template for users to create Solver wrappers."""
import sys
import subprocess
from pathlib import Path
from sparkle.types import SolverStatus
from sparkle.tools.solver_wrapper_parsing import parse_solver_wrapper_args

# Convert the arguments to a dictionary
args = parse_solver_wrapper_args(sys.argv[1:])

# Extract and delete data that needs specific formatting
solver_dir = Path(args["solver_dir"])
instance = Path(args["instance"])
seed = args["seed"]

del args["solver_dir"]
del args["instance"]
del args["cutoff_time"]
del args["seed"]

solver_name = "EXAMPLE_SOLVER"
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
# Optional: Print original output so the solution can be verified by SATVerifier
print(output_str)

status = SolverStatus.CRASHED
for line in output_str.splitlines():
    line = line.strip()
    if (line == r"s SATISFIABLE") or (line == r"s UNSATISFIABLE"):
        status = SolverStatus.SUCCESS
        break
    elif line == r"s UNKNOWN":
        status = SolverStatus.TIMEOUT
        break

outdir = {"status": status.value,
          "quality": 0,
          "solver_call": solver_cmd + params}

print(outdir)
