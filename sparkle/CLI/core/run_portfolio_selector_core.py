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
from sparkle.solver import Solver, Selector
from sparkle.types import SolverStatus


def call_solver_solve_instance(
        solver: Solver,
        instance: Path,
        cutoff_time: int,
        log_dir: Path,
        performance_data: PerformanceDataFrame = None) -> bool:
    """Call the Sparkle portfolio selector to solve a single instance with a cutoff.

    Args:
        solver: The solver to run on the instance
        instance: The path to the instance
        cutoff_time: The cutoff time for the solver
        log_dir: The log directory for the solver
        performance_data: The dataframe to store the results in

    Returns:
        Whether the instance was solved by the solver
    """
    objectives = gv.settings().get_general_sparkle_objectives()
    solver_output = solver.run(
        instance.absolute(),
        objectives=objectives,
        seed=gv.get_seed(),
        cutoff_time=cutoff_time,
        log_dir=log_dir,
        run_on=Runner.LOCAL)
    status_key = [o.name for o in objectives if o.name.startswith("status")][0]
    status = solver_output[status_key]
    flag_solved = False
    if (status == SolverStatus.SUCCESS
            or status == SolverStatus.SAT or status == SolverStatus.UNSAT):
        flag_solved = True

    if performance_data is not None:
        solver_name = performance_data.solvers[0]
        try:
            # Creating a seperate locked file for writing
            lock = FileLock(f"{performance_data.csv_filepath}.lock")
            with lock.acquire(timeout=60):
                # Reload the dataframe to latest version
                performance_data = PerformanceDataFrame(performance_data.csv_filepath)
                for objective in objectives:
                    performance_data.set_value(solver_output[objective.name],
                                               solver_name,
                                               instance.name,
                                               objective=objective.name)
                performance_data.save_csv()
            lock.release()
        except Timeout:
            print(f"ERROR: Cannot acquire File Lock on {performance_data}.")

    if flag_solved:
        print(f"Instance solved by solver {solver.name}")
    else:
        print(f"Solver {solver.name} failed to solve the instance with status "
              f"{status}")
    return flag_solved


if __name__ == "__main__":
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--selector", required=True, type=Path,
                        help="path to portfolio selector")
    parser.add_argument("--instance", required=True, type=str,
                        help="path to instance to run on")
    parser.add_argument("--feature-data-csv", required=True, type=Path,
                        help="path to performance data csv")
    parser.add_argument("--performance-data-csv", required=True, type=Path,
                        help="path to performance data csv")
    parser.add_argument("--log-dir", type=Path, required=False,
                        help="path to the log directory")
    args = parser.parse_args()

    # Process command line arguments
    log_dir =\
        args.log_dir if args.log_dir is not None else gv.settings().DEFAULT_tmp_output
    feature_data = FeatureDataFrame(Path(args.feature_data_csv))
    performance_data = PerformanceDataFrame(Path(args.performance_data_csv))

    # Run portfolio selector
    print("Sparkle portfolio selector predicting ...")
    selector = Selector(gv.settings().get_selection_class(),
                        gv.settings().get_selection_model())
    predict_schedule = selector.run(args.selector,
                                    args.instance,
                                    feature_data)

    if predict_schedule is None:  # Selector Failed to produce prediction
        sys.exit(-1)
    print("Predicting done!")
    for solver, cutoff_time in predict_schedule:
        solver = Solver(Path(solver))
        print(f"Calling solver {solver.name} with time budget {cutoff_time} ...")
        flag_solved = call_solver_solve_instance(
            solver, Path(args.instance), cutoff_time, log_dir, performance_data)
        print(f"Calling solver {solver.name} done!")

        if flag_solved:
            break
        print("The instance is not solved in this call")
