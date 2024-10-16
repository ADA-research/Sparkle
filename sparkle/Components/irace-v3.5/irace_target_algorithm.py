#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Handles IRACE calls passing to sparkle solver wrappers."""
import sys
from pathlib import Path

from runrunner import Runner

from sparkle.solver import Solver
from sparkle.types import resolve_objective


if __name__ == "__main__":
    # Incoming call from IRACE:
    # Translate input to Solver object input
    solver_dir = Path(sys.argv[1])  # First argument is the path to the solver
    objective = resolve_objective(sys.argv[2])  # Second is the objective to optimise
    cutoff_time = float(sys.argv[3])  # Third is the cutoff time
    # Argument 4,5 are configuration id and instance id
    seed = int(sys.argv[6])  # Fifth is the seed
    instance = Path(sys.argv[7])  # Sixth argument is the path to the instance
    argsiter = iter(sys.argv[8:])
    args = zip(argsiter, argsiter)
    configuration = {arg.strip("-"): val for arg, val in args}
    runsolver_binary = solver_dir / "runsolver"
    solver = Solver(solver_dir,
                    raw_output_directory=Path(),
                    runsolver_exec=runsolver_binary)
    # Call Runsolver with the solver configurator wrapper and its arguments
    output = solver.run(instance=instance,
                        objectives=[objective],
                        seed=seed,
                        cutoff_time=cutoff_time,
                        configuration=configuration,
                        run_on=Runner.LOCAL)
    # Return the objective value and the used CPU time
    print(f"{output[objective.name]} {output['cpu_time']}")
