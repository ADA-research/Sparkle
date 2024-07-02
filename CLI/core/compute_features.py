#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Compute features for an instance, only for internal calls from Sparkle."""

import subprocess
import time
import argparse
from pathlib import Path, PurePath
from filelock import FileLock

import global_variables as gv
import tools.general as tg
from sparkle.platform import file_help as sfh, settings_help
from sparkle.structures import feature_data_csv_help as sfdcsv
from sparkle.instance import InstanceSet

if __name__ == "__main__":
    # Initialise settings
    global settings
    settings_dir = Path("Settings")
    file_path_latest = PurePath(settings_dir / "latest.ini")
    gv.settings = settings_help.Settings(file_path_latest)

    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", required=True, type=str,
                        help="path to instance file(s) to run on")
    parser.add_argument("--extractor", required=True, type=str,
                        help="path to feature extractor")
    parser.add_argument("--feature-csv", required=True, type=str,
                        help="path to feature data CSV file")
    args = parser.parse_args()

    # Process command line arguments
    instance_path = Path(args.instance)
    instance_name = instance_path.name
    if not instance_path.exists():
        # If its an instance name (Multi-file instance), retrieve path list
        instance_set = InstanceSet(instance_path.parent)
        instance_path = instance_set.get_path_by_name(instance_name)

    extractor_path = Path(args.extractor)
    feature_data_csv_path = Path(args.feature_csv)

    if len(gv.extractor_list) == 0:
        cutoff_time_each_extractor_run = gv.settings.get_general_extractor_cutoff_time()
    else:
        cutoff_time_each_extractor_run = (
            gv.settings.get_general_extractor_cutoff_time() / len(gv.extractor_list))

    cutoff_time_each_run_option = "--cpu-limit " + str(cutoff_time_each_extractor_run)

    key_str = (f"{extractor_path.name}_"
               f"{instance_name}_"
               f"{tg.get_time_pid_random_string()}")
    result_path = Path(f"Feature_Data/{key_str}.csv")
    runsolver_watch_data_path = f"{result_path}.log"
    runsolver_watch_data_path_option = "-w " + runsolver_watch_data_path
    # Ensure stringifcation of path objects
    if isinstance(instance_path, list):
        instance_path = " ".join([str(filepath) for filepath in instance_path])
    cmd = [gv.runsolver_path, cutoff_time_each_run_option,
           runsolver_watch_data_path_option,
           extractor_path / gv.sparkle_extractor_wrapper,
           "-extractor_dir", extractor_path,
           "-instance_file", instance_path,
           "-output_file", result_path]
    print(" ".join([str(c) for c in cmd]))
    start_time = time.time()
    try:
        task_run_status_path = f"Tmp/SBATCH_Extractor_Jobs/{key_str}.statusinfo"
        status_info_str = (
            "Status: Running\nExtractor: "
            f"{extractor_path.name}\n"
            f"Instance: {instance_path.name}\n")
        status_info_str += (
            "Start Time: "
            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}\n")
        status_info_str += "Start Timestamp: " + str(start_time) + "\n"
        cutoff_str = f"Cutoff Time: {str(cutoff_time_each_extractor_run)} second(s)\n"
        status_info_str += cutoff_str
        sfh.write_string_to_file(task_run_status_path, status_info_str)
        r = subprocess.run(cmd, capture_output=True)
        print(r.stderr.decode())
        print(r.stdout.decode())
    except Exception:
        if not Path(result_path).exists():
            sfh.create_new_empty_file(result_path)
    end_time = time.time()

    # Now that we have our result, we write it to the FeatureDataCSV with a FileLock
    lock = FileLock(f"{feature_data_csv_path}.lock")
    try:
        tmp_fdcsv = sfdcsv.SparkleFeatureDataCSV(result_path,
                                                 gv.extractor_list)
        feature_vector = tmp_fdcsv.get_value(tmp_fdcsv.list_rows()[0])
        with lock.acquire(timeout=60):
            feature_data_csv = sfdcsv.SparkleFeatureDataCSV(feature_data_csv_path)
            #feature_data_csv.combine(tmp_fdcsv)
            feature_data_csv.set_value(instance_name, None, feature_vector)
            feature_data_csv.save_csv()
        result_string = "Successful"
    except Exception:
        print(f"****** WARNING: Feature vector computation on instance {instance_path}"
              " failed! ******")
        print(f"****** WARNING: The feature vector in {result_path} of this instance "
              "consists of missing values ******")
        length = int(gv.extractor_feature_vector_size_mapping[str(extractor_path)])
        missing_values_row = [sfdcsv.SparkleFeatureDataCSV.missing_value] * length
        with lock.acquire(timeout=60):
            feature_data_csv = sfdcsv.SparkleFeatureDataCSV(feature_data_csv_path,
                                                            gv.extractor_list)
            feature_data_csv.set_value(instance_name, None, missing_values_row)
            feature_data_csv.save_csv()
        result_string = "Failed -- using missing value instead"
    lock.release()
    result_path.unlink(missing_ok=True)

    description_str = f"[Extractor: {extractor_path.name}, Instance: {instance_name}]"
    start_time_str = (
        "[Start Time: "
        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}]")
    end_time_str = (
        f"[End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}]")
    run_time_str = f"[Actual Run Time: {end_time - start_time} second(s)]"
    result_string_str = f"[Result String: {result_string}]"

    log_str = (f"{description_str}, {start_time_str}, {end_time_str}, {run_time_str}, "
               f"{result_string_str}")
    sfh.write_string_to_file(gv.sparkle_system_log_path, log_str, append=True)
    sfh.rmfiles([task_run_status_path, runsolver_watch_data_path])
