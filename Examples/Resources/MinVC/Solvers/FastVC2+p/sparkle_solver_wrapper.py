#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""FastVC2+p solver wrapper."""
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
cutoff = args["cutoff_time"]

del args["solver_dir"]
del args["instance"]
del args["cutoff_time"]
del args["seed"]

solver_name = "fastvc2+p"
if solver_dir != Path("."):
    solver_exec = f"{solver_dir / solver_name}"
else:
    f"./{solver_name}"

# NOTE: This algorithm requires the cutoff time, but to ensure consistent runtime
# measurements by Sparkle we multiply it by 10 to make sure the algorithm does not
# stop early, but is stopped by Sparkle (runsolver) consistenty with other solvers

# NOTE: Unused optional arguments:
# -opt <optimal_size>
# -cand_count <cand_count>
solver_cmd = [solver_exec,
              "-inst", str(instance),
              "-seed", str(seed),
              "-cutoff_time", str(cutoff * 10)]

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

status = SolverStatus.UNKNOWN
solution_quality = sys.maxsize
for line in output_str.splitlines():
    words = line.strip().split()
    if len(words) <= 0:
        continue
    if len(words) >= 4 and words[1] == 'c' and words[2] == 'Arguments' and \
            words[3] == 'Error!':
        status = SolverStatus.CRASHED
        break
    if len(words) >= 4 and words[1] == 'c' and words[2] == 'vertex_cover:':
        temp_solution_quality = int(words[3])
        if solution_quality < 0 or temp_solution_quality < solution_quality:
            solution_quality = temp_solution_quality
            status = SolverStatus.SUCCESS

outdir = {"status": status.value,
          "quality": solution_quality,
          "solver_call": solver_cmd + params}

print(outdir)
