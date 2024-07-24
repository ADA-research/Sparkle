#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Run a solver on an instance, only for internal calls from Sparkle."""
from filelock import FileLock
import argparse
from pathlib import Path

from sparkle.CLI.help import global_variables as gv
import sparkle.tools.general as tg
from sparkle.platform.settings_objects import Settings
from sparkle.CLI.support import run_solvers_help as srs
from sparkle.solver import Solver
from sparkle.instance import InstanceSet
from sparkle.types.objective import PerformanceMeasure
from sparkle.structures import PerformanceDataFrame


if __name__ == "__main__":
    # Initialise settings
    global settings
    file_path_latest = Path("Settings/latest.ini")
    gv.settings = Settings(file_path_latest)
    perf_measure = gv.settings.DEFAULT_general_sparkle_objective.PerformanceMeasure
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--performance-data", required=True, type=Path,
                        help="path to the performance dataframe")
    parser.add_argument("--instance", required=True, type=str,
                        help="path to instance to run on")
    parser.add_argument("--solver", required=True, type=Path, help="path to solver")
    parser.add_argument("--performance-measure", choices=PerformanceMeasure.__members__,
                        default=perf_measure,
                        help="the performance measure, e.g. runtime")
    parser.add_argument("--seed", type=str, required=False,
                        help="sets the seed used for the solver")
    args = parser.parse_args()

    # Process command line arguments
    # Resolve possible multi-file instance
    instance_path = Path(args.instance)
    instance_name = instance_path.name
    instance_key = instance_path
    if not instance_path.exists():
        # If its an instance name (Multi-file instance), retrieve path list
        instance_set = InstanceSet(instance_path.parent)
        instance_path = instance_set.get_path_by_name(instance_name)
        instance_key = instance_name

    solver = Solver(Path(args.solver))
    performance_measure = PerformanceMeasure.from_str(args.performance_measure)
    key_str = f"{solver.name}_{instance_name}_{tg.get_time_pid_random_string()}"
    raw_result_path = f"Tmp/{key_str}.rawres"
    cutoff = gv.settings.get_general_target_cutoff_time()
    cpu_time, wc_time, cpu_time_penalised, quality, status, raw_result_path =\
        srs.run_solver_on_instance_and_process_results(solver,
                                                       instance_path,
                                                       cutoff,
                                                       args.seed)

    if performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE:
        measurement = quality[0]  # TODO: Handle the multi-objective case
    elif performance_measure == PerformanceMeasure.RUNTIME:
        measurement = cpu_time_penalised
    else:
        print(f"*** ERROR: Unknown performance measure detected: {performance_measure}")
    # Now that we have all the results, we can add them to the performance dataframe
    lock = FileLock(f"{args.performance_data}.lock")  # Lock the file
    with lock.acquire(timeout=60):
        performance_dataframe = PerformanceDataFrame(Path(args.performance_data))
        performance_dataframe.set_value(measurement,
                                        solver=str(args.solver),
                                        instance=str(args.instance))
        performance_dataframe.save_csv()
    lock.release()
