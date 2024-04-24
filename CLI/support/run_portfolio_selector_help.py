#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for the execution of a portfolio selector."""

import pathlib
import subprocess
import sys
import fcntl
from pathlib import Path
import ast

import runrunner as rrr
from runrunner.base import Runner

from sparkle.platform import file_help as sfh
from CLI.sparkle_help import sparkle_global_help as sgh
from sparkle.structures import feature_data_csv_help as sfdcsv
from sparkle.structures.performance_dataframe import PerformanceDataFrame
from CLI.support import run_solvers_help as srs
from CLI.help.reporting_scenario import Scenario
from sparkle.instance import instances_help as sih
from CLI.help.command_help import CommandName
from sparkle.platform import slurm_help as ssh


def get_list_feature_vector(extractor_path: str, instance_path: str, result_path: str,
                            cutoff_time_each_extractor_run: float) -> list[str]:
    """Return the feature vector for an instance as a list."""
    err_path = result_path.replace(".rawres", ".err")
    runsolver_watch_data_path = result_path.replace(".rawres", ".log")
    runsolver_value_data_path = result_path.replace(".rawres", ".val")

    cmd_list_runsolver = [sgh.runsolver_path,
                          "--cpu-limit", str(cutoff_time_each_extractor_run),
                          "-w", runsolver_watch_data_path,  # Set log path
                          "-v", runsolver_value_data_path]  # Set information path
    cmd_list_extractor = [f"{extractor_path}/{sgh.sparkle_run_default_wrapper}",
                          f"{extractor_path}/", instance_path, result_path]

    runsolver = subprocess.run(cmd_list_runsolver, capture_output=True)
    extractor = subprocess.run(cmd_list_extractor, capture_output=True)

    if runsolver.returncode < 0 or extractor.returncode < 0:
        print("Possible issue with runsolver or extractor.")

    if Path(runsolver_value_data_path).exists():
        with Path(runsolver_value_data_path).open() as file:
            if "TIMEOUT=true" in file.read():
                print(f"****** WARNING: Feature vector computing on instance "
                      f"{instance_path} timed out! ******")

    if not Path(result_path).exists():
        # TODO: This protocol seems to make no sense. Why create an empty file?
        # Needs to be fixed
        print(f"WARNING: Result file {result_path} does not exist.")
        sfh.create_new_empty_file(result_path)

    try:
        sfdcsv.SparkleFeatureDataCSV(result_path)
    except Exception:
        print(f"****** WARNING: Feature vector computing on instance {instance_path}"
              " failed! ******")
        print("****** WARNING: The feature vector of this instance will be imputed as "
              "the mean value of all other non-missing values! ******")
        feature_data_csv = sfdcsv.SparkleFeatureDataCSV(sgh.feature_data_csv_path)
        list_feature_vector = feature_data_csv.generate_mean_value_feature_vector()
    else:
        fin = Path(result_path).open("r+")
        fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
        myline = fin.readline().strip()
        myline = fin.readline().strip()
        list_feature_vector = myline.split(",")
        del list_feature_vector[0]
        fin.close()

    sfh.rmfiles([result_path, err_path,
                runsolver_watch_data_path, runsolver_value_data_path])
    return list_feature_vector


def print_predict_schedule(predict_schedule_result_path: str) -> None:
    """Print the predicted algorithm schedule."""
    with Path(predict_schedule_result_path).open("r+") as fin:
        fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
        line = fin.readline().strip()
        print(line)


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
              f"Selector error output path: {sgh.sparkle_err_path}")
        sys.exit(-1)

    predict_schedule_string = predict_schedule[len(prefix_string):]
    # eval insecure, so use ast.literal_eval instead
    return ast.literal_eval(predict_schedule_string)


def call_solver_solve_instance_within_cutoff(solver_path: str,
                                             instance_path: str,
                                             cutoff_time: int,
                                             performance_data_csv_path: str = None)\
        -> bool:
    """Call the Sparkle portfolio selector to solve a single instance with a cutoff."""
    _, _, cpu_time_penalised, _, status, raw_result_path = (
        srs.run_solver_on_instance_and_process_results(solver_path, instance_path,
                                                       custom_cutoff=cutoff_time))
    flag_solved = False
    if status == "SUCCESS" or status == "SAT" or status == "UNSAT":
        flag_solved = True

    if performance_data_csv_path is not None:
        solver_name = "Sparkle_Portfolio_Selector"
        check_selector_status(solver_name)
        with Path(performance_data_csv_path).open("r+") as fo:
            fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
            performance_data_csv = PerformanceDataFrame(performance_data_csv_path)
            performance_data_csv.set_value(cpu_time_penalised,
                                           solver_name, instance_path)
            performance_data_csv.save_csv()
    else:
        if flag_solved:
            print(f"Instance solved by solver {solver_path}")
        else:
            print(f"Solver {solver_path} failed to solve the instance with status "
                  f"{status}")

    sfh.rmfiles(raw_result_path)
    return flag_solved


