#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to inform about Sparkle's system status."""

from pathlib import Path

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_file_help as sfh
from Commands.sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from Commands.sparkle_help import sparkle_performance_data_csv_help as spdcsv
from Commands.sparkle_help import sparkle_job_help


def print_solver_list(verbose: bool = False) -> None:
    """Print the list of solvers in Sparkle.

    Args:
        verbose: Indicating if output should be verbose
    """
    solver_list = sgh.solver_list
    print("")
    print("Currently Sparkle has " + str(len(solver_list)) + " solvers"
          + (":" if verbose else ""))

    if verbose:
        for i, solver in enumerate(solver_list):
            print(f"[{i + 1}]: Solver: {sfh.get_last_level_directory_name(solver)}")

    print("")
    return


def print_extractor_list(verbose: bool = False) -> None:
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


def print_instance_list(verbose: bool = False) -> None:
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
            instance_dir = Path(instance).parent
            print(f"[{str(i)}]: [{instance_dir}] Instance: ",
                  f"{sfh.get_last_level_directory_name(instance)}")
            i += 1

    print("")
    return


def print_list_remaining_feature_computation_job(feature_data_csv_path: str,
                                                 verbose: bool = False) -> None:
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
        for job in list_feature_computation_job:
            instance_path = job[0]
            extractor_list = job[1]
            for extractor_path in extractor_list:
                print(f"[{current_job_num}]: Extractor: "
                      f"{Path(extractor_path).name}, Instance: "
                      f"{Path(instance_path).name}")
                current_job_num += 1

    print("")
    return


def print_list_remaining_performance_computation_job(performance_data_csv_path: str,
                                                     verbose: bool = False) -> None:
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
        for job in list_performance_computation_job:
            instance_path = job[0]
            solver_list = job[1]
            for solver_path in solver_list:
                print(f"[{current_job_num}]: Solver: "
                      f"{Path(solver_path).name}, Instance: "
                      f"{Path(instance_path).name}")
                current_job_num += 1

    print("")
    return
