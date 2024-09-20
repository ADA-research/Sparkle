#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
import time
from pathlib import Path

from runrunner import Runner

from sparkle.solver import Solver
from sparkle.types import resolve_objective


if __name__ == "__main__":
    # Incoming call from SMAC:
    # Translate input to Solver object input
    argsiter = iter(sys.argv[8:])
    args = zip(argsiter, argsiter)
    configuration = {arg.strip("-"): val for arg, val in args}
    # Args 1-7 conditions of the run, the rest are configurations for the solver
    # [Solver_dir, SparkleObjective, instance, specifics, cutoff_time, runlength, seed]
    solver_dir = Path(sys.argv[1])
    objective = resolve_objective(sys.argv[2])
    instance = sys.argv[3]
    cutoff_time = float(sys.argv[5])
    seed = int(sys.argv[7])

    runsolver_binary = solver_dir / "runsolver"
    solver = Solver(solver_dir,
                    raw_output_directory=Path(),
                    runsolver_exec=runsolver_binary)
    # Call Runsolver with the solver configurator wrapper and its arguments
    start_t = time.time()
    output = solver.run(instance=instance,
                        objectives=[objective],
                        seed=seed,
                        cutoff_time=cutoff_time,
                        configuration=configuration,
                        run_on=Runner.LOCAL)
    run_time = min(time.time() - start_t, cutoff_time)

    # Return values to SMAC
    # SMAC2 does not accept nan values etc for quality
    quality = "0"
    if not objective.time and objective.name in output.keys():
        quality = float(output[objective.name])
        if not objective.minimise:
            quality = -1 * quality
    print("Result for SMAC: "
          f"{output['status']}, {output['cpu_time']}, 0, {quality}, {seed}")
