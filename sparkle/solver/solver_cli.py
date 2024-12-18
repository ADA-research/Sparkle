#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Run a solver, read/write to performance dataframe."""
from filelock import FileLock
import argparse
from pathlib import Path
import random
import ast
import time

from runrunner import Runner

from sparkle.solver import Solver
from sparkle.instance import Instance_Set
from sparkle.types import resolve_objective
from sparkle.structures import PerformanceDataFrame


if __name__ == "__main__":
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--performance-dataframe", required=True, type=Path,
                        help="path to the performance dataframe")
    parser.add_argument("--solver", required=True, type=Path, help="path to solver")
    parser.add_argument("--instance", required=True, type=str,
                        help="path to instance to run on")
    parser.add_argument("--run-index", required=True, type=int,
                        help="run index in the dataframe.")
    parser.add_argument("--log-dir", type=Path, required=True,
                        help="path to the log directory")
    parser.add_argument("--configuration", type=dict, required=False,
                        help="configuration for the solver. If not provided, read from "
                             "the PerformanceDataFrame.")
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
    instance_path = Path(args.instance)
    instance_name = instance_path.name
    instance_key = instance_path
    run_index = args.run_index
    if not instance_path.exists():
        # If its an instance name (Multi-file instance), retrieve path list
        data_set = Instance_Set(instance_path.parent)
        instance_path = data_set.get_path_by_name(instance_name)
        instance_key = instance_name

    solver = Solver(args.solver)

    if not args.configuration or not args.seed:  # Read
        # Desyncronize from other possible jobs writing to the same file
        time.sleep(random.random() * 10)
        lock = FileLock(f"{args.performance_dataframe}.lock")  # Lock the file
        with lock.acquire(timeout=600):
            performance_dataframe = PerformanceDataFrame(args.performance_dataframe)

        objectives = performance_dataframe.objectives
        # Filter out possible errors, shouldn't occur
        objectives = [o for o in objectives if o is not None]
        if args.best_configuration_instances:  # Determine best configuration
            best_configuration_instances = args.best_configuration_instances.split(",")
            target_objective = resolve_objective(args.target_objective)
            configuration, value = performance_dataframe.best_configuration(
                solver=str(args.solver),
                objective=target_objective,
                instances=best_configuration_instances,
            )
            # Read the seed from the dataframe
            seed = performance_dataframe.get_value(
                str(args.solver),
                str(args.instance),
                objective=target_objective.name,
                run=run_index,
                solver_fields=[PerformanceDataFrame.column_seed])
        else:
            target = performance_dataframe.get_value(
                str(args.solver),
                str(args.instance),
                objective=None,
                run=run_index,
                solver_fields=[PerformanceDataFrame.column_seed,
                               PerformanceDataFrame.column_configuration])
            if isinstance(target[0], list):  # We take the first value we find
                target = target[0]
            seed, df_configuration = target
            configuration = args.configuration
            if configuration is None:  # Try to read from the dataframe
                if not isinstance(df_configuration, dict):
                    try:
                        configuration = ast.literal_eval(df_configuration)
                    except Exception:
                        print("Failed to read configuration from dataframe: "
                              f"{df_configuration}")
                else:
                    configuration = df_configuration
        seed = args.seed or seed
        # If no seed is provided and no seed can be read, generate one
        if not isinstance(seed, int):
            seed = random.randint(0, 2**32 - 1)

    print(f"Running Solver {solver} on instance {instance_path.name} with seed {seed}..")
    solver_output = solver.run(
        instance_path.absolute(),
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
    if args.best_configuration_instances:  # Need to specify the configuration
        result.append([configuration] * len(objectives))
        solver_fields.append(PerformanceDataFrame.column_configuration)
    objective_values = [f"{objective.name}: {solver_output[objective.name]}"
                        for objective in objectives]
    print(f"Appending value objective values: {', '.join(objective_values)}")
    print(f"For index: Instance {args.instance}, Run {args.run_index}")

    # Desyncronize from other possible jobs writing to the same file
    time.sleep(random.random() * 10)

    # Now that we have all the results, we can add them to the performance dataframe
    lock = FileLock(f"{args.performance_dataframe}.lock")  # Lock the file
    with lock.acquire(timeout=600):
        performance_dataframe = PerformanceDataFrame(args.performance_dataframe)
        performance_dataframe.set_value(
            result,
            solver=str(args.solver),
            instance=str(args.instance),
            objective=[o.name for o in objectives],
            run=run_index,
            solver_fields=solver_fields,
            append_write_csv=True)