def call_sparkle_portfolio_selector_solve_instance(
        instance_path: str,
        performance_data_csv_path: str = None) -> None:
    """Call the Sparkle portfolio selector to solve a single instance.

    Args:
        instance_path: Path to the instance to run on
        performance_data_csv_path: path to the performance data
    """
    # Create instance strings to accommodate multi-file instances
    instance_path_list = instance_path.split()
    instance_file_list = []

    for instance in instance_path_list:
        instance_file_list.append(Path(instance).name)

    instance_files_str = " ".join(instance_file_list)
    instance_files_str_ = "_".join(instance_file_list)

    print("Start running Sparkle portfolio selector on solving instance "
          f"{instance_files_str} ...")

    Path("Tmp/").mkdir(exist_ok=True)

    print(f"Sparkle computing features of instance {instance_files_str} ...")
    list_feature_vector = []

    if len(sgh.extractor_list) == 0:
        print("ERROR: No feature extractor added to Sparkle.")
        sys.exit(-1)

    cutoff_time_each_extractor_run = (
        sgh.settings.get_general_extractor_cutoff_time() / len(sgh.extractor_list))

    for extractor_path in sgh.extractor_list:
        extractor_name = Path(extractor_path).name
        print(f"Extractor {extractor_name} computing "
              f"features of instance {instance_files_str} ...")
        result_path = (f"Tmp/{extractor_name}_{instance_files_str_}_"
                       f"{sgh.get_time_pid_random_string()}.rawres")

        list_feature_vector = list_feature_vector + get_list_feature_vector(
            extractor_path, instance_path, result_path, cutoff_time_each_extractor_run)
        print(f"Extractor {extractor_name} computing "
              f"features of instance {instance_files_str} done!")

    print(f"Sparkle computing features of instance {instance_files_str} done!")

    predict_schedule_result_path = ("Tmp/predict_schedule_"
                                    f"{sgh.get_time_pid_random_string()}"
                                    ".predres")
    print("Sparkle portfolio selector predicting ...")
    cmd_list = [sgh.python_executable, sgh.autofolio_path, "--load",
                sgh.sparkle_algorithm_selector_path, "--feature_vec",
                " ".join(map(str, list_feature_vector))]

    process = subprocess.run(cmd_list,
                             stdout=Path(predict_schedule_result_path).open("w+"),
                             stderr=Path(sgh.sparkle_err_path).open("w+"))

    if process.returncode != 0:
        # AutoFolio Error: "TypeError: Argument 'placement' has incorrect type"
        print(f"Error getting predict schedule! See {sgh.sparkle_err_path} for output.")
        sys.exit(process.returncode)
    print("Predicting done!")

    print_predict_schedule(predict_schedule_result_path)
    list_predict_schedule = get_list_predict_schedule_from_file(
        predict_schedule_result_path)
    sfh.rmfiles([predict_schedule_result_path, sgh.sparkle_err_path])

    for pred in list_predict_schedule:
        solver_path = pred[0]
        cutoff_time = pred[1]
        print(f"Calling solver {Path(solver_path).name} with "
              f"time budget {str(cutoff_time)} for solving ...")
        sys.stdout.flush()
        flag_solved = call_solver_solve_instance_within_cutoff(
            solver_path, instance_path, cutoff_time, performance_data_csv_path)
        print(f"Calling solver {Path(solver_path).name} done!")

        if flag_solved:
            break
        else:
            print("The instance is not solved in this call")

    return


def call_sparkle_portfolio_selector_solve_directory(
        instance_directory_path: str,
        run_on: Runner = Runner.SLURM) -> None:
    """Call the Sparkle portfolio selector to solve all instances in a directory.

    Args:
        instance_directory_path: The path to the directory of instances.
        run_on: Whether to run with Slurm or Local.
    """
    instance_directory_path = Path(instance_directory_path)
    instance_directory_name = instance_directory_path.name

    test_case_path = Path("Test_Cases") / instance_directory_name

    # Update latest scenario
    sgh.latest_scenario().set_selection_test_case_directory(
        test_case_path)
    sgh.latest_scenario().set_latest_scenario(Scenario.SELECTION)
    # Write used scenario to file
    sgh.latest_scenario().write_scenario_ini()
    test_case_tmp_path = test_case_path / "Tmp"
    test_case_tmp_path.mkdir(parents=True, exist_ok=True)

    test_performance_data_path = test_case_path / "sparkle_performance_data.csv"
    test_performance_data_csv = PerformanceDataFrame(test_performance_data_path)

    total_job_list = []

    list_all_filename = sih.get_instance_list_from_path(instance_directory_path)

    for filename in list_all_filename:
        test_performance_data_csv.add_instance(str(filename))
        total_job_list.append([str(filename)])

    solver_name = "Sparkle_Portfolio_Selector"
    check_selector_status(solver_name)
    test_performance_data_csv.add_solver(solver_name)

    test_performance_data_csv.save_csv()

    n_jobs = len(total_job_list)
    target_call = "python CLI/core/run_sparkle_portfolio_core.py" +\
                  f" --performance-data-csv {test_performance_data_path}"
    cmd_list = [f"{target_call} --instance {job_instance[0]}"
                for job_instance in total_job_list]
    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=CommandName.RUN_SPARKLE_PORTFOLIO_SELECTOR,
        base_dir=str(test_case_tmp_path),
        parallel_jobs=n_jobs,
        sbatch_options=ssh.get_slurm_options_list(),
        srun_options=["-N1", "-n1", "--exclusive"])

    if run_on == Runner.LOCAL:
        run.wait()


def check_selector_status(solver_name: str) -> None:
    """Check if there is a selector at the given path.

    If it does not exist the function will terminate the whole program.
    """
    selector = pathlib.Path(f"{solver_name}/sparkle_portfolio_selector__@@SPARKLE@@__")
    if not selector.exists() or not selector.is_file():
        print("ERROR: The portfolio selector could not be found. Please make sure to "
              "first construct a portfolio selector.")
        sys.exit(-1)
