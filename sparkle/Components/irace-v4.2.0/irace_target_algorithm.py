#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Handles IRACE calls passing to sparkle solver wrappers."""
import sys
import warnings
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
    config_id = sys.argv[4]
    instance_id = sys.argv[5]
    seed = int(sys.argv[6])  # Fifth is the seed
    if str(config_id) == "1" and int(seed) == 1234567:
        print(0, int(cutoff_time))  # Test call to Solver
        sys.exit()
    instance = Path(sys.argv[7])  # Sixth argument is the path to the instance
    argsiter = iter(sys.argv[8:])
    args = zip(argsiter, argsiter)
    configuration = {arg.strip("-"): val for arg, val in args}
    runsolver_binary = solver_dir / "runsolver"
    solver = Solver(solver_dir,
                    raw_output_directory=(Path.cwd() / "tmp").absolute(),
                    runsolver_exec=runsolver_binary)
    # Call Runsolver with the solver configurator wrapper and its arguments
    # IRACE cannot deal with printed warnings, we filter out missing RunSolver logs
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    output = solver.run(instances=instance,
                        objectives=[objective],
                        seed=seed,
                        cutoff_time=cutoff_time,
                        configuration=configuration,
                        run_on=Runner.LOCAL)
    warnings.resetwarnings()
    objective_value =\
        output[objective.name] if objective.minimise else -1 * output[objective.name]

    print(f"{objective_value} {output['cpu_time']}")
