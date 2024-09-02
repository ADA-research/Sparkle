#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions to inform about Sparkle's system status."""
from pathlib import Path

from sparkle.structures import FeatureDataFrame, PerformanceDataFrame


def print_sparkle_list(objects: list[any], type: str, details: bool = False) -> None:
    """Print a list of sparkle objects.

    Args:
        objects: The objects to print
        type: The name of the object type
        details: Indicating if output should be detailed
    """
    print(f"\nCurrently Sparkle has {len(objects)} {type}(s)"
          + (":" if details else ""))

    if details:
        for i, object in enumerate(objects):
            print(f"[{i + 1}]: {type}: {Path(object).name}")


def print_feature_computation_jobs(feature_data_csv: Path,
                                   verbose: bool = False) -> None:
    """Print a list of remaining feature computation jobs.

    Args:
        feature_data_csv: Path to the feature data csv
        verbose: Indicating, if output should be verbose
    """
    if not feature_data_csv.exists():
        print("\nNo feature data found, cannot determine remaining jobs.")

    feature_data = FeatureDataFrame(feature_data_csv)
    jobs = feature_data.remaining_jobs()

    print(f"\nCurrently Sparkle has {len(jobs)} remaining feature computation "
          "jobs that need to be performed before creating an algorithm selector"
          + (":" if verbose else ""))

    if verbose:
        for i, job in enumerate(jobs):
            print(f"[{i + 1}]: Extractor: {Path(job[1]).name}, Group: {job[2]}, "
                  f"Instance: {Path(job[0]).name}")
    print()


def print_performance_computation_jobs(performance_data_csv_path: Path,
                                       verbose: bool = False) -> None:
    """Print a list of remaining performance computation jobs.

    Args:
        performance_data_csv_path: Path to the performance data csv
        verbose: Indicating, if output should be verbose
    """
    if not performance_data_csv_path.exists():
        print("\nNo performance data found, cannot determine remaining jobs.")
        return
    performance_data_csv = PerformanceDataFrame(performance_data_csv_path)
    jobs = performance_data_csv.remaining_jobs()
    total_job_num = sum([len(jobs[instance]) for instance in jobs.keys()])

    print(f"\nCurrently Sparkle has {total_job_num} remaining performance computation"
          " jobs that need to be performed before creating an algorithm selector"
          + (":" if verbose else ""))

    if verbose:
        i = 0
        for instance in jobs.keys():
            for extractor in jobs[instance]:
                print(f"[{i + 1}]: Solver: "
                      f"{Path(extractor).name}, Instance: "
                      f"{Path(instance).name}")
                i += 1

    print()
