#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Execute Sparkle portfolio, only for internal calls from Sparkle."""
import argparse
import sys
from filelock import FileLock, Timeout
from pathlib import Path

from runrunner.base import Runner

from sparkle.CLI.help import global_variables as gv
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.solver import Solver
from sparkle.selector import SelectionScenario


if __name__ == "__main__":
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--selector-scenario", required=True, type=Path,
                        help="path to portfolio selector scenario")
    parser.add_argument("--instance", required=True, type=str,
                        help="path to instance to run on")
    parser.add_argument("--feature-data-csv", required=True, type=Path,
                        help="path to performance data csv")
    parser.add_argument("--log-dir", type=Path, required=False,
                        help="path to the log directory")
    args = parser.parse_args()

    # Process command line arguments
    selector_scenario = SelectionScenario.from_file(args.selector_scenario)
    feature_data = FeatureDataFrame(Path(args.feature_data_csv))

    # Run portfolio selector
    print("Sparkle portfolio selector predicting ...")
    predict_schedule = selector_scenario.selector.run(
        selector_scenario.selector_file_path,
        args.instance,
        feature_data)

    if predict_schedule is None:  # Selector Failed to produce prediction
        sys.exit(-1)

    print("Predicting done!")
    performance_data = selector_scenario.selector_performance_data
    selector_used_budget = 0.0
    selector_output = {}
    for solver, config_id, cutoff_time in predict_schedule:
        config = performance_data.get_full_configuration(solver, config_id)
        solver = Solver(Path(solver))
        print(f"Calling solver {solver.name} with time budget {cutoff_time} ...")
        solver_output = solver.run(
            Path(args.instance).absolute(),
            objectives=[selector_scenario.objective],
            seed=gv.get_seed(),
            cutoff_time=cutoff_time,
            configuration=config,
            log_dir=args.log_dir,
            run_on=Runner.LOCAL)
        for key in solver_output:
            if key in selector_output and isinstance(solver_output[key], (int, float)):
                selector_output[key] += solver_output[key]
            else:
                selector_output[key] = solver_output[key]
        print(f"Calling solver {solver.name} done!")

        if solver_output["status"].positive:
            break
        print("The instance is not solved in this call")

    # TODO deal with the objectives for selector...
    selector_value = selector_output[selector_scenario.objective.name]
    if selector_scenario.objective.post_process:
        selector_value = selector_scenario.objective.post_process(
            selector_output[selector_scenario.objective.name],
            cutoff_time,
            selector_output["status"])
    try:
        # Creating a seperate locked file for writing
        lock = FileLock(f"{performance_data.csv_filepath}.lock")
        with lock.acquire(timeout=60):
            # Reload the dataframe to latest version
            performance_data = PerformanceDataFrame(performance_data.csv_filepath)
            performance_data.set_value(selector_value,
                                       selector_scenario.__selector_solver_name__,
                                       str(args.instance),
                                       objective=selector_scenario.objective.name)
            performance_data.save_csv()
        lock.release()
    except Timeout:
        print(f"ERROR: Cannot acquire File Lock on {performance_data}.")
