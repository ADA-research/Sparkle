#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
import time
from pathlib import Path

from runrunner import Runner

from sparkle.solver import Solver


if __name__ == "__main__":
    # Incoming call from SMAC:
    # Translate input to Solver object input
    argsiter = iter(sys.argv[7:])
    args = zip(argsiter, argsiter)
    configuration = {arg.strip("-"): val for arg, val in args}
    # Args 1-6 conditions of the run, the rest are configurations for the solver
    # [Solver_dir, instance, specifics, cutoff_time, runlength, seed]
    solver_dir = Path(sys.argv[1])
    instance = sys.argv[2]
    cutoff_time = float(sys.argv[4])
    seed = int(sys.argv[6])

    runsolver_binary = solver_dir / "runsolver"
    solver = Solver(solver_dir,
                    raw_output_directory=Path(),
                    runsolver_exec=runsolver_binary)
    # Call Runsolver with the solver configurator wrapper and its arguments
    start_t = time.time()
    output = solver.run(instance=instance,
                        seed=seed,
                        cutoff_time=float(sys.argv[4]),
                        configuration=configuration,
                        run_on=Runner.LOCAL)
    run_time = min(time.time() - start_t, cutoff_time)

    # Return values to SMAC
    # SMAC2 does not accept nan values etc for quality
    quality = "0"
    if "quality" in output.keys():
        quality = output["quality"]
        if isinstance(quality, dict):
            # SMAC2 does not support multi-objective so always opt for the first value
            quality = quality[quality.keys()[0]]
        if not isinstance(quality, int) and not isinstance(quality, float):
            if not quality.replace("-", "").replace(".", "").isdigit():
                # Not a number
                quality = "0"
    print("Result for SMAC: "
          f"{output['status']}, {output['runtime']}, 0, {quality}, {seed}")
