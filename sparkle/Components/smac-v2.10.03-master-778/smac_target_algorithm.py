#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import ast
import time
import random
import subprocess
from pathlib import Path

from sparkle.solver import Solver
from sparkle.tools.runsolver_parsing import get_runtime


if __name__ == "__main__":
    # Incoming call from SMAC:
    # 1. Translate input from SMAC to standardized form
    argsiter = iter(sys.argv[7:])
    args = zip(argsiter, argsiter)
    args = {arg.strip("-"): val for arg, val in args}
    # Args 1-6 conditions of the run, the rest are configurations for the solver
    # First argument is the solver directory
    solver_dir = Path(sys.argv[1])
    args["solver_dir"] = str(solver_dir)
    args["instance"] = sys.argv[2]
    args["specifics"] = sys.argv[3]
    args["cutoff_time"] = float(sys.argv[4])
    args["run_length"] = int(sys.argv[5])
    args["seed"] = int(sys.argv[6])
    cutoff_time = int(args["cutoff_time"])
    # 2. Build Run Solver call
    runsolver_binary = solver_dir / "runsolver"
    log_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    log_randstamp = int(random.getrandbits(32))
    runsolver_watch_data_path = Path(f"runsolver_{log_randstamp}_{log_timestamp}.log")
    runsolver_var_data_path = Path(f"runsolver_{log_randstamp}_{log_timestamp}.var")

    runsolver_call = [str(runsolver_binary),
                      "-w", str(runsolver_watch_data_path),
                      "-v", str(runsolver_var_data_path),
                      "--cpu-limit", str(cutoff_time),
                      str(solver_dir / Solver.wrapper),
                      '"' + str(args) + '"']
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

    try:
        if run_solver.stdout.decode() == "":
            # Runsolver cutoff solver wrapper, default values
            outdict = {"status": "TIMEOUT"}
        else:
            outdict = ast.literal_eval(run_solver.stdout.decode())
    except Exception as ex:
        print("ERROR: Could not decode Solver Wrapper output:\n"
              f"Return code: {run_solver.returncode}"
              f"stdout: {run_solver.stdout}\n "
              f"stderr: {run_solver.stderr}\n "
              f"Exception whilst decoding dictionary: {ex}")
        sys.exit(-1)

    # Overwrite the CPU runtime with runsolver log value
    # TODO: Runsolver also registers WALL time, add as a settings option in Sparkle
    runsolver_runtime, run_wtime = get_runtime(runsolver_var_data_path)
    if runsolver_runtime != -1.0:  # Valid value found
        run_time = runsolver_runtime
        runsolver_var_data_path.unlink(missing_ok=True)
    elif run_wtime != -1.0:
        run_time = run_wtime
        print("WARNING: CPU time not found in Runsolver log. "
              "Using Runsolver Wall Time instead.")
    else:
        print("WARNING: Was not able to deduce runtime from Runsolver. Using Python "
              f"timer instead for runtime. See {runsolver_var_data_path}")

    # 5. Return values to SMAC
    # We need to check how the "quality" in the output directory must be formatted
    quality = "0"
    if "quality" in outdict.keys():
        quality = outdict["quality"]
        if isinstance(quality, dict):
            # SMAC2 does not support multi-objective so always opt for the first value
            quality = quality[quality.keys()[0]]

    print("Result for SMAC: "
          f"{outdict['status']}, {run_time}, 0, {quality}, {args['seed']}")
