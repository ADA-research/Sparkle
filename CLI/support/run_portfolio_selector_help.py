#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for the execution of a portfolio selector."""
import subprocess
import sys
import fcntl
from filelock import FileLock, Timeout
from pathlib import Path
import ast

import runrunner as rrr
from runrunner.base import Runner

from sparkle.platform import file_help as sfh
from sparkle.solver import Extractor, Solver
import global_variables as gv
import tools.general as tg
from sparkle.structures.performance_dataframe import PerformanceDataFrame
from CLI.support import run_solvers_help as srs

from CLI.help.command_help import CommandName


# Called in call_sparkle_portfolio_selector_solve_instance
# Called in compute_marginal_contribution_help
def get_list_predict_schedule_from_file(predict_schedule_result_path: str) -> list:
    """Return the predicted algorithm schedule as a list."""
    prefix_string = "Selected Schedule [(algorithm, budget)]: "
    predict_schedule = ""
    with Path(predict_schedule_result_path).open("r+") as fin:
        fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
        predict_schedule_lines = fin.readlines()
        for line in predict_schedule_lines:
            if line.strip().startswith(prefix_string):
                predict_schedule = line.strip()
                break
    if predict_schedule == "":
        print("ERROR: Failed to get schedule from algorithm portfolio. Stopping "
              "execution!\n"
              f"Schedule file appears to be empty: {predict_schedule_result_path}\n"
              f"Selector error output path: {gv.sparkle_err_path}")
        sys.exit(-1)

    predict_schedule_string = predict_schedule[len(prefix_string):]
    # eval insecure, so use ast.literal_eval instead
    return ast.literal_eval(predict_schedule_string)


# Only called in call_sparkle_portfolio_selector_solve_instance
def call_solver_solve_instance_within_cutoff(solver: Solver,
                                             instance_path: str,
                                             cutoff_time: int,
                                             performance_data_csv: str = None)\
        -> bool:
    """Call the Sparkle portfolio selector to solve a single instance with a cutoff."""
    _, _, cpu_time_penalised, _, status, raw_result_path = (
        srs.run_solver_on_instance_and_process_results(solver, instance_path,
                                                       custom_cutoff=cutoff_time))
    flag_solved = False
    if status == "SUCCESS" or status == "SAT" or status == "UNSAT":
        flag_solved = True

    if performance_data_csv is not None:
        performance_data_csv_path = Path(performance_data_csv)
        solver_name = "Sparkle_Portfolio_Selector"
        print(f"Trying to write: {cpu_time_penalised}, {solver_name}, {instance_path}")
        try:
            # Creating a seperate locked file for writing
            lock = FileLock(f"{performance_data_csv}.lock")
            with lock.acquire(timeout=60):
                performance_dataframe = PerformanceDataFrame(performance_data_csv_path)
                performance_dataframe.set_value(cpu_time_penalised, solver_name,
                                                Path(instance_path).name)
                performance_dataframe.save_csv()
            lock.release()
        except Timeout:
            print(f"ERROR: Cannot acquire File Lock on {performance_data_csv}.")
    else:
        if flag_solved:
            print(f"Instance solved by solver {solver.name}")
        else:
            print(f"Solver {solver.name} failed to solve the instance with status "
                  f"{status}")
    sfh.rmfiles(raw_result_path)
    return flag_solved


