#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Run a solver on an instance, only for internal calls from Sparkle."""
import time
import fcntl
import argparse
import shutil
from pathlib import Path

from CLI.sparkle_help import sparkle_global_help as sgh
from sparkle.platform import file_help as sfh, settings_help
from CLI.sparkle_help import sparkle_run_solvers_help as srs
from sparkle.types.objective import PerformanceMeasure
from CLI.help.status_info import SolverRunStatusInfo


if __name__ == "__main__":
    # Initialise settings
    global settings
    file_path_latest = Path("Settings/latest.ini")
    sgh.settings = settings_help.Settings(file_path_latest)
    perf_measure = sgh.settings.DEFAULT_general_sparkle_objective.PerformanceMeasure
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", required=False, type=str, nargs="+",
                        help="path to instance to run on")
    parser.add_argument("--solver", required=True, type=str, help="path to solver")
    parser.add_argument("--performance-measure", choices=PerformanceMeasure.__members__,
                        default=perf_measure,
                        help="the performance measure, e.g. runtime")
    parser.add_argument("--run-status-path", type=Path,
                        choices=[sgh.run_solvers_sbatch_tmp_path,
                                 sgh.pap_sbatch_tmp_path],
                        default=sgh.run_solvers_sbatch_tmp_path,
                        help="set the runstatus path of the process")
    parser.add_argument("--seed", type=str, required=False,
                        help="sets the seed used for the solver")
    args = parser.parse_args()

    # Process command line arguments
    # Turn multiple instance files into a space separated string
    # NOTE: I am not sure who made this ``change'' for multiple instance_paths
    # But in all code hereafter, it seems to be treated as a single instance.
    instance_path = " ".join(args.instance)
    instance_name = Path(instance_path).name
    if Path(instance_path).is_file():
        instance_name = Path(instance_path).parent.name
    solver_path = Path(args.solver)
    if args.seed is not None:
        # Creating a new directory for the solver to facilitate running several
        # solver_instances in parallel.
        new_solver_directory_path = Path(
            f"{sgh.sparkle_tmp_path}{solver_path.name}_"
            f"seed_{args.seed}_{instance_name}")
        subtarget = new_solver_directory_path / solver_path.name
        shutil.copytree(solver_path, subtarget, dirs_exist_ok=True)
        solver_path = subtarget

    performance_measure = PerformanceMeasure.from_str(args.performance_measure)
    run_status_path = args.run_status_path
    key_str = (f"{solver_path.name}_"
               f"{instance_name}_"
               f"{sgh.get_time_pid_random_string()}")
    raw_result_path = f"Tmp/{key_str}.rawres"
    start_time = time.time()
    # create statusinfo file
    status_info = SolverRunStatusInfo()
    status_info.set_solver(solver_path.name)
    status_info.set_instance(instance_name)
    cutoff_str = str(sgh.settings.get_general_target_cutoff_time())
    status_info.set_cutoff_time(f"{cutoff_str}"
                                f" second(s)")
    print("Writing run status to file")
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
                             f"{str(sgh.settings.get_general_penalty_multiplier())}): "
                             f"{str(cpu_time_penalised)} second(s)]")
    status_str = "[Run Status: " + status + "]"

    log_str = (f"{description_str}, {cutoff_str}, {start_time_str}, {end_time_str}, "
               f"{run_time_str}, {recorded_run_time_str}, {status_str}")
    sfh.write_string_to_file(sgh.sparkle_system_log_path, log_str, append=True)
    status_info.delete()

    if run_status_path != sgh.pap_sbatch_tmp_path:
        if sgh.sparkle_tmp_path in solver_path.parents:
            shutil.rmtree(solver_path)

    if performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE:
        obj_str = str(quality[0])  # TODO: Handle the multi-objective case
    elif performance_measure == PerformanceMeasure.RUNTIME:
        obj_str = str(cpu_time_penalised)
    else:
        print(f"*** ERROR: Unknown performance measure detected: {performance_measure}")
    processed_result_path = sgh.performance_data_dir / "Tmp" / f"{key_str}.result"
    with Path(processed_result_path).open("w+") as fout:
        fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
        fout.write(f"{instance_path}\n"
                   f"{solver_path}\n"
                   f"{obj_str}\n")

    pap_result_path = sgh.pap_performance_data_tmp_path / f"{key_str}.result"
    with pap_result_path.open("w+") as fout:
        fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
        fout.write(f"{instance_path}\n"
                   f"{solver_path}\n"
                   f"{obj_str}\n")

    # TODO: Make removal conditional on a success status (SUCCESS, SAT or UNSAT)
    # sfh.rmfiles(raw_result_path)
