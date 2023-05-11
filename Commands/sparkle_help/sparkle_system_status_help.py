#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to inform about Sparkle's sytem status."""

import os
import time
from pathlib import Path
from sparkle_help import sparkle_global_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_job_help


def print_solver_list(mode: int = 1):
    """Print the list of solvers in Sparkle."""
    solver_list = sparkle_global_help.solver_list
    print("")
    print("Currently Sparkle has " + str(len(solver_list)) + " solvers:")

    if mode == 2:
        i = 1
        for solver in solver_list:
            print(f"[{str(i)}]: Solver: {sfh.get_last_level_directory_name(solver)}")
            i += 1

    print("")
    return


def print_extractor_list(mode: int = 1):
    """Print the list of feature extractors in Sparkle."""
    extractor_list = sparkle_global_help.extractor_list
    print("")
    print("Currently Sparkle has " + str(len(extractor_list)) + " feature extractors:")

    if mode == 2:
        i = 1
        for extractor in extractor_list:
            print(
                f"[{str(i)}]: Extractor: {sfh.get_last_level_directory_name(extractor)}")
            i += 1

    print("")
    return


def print_instance_list(mode: int = 1):
    """Print the list of instances in Sparkle."""
    instance_list = sparkle_global_help.instance_list
    print("")
    print("Currently Sparkle has " + str(len(instance_list)) + " instances:")

    if mode == 2:
        i = 1
        for instance in instance_list:
            print(f"[{str(i)}]: Instance: {sfh.get_last_level_directory_name(instance)}")
            i += 1

    print("")
    return


def print_list_remaining_feature_computation_job(feature_data_csv_path, mode: int = 1):
    """Print a list of remaining feature computation jobs."""
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
          "jobs needed to be performed:")

    if mode == 2:
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


def print_list_remaining_performance_computation_job(performance_data_csv_path,
                                                     mode: int = 1):
    """Print a list of remaining performance computation jobs."""
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
          " jobs needed to be performed:")

    if mode == 2:
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


def print_portfolio_selector_info():
    """Print information about the Sparkle portfolio selector."""
    sparkle_portfolio_selector_path = sparkle_global_help.sparkle_portfolio_selector_path
    print("")
    print("Status of portfolio selector in Sparkle:")

    key_str = "construct_sparkle_portfolio_selector"
    task_run_status_path = "Tmp/SBATCH_Portfolio_Jobs/" + key_str + ".statusinfo"
    if Path(task_run_status_path).is_file():
        print("Currently Sparkle portfolio selector is constructing ...")
    elif Path(sparkle_portfolio_selector_path).is_file():
        print("Path: " + sparkle_portfolio_selector_path)
        print("Last modified time: "
              f"{get_file_modify_time(sparkle_portfolio_selector_path)}")
    else:
        print("No portfolio selector exists!")
    print("")
    return


def print_report_info():
    """Print the current status of a the Sparkle algorithm selection report."""
    sparkle_report_path = sparkle_global_help.sparkle_report_path
    print("")
    print("Status of report in Sparkle:")

    key_str = "generate_report"
    task_run_status_path = "Tmp/SBATCH_Report_Jobs/" + key_str + ".statusinfo"
    if Path(task_run_status_path).is_file():
        print("Currently Sparkle report is generating ...")
    elif Path(sparkle_report_path).is_file():
        print("Path: " + sparkle_report_path)
        print("Last modified time: " + get_file_modify_time(sparkle_report_path))
    else:
        print("No report exists!")
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