# Only called in portfolio_core and run_sparkle_portfolio_selector
def call_sparkle_portfolio_selector_solve_instance(
        instance_path: Path,
        performance_data_csv_path: str = None) -> None:
    """Call the Sparkle portfolio selector to solve a single instance.

    Args:
        instance_path: Path to the instance to run on
        performance_data_csv_path: path to the performance data
    """
    # Create instance strings to accommodate multi-file instances
    if isinstance(instance_path, Path):
        instance_path = str(instance_path)
    instance_path_list = instance_path.split()
    instance_file_list = []

    for instance in instance_path_list:
        instance_file_list.append(Path(instance).name)

    instance_files_str = " ".join(instance_file_list)

    print("Running Sparkle portfolio selector on solving instance "
          f"{instance_files_str} ...")

    cutoff_extractor = gv.settings.get_general_extractor_cutoff_time()
    print(f"Sparkle computing features of instance {instance_files_str} ...")
    feature_vector = []
    extractor_paths = [p for p in gv.extractor_dir.iterdir()]
    if len(extractor_paths) == 0:
        print("ERROR: No feature extractor added to Sparkle.")
        sys.exit(-1)
    for extractor_path in extractor_paths:
        extractor = Extractor(Path(extractor_path),
                              gv.runsolver_path,
                              gv.sparkle_tmp_path)
        # We create a watch log to filter out runsolver output
        runsolver_watch_path =\
            gv.sparkle_tmp_path / f"{extractor_path.name}_{instance_path}.wlog"
        features = extractor.run(instance_path_list,
                                 runsolver_args=["--cpu-limit", str(cutoff_extractor),
                                                 "-w", runsolver_watch_path])
        for _, _, value in features:
            feature_vector.append(value)
        runsolver_watch_path.unlink(missing_ok=True)
    print(f"Sparkle computing features of instance {instance_files_str} done!")

    predict_schedule_result_path = Path(
        f"Tmp/predict_schedule_{tg.get_time_pid_random_string()}.predres")

    print("Sparkle portfolio selector predicting ...")
    cmd_list = [gv.python_executable, gv.autofolio_exec_path, "--load",
                gv.sparkle_algorithm_selector_path, "--feature_vec",
                " ".join(map(str, feature_vector))]

    print(" ".join(cmd_list))
    input()
    # Run AutoFolio
    process = subprocess.run(cmd_list,
                             stdout=predict_schedule_result_path.open("w+"),
                             stderr=gv.sparkle_err_path.open("w+"))

    if process.returncode != 0:
        # AutoFolio Error: "TypeError: Argument 'placement' has incorrect type"
        print(f"Error getting predict schedule! See {gv.sparkle_err_path} for output.")
        sys.exit(process.returncode)
    print("Predicting done!")

    print(predict_schedule_result_path.open("r").read())
    list_predict_schedule = get_list_predict_schedule_from_file(
        predict_schedule_result_path)
    sfh.rmfiles([predict_schedule_result_path, gv.sparkle_err_path])

    for pred in list_predict_schedule:
        solver = Solver(Path(pred[0]))
        cutoff_time = pred[1]
        print(f"Calling solver {solver.name} with "
              f"time budget {cutoff_time} for solving ...")
        flag_solved = call_solver_solve_instance_within_cutoff(
            solver, instance_path, cutoff_time, performance_data_csv_path)
        print(f"Calling solver {solver.name} done!")

        if flag_solved:
            return
        else:
            print("The instance is not solved in this call")


# Only called in run_sparkle_portfolio_selector
def run_portfolio_selector_on_instances(
        instances: list[Path],
        performance_data: PerformanceDataFrame,
        portfolio_selector: Path,
        run_on: Runner = Runner.SLURM) -> None:
    """Call the Sparkle portfolio selector to solve all instances in a directory.

    Args:
        instances: The paths to the instances.
        performance_data: The dataframe to store the results in.
        portfolio_selector: Path to the selector.
        run_on: Whether to run with Slurm or Local.
    """
    for instance_path in instances:
        performance_data.add_instance(instance_path.name)

    performance_data.add_solver(portfolio_selector.parent)

    performance_data.save_csv()

    # TODO: Instead of using run_sparkle_portfolio_core.py, we should do here:
    # 1. Get feature data for every feature extractor
    # 2. Use autofolio call to predict the solver per instance with
    #    a dependency on run object of 1
    # 3. Run the solver and place the results in the performance dataframe w dependency
    #    (Difficult, which solver is determined by 2)

    cmd_list = ["python CLI/core/run_sparkle_portfolio_core.py "
                f"--performance-data-csv {performance_data.csv_filepath} "
                f"--instance {instance_path}" for instance_path in instances]
    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=CommandName.RUN_SPARKLE_PORTFOLIO_SELECTOR,
        base_dir=gv.sparkle_tmp_path,
        sbatch_options=gv.settings.get_slurm_extra_options(as_args=True),
        srun_options=["-N1", "-n1", "--exclusive"])

    if run_on == Runner.LOCAL:
        run.wait()
        print("Running Sparkle portfolio selector done!")
    else:
        print("Sparkle portfolio selector is running ...")
