#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
import ast
import subprocess
from pathlib import Path
from sparkle.types import SolverStatus
from sparkle.tools.general import get_time_pid_random_string


# Convert the argument of the target_algorithm script to dictionary
args = ast.literal_eval(sys.argv[1])

# Extract and delete data that needs specific formatting
instance = args["instance"]
cutoff_time = int(args["cutoff_time"]) + 1
seed = args["seed"]

del args["instance"]
del args["cutoff_time"]
del args["seed"]

runsolver_binary = "./runsolver"
solver_binary = "./PbO-CCSAT"

tmp_directory = Path("tmp/")
tmp_directory.mkdir(exist_ok=True)

instance_name = Path(instance).name
solver_name = Path(solver_binary).name
runsolver_watch_data_path = tmp_directory / (solver_name + "_" + instance_name + "_"
                                             + get_time_pid_random_string() + ".log")

runsolver_call = [runsolver_binary,
                  "-w", str(runsolver_watch_data_path),
                  "--cpu-limit", str(cutoff_time),
                  solver_binary,
                  "-inst", instance,
                  "-seed", str(seed)]

params = []
for key in args:
    if args[key] is not None:
        params.extend(["-" + str(key), str(args[key])])

solver_call = subprocess.run(runsolver_call + params,
                             capture_output=True)

output_list = solver_call.stdout.decode().splitlines()

Path(runsolver_watch_data_path).unlink(missing_ok=True)

status = SolverStatus.CRASHED
for line in output_list:
    line = line.strip()
    if (line == r's SATISFIABLE') or (line == r's UNSATISFIABLE'):
        status = SolverStatus.SUCCESS
        break
    elif line == r's UNKNOWN':
        status = SolverStatus.TIMEOUT
        break

outdir = {"status": status.value,
          "solver_call": runsolver_call + params,
          "raw_output": output_list}

print(outdir)
