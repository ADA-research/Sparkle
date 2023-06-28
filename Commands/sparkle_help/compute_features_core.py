#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Compute features for an instance, only for internal calls from Sparkle."""

import os
import time
import argparse
from pathlib import Path
from pathlib import PurePath

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_basic_help
from Commands.sparkle_help import sparkle_file_help as sfh
from Commands.sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from Commands.sparkle_help import sparkle_compute_features_help as scf
from Commands.sparkle_help import sparkle_settings


if __name__ == "__main__":
    # Initialise settings
    global settings
    settings_dir = Path("Settings")
    file_path_latest = PurePath(settings_dir / "latest.ini")
    sgh.settings = sparkle_settings.Settings(file_path_latest)

    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", required=False, type=str, nargs="+",
                        help="path to instance file(s) to run on")
    parser.add_argument("--extractor", required=True, type=str,
                        help="path to feature extractor")
    parser.add_argument("--feature-csv", required=True, type=str,
                        help="path to feature data CSV file")
    args = parser.parse_args()

    # Process command line arguments
    # Turn multiple instance files into a space separated string
    instance_path = Path(" ".join(args.instance))
    extractor_path = Path(args.extractor)
    feature_data_csv_path = Path(args.feature_csv)

    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(feature_data_csv_path)
    runsolver_path = sgh.runsolver_path

    if len(sgh.extractor_list) == 0:
        cutoff_time_each_extractor_run = sgh.settings.get_general_extractor_cutoff_time()
    else:
        cutoff_time_each_extractor_run = (
            sgh.settings.get_general_extractor_cutoff_time() / len(sgh.extractor_list))

    cutoff_time_each_run_option = "--cpu-limit " + str(cutoff_time_each_extractor_run)

    key_str = (f"{sfh.get_last_level_directory_name(extractor_path)}_"
               f"{sfh.get_last_level_directory_name(instance_path)}_"
               f"{sparkle_basic_help.get_time_pid_random_string()}")
    result_path = Path(f"Feature_Data/Tmp/{key_str}.csv")
    basic_part = "Tmp/" + key_str
    err_path = basic_part + ".err"
    runsolver_watch_data_path = basic_part + ".log"
    runsolver_watch_data_path_option = "-w " + runsolver_watch_data_path
    command_line = (f"{runsolver_path} {cutoff_time_each_run_option} "
                    f"{runsolver_watch_data_path_option} {extractor_path}/"
                    f"{sgh.sparkle_run_default_wrapper} {extractor_path}/ "
                    f"{instance_path} {result_path} 2> {err_path}")

    try:
        task_run_status_path = "Tmp/SBATCH_Extractor_Jobs/" + key_str + ".statusinfo"
        status_info_str = (
            "Status: Running\nExtractor: "
            f"{sfh.get_last_level_directory_name(extractor_path)}\n"
            f"Instance: {sfh.get_last_level_directory_name(instance_path)}\n")

        start_time = time.time()
        status_info_str += (
            "Start Time: "
            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}\n")
        status_info_str += "Start Timestamp: " + str(start_time) + "\n"
        cutoff_str = f"Cutoff Time: {str(cutoff_time_each_extractor_run)} second(s)\n"
        status_info_str += cutoff_str
        sfh.write_string_to_file(task_run_status_path, status_info_str)
        os.system(command_line)
        end_time = time.time()
    except Exception:
        if not Path(result_path).exists():
            sfh.create_new_empty_file(result_path)

    try:
        tmp_fdcsv = sfdcsv.SparkleFeatureDataCSV(result_path)
        result_string = "Successful"
    except Exception:
        print(f"****** WARNING: Feature vector computing on instance {instance_path}"
              " failed! ******")
        print("****** WARNING: The feature vector of this instace consists of missing "
              "values ******")

        command_line = "rm -f " + result_path
        os.system(command_line)
        tmp_fdcsv = scf.generate_missing_value_csv_like_feature_data_csv(
            feature_data_csv, instance_path, extractor_path, result_path)
        result_string = "Failed -- using missing value instead"

    description_str = (
        f"[Extractor: {sfh.get_last_level_directory_name(extractor_path)},"
        f" Instance: {sfh.get_last_level_directory_name(instance_path)}]")
    start_time_str = (
        "[Start Time: "
        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}]")
    end_time_str = (
        f"[End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}]")
    run_time_str = "[Actual Run Time: " + str(end_time - start_time) + " second(s)]"
    result_string_str = "[Result String: " + result_string + "]"

    log_str = (f"{description_str}, {start_time_str}, {end_time_str}, {run_time_str}, "
               f"{result_string_str}")

    sfh.append_string_to_file(sgh.sparkle_system_log_path, log_str)
    os.system("rm -f " + task_run_status_path)

    tmp_fdcsv.save_csv(result_path)

    command_line = "rm -f " + err_path
    os.system(command_line)
    command_line = "rm -f " + runsolver_watch_data_path
    os.system(command_line)
