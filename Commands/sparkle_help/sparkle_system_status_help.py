#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to inform about Sparkle's system status."""

import os
import time
from pathlib import Path
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_job_help
from sparkle_help import sparkle_command_help as sch


def print_solver_list(verbose: bool = False):
    """Print the list of solvers in Sparkle.

    Args:
        verbose: Indicating if output should be verbose
    """
    solver_list = sgh.solver_list
    print("")
    print("Currently Sparkle has " + str(len(solver_list)) + " solvers"
          + (":" if verbose else ""))

    if verbose:
        i = 1
        for solver in solver_list:
            print(f"[{str(i)}]: Solver: {sfh.get_last_level_directory_name(solver)}")
            i += 1

    print("")
    return


def print_extractor_list(verbose: bool = False):
    """Print the list of feature extractors in Sparkle.

    Args:
        verbose: Indicating if output should be verbose
    """
    extractor_list = sgh.extractor_list
    print("")
    print("Currently Sparkle has " + str(len(extractor_list)) + " feature extractors"
          + (":" if verbose else ""))

    if verbose:
        i = 1
        for extractor in extractor_list:
            print(
                f"[{str(i)}]: Extractor: {sfh.get_last_level_directory_name(extractor)}")
            i += 1

    print("")
    return


def print_instance_list(verbose: bool = False):
    """Print the list of instances in Sparkle.

    Args:
        verbose: Indicating, if output should be verbose
    """
    instance_list = sgh.instance_list
    print("")
    print("Currently Sparkle has " + str(len(instance_list)) + " instances"
          + (":" if verbose else ""))
    if verbose:
        i = 1
        for instance in instance_list:
            instance_dir = sfh.get_directory(instance).split("Instances/")[1][:-1]
            print(f"[{str(i)}]: [{instance_dir}] Instance: ",
                  f"{sfh.get_last_level_directory_name(instance)}")
            i += 1

    print("")
    return


def print_list_remaining_feature_computation_job(feature_data_csv_path: str,
                                                 verbose: bool = False):
    """Print a list of remaining feature computation jobs.

    Args:
        feature_data_csv_path: path to the feature data csv
        verbose: Indicating, if output should be verbose
    """
    try:
        feature_data_csv = sfdcsv.SparkleFeatureDataCSV(feature_data_csv_path)
        list_feature_computation_job = (
            feature_data_csv.get_list_remaining_feature_computation_job())
    except Exception:
        list_feature_computation_job = []
    total_job_num = sparkle_job_help.get_num_of_total_job_from_list(
        list_feature_computation_job)

    print("")
    print(f"Currently Sparkle has {str(total_job_num)} remaining feature computation "
          "jobs that need to be performed before creating an algorithm selector"
          + (":" if verbose else ""))

    if verbose:
        current_job_num = 1
        for i in range(0, len(list_feature_computation_job)):
            instance_path = list_feature_computation_job[i][0]
            extractor_list = list_feature_computation_job[i][1]
            len_extractor_list = len(extractor_list)
            for j in range(0, len_extractor_list):
                extractor_path = extractor_list[j]
                print(f"[{str(current_job_num)}]: Extractor: "
                      f"{sfh.get_last_level_directory_name(extractor_path)}, Instance: "
                      f"{sfh.get_last_level_directory_name(instance_path)}")
                current_job_num += 1

    print("")
    return


def print_list_remaining_performance_computation_job(performance_data_csv_path: str,
                                                     verbose: bool = False):
    """Print a list of remaining performance computation jobs.

    Args:
        performance_data_csv_path: path to the performance data csv
        verbose: Indicating, if output should be verbose
    """
    try:
        performance_data_csv = spdcsv.SparklePerformanceDataCSV(
            performance_data_csv_path)
        list_performance_computation_job = (
            performance_data_csv.get_list_remaining_performance_computation_job())
    except Exception:
        list_performance_computation_job = []
    total_job_num = sparkle_job_help.get_num_of_total_job_from_list(
        list_performance_computation_job)

    print("")
    print(f"Currently Sparkle has {str(total_job_num)} remaining performance computation"
          " jobs that need to be performed before creating an algorithm selector"
          + (":" if verbose else ""))

    if verbose:
        current_job_num = 1
        for i in range(0, len(list_performance_computation_job)):
            instance_path = list_performance_computation_job[i][0]
            solver_list = list_performance_computation_job[i][1]
            len_solver_list = len(solver_list)
            for j in range(0, len_solver_list):
                solver_path = solver_list[j]
                print(f"[{str(current_job_num)}]: Solver: "
                      f"{sfh.get_last_level_directory_name(solver_path)}, Instance: "
                      f"{sfh.get_last_level_directory_name(instance_path)}")
                current_job_num += 1

    print("")
    return


def print_algorithm_selector_info():
    """Print information about the Sparkle algorithm selector."""
    sparkle_algorithm_selector_path = sgh.sparkle_algorithm_selector_path
    print("")
    print("Status of algorithm selector in Sparkle:")

    key_str = "construct_sparkle_algorithm_selector"
    task_run_status_path = f"Tmp/{sgh.algorithm_selector_job_path}/{key_str}.statusinfo"
    if Path(task_run_status_path).is_file():
        print("Currently Sparkle algorithm selector is constructing ...")
    elif Path(sparkle_algorithm_selector_path).is_file():
        print(f"Path: {sparkle_algorithm_selector_path}")
        print("Last modified time: "
              f"{get_file_modify_time(sparkle_algorithm_selector_path)}")
    else:
        print("No algorithm selector exists!")
    print("")
    return


