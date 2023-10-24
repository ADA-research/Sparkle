#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Run a solver on an instance, only for internal calls from Sparkle."""

import os
import time
import fcntl
import argparse
import shutil
from pathlib import Path
from pathlib import PurePath

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_basic_help as sbh
from Commands.sparkle_help import sparkle_file_help as sfh
from Commands.sparkle_help import sparkle_run_solvers_help as srs
from Commands.sparkle_help.sparkle_settings import PerformanceMeasure
from Commands.sparkle_help import sparkle_settings
from Commands.Structures.status_info import SolverRunStatusInfo


if __name__ == "__main__":
    # Initialise settings
    global settings
    settings_dir = Path("Settings")
    file_path_latest = PurePath(settings_dir / "latest.ini")
    sgh.settings = sparkle_settings.Settings(file_path_latest)

    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", required=False, type=str, nargs="+",
                        help="path to instance to run on")
    parser.add_argument("--solver", required=True, type=str, help="path to solver")
    parser.add_argument("--performance-measure", choices=PerformanceMeasure.__members__,
                        default=sgh.settings.DEFAULT_general_performance_measure,
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
    instance_path = " ".join(args.instance)
    solver_path = args.solver
    if args.seed is not None:
        # Creating a new directory for the solver to facilitate running several
        # solver_instances in parallel.
        new_solver_directory_path = (
            f"{sgh.sparkle_tmp_path}{sfh.get_last_level_directory_name(solver_path)}_"
            f"seed_{args.seed}_{sfh.get_last_level_directory_name(instance_path)}")
        command_line = f"cp -a -r {str(solver_path)} {str(new_solver_directory_path)}"
        os.system(command_line)
        solver_path = new_solver_directory_path

    performance_measure = PerformanceMeasure.from_str(args.performance_measure)
    run_status_path = args.run_status_path
    key_str = (f"{sfh.get_last_level_directory_name(solver_path)}_"
               f"{sfh.get_last_level_directory_name(instance_path)}_"
               f"{sbh.get_time_pid_random_string()}")
    raw_result_path = r"Tmp/" + key_str + r".rawres"
    processed_result_path = r"Performance_Data/Tmp/" + key_str + r".result"

    start_time = time.time()
    # create statusinfo file
    status_info = SolverRunStatusInfo()
    status_info.set_solver(sfh.get_last_level_directory_name(solver_path))
    status_info.set_instance(sfh.get_last_level_directory_name(instance_path))
    cutoff_str = str(sgh.settings.get_general_target_cutoff_time())
    status_info.set_cutoff_time(f"{cutoff_str}"
                                f" second(s)")
    print("Writing run status to file")
    status_info.save()

    cpu_time, wc_time, cpu_time_penalised, quality, status, raw_result_path = (
        srs.run_solver_on_instance_and_process_results(solver_path, instance_path,
                                                       args.seed))

    description_str = (f"[Solver: {sfh.get_last_level_directory_name(solver_path)}, "
                       f"Instance: {sfh.get_last_level_directory_name(instance_path)}]")
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

    sfh.append_string_to_file(sgh.sparkle_system_log_path, log_str)
    status_info.delete()

    if run_status_path != sgh.pap_sbatch_tmp_path:
        if solver_path.startswith(sgh.sparkle_tmp_path):
            shutil.rmtree(solver_path)

    if performance_measure == PerformanceMeasure.RUNTIME:
        obj_str = str(cpu_time_penalised)
    else:
        obj_str = str(quality[0])  # TODO: Handle the multi-objective case

    fout = Path(processed_result_path).open("w+")
    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
    fout.write(instance_path + "\n")
    fout.write(solver_path + "\n")
    fout.write(obj_str + "\n")
    fout.close()

    # TODO: Make removal conditional on a success status (SUCCESS, SAT or UNSAT)
    # command_line = r'rm -f ' + raw_result_path
    # os.system(command_line)
