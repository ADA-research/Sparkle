#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for feature data computation."""

import os
import sys

try:
    from sparkle_help import sparkle_global_help as sgh
    from sparkle_help import sparkle_basic_help
    from sparkle_help import sparkle_file_help as sfh
    from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
    from sparkle_help import sparkle_job_help
except ImportError:
    import sparkle_global_help as sgh
    import sparkle_basic_help
    import sparkle_file_help as sfh
    import sparkle_feature_data_csv_help as sfdcsv
    import sparkle_job_help


def generate_missing_value_csv_like_feature_data_csv(feature_data_csv, instance_path,
                                                     extractor_path, result_path):
    """Create a CSV file with the right number of commas and rows."""
    sfdcsv.SparkleFeatureDataCSV.create_empty_csv(result_path)
    zero_value_csv = sfdcsv.SparkleFeatureDataCSV(result_path)

    for column_name in feature_data_csv.list_columns():
        zero_value_csv.add_column(column_name)

    length = int(sgh.extractor_feature_vector_size_mapping[extractor_path])
    value_list = [sgh.sparkle_missing_value] * length

    zero_value_csv.add_row(instance_path, value_list)

    return zero_value_csv


def computing_features(feature_data_csv_path, mode):
    """Compute features for all instance and feature extractor combinations."""
    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(feature_data_csv_path)
    if mode == 1:
        list_feature_computation_job = (
            feature_data_csv.get_list_remaining_feature_computation_job())
    elif mode == 2:
        list_feature_computation_job = (
            feature_data_csv.get_list_recompute_feature_computation_job())
    else:
        print("Computing features mode error!")
        print("Do not compute features")
        sys.exit()

    runsolver_path = sgh.runsolver_path
    if len(sgh.extractor_list) == 0:
        cutoff_time_each_extractor_run = sgh.settings.get_general_extractor_cutoff_time()
    else:
        cutoff_time_each_extractor_run = (
            sgh.settings.get_general_extractor_cutoff_time() / len(sgh.extractor_list))
    cutoff_time_each_run_option = r"--cpu-limit " + str(cutoff_time_each_extractor_run)
    print("Cutoff time for each run on computing features is set to "
          f"{str(cutoff_time_each_extractor_run)} seconds")

    total_job_num = sparkle_job_help.get_num_of_total_job_from_list(
        list_feature_computation_job)

    # If there are no jobs, stop
    if total_job_num < 1:
        print("No feature computation jobs to run; stopping execution! To recompute "
              "feature values use the --recompute flag.")
        sys.exit()
    # If there are jobs update feature data ID
    else:
        update_feature_data_id()

    current_job_num = 1
    print("The number of total running jobs: " + str(total_job_num))

    for i in range(0, len(list_feature_computation_job)):
        instance_path = list_feature_computation_job[i][0]
        extractor_list = list_feature_computation_job[i][1]
        len_extractor_list = len(extractor_list)
        for j in range(0, len_extractor_list):
            extractor_path = extractor_list[j]
            basic_part = (f"Tmp/{sfh.get_last_level_directory_name(extractor_path)}_"
                          f"{sfh.get_last_level_directory_name(instance_path)}_"
                          f"{sparkle_basic_help.get_time_pid_random_string()}")
            result_path = f"{basic_part}.rawres"
            err_path = f"{basic_part}.err"
            runsolver_watch_data_path = f"{basic_part}.log"
            runsolver_watch_data_path_option = f"-w {runsolver_watch_data_path}"
            runsolver_value_data_path = result_path.replace(".rawres", ".val")
            runsolver_value_data_path_option = f"-v {runsolver_value_data_path}"

            command_line = (f"{runsolver_path} {cutoff_time_each_run_option} "
                            f"{runsolver_watch_data_path_option} "
                            f"{runsolver_value_data_path_option} {extractor_path}/"
                            f"{sgh.sparkle_run_default_wrapper} {extractor_path}/ "
                            f"{instance_path} {result_path} 2> {err_path}")

            print("")
            print(f"Extractor {sfh.get_last_level_directory_name(extractor_path)}"
                  " computing feature vector of instance "
                  f"{sfh.get_last_level_directory_name(instance_path)} ...")

            try:
                os.system(command_line)
                with open(runsolver_value_data_path) as file:
                    if "TIMEOUT=true" in file.read():
                        print(f"****** WARNING: Feature vector computing on instance "
                              f"{instance_path} timed out! ******")
            except Exception:
                if not os.path.exists(result_path):
                    sfh.create_new_empty_file(result_path)

            try:
                tmp_fdcsv = sfdcsv.SparkleFeatureDataCSV(result_path)
            except Exception:
                print("****** WARNING: Feature vector computing on instance "
                      f"{instance_path} failed! ******")
                print("****** WARNING: The feature vector of this instace consists of "
                      "missing values ******")
                command_line = "rm -f " + result_path
                os.system(command_line)
                tmp_fdcsv = generate_missing_value_csv_like_feature_data_csv(
                    feature_data_csv, instance_path, extractor_path, result_path)

            feature_data_csv.combine(tmp_fdcsv)

            command_line = f"rm -f {result_path}"
            os.system(command_line)
            command_line = f"rm -f {err_path}"
            os.system(command_line)
            command_line = f"rm -f {runsolver_watch_data_path}"
            os.system(command_line)
            command_line = f"rm -f {runsolver_value_data_path}"
            os.system(command_line)

            print(f"Executing Progress: {str(current_job_num)} out of "
                  f"{str(total_job_num)}")
            current_job_num += 1

            feature_data_csv.update_csv()

            print(f"Extractor {sfh.get_last_level_directory_name(extractor_path)}"
                  " computing feature vector of instance "
                  f"{sfh.get_last_level_directory_name(instance_path)} done!\n")

    return


def update_feature_data_id():
    """Update the feature data ID."""
    # Get current fd_id
    fd_id = get_feature_data_id()

    # Increment fd_id
    fd_id = fd_id + 1

    # Write new fd_id
    fd_id_path = sgh.feature_data_id_path

    with open(fd_id_path, "w") as fd_id_file:
        fd_id_file.write(str(fd_id))

    return


def get_feature_data_id() -> int:
    """Return the current feature data ID."""
    fd_id = -1
    fd_id_path = sgh.feature_data_id_path

    try:
        with open(fd_id_path, "r") as fd_id_file:
            fd_id = int(fd_id_file.readline())
    except FileNotFoundError:
        fd_id = 0

    return fd_id
