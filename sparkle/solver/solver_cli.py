#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Run a solver, read/write to performance dataframe."""
from filelock import FileLock
import argparse
from pathlib import Path

from runrunner import Runner

from sparkle.solver import Solver
from sparkle.solver.verifier import SATVerifier
from sparkle.instance import Instance_Set
from sparkle.types import resolve_objective
from sparkle.structures import PerformanceDataFrame


if __name__ == "__main__":
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--performance-dataframe", required=True, type=Path,
                        help="path to the performance dataframe")
    parser.add_argument("--solver", required=True, type=Path, help="path to solver")
    parser.add_argument("--objectives", required=False, type=str,
                        help="The objectives to use for the solver. Comma separated. "
                             "If not provided, read from the PerformanceDataFrame.")
    parser.add_argument("--instance", required=True, type=str,
                        help="path to instance to run on")
    parser.add_argument("--run", required=True, type=int,
                        help="run index in the dataframe")
    parser.add_argument("--log-dir", type=Path, required=True,
                        help="path to the log directory")
    parser.add_argument("--configuration", type=dict, required=False,
                        help="configuration for the solver. If not provided, read from "
                             "the PerformanceDataFrame.")
    parser.add_argument("--seed", type=str, required=False,
                        help=" seed to use for the solver. If not provided, read from "
                             "the PerformanceDataFrame.")
    parser.add_argument("--cutoff", type=int, required=False,
                        help="the cutoff time for the solver.")
    parser.add_argument("--use-verifier", required=False, type=bool,
                        help="Indicator whether to use SAT solution verifier.")
    args = parser.parse_args()
    # Process command line arguments
    log_dir = args.log_dir

    # Resolve possible multi-file instance
    instance_path = Path(args.instance)
    instance_name = instance_path.name
    instance_key = instance_path
    if not instance_path.exists():
        # If its an instance name (Multi-file instance), retrieve path list
        data_set = Instance_Set(instance_path.parent)
        instance_path = data_set.get_path_by_name(instance_name)
        instance_key = instance_name

    verifier = SATVerifier() if args.use_verifier else None
    solver = Solver(args.solver, verifier=verifier)
    cutoff = args.cutoff

    if not args.configuration or not args.seed or not args.objectives:  # Read
        # FileLock not required as its just reading?
        performance_dataframe = PerformanceDataFrame(args.performance_dataframe)

        if args.objectives:
            objectives = [resolve_objective(o) for o in args.objectives.split(",")]
        else:
            objectives = performance_dataframe.objectives

        seed, configuration = performance_dataframe.get_value(
            str(args.solver),
            str(args.instance),
            objectives[0].name,
            run=args.run,
            solver_fields=["Seed", "Configuration"])
        seed = args.seed or seed
        configuration = args.configuration or dict(configuration)

    solver_output = solver.run(
        instance_path.absolute(),
        objectives=objectives,
        seed=seed,
        configuration=configuration,
        cutoff_time=cutoff,
        log_dir=log_dir,
        run_on=Runner.LOCAL)

    # Now that we have all the results, we can add them to the performance dataframe
    lock = FileLock(f"{args.performance_dataframe}.lock")  # Lock the file
    with lock.acquire(timeout=60):
        performance_dataframe = PerformanceDataFrame(args.args.performance_dataframe)
        for objective in objectives:
            measurement = solver_output[objective.name]
            performance_dataframe.set_value(measurement,
                                            solver=str(args.solver),
                                            instance=str(args.instance),
                                            objective=objective.name)
        performance_dataframe.save_csv()
    lock.release()
