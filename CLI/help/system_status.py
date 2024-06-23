#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to inform about Sparkle's system status."""
from pathlib import Path

from sparkle.structures import feature_data_csv_help as sfdcsv
from sparkle.structures.performance_dataframe import PerformanceDataFrame
from CLI.support import sparkle_job_help


def print_sparkle_list(objects: list[str], type: str, details: bool = False) -> None:
    """Print a list of sparkle objects.

    Args:
        objects: The objects to print
        type: The name of the object type
        details: Indicating if output should be detailed
    """
    print()
    print(f"\nCurrently Sparkle has {len(objects)} {type}(s)"
          + (":" if details else ""))

    if details:
        for i, object in enumerate(objects):
            print(f"[{i + 1}]: {type}: {Path(object).name}")

    print()


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

    print(f"\nCurrently Sparkle has {str(total_job_num)} remaining feature computation "
          "jobs that need to be performed before creating an algorithm selector"
          + (":" if verbose else ""))

    if verbose:
        for index, job in enumerate(list_feature_computation_job):
            instance_path, extractor_list = job[0], job[1]
            for extractor_path in extractor_list:
                print(f"[{index + 1}]: Extractor: "
                      f"{Path(extractor_path).name}, Instance: "
                      f"{Path(instance_path).name}")
    print()


def print_list_remaining_performance_computation_job(performance_data_csv_path: str,
                                                     verbose: bool = False) -> None:
    """Print a list of remaining performance computation jobs.

    Args:
        performance_data_csv_path: path to the performance data csv
        verbose: Indicating, if output should be verbose
    """
    try:
        performance_data_csv = PerformanceDataFrame(performance_data_csv_path)
        list_performance_computation_job = (
            performance_data_csv.get_list_remaining_performance_computation_job())
    except Exception:
        list_performance_computation_job = []
    total_job_num = sparkle_job_help.get_num_of_total_job_from_list(
        list_performance_computation_job)

    print()
    print(f"Currently Sparkle has {str(total_job_num)} remaining performance computation"
          " jobs that need to be performed before creating an algorithm selector"
          + (":" if verbose else ""))

    if verbose:
        for index, job in enumerate(list_performance_computation_job):
            instance_path, solver_list = job[0], job[1]
            for solver_path in solver_list:
                print(f"[{index + 1}]: Solver: "
                      f"{Path(solver_path).name}, Instance: "
                      f"{Path(instance_path).name}")

    print()