def print_parallel_portfolio_info():
    """Print information about the Sparkle parallel portfolio."""
    sparkle_parallel_portfolio_path = sgh.sparkle_parallel_portfolio_path
    print("")
    print("Status of parallel portfolio in Sparkle:")

    key_str = "construct_sparkle_parallel_portfolio"
    task_run_status_path = f"Tmp/{sgh.pap_sbatch_tmp_path}/{key_str}.statusinfo"
    if Path(task_run_status_path).is_file():
        print("Currently Sparkle parallel portfolio is constructing ...")
    elif Path(sparkle_parallel_portfolio_path).is_file():
        print(f"Path: {sparkle_parallel_portfolio_path}")
        print("Last modified time: "
              f"{get_file_modify_time(sparkle_parallel_portfolio_path)}")
    else:
        print("No parallel portfolio exists!")
    print("")
    return


def print_algorithm_configuration_info():
    """Print information about the Sparkle algorithm configuration."""
    print("")
    print("Status of algorithm configuration in Sparkle:")

    key_str = "algorithm_configuration"
    task_run_status_path = f"Tmp/{sgh.configuration_job_path}/{key_str}.statusinfo"
    if Path(task_run_status_path).is_file():
        print("Currently Sparkle configurator is constructing ...")
    elif sgh.latest_scenario is not None:
        solver = sgh.latest_scenario.get_config_solver()
        instance_set_train = sgh.latest_scenario.get_config_instance_set_train()
        last_configuration_file_path = Path(
            sgh.smac_dir,
            "example_scenarios",
            f"{solver.name}_{instance_set_train.name}",
            sgh.sparkle_last_configuration_file_name
        )
        if last_configuration_file_path.is_file():
            print(f"Path: {last_configuration_file_path}")
            print("Last modified time: "
                  f"{get_file_modify_time(last_configuration_file_path)}")
    else:
        print("No configurator exists!")
    print("")


def print_algorithm_selection_report_info():
    """Print the current status of a Sparkle algorithm selection report."""
    sparkle_report_path = Path("Components/Sparkle-latex-generator/Sparkle_Report.pdf")
    print("")
    print("Status of algorithm selection report in Sparkle:")

    key_str = f"generate_report_{sgh.ReportType.ALGORITHM_SELECTION}"
    task_run_status_path = f"Tmp/{sgh.report_job_path}/{key_str}.statusinfo"
    if Path(task_run_status_path).is_file():
        print("Currently Sparkle algorithm selection report is generating ...")
    elif Path(sparkle_report_path).is_file():
        print(f"Path :{sparkle_report_path}")
        print(f"Last modified time: {get_file_modify_time(sparkle_report_path)}")
    else:
        print("No algorithm selection report exists!")
    print("")
    return


def print_algorithm_configuration_report_info():
    """Print the current status of the Sparkle algorithm configuration report."""
    sparkle_report_base_path = Path("Configuration_Reports")
    report_file_name = \
        "Sparkle-latex-generator-for-configuration/Sparkle_Report_for_Configuration.pdf"
    print("")
    print("Status of algorithm configuration report in Sparkle:")

    key_str = f"generate_report_{sgh.ReportType.ALGORITHM_CONFIGURATION}"
    task_run_status_path = f"Tmp/{sgh.report_job_path}/{key_str}.statusinfo"
    if Path(task_run_status_path).is_file():
        print("Currently Sparkle algorithm configuration report is generating ...")
    elif sparkle_report_base_path.is_dir():
        for folder in [x for x in sparkle_report_base_path.iterdir() if x.is_dir()]:
            act_path = (folder / report_file_name)
            if act_path.is_file():
                print(f"Path: {str(act_path)}")
                print(f"Last modified time: {get_file_modify_time(act_path)}")
                print("")
    else:
        print("No algorthm configuration report exists!")
    print("")
    return


def print_parallel_portfolio_report_info():
    """Print the current status of a Sparkle parallel portfolio report."""
    sparkle_report_path = Path("Components/Sparkle-latex-generator"
                               + "-for-parallel-portfolio/template-Sparkle.pdf")
    print("")
    print("Status of parallel portfolio report in Sparkle:")

    key_str = f"generate_report_{sgh.ReportType.ALGORITHM_SELECTION}"
    task_run_status_path = f"Tmp/{sgh.report_job_path}/{key_str}.statusinfo"
    if Path(task_run_status_path).is_file():
        print("Currently Sparkle parallel portfolio report is generating ...")
    elif Path(sparkle_report_path).is_file():
        print(f"Path: {sparkle_report_path}")
        print(f"Last modified time: {get_file_modify_time(sparkle_report_path)}")
    else:
        print("No parallel portfolio report exists!")
    print("")
    return


def timestamp_to_time(timestamp) -> str:
    """Return a timestamp as a readable str."""
    time_struct = time.gmtime(timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", time_struct)


def get_file_modify_time(file_path):
    """Return the last time a file was modified."""
    timestamp = os.path.getmtime(file_path)
    return timestamp_to_time(timestamp) + " (UTC+0)"


def generate_task_run_status(command_name: sch.CommandName, job_path: Path) -> None:
    """Generate run status info files for Slurm batch jobs.

    Args:
        command_name: enum name of the executed command
        job_path: path to the commands job folder
    """
    task_run_status_path = Path(f"{job_path}/{command_name}.statusinfo")
    status_info_str = "Status: Running\n"
    sfh.write_string_to_file(task_run_status_path, status_info_str)

    return


def delete_task_run_status(command_name: sch.CommandName, job_path: Path) -> None:
    """Remove run status info files for Slurm batch jobs.

    Args:
        command_name: enum name of the executed command
        job_path: path to the commands job folder
    """
    task_run_status_path = Path(f"{job_path}/{command_name}.statusinfo")
    task_run_status_path.unlink()

    return
