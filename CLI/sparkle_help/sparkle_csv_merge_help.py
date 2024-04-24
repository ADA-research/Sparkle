#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Merge new performance/feature data into CSVs, only for internal calls from Sparkle."""
#Team1
import fcntl
from pathlib import Path

from CLI.sparkle_help import sparkle_global_help as sgh
from CLI.sparkle_help import sparkle_file_help as sfh
from sparkle.sparkle.structures import feature_data_csv_help as sfdcsv
from sparkle.sparkle_performance_dataframe import PerformanceDataFrame


def feature_data_csv_merge() -> None:
    """Merge feature data of new results into the main feature data CSV."""
    try:
        feature_data_csv = sfdcsv.SparkleFeatureDataCSV(
            sgh.feature_data_csv_path)
        tmp_feature_data_csv_directory = sgh.feature_data_dir / "Tmp"
        csv_list = sfh.get_list_all_extensions(tmp_feature_data_csv_directory, "csv")
    except Exception:
        return
    for csv_name in csv_list:
        tmp_feature_data_csv = sfdcsv.SparkleFeatureDataCSV(str(csv_name))
        feature_data_csv.combine(tmp_feature_data_csv)
        feature_data_csv.save_csv()
        Path(csv_name).unlink(missing_ok=True)
    return


def performance_data_csv_merge() -> None:
    """Merge performance data of new results into the main performance data CSV."""
    try:
        performance_data_csv = PerformanceDataFrame(
            sgh.performance_data_csv_path)
        tmp_performance_data_result_directory = sgh.performance_data_dir / "Tmp"
        result_list = sfh.get_list_all_extensions(
            tmp_performance_data_result_directory, "result")
    except Exception:
        return

    wrong_solver_list = []

    for result_path in result_list:
        try:
            with Path(result_path).open("r+") as fin:
                fcntl.flock(fin.fileno(), fcntl.LOCK_EX)
                instance_path = fin.readline().strip()
                if not instance_path:
                    continue
                solver_path = fin.readline().strip()
                if not solver_path:
                    continue
                runtime_str = fin.readline().strip()
                if not runtime_str:
                    continue
                runtime = float(runtime_str)
                performance_data_csv.set_value(runtime, solver_path, instance_path)
            performance_data_csv.save_csv()
            sfh.rmfiles(result_path)
        except Exception:
            print(f"ERROR: Could not remove file: {result_path}")
    for wrong_solver_path in wrong_solver_list:
        performance_data_csv.remove_solver(wrong_solver_path)
        performance_data_csv.save_csv()
        sfh.add_remove_platform_item(wrong_solver_path,
                                     sgh.solver_list_path,
                                     remove=True)
        sfh.add_remove_platform_item(None,
                                     sgh.solver_nickname_list_path,
                                     key=wrong_solver_path,
                                     remove=True)

    return


if __name__ == "__main__":
    feature_data_csv_merge()
    performance_data_csv_merge()
