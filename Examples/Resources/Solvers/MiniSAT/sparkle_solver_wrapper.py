#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""MiniSAT Solver wrapper."""

import time
import sys
import subprocess
from pathlib import Path
from tools.slurm_parsing import parse_commandline_dict

# Convert the argument of the target_algorithm script to dictionary
args = parse_commandline_dict(sys.argv[1:])


# Extract and delete data that needs specific formatting
solver_dir = Path(args["solver_dir"])
instance = Path(args["instance"])
specifics = args["specifics"]
seed = args["seed"]
cpu_limit = args["cutoff_time"]

del args["solver_dir"]
del args["instance"]
del args["cutoff_time"]
del args["seed"]
del args["specifics"]
del args["run_length"]

solver_name = "minisat"
if solver_dir != Path("."):
    solver_exec = f"{solver_dir / solver_name}"
else:
    f"./{solver_name}"
# Set verbose to maximum for logging and set the random seed
solver_cmd = [solver_exec, "-verb=2", f"-rnd-seed={float(seed)}"]

# Construct call from args dictionary
"""Possible Parameters:
  CORE OPTIONS:
  -luby, -no-luby                         (default: on)
  -rnd-init, -no-rnd-init                 (default: off)

  -gc-frac      = <double> (   0 ..  inf) (default: 0.2)
  -rinc         = <double> (   1 ..  inf) (default: 2)
  -rnd-seed     = <double> (   0 ..  inf) (default: 9.16483e+07)
  -rnd-freq     = <double> [   0 ..    1] (default: 0)
  -cla-decay    = <double> (   0 ..    1) (default: 0.999)
  -var-decay    = <double> (   0 ..    1) (default: 0.95)

  -rfirst       = <int32>  [   1 .. imax] (default: 100)
  -ccmin-mode   = <int32>  [   0 ..    2] (default: 2)
  -phase-saving = <int32>  [   0 ..    2] (default: 2)
  -min-learnts  = <int32>  [   0 .. imax] (default: 0)

MAIN OPTIONS:

  -strict, -no-strict                     (default: off)
  -solve, -no-solve                       (default: on)
  -pre, -no-pre                           (default: on)

  -mem-lim      = <int32>  [   0 .. imax] (default: 0)
  -cpu-lim      = <int32>  [   0 .. imax] (default: 0)
  -verb         = <int32>  [   0 ..    2] (default: 1)

  -dimacs     = <string>

SIMP OPTIONS:
  -elim, -no-elim                         (default: on)
  -rcheck, -no-rcheck                     (default: off)
  -asymm, -no-asymm                       (default: off)

  -simp-gc-frac = <double> (   0 ..  inf) (default: 0.5)

  -grow         = <int32>  [imin .. imax] (default: 0)
  -sub-lim      = <int32>  [  -1 .. imax] (default: 1000)
  -cl-lim       = <int32>  [  -1 .. imax] (default: 20)"""

params = [f"-cpu-lim={cpu_limit}"] if "cpu-lim" not in args else []
for key in args:
    if args[key] is not None:
        params.append(f"-{key}={args[key]}")

# MiniSAT does not use an instance param, instead the filename is just at the end
params += [str(instance)]

try:
    solver_call = subprocess.run(solver_cmd + params,
                                 capture_output=True)
except Exception as ex:
    print(f"Solver call failed with exception:\n{ex}")

# Convert Solver output to dictionary for configurator target algorithm script
output_str = solver_call.stdout.decode()

status = r"CRASHED"
for line in output_str.splitlines():
    line = line.strip()
    if (line == r"SATISFIABLE") or (line == r"UNSATISFIABLE"):
        status = r"SUCCESS"
        break
    elif line == r"INDETERMINATE":
        status = r"TIMEOUT"
        break

if specifics == "rawres":
    tmp_directory = Path("tmp/")
    timestamp = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(time.time()))
    rawres_file_name = Path(f"{solver_name}_{instance.name}_{timestamp}.rawres_solver")
    if Path.cwd().name != tmp_directory.name:
        tmp_directory.mkdir(exist_ok=True)
        raw_result_path = tmp_directory / rawres_file_name
    else:
        raw_result_path = rawres_file_name
    raw_result_path.parent.mkdir(parents=True, exist_ok=True)
    with raw_result_path.open("w") as outfile:
        outfile.write(output_str)

outdir = {"status": status,
          "quality": 0,
          "solver_call": solver_cmd + params}

print(outdir)
