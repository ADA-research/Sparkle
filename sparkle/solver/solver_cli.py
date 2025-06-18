#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Run a solver, read/write to performance dataframe."""
from filelock import FileLock
import argparse
from pathlib import Path
import random
import time

from runrunner import Runner

from sparkle.solver import Solver
from sparkle.types import resolve_objective
from sparkle.structures import PerformanceDataFrame


if __name__ == "__main__":
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--performance-dataframe", required=True, type=Path,
                        help="path to the performance dataframe")
    parser.add_argument("--solver", required=True, type=Path, help="path to solver")
    parser.add_argument("--instance", required=True, type=Path, nargs="+",
                        help="path to instance to run on")
    parser.add_argument("--run-index", required=True, type=int,
                        help="run index in the dataframe to set.")
    parser.add_argument("--log-dir", type=Path, required=True,
                        help="path to the log directory")

    # These two arguments should be mutually exclusive
    parser.add_argument("--configuration-id", type=str, required=False,
                        help="configuration id to read from the PerformanceDataFrame.")
    parser.add_argument("--configuration", type=dict, required=False,
                        help="configuration for the solver")

    parser.add_argument("--seed", type=str, required=False,
                        help="seed to use for the solver. If not provided, read from "
                             "the PerformanceDataFrame or generate one.")
    parser.add_argument("--cutoff-time", type=int, required=False,
                        help="the cutoff time for the solver.")
    parser.add_argument("--target-objective", required=False, type=str,
                        help="The objective to use to determine the best configuration.")
    parser.add_argument("--best-configuration-instances", required=False, type=str,
                        help="If given, will ignore any given configurations, and try to"
                             " determine the best found configurations over the given "
                             "instances. Defaults to the first objective given in the "
                             " objectives argument or the one given by the dataframe "
                             " to use to determine the best configuration.")
    args = parser.parse_args()
    # Process command line arguments
    log_dir = args.log_dir
    print(f"Running Solver and read/writing results with {args.performance_dataframe}")
    # Resolve possible multi-file instance
    instance_path: list[Path] = args.instance
    instance_path = instance_path[0] if len(instance_path) == 1 else instance_path
    instance_name = instance_path.stem if isinstance(
        instance_path, Path) else instance_path[0].stem
    run_index = args.run_index
    # Ensure stringifcation of path objects
    if isinstance(instance_path, list):
        # Double list because of solver.run
        run_instances = [[str(filepath) for filepath in instance_path]]
    else:
        run_instances = str(instance_path)

    solver = Solver(args.solver)

    if args.configuration_id or args.best_configuration_instances:  # Read
        # Desyncronize from other possible jobs writing to the same file
        time.sleep(random.random() * 10)
        lock = FileLock(f"{args.performance_dataframe}.lock")  # Lock the file
        with lock.acquire(timeout=600):
            performance_dataframe = PerformanceDataFrame(args.performance_dataframe)

        objectives = performance_dataframe.objectives
        # Filter out possible errors, shouldn't occur
        objectives = [o for o in objectives if o is not None]
        if args.best_configuration_instances:  # Determine best configuration
            # TODO What if best_configuration_instances is multi file?
            best_configuration_instances = args.best_configuration_instances.split(",")
            target_objective = resolve_objective(args.target_objective)
            config_id, value = performance_dataframe.best_configuration(
                solver=str(args.solver),
                objective=target_objective,
                instances=best_configuration_instances,
            )
            configuration = performance_dataframe.get_full_configuration(
                str(args.solver), config_id)
            # Read the seed from the dataframe
            seed = performance_dataframe.get_value(
                str(args.solver),
                instance_name,
                objective=target_objective.name,
                run=run_index,
                solver_fields=[PerformanceDataFrame.column_seed])
        elif args.configuration_id:  # Read from DF the ID
            config_id = args.configuration_id
            configuration = performance_dataframe.get_full_configuration(
                str(args.solver), config_id)
            seed = performance_dataframe.get_value(
                str(args.solver),
                instance_name,
                objective=None,
                run=run_index,
                solver_fields=[PerformanceDataFrame.column_seed])
        else:  # Direct config given
            configuration = args.configuration
            config_id = configuration["config_id"]

        seed = args.seed or seed
        # If no seed is provided and no seed can be read, generate one
        if not isinstance(seed, int):
            seed = random.randint(0, 2**32 - 1)

    print(f"Running Solver {solver} on instance {instance_name} with seed {seed}..")
    solver_output = solver.run(
        run_instances,
        objectives=objectives,
        seed=seed,
        configuration=configuration.copy() if configuration else None,
        cutoff_time=args.cutoff_time,
        log_dir=log_dir,
        run_on=Runner.LOCAL)

    # Prepare the results for the DataFrame for each objective
    result = [[solver_output[objective.name] for objective in objectives],
              [seed] * len(objectives)]
    solver_fields = [PerformanceDataFrame.column_value, PerformanceDataFrame.column_seed]
    objective_values = [f"{objective.name}: {solver_output[objective.name]}"
                        for objective in objectives]
    print(f"Appending value objective values: {', '.join(objective_values)}")
    print(f"For Solver/config: {solver}/{config_id}")
    print(f"For index: Instance {instance_name}, Run {args.run_index}")

    # Desyncronize from other possible jobs writing to the same file
    time.sleep(random.random() * 10)

    # Now that we have all the results, we can add them to the performance dataframe
    lock = FileLock(f"{args.performance_dataframe}.lock")  # Lock the file
    with lock.acquire(timeout=600):
        performance_dataframe = PerformanceDataFrame(args.performance_dataframe)
        performance_dataframe.set_value(
            result,
            solver=str(args.solver),
            instance=instance_name,
            configuration=config_id,
            objective=[o.name for o in objectives],
            run=run_index,
            solver_fields=solver_fields,
            append_write_csv=True)
