#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Run a solver, read/write to performance dataframe."""

import sys
from filelock import FileLock
import argparse
from pathlib import Path
import random
import time

from runrunner import Runner

from sparkle.solver import Solver
from sparkle.types import resolve_objective
from sparkle.structures import PerformanceDataFrame
from sparkle.tools.solver_wrapper_parsing import parse_commandline_dict


def main(argv: list[str]) -> None:
    """Main function of the command."""
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--performance-dataframe",
        required=True,
        type=Path,
        help="path to the performance dataframe",
    )
    parser.add_argument("--solver", required=True, type=Path, help="path to solver")
    parser.add_argument(
        "--instance",
        required=True,
        type=Path,
        nargs="+",
        help="path to instance to run on",
    )
    parser.add_argument(
        "--run-index",
        required=True,
        type=int,
        help="run index in the dataframe to set.",
    )
    parser.add_argument(
        "--log-dir", type=Path, required=True, help="path to the log directory"
    )

    # These two arguments should be mutually exclusive
    parser.add_argument(
        "--configuration-id",
        type=str,
        required=False,
        help="configuration id to read from the PerformanceDataFrame.",
    )
    parser.add_argument(
        "--configuration",
        type=str,
        nargs="+",
        required=False,
        help="configuration for the solver",
    )

    parser.add_argument(
        "--seed",
        type=int,
        required=False,
        help="seed to use for the solver. If not provided, generates one.",
    )
    parser.add_argument(
        "--cutoff-time",
        type=int,
        required=False,
        help="the cutoff time for the solver.",
    )
    parser.add_argument(
        "--objectives",
        type=str,
        required=False,
        nargs="+",
        help="The objectives to evaluate to Solver on. If not provided, read from the PerformanceDataFrame.",
    )
    parser.add_argument(
        "--target-objective",
        required=False,
        type=str,
        help="The objective to use to determine the best configuration.",
    )
    parser.add_argument(
        "--best-configuration-instances",
        required=False,
        type=str,
        nargs="+",
        help="If given, will ignore any given configurations, and try to"
        " determine the best found configurations over the given "
        "instances. Uses the 'target-objective' given in the arguments"
        " or the first one given by the dataframe to determine the best"
        "configuration.",
    )
    args = parser.parse_args(argv)
    # Process command line arguments
    log_dir = args.log_dir
    print(f"Running Solver and read/writing results with {args.performance_dataframe}")
    # Resolve possible multi-file instance
    instance_path: list[Path] = args.instance
    # If instance is only one file then we don't need a list
    instance_path = instance_path[0] if len(instance_path) == 1 else instance_path
    instance_name = (
        instance_path.stem if isinstance(instance_path, Path) else instance_path[0].stem
    )
    run_index = args.run_index
    # Ensure stringifcation of path objects
    if isinstance(instance_path, list):
        # Double list because of solver.run
        run_instances = [[str(filepath) for filepath in instance_path]]
    else:
        run_instances = str(instance_path)

    solver = Solver(args.solver)
    # By default, run the default configuration
    config_id = PerformanceDataFrame.default_configuration
    configuration = None
    # If no seed is provided by CLI, generate one
    seed = args.seed if args.seed else random.randint(0, 2**32 - 1)
    # Parse the provided objectives if present
    objectives = (
        [resolve_objective(o) for o in args.objectives] if args.objectives else None
    )

    if args.configuration:  # Configuration provided, override
        configuration = parse_commandline_dict(args.configuration)
        config_id = configuration["configuration_id"]
    elif (
        args.configuration_id or args.best_configuration_instances or not objectives
    ):  # Read from PerformanceDataFrame, can be slow
        # Desyncronize from other possible jobs writing to the same file
        print(
            "Reading from Performance DataFrame.. "
            f"[{'configuration' if (args.configuration_id or args.best_configuration_instances) else ''} "
            f"{'objectives' if not objectives else ''}]"
        )
        time.sleep(random.random() * 10)
        lock = FileLock(f"{args.performance_dataframe}.lock")  # Lock the file
        with lock.acquire(timeout=600):
            performance_dataframe = PerformanceDataFrame(args.performance_dataframe)

        if not objectives:
            objectives = performance_dataframe.objectives

        if args.best_configuration_instances:  # Determine best configuration
            best_configuration_instances: list[str] = args.best_configuration_instances
            # Get the unique instance names
            best_configuration_instances = list(
                set([Path(instance).stem for instance in best_configuration_instances])
            )
            target_objective = (
                resolve_objective(args.target_objective)
                if args.target_objective
                else objectives[0]
            )
            config_id, _ = performance_dataframe.best_configuration(
                solver=str(args.solver),
                objective=target_objective,
                instances=best_configuration_instances,
            )
            configuration = performance_dataframe.get_full_configuration(
                str(args.solver), config_id
            )

        elif (
            args.configuration_id
        ):  # Read from PerformanceDataFrame the configuration using the ID
            config_id = args.configuration_id
            configuration = performance_dataframe.get_full_configuration(
                str(args.solver), config_id
            )

    print(f"Running Solver {solver} on instance {instance_name} with seed {seed}..")
    solver_output = solver.run(
        run_instances,
        objectives=objectives,
        seed=seed,
        configuration=configuration.copy() if configuration else None,
        cutoff_time=args.cutoff_time,
        log_dir=log_dir,
        run_on=Runner.LOCAL,
    )

    # Prepare the results for the DataFrame for each objective
    result = [
        [solver_output[objective.name] for objective in objectives],
        [seed] * len(objectives),
    ]
    solver_fields = [
        PerformanceDataFrame.column_value,
        PerformanceDataFrame.column_seed,
    ]

    print(f"For Solver/config: {solver}/{config_id}")
    print(f"For index: Instance {instance_name}, Run {args.run_index}, Seed {seed}")
    print("Appending the following objective values:")  # {', '.join(objective_values)}")
    for objective in objectives:
        print(
            f"{objective.name}, {instance_name}, {args.run_index} | {args.solver}, {config_id}: {solver_output[objective.name]}"
        )

    # Desyncronize from other possible jobs writing to the same file
    time.sleep(random.random() * 100)
    # TESTLOG
    # lock = FileLock("test.log.lock")
    # with lock.acquire(timeout=600):
    #     with Path("test.log").open("a") as f:
    #         for objective in objectives:
    #             f.write(f"{objective.name}, {instance_name}, {args.run_index} | {solver} {config_id}: {solver_output[objective.name]}, {seed}\n")

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
            append_write_csv=True,  # We do not have to save the PDF here, thanks to this argument
        )


if __name__ == "__main__":
    main(sys.argv[1:])
