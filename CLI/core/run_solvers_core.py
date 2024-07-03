#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Run a solver on an instance, only for internal calls from Sparkle."""
import time
from filelock import FileLock
import argparse
import shutil
from pathlib import Path

import global_variables as gv
import tools.general as tg
from sparkle.platform import file_help as sfh, settings_help
from CLI.support import run_solvers_help as srs
from sparkle.instance import InstanceSet
from sparkle.types.objective import PerformanceMeasure
from sparkle.structures.performance_dataframe import PerformanceDataFrame
from CLI.help.status_info import SolverRunStatusInfo


if __name__ == "__main__":
    # Initialise settings
    global settings
    file_path_latest = Path("Settings/latest.ini")
    gv.settings = settings_help.Settings(file_path_latest)
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
    has_instance_set = False
    if not instance_path.exists():
        # If its an instance name (Multi-file instance), retrieve path list
        instance_set = InstanceSet(instance_path.parent)
        instance_path = instance_set.get_path_by_name(instance_name)
        has_instance_set = True
        instance_key = instance_name

    solver_path = Path(args.solver)
    if args.seed is not None:
        # Creating a new directory for the solver to facilitate running several
        # solver_instances in parallel.
        new_solver_directory_path = Path(
            f"{gv.sparkle_tmp_path}{solver_path.name}_"
            f"seed_{args.seed}_{instance_name}")
        subtarget = new_solver_directory_path / solver_path.name
        shutil.copytree(solver_path, subtarget, dirs_exist_ok=True)
        solver_path = subtarget

    performance_measure = PerformanceMeasure.from_str(args.performance_measure)
    key_str = f"{solver_path.name}_{instance_name}_{tg.get_time_pid_random_string()}"
    raw_result_path = f"Tmp/{key_str}.rawres"
    start_time = time.time()
    # create statusinfo file
    status_info = SolverRunStatusInfo()
    status_info.set_solver(solver_path.name)
    status_info.set_instance(instance_name)
    cutoff_str = str(gv.settings.get_general_target_cutoff_time())
    status_info.set_cutoff_time(f"{cutoff_str}"
                                f" second(s)")
    status_info.save()
    cpu_time, wc_time, cpu_time_penalised, quality, status, raw_result_path = (
        srs.run_solver_on_instance_and_process_results(solver_path, instance_path,
                                                       args.seed))

    description_str = (f"[Solver: {solver_path.name}, "
                       f"Instance: {instance_name}]")
    start_time_str = (
        f"[Start Time: {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time))}]")
    end_time_str = ("[End Time (after completing run time + processing time): "
                    f"{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}]")
    run_time_str = "[Actual Run Time (wall clock): " + str(wc_time) + " second(s)]"
    recorded_run_time_str = ("[Recorded Run Time (CPU PAR"
                             f"{gv.settings.get_general_penalty_multiplier()}): "
                             f"{cpu_time_penalised} second(s)]")
    status_str = f"[Run Status: {status}]"

    log_str = (f"{description_str}, {cutoff_str}, {start_time_str}, {end_time_str}, "
               f"{run_time_str}, {recorded_run_time_str}, {status_str}")
    sfh.write_string_to_file(gv.sparkle_system_log_path, log_str, append=True)
    status_info.delete()

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
                                        solver=str(solver_path),
                                        instance=str(instance_key))
        performance_dataframe.save_csv()
    lock.release()
