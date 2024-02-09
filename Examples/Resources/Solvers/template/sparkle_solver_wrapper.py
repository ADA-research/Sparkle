#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Sparkle Configurator wrapper template."""

import random
import sys
import ast
import subprocess
from pathlib import Path

# TODO: Add imports required by your changes

# Process arguments given by "*_target_algorithm.py"
args = ast.literal_eval(sys.argv[1])

# Extract and delete data that needs specific formatting
instance = args["instance"]
specifics = args["specifics"]
cutoff_time = int(args["cutoff_time"]) + 1
run_length = args["run_length"]
seed = args["seed"]

del args["instance"]
del args["cutoff_time"]
del args["seed"]
del args["specifics"]
del args["run_length"]

runsolver_binary = "./runsolver"
# TODO: Change solver name
solver_binary = "./SOME_SOLVER_NAME"

tmp_directory = Path("tmp/")
tmp_directory.mkdir(exist_ok=True)

instance_name = Path(instance).name
solver_name = Path(solver_binary).name
# Create a unique name for your runsolver log file, for example:
runsolver_watch_data_path = tmp_directory \
    / f"{solver_name}_{instance_name}_{random.randint()}.log"

# Process parameters
# TODO: Make sure parameters are processed correctly for your solver
params = []
for key in args:
    if args[key] is not None:
        params.extend(["-" + str(key), str(args[key])])
# TODO: Change call to solver (Solver_binary)
runsolver_call = [runsolver_binary,
                  "-w", str(runsolver_watch_data_path),
                  "--cpu-limit", str(cutoff_time),
                  solver_binary,
                  "-inst", instance,
                  "-seed", str(seed)]

# Execute and process output
solver_call = subprocess.run(runsolver_call + params,
                             capture_output=True)

output_list = solver_call.stdout.decode().splitlines()

# Cleanup
Path(runsolver_watch_data_path).unlink(missing_ok=True)
# TODO: Any problem specific cleanup

# Process run status
# TODO: Change checks for status for your specific problem output
status = "CRASHED"
run_length = 0
quality = 0
for line in output_list:
    line = line.strip()
    if (line == "s SATISFIABLE") or (line == "s UNSATISFIABLE"):
        status = "SUCCESS"
        break
    elif line == "s UNKNOWN":
        status = "TIMEOUT"
        break

# Output results in the format target_algorithm requires
outdir = {"status": status,
          "quality": 0,
          "solver_call": runsolver_call + params,
          "raw_output": output_list}

# Write raw solver output to file for Sparkle when calling run_configured_solver.py
if specifics == "rawres":
    raw_result_path = Path(runsolver_watch_data_path.replace(".log", ".rawres"))

    with raw_result_path.open("w") as outfile:
        for line in output_list:
            outfile.write(line)

print(outdir)