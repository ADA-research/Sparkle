#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Execute Sparkle portfolio selector, read/write to SelectionScenario."""

import argparse
import sys
from filelock import FileLock, Timeout
from pathlib import Path

from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.solver import Solver
from sparkle.selector import SelectionScenario
from sparkle.instance import Instance_Set


def main(argv: list[str]) -> None:
    """Main function of the Selector CLI."""
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--selector-scenario",
        required=True,
        type=Path,
        help="path to portfolio selector scenario",
    )
    parser.add_argument(
        "--instance", required=True, type=Path, help="path to instance to run on"
    )
    parser.add_argument(
        "--feature-data", required=True, type=Path, help="path to feature data"
    )
    parser.add_argument(
        "--seed",
        type=int,
        required=False,
        help="seed to use for the solver. If not provided, read from "
        "the PerformanceDataFrame or generate one.",
    )
    parser.add_argument(
        "--log-dir", type=Path, required=False, help="path to the log directory"
    )
    args = parser.parse_args(argv)

    # Process command line arguments
    selector_scenario = SelectionScenario.from_file(args.selector_scenario)
    feature_data = FeatureDataFrame(Path(args.feature_data))
    instance_set = Instance_Set(args.instance)
    instance = str(instance_set.instance_paths[0])
    instance_name = instance_set.instance_names[0]
    seed = args.seed
    if seed is None:
        # Try to read from PerformanceDataFrame
        seed = selector_scenario.selector_performance_data.get_value(
            selector_scenario.__selector_solver_name__,
            instance_name,
            solver_fields=[PerformanceDataFrame.column_seed],
        )
        if seed is None:  # Still no value
            import random

            seed = random.randint(0, 2**32 - 1)

    # Note: Following code could be adjusted to run entire instance set
    # Run portfolio selector
    print(f"Sparkle portfolio selector predicting for instance {instance_name} ...")
    feature_instance_name = instance_name
    if instance_name not in feature_data.instances:
        if Path(instance_name).name in feature_data.instances:
            feature_instance_name = Path(instance_name).name
        elif str(instance) in feature_data.instances:
            feature_instance_name = str(instance)
        elif str(Path(instance).with_suffix("")) in feature_data.instances:
            feature_instance_name = str(Path(instance).with_suffix(""))
        else:
            raise ValueError(
                f"Could not resolve {instance} features in {feature_data.csv_filepath}"
            )
    predict_schedule = selector_scenario.selector.run(
        selector_scenario.selector_file_path, feature_instance_name, feature_data
    )

    if predict_schedule is None:  # Selector Failed to produce prediction
        sys.exit(-1)

    print("Predicting done! Running schedule...")
    performance_data = selector_scenario.selector_performance_data
    selector_output = {}
    for solver, config_id, cutoff_time in predict_schedule:
        config = performance_data.get_full_configuration(solver, config_id)
        solver = Solver(Path(solver))
        print(
            f"\t- Calling {solver.name} ({config_id}) with time budget {cutoff_time} "
            f"on instance {instance}..."
        )
        solver_output = solver.run(  # Runs locally by default
            instance,
            objectives=[selector_scenario.objective],
            seed=seed,
            cutoff_time=cutoff_time,
            configuration=config,
            log_dir=args.log_dir,
        )
        print(solver_output)
        for key in solver_output:
            if key in selector_output and isinstance(solver_output[key], (int, float)):
                selector_output[key] += solver_output[key]
            else:
                selector_output[key] = solver_output[key]
        print(f"\t- Calling solver {solver.name} ({config_id}) done!")

        if solver_output["status"].positive:
            print(f"{instance} was solved by {solver.name} ({config_id})")
            break
        print(f"{instance} is not solved in this call")

    selector_value = selector_output[selector_scenario.objective.name]
    if selector_scenario.objective.post_process:
        selector_value = selector_scenario.objective.post_process(
            selector_output[selector_scenario.objective.name],
            cutoff_time,
            selector_output["status"],
        )
    if solver_output["status"].positive:
        print(
            f"Selector {selector_scenario.selector.name} solved {instance} "
            f"with a value of {selector_value} ({selector_scenario.objective.name})."
        )
    else:
        print(f"Selector {selector_scenario.selector.name} did not solve {instance}.")
    print(f"Writing results to {performance_data.csv_filepath} ...")
    try:
        # Creating a seperate locked file for writing
        lock = FileLock(f"{performance_data.csv_filepath}.lock")
        with lock.acquire(timeout=60):
            # Reload the dataframe to latest version
            performance_data = PerformanceDataFrame(performance_data.csv_filepath)
            performance_data.set_value(
                selector_value,
                selector_scenario.__selector_solver_name__,
                instance_name,
                objective=selector_scenario.objective.name,
            )
            performance_data.save_csv()
        lock.release()
    except Timeout:
        print(f"ERROR: Cannot acquire File Lock on {performance_data}.")


if __name__ == "__main__":
    main(sys.argv[1:])
