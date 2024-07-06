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
from sparkle.structures import feature_dataframe as sfdcsv
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
    has_instance_set = False
    if not instance_path.exists():
        # If its an instance name (Multi-file instance), retrieve path list
        instance_set = InstanceSet(instance_path.parent)
        instance_path = instance_set.get_path_by_name(instance_name)
        has_instance_set = True

    extractor_path = Path(args.extractor)
    feature_data_csv_path = Path(args.feature_csv)
    cutoff_time_each_extractor_run = gv.settings.get_general_extractor_cutoff_time()

    key_str = (f"{extractor_path.name}_"
               f"{instance_name}_"
               f"{tg.get_time_pid_random_string()}")
    result_path = Path(f"Feature_Data/{key_str}.csv")
    runsolver_watch_data_path = f"{result_path}.log"
    # Ensure stringifcation of path objects
    if isinstance(instance_path, list):
        instance_list = [str(filepath) for filepath in instance_path]
    else:
        instance_list = [instance_path]
    cmd = [gv.runsolver_path,
           "--cpu-limit", str(cutoff_time_each_extractor_run),
           "-w", runsolver_watch_data_path,
           extractor_path / gv.sparkle_extractor_wrapper,
           "-extractor_dir", extractor_path,
           "-instance_file"] + instance_list + ["-output_file", result_path]
    start_time = time.time()

    task_run_status_path = f"Tmp/SBATCH_Extractor_Jobs/{key_str}.statusinfo"
    status_info_str = (
        "Status: Running\nExtractor: "
        f"{extractor_path.name}\n"
        f"Instance: {instance_name}\n")
    status_info_str += (
        "Start Time: "
        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}\n")
    status_info_str += "Start Timestamp: " + str(start_time) + "\n"
    cutoff_str = f"Cutoff Time: {cutoff_time_each_extractor_run} second(s)\n"
    status_info_str += cutoff_str
    cmd_str = " ".join([str(c) for c in cmd])
    subprocess.run(cmd, capture_output=True)
    end_time = time.time()

    # Now that we have our result, we write it to the FeatureDataCSV with a FileLock
    lock = FileLock(f"{feature_data_csv_path}.lock")
    try:
        tmp_fdcsv = sfdcsv.FeatureDataFrame(result_path,
                                                 gv.extractor_list)
        # rename row
        if not has_instance_set:
            tmp_fdcsv.dataframe = tmp_fdcsv.dataframe.set_axis(
                [str(instance_path)], axis=0)
        else:
            tmp_fdcsv.dataframe = tmp_fdcsv.dataframe.set_axis(
                [instance_set.directory / instance_name], axis=0)
        with lock.acquire(timeout=60):
            feature_data_csv = sfdcsv.FeatureDataFrame(feature_data_csv_path)
            feature_data_csv.combine(tmp_fdcsv)
            feature_data_csv.save_csv()
        result_string = "Successful"
    except Exception as ex:
        print(f"EXCEPTION during retrieving extractor results: {ex}")
        print(f"****** WARNING: Feature vector computation on instance {instance_path}"
              " failed! ******")
        print(f"****** WARNING: The feature vector in {result_path} of this instance "
              "consists of missing values ******")
        length = int(gv.extractor_feature_vector_size_mapping[str(extractor_path)])
        missing_values_row = [sfdcsv.FeatureDataFrame.missing_value] * length
        with lock.acquire(timeout=60):
            feature_data_csv = sfdcsv.FeatureDataFrame(feature_data_csv_path,
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
    sfh.rmfiles([task_run_status_path, runsolver_watch_data_path])
