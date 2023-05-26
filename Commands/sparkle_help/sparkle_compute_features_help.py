#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for feature data computation."""

import os
import sys
from pathlib import Path

try:
    from sparkle_help import sparkle_global_help as sgh
    from sparkle_help import sparkle_basic_help
    from sparkle_help import sparkle_file_help as sfh
    from sparkle_help import sparkle_slurm_help as ssh
    from sparkle_help import sparkle_logging as sl
    from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
    from sparkle_help import sparkle_job_help
    from sparkle_help.sparkle_command_help import CommandName
except ImportError:
    import sparkle_global_help as sgh
    import sparkle_basic_help
    import sparkle_file_help as sfh
    import sparkle_slurm_help as ssh
    import sparkle_logging as sl
    import sparkle_feature_data_csv_help as sfdcsv
    import sparkle_job_help
    from sparkle_command_help import CommandName


def generate_missing_value_csv_like_feature_data_csv(
        feature_data_csv: sfdcsv.SparkleFeatureDataCSV,
        instance_path: Path,
        extractor_path: Path,
        result_path: Path) -> sfdcsv.SparkleFeatureDataCSV:
    """Create a CSV file with the right number of commas and rows.

    Args:
        feature_data_csv: the feature data csv
        instance_path: path to the instance
        extractor_path: path to the extractor
        result_path:: path for storing the results
    Returns:
        zero_value_csv: a new csv filled with zero values
    """
    sfdcsv.SparkleFeatureDataCSV.create_empty_csv(result_path)
    zero_value_csv = sfdcsv.SparkleFeatureDataCSV(result_path)

    for column_name in feature_data_csv.list_columns():
        zero_value_csv.add_column(column_name)

    length = int(sgh.extractor_feature_vector_size_mapping[extractor_path])
    value_list = [sgh.sparkle_missing_value] * length

    zero_value_csv.add_row(instance_path, value_list)

    return zero_value_csv


def computing_features(feature_data_csv_path: Path, recompute: bool) -> None:
    """Compute features for all instance and feature extractor combinations.

    Args:
        feature_data_csv_path: path of feature data csv
        recompute: boolean indicating if features should be recomputed

    """

    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(feature_data_csv_path)
    list_feature_computation_job = get_feature_computation_job_list(
        feature_data_csv, recompute)

    runsolver_path = sgh.runsolver_path
    if len(sgh.extractor_list) == 0:
        cutoff_time_each_extractor_run = sgh.settings.get_general_extractor_cutoff_time()
    else:
        cutoff_time_each_extractor_run = (
                sgh.settings.get_general_extractor_cutoff_time() / len(
            sgh.extractor_list))
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
                with Path(runsolver_value_data_path).open() as file:
                    if "TIMEOUT=true" in file.read():
                        print(f"****** WARNING: Feature vector computing on instance "
                              f"{instance_path} timed out! ******")
            except Exception:
                if not Path(result_path).exists():
                    sfh.create_new_empty_file(result_path)

            try:
                tmp_fdcsv = sfdcsv.SparkleFeatureDataCSV(result_path)
            except Exception:
                print("****** WARNING: Feature vector computing on instance "
                      f"{instance_path} failed! ******")
                print("****** WARNING: The feature vector of this instance consists of "
                      "missing values ******")
                command_line = "rm -f " + result_path
                os.system(command_line)
                tmp_fdcsv = generate_missing_value_csv_like_feature_data_csv(
                    feature_data_csv, Path(instance_path), Path(extractor_path),
                    Path(result_path))

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


def computing_features_parallel(feature_data_csv_path: Path, recompute: bool) -> str:
    """Compute features in parallel.

    Args:
        feature_data_csv_path: Specifies the path of the csv file where
            the feature data is stored.
        recompute: Specifies if features should be recomputed.

    Returns:
        jobid: The jobid of the created slurm job

    """
    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(feature_data_csv_path)
    list_feature_computation_job = get_feature_computation_job_list(
        feature_data_csv, recompute)

    ####
    # Expand the job list
    total_job_num = (
        sparkle_job_help.get_num_of_total_job_from_list(list_feature_computation_job))

    # If there are no jobs, stop
    if total_job_num < 1:
        print("No feature computation jobs to run; stopping execution! To recompute "
              "feature values use the --recompute flag.")
        sys.exit()
    # If there are jobs update feature data ID
    else:
        update_feature_data_id()

    print("The number of total running jobs: " + str(total_job_num))
    total_job_list = (
        sparkle_job_help.expand_total_job_from_list(list_feature_computation_job))
    ####

    ####
    # Generate the sbatch script
    n_jobs = len(total_job_list)
    sbatch_script_name, sbatch_script_dir = (
        ssh.generate_sbatch_script_for_feature_computation(n_jobs, feature_data_csv_path,
                                                           total_job_list))
    ####

    execution_dir = "./"
    sbatch_script_path = sbatch_script_dir + sbatch_script_name
    # Execute the sbatch script via slurm
    jobid = ssh.submit_sbatch_script(sbatch_script_path, CommandName.COMPUTE_FEATURES,
                                     execution_dir)

    # Log output paths
    sl.add_output(sbatch_script_path,
                  "Slurm batch script to compute features in parallel")

    return jobid


def get_feature_computation_job_list(feature_data_csv: sfdcsv.SparkleFeatureDataCSV,
                                     recompute: bool) -> list[list[list[str]]]:
    """computes the needed feature computation jobs

    Args:
        feature_data_csv: the csv containing the feature data
        recompute: variable indicating if the features need to be recomputed

    Returns:
        list_feature_computation_job: a list of feature
            computations to do per instance and solver
    """
    if recompute:
        # recompute is true, so the list of computation jobs is the list of all jobs
        # (recomputing)
        feature_data_csv.clean_csv()
        list_feature_computation_job = (
            feature_data_csv.get_list_recompute_feature_computation_job())
    else:
        # recompute is false, so the list of computation jobs is the list of the
        # remaining jobs
        list_feature_computation_job = (
            feature_data_csv.get_list_remaining_feature_computation_job())
    return list_feature_computation_job


def update_feature_data_id() -> None:
    """Update the feature data ID."""
    # Get current fd_id
    fd_id = get_feature_data_id()

    # Increment fd_id
    fd_id = fd_id + 1

    # Write new fd_id
    fd_id_path = sgh.feature_data_id_path

    with Path(fd_id_path).open("w") as fd_id_file:
        fd_id_file.write(str(fd_id))

    return


def get_feature_data_id() -> int:
    """Return the current feature data ID."""
    fd_id_path = sgh.feature_data_id_path

    try:
        with Path(fd_id_path).open("r") as fd_id_file:
            fd_id = int(fd_id_file.readline())
    except FileNotFoundError:
        fd_id = 0

    return fd_id
