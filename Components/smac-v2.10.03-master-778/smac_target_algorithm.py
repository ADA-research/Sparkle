#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import ast
import time
import subprocess
from pathlib import Path

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_run_solvers_help as srsh


if __name__ == "__main__":
    # Incoming call from SMAC:
    # 1. Translate input from SMAC to standardized form
    argsiter = iter(sys.argv[6:])
    args = zip(argsiter, argsiter)
    args = {arg.strip("-"): val for arg, val in args}
    # Args 1-5 conditions of the run, the rest are configurations for the solver
    args["instance"] = sys.argv[1]
    args["specifics"] = sys.argv[2]
    args["cutoff_time"] = float(sys.argv[3])
    args["run_length"] = int(sys.argv[4])
    args["seed"] = int(sys.argv[5])
    cutoff_time = int(args["cutoff_time"])+1

    # 2. Build Run Solver call
    runsolver_binary = "./runsolver"
    log_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
    runsolver_watch_data_path = f"{str(Path.cwd())}_"\
                                f"{log_timestamp}.log"

    runsolver_call = [runsolver_binary,
                      "-w", str(runsolver_watch_data_path),
                      "--cpu-limit", str(cutoff_time),
                      str(Path.cwd() / sgh.sparkle_solver_wrapper),
                      str(args)]

    # 3. Call Runsolver with the solver configurator wrapper and its arguments
    start_t = time.time()
    run_solver = subprocess.run(runsolver_call,
                                capture_output=True)
    run_time = min(time.time() - start_t, cutoff_time)

    # 4. Decode solver output and return required values to SMAC.
    # Solver output can be found in the regular subprocess.stdout
    if run_solver.returncode != 0:
        # Failure from run solver or solver wrapper
        print("WARNING: Subprocess for Solver Wrapper crashed with code "
              f"{run_solver.returncode}:\n {run_solver.stderr}")
        print(f"Result for SMAC: CRASHED, {run_time}, 0, 0, {args['seed']}")
        sys.exit()
        
    outdict = ast.literal_eval(run_solver.stdout.decode())

    # Overwrite the CPU runtime with runsolver log value
    # TODO: Runsolver also registers WALL time, add as a settings option in Sparkle
    runtime, wtime =  srsh.get_runtime_from_runsolver(runsolver_watch_data_path)
    Path(runsolver_watch_data_path).unlink(missing_ok=True)

    # 5. Return values to SMAC
    # We need to check how the "quality" in the output directory must be formatted
    quality = '\0'
    if "quality" in outdict.keys():
        quality = outdict["quality"]
        if isinstance(quality, dict):
            #SMAC2 does not support multi-objective so always opt for the first objective
            objective = sgh.settings.get_general_sparkle_objectives()[0]
            quality = quality[objective.metric]
        
    print(f"Result for SMAC: {outdict['status']}, {run_time}, 0, {quality}, {args['seed']}")
