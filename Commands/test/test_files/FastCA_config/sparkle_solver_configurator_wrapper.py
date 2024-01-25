#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Sparkle Configurator wrapper for the FastCA algorithm."""

import os
import time
import random
import sys
import ast
import subprocess
from pathlib import Path


def get_time_pid_random_string() -> str:
    """Return a combination of time, PID, and random str."""
    my_time_str = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(time.time()))
    my_pid = os.getpid()
    my_pid_str = str(my_pid)
    my_random = random.randint(1, sys.maxsize)
    my_random_str = str(my_random)
    my_time_pid_random_str = my_time_str + "_" + my_pid_str + "_" + my_random_str
    return my_time_pid_random_str


def _is_a_number(input_str: str) -> bool:
    """Check if an input string is a number (float or int)."""
    try:
        # eval insecure, so use ast.literal_eval instead
        input_val = ast.literal_eval(input_str)
        if (type(input_val) == float) or (type(input_val) == int):
            return True
        else:
            return False
    except Exception:
        return False


def parse_output(output_list: list[str]) -> (str, float):
    """Parse problem specific output and return it."""
    # Read solution quality from output_list
    solution_quality = sys.maxsize
    status = "UNKNOWN"
    lines = output_list

    for line in lines:
        words = line.strip().split()
        if len(words) <= 0:
            continue
        if len(words) == 17 and words[0] == "We" and words[1] == "recommend":
            # First output line is normal, probably no crash
            solution_quality = sys.maxsize - 1
            # If no actual solution is found, we probably reach the cutoff time before
            # finding a solution
            status = "TIMEOUT"
        if (len(words) == 3 and _is_a_number(words[0]) and _is_a_number(words[1])
           and _is_a_number(words[2])):
            temp_solution_quality = int(words[1])
            if temp_solution_quality < solution_quality:
                solution_quality = temp_solution_quality
                status = "SUCCESS"

    if solution_quality == sys.maxsize:
        status = "CRASHED"

    return status, solution_quality


# Convert the argument of the target_algorithm script to dictionary
args = ast.literal_eval(sys.argv[1])

# Extract and delete data that needs specific formatting
instance = args["instance"]
specifics = args["specifics"]
cutoff_time = int(args["cutoff_time"]) + 1
# run_length = args["run_length"]
seed = args["seed"]

del args["instance"]
del args["cutoff_time"]
del args["seed"]
del args["specifics"]
del args["run_length"]

inst_list = instance.split()
inst_model = inst_list[0]
inst_constr = inst_list[1]

runsolver_binary = "./runsolver"
solver_binary = "./FastCA"

tmp_directory = Path("tmp/")
tmp_directory.mkdir(exist_ok=True)

instance_model_name = Path(inst_model).name
instance_constr_name = Path(inst_constr).name
solver_name = Path(solver_binary).name
runsolver_watch_data_path = (f"{tmp_directory}{solver_name}_{instance_model_name}_"
                             f"{get_time_pid_random_string()}.log")

command = (f"{runsolver_binary} -w {runsolver_watch_data_path} --cpu-limit "
           f"{str(cutoff_time)} {solver_binary} {inst_model} {inst_constr} "
           f"{str(cutoff_time)}")

runsolver_call = [runsolver_binary,
                  "-w", str(runsolver_watch_data_path),
                  "--cpu-limit", str(cutoff_time),
                  solver_binary,
                  "-inst", inst_model, inst_constr,
                  str(cutoff_time)]

params = []
for key in args:
    if args[key] is not None:
        params.extend(["-" + str(key), str(args[key])])

solver_call = subprocess.run(runsolver_call + params,
                             capture_output=True)

output_list = solver_call.stdout.decode().splitlines()

Path(runsolver_watch_data_path).unlink(missing_ok=True)

status, quality = parse_output(output_list)

outdir = {"status": status,
          "quality": 0,
          "solver_call": runsolver_call + params,
          "raw_output": output_list}

print(outdir)
