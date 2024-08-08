#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
import subprocess
from pathlib import Path
from sparkle.types import SolverStatus
from sparkle.tools.slurm_parsing import parse_commandline_dict

# Convert the argument of the target_algorithm script to dictionary
args = parse_commandline_dict(sys.argv[1:])

# Extract and delete data that needs specific formatting
solver_dir = Path(args["solver_dir"])
instance = Path(args["instance"])
seed = int(args["seed"])

del args["solver_dir"]
del args["instance"]
del args["cutoff_time"]
del args["seed"]

solver_name = "PbO-CCSAT"
solver_exec = f"{solver_dir / solver_name}" if solver_dir != Path(".") else "./" + \
    solver_name
solver_cmd = [solver_exec,
              "-inst", str(instance),
              "-seed", str(seed)]

# Construct call from args dictionary
params = []
if "config_path" in args:
    # The arguments were not directly given and must be parsed from a file
    config_str = Path(args["config_path"]).open("r").readlines()[seed]
    # Extract the args without any quotes
    config_split = [arg.strip().replace("'", "").replace('"', "").strip("-")
                    for arg in config_str.split(" -") if arg.strip() != ""]
    for arg in config_split:
        varname, value = arg.strip("'").strip('"').split(" ", maxsplit=1)
        params.extend([f"-{varname}", value])
else:
    # Construct from dictionary arguments
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
