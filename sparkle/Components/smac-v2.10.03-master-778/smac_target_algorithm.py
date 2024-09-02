#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
import time
from pathlib import Path

from runrunner import Runner

from sparkle.solver import Solver
from sparkle.types.objective import SparkleObjective, PerformanceMeasure


if __name__ == "__main__":
    # Incoming call from SMAC:
    # Translate input to Solver object input
    argsiter = iter(sys.argv[8:])
    args = zip(argsiter, argsiter)
    configuration = {arg.strip("-"): val for arg, val in args}
    # Args 1-7 conditions of the run, the rest are configurations for the solver
    # [Solver_dir, SparkleObjective, instance, specifics, cutoff_time, runlength, seed]
    solver_dir = Path(sys.argv[1])
    objectives = SparkleObjective.from_multi_str(sys.argv[2])
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
                        objectives=objectives,
                        seed=seed,
                        cutoff_time=cutoff_time,
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
        elif isinstance(quality, list):
            quality = quality[0]
        if not isinstance(quality, int) and not isinstance(quality, float):
            if not quality.replace("-", "").replace(".", "").isdigit():
                # Not a number
                quality = "0"
    # SMAC2 does not do maximisation, auto-convert
    if (objectives[0].PerformanceMeasure
            == PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION):
        quality = -1 * float(quality)
    print("Result for SMAC: "
          f"{output['status']}, {output['runtime']}, 0, {quality}, {seed}")
