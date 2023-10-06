#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for feature data computation."""

import os
import sys
from pathlib import Path

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_basic_help
from Commands.sparkle_help import sparkle_file_help as sfh
from Commands.sparkle_help import sparkle_slurm_help as ssh
from Commands.sparkle_help import sparkle_job_help as sjh
from Commands.sparkle_help import sparkle_logging as sl
from Commands.sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from Commands.sparkle_help import sparkle_job_help
from Commands.sparkle_help.sparkle_command_help import CommandName

from sparkle.slurm_parsing import SlurmBatch

import runrunner as rrr
from runrunner.base import Runner


def generate_missing_value_csv_like_feature_data_csv(
        feature_data_csv: sfdcsv.SparkleFeatureDataCSV,
        instance_path: Path,
        extractor_path: Path,
        result_path: Path) -> sfdcsv.SparkleFeatureDataCSV:
    """Create a CSV file with missing values for a given instance and extractor pair.

    Args:
        feature_data_csv: Reference to a SparkleFeatureDataCSV object for which the
            dimensions will be used to create a new SparkleFeatureDataCSV with the same
            dimensions.
        instance_path: Path to the instance, to be used for a row with missing values in
            the new CSV file.
        extractor_path: Path to the extractor, to be used to determine the number of
            missing values to add for the instance.
        result_path: The path to store the new created CSV file in.

    Returns:
        A newly created SparkleFeatureDataCSV object with missing (zero) values for the
        provided instance_path with the same number of columns as feature_data_csv.
    """
    # create an empty CSV
    sfdcsv.SparkleFeatureDataCSV.create_empty_csv(result_path)
    zero_value_csv = sfdcsv.SparkleFeatureDataCSV(result_path)

    # add as many columns as feature_data_csv has
    for column_name in feature_data_csv.list_columns():
        zero_value_csv.add_column(column_name)

    # Add missing values based on the number of features this extractor computes.
    # WARNING: This currently does not correctly handle which columns should be set in
    # case of multiple feature extractors.
    length = int(sgh.extractor_feature_vector_size_mapping[str(extractor_path)])
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
            sgh.settings.get_general_extractor_cutoff_time() / len(sgh.extractor_list))

    cutoff_time_each_run_option = f"--cpu-limit {str(cutoff_time_each_extractor_run)}"
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
    print(f"Total number of jobs to run: {str(total_job_num)}")

    for i in range(0, len(list_feature_computation_job)):
        instance_path = list_feature_computation_job[i][0]
        extractor_list = list_feature_computation_job[i][1]
        len_extractor_list = len(extractor_list)

        for j in range(0, len_extractor_list):
            extractor_path = extractor_list[j]
            basic_part = (f"{sgh.sparkle_tmp_path}/"
                          f"{sfh.get_last_level_directory_name(extractor_path)}_"
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

            print(f"Extractor {sfh.get_last_level_directory_name(extractor_path)}"
                  " computing feature vector of instance "
                  f"{sfh.get_last_level_directory_name(instance_path)} ...")

            try:
                os.system(command_line)
                with Path(runsolver_value_data_path).open() as file:
                    if "TIMEOUT=true" in file.read():
                        print(f"****** WARNING: Feature vector computation on instance "
                              f"{instance_path} timed out! ******")
            except Exception:
                if not Path(result_path).exists():
                    sfh.create_new_empty_file(result_path)

            try:
                tmp_fdcsv = sfdcsv.SparkleFeatureDataCSV(result_path)
            except Exception:
                print("****** WARNING: Feature vector computation on instance "
                      f"{instance_path} failed! ******")
                print("****** WARNING: The feature vector of this instance consists of "
                      "missing values ******")
                Path(result_path).unlink(missing_ok=True)
                tmp_fdcsv = generate_missing_value_csv_like_feature_data_csv(
                    feature_data_csv, Path(instance_path), Path(extractor_path),
                    Path(result_path))

            feature_data_csv.combine(tmp_fdcsv)

            Path(result_path).unlink(missing_ok=True)
            Path(err_path).unlink(missing_ok=True)
            Path(runsolver_watch_data_path).unlink(missing_ok=True)
            Path(runsolver_value_data_path).unlink(missing_ok=True)

            print(f"Executing Progress: {str(current_job_num)} out of "
                  f"{str(total_job_num)}")
            current_job_num += 1

            feature_data_csv.update_csv()

            print(f"Extractor {sfh.get_last_level_directory_name(extractor_path)}"
                  " computation of feature vector of instance "
                  f"{sfh.get_last_level_directory_name(instance_path)} done!\n")


def computing_features_parallel(feature_data_csv_path: Path,
                                recompute: bool,
                                run_on: Runner = Runner.SLURM) -> str:
    """Compute features for all instance and feature extractor combinations in parallel.

    A sbatch job is submitted for the computation of the features. The results are then
    stored in the csv file specified by feature_data_csv_path.

    Args:
        feature_data_csv_path: Create a new feature data CSV file in the path
            specified by this parameter.
        recompute: Specifies if features should be recomputed.
        run_on: Runner
            On which computer or cluster environment to run the solvers.
            Available: Runner.LOCAL, Runner.SLURM. Default: Runner.SLURM

    Returns:
        The Slurm job ID of the sbatch job will be returned as a str
        jobid: The jobid of the created slurm job

    """
    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(feature_data_csv_path)
    list_feature_computation_job = get_feature_computation_job_list(
        feature_data_csv, recompute)

    n_jobs = sparkle_job_help.get_num_of_total_job_from_list(
        list_feature_computation_job)

    # If there are no jobs, stop
    if n_jobs < 1:
        print("No feature computation jobs to run; stopping execution! To recompute "
              "feature values use the --recompute flag.")
        sys.exit()
    # If there are jobs update feature data ID
    else:
        update_feature_data_id()

    print("The number of total running jobs: " + str(n_jobs))
    total_job_list = (
        sparkle_job_help.expand_total_job_from_list(list_feature_computation_job))

    if run_on == Runner.LOCAL:
        print("Running the solvers locally")
    elif run_on == Runner.SLURM:
        print("Running the solvers through Slurm")

    # Generate the sbatch script
    n_jobs = len(total_job_list)
    sbatch_script_name, sbatch_script_dir = (
        ssh.generate_sbatch_script_for_feature_computation(n_jobs, feature_data_csv_path,
                                                           total_job_list))

    if run_on == Runner.SLURM:
        # Execute the sbatch script via slurm
        execution_dir = "./"
        sbatch_script_path = sbatch_script_dir + sbatch_script_name
        run = ssh.submit_sbatch_script(sbatch_script_path, CommandName.COMPUTE_FEATURES,
                                       execution_dir)

        # Log output paths
        sl.add_output(sbatch_script_path,
                      "Slurm batch script to compute features in parallel")
    else:
        batch = SlurmBatch(sbatch_script_path)
        # Execute the batch locally
        if run_on == Runner.SLURM_RR:
            run_on = Runner.SLURM

        cmd_list = [f"{batch.cmd} {param}" for param in batch.cmd_params]
        run = rrr.add_to_queue(
            runner=run_on,
            cmd=cmd_list,
            name="compute_features",
            base_dir="Tmp",
            sbatch_options=batch.sbatch_options,
            srun_options=batch.srun_options)

        # Remove the below if block once runrunner works satisfactorily
        if run_on == Runner.SLURM:
            run_on = Runner.SLURM_RR

    if run_on == Runner.SLURM_RR:  # Change to SLURM once runrunner works satisfactorily
        # Add the run to the list of active job.
        sjh.write_active_job(run.run_id, CommandName.RUN_SOLVERS)

    return run


def get_feature_computation_job_list(feature_data_csv: sfdcsv.SparkleFeatureDataCSV,
                                     recompute: bool) -> list[list[list[str]]]:
    """Computes the needed feature computation jobs.

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
    """Updates the feature data ID by incrementing the current feature data ID by 1."""
    # Get current fd_id
    fd_id = get_feature_data_id()

    # Increment fd_id
    fd_id = fd_id + 1

    # Write new fd_id
    fd_id_path = sgh.feature_data_id_path

    with Path(fd_id_path).open("w") as fd_id_file:
        fd_id_file.write(str(fd_id))


def get_feature_data_id() -> int:
    """Returns the current feature data ID.

    Returns:
        An int containing the current feature data ID.
    """
    fd_id_path = sgh.feature_data_id_path

    try:
        with Path(fd_id_path).open("r") as fd_id_file:
            fd_id = int(fd_id_file.readline())
    except FileNotFoundError:
        fd_id = 0

    return fd_id
