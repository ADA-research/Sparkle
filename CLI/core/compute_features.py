#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Compute features for an instance, only for internal calls from Sparkle."""

import subprocess
import time
import argparse
from pathlib import Path
from pathlib import PurePath

import global_variables as sgh
from sparkle.platform import file_help as sfh, settings_help
from sparkle.structures import feature_data_csv_help as sfdcsv
from sparkle.instance import compute_features_help as scf

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

    # TODO: Handle multi-file instances
    key_str = (f"{extractor_path.name}_"
               f"{instance_path.name}_"
               f"{sgh.get_time_pid_random_string()}")
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
        task_run_status_path = f"Tmp/SBATCH_Extractor_Jobs/{key_str}.statusinfo"
        status_info_str = (
            "Status: Running\nExtractor: "
            f"{extractor_path.name}\n"
            f"Instance: {instance_path.name}\n")

        start_time = time.time()
        status_info_str += (
            "Start Time: "
            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}\n")
        status_info_str += "Start Timestamp: " + str(start_time) + "\n"
        cutoff_str = f"Cutoff Time: {str(cutoff_time_each_extractor_run)} second(s)\n"
        status_info_str += cutoff_str
        sfh.write_string_to_file(task_run_status_path, status_info_str)
        subprocess.run(command_line.split(" "))
        end_time = time.time()
    except Exception:
        if not Path(result_path).exists():
            sfh.create_new_empty_file(result_path)

    try:
        tmp_fdcsv = sfdcsv.SparkleFeatureDataCSV(result_path)
        result_string = "Successful"
    except Exception:
        print(f"****** WARNING: Feature vector computation on instance {instance_path}"
              " failed! ******")
        print("****** WARNING: The feature vector of this instace consists of missing "
              "values ******")

        result_path.unlink(missing_ok=True)
        tmp_fdcsv = scf.generate_missing_value_csv_like_feature_data_csv(
            feature_data_csv, instance_path, extractor_path, result_path)
        result_string = "Failed -- using missing value instead"

    # TODO: Handle multi-file instances
    description_str = (
        f"[Extractor: {extractor_path.name},"
        f" Instance: {instance_path.name}]")
    start_time_str = (
        "[Start Time: "
        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}]")
    end_time_str = (
        f"[End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}]")
    run_time_str = f"[Actual Run Time: {end_time - start_time} second(s)]"
    result_string_str = f"[Result String: {result_string}]"

    log_str = (f"{description_str}, {start_time_str}, {end_time_str}, {run_time_str}, "
               f"{result_string_str}")
    sfh.write_string_to_file(sgh.sparkle_system_log_path, log_str, append=True)
    tmp_fdcsv.save_csv(result_path)
    sfh.rmfiles([task_run_status_path, err_path, runsolver_watch_data_path])
