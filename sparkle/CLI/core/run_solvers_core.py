#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Run a solver on an instance, only for internal calls from Sparkle."""
from filelock import FileLock
import argparse
from pathlib import Path

from runrunner import Runner

from sparkle.CLI.help import global_variables as gv
import sparkle.tools.general as tg
from sparkle.solver import Solver
from sparkle.instance import instance_set
from sparkle.types import resolve_objective
from sparkle.structures import PerformanceDataFrame


if __name__ == "__main__":
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--performance-data", required=True, type=Path,
                        help="path to the performance dataframe")
    parser.add_argument("--instance", required=True, type=str,
                        help="path to instance to run on")
    parser.add_argument("--solver", required=True, type=Path, help="path to solver")
    parser.add_argument("--objectives", required=True, type=str,
                        help="The objectives to use for the solver. Comma separated.")
    parser.add_argument("--log-dir", type=Path, required=False,
                        help="path to the log directory")
    parser.add_argument("--seed", type=str, required=False,
                        help="sets the seed used for the solver")
    args = parser.parse_args()
    # Process command line arguments
    cwd = args.log_dir if args.log_dir is not None else gv.settings().DEFAULT_tmp_output
    # Resolve possible multi-file instance
    instance_path = Path(args.instance)
    instance_name = instance_path.name
    instance_key = instance_path
    if not instance_path.exists():
        # If its an instance name (Multi-file instance), retrieve path list
        data_set = instance_set(instance_path.parent)
        instance_path = data_set.get_path_by_name(instance_name)
        instance_key = instance_name

    verifier = gv.settings().get_general_solution_verifier()
    solver = Solver(args.solver, verifier=verifier)
    key_str = f"{solver.name}_{instance_name}_{tg.get_time_pid_random_string()}"
    cutoff = gv.settings().get_general_target_cutoff_time()

    objectives = [resolve_objective(name) for name in args.objectives.split(",")]
    solver_output = solver.run(
        instance_path.absolute(),
        objectives=objectives,
        seed=args.seed if args.seed else 42,
        cutoff_time=cutoff,
        cwd=cwd,
        run_on=Runner.LOCAL)

    # Now that we have all the results, we can add them to the performance dataframe
    lock = FileLock(f"{args.performance_data}.lock")  # Lock the file
    with lock.acquire(timeout=60):
        performance_dataframe = PerformanceDataFrame(args.performance_data)
        for objective in objectives:
            measurement = solver_output[objective.name]
            performance_dataframe.set_value(measurement,
                                            solver=str(args.solver),
                                            instance=str(args.instance),
                                            objective=objective.name)
        performance_dataframe.save_csv()
    lock.release()
