#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""MiniSAT Solver wrapper."""
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

# Get further params for the solver call
params = get_solver_call_params(args_dict)

# MiniSAT does not use an instance param, instead the filename is just at the end
params += [str(instance)]

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
    if (line == r"SATISFIABLE") or (line == r"UNSATISFIABLE"):
        status = SolverStatus.SUCCESS
        break
    elif line == r"INDETERMINATE":
        status = SolverStatus.TIMEOUT
        break

outdir = {"status": status.value,
          "quality": 0,
          "solver_call": solver_cmd + params}

print(outdir)
