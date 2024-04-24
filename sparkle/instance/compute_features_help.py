#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for feature data computation."""
import subprocess
import sys
from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner

import global_variables as gv
from sparkle.platform import file_help as sfh
from sparkle.platform import slurm_help as ssh
from CLI.support import sparkle_job_help as sjh
from sparkle.structures import feature_data_csv_help as sfdcsv
from CLI.support import sparkle_job_help
from CLI.help.command_help import CommandName


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
    length = int(gv.extractor_feature_vector_size_mapping[str(extractor_path)])
    value_list = [gv.sparkle_missing_value] * length

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

    runsolver_path = gv.runsolver_path

    if len(gv.extractor_list) == 0:
        cutoff_time_each_extractor_run = gv.settings.get_general_extractor_cutoff_time()
    else:
        cutoff_time_each_extractor_run = (
            gv.settings.get_general_extractor_cutoff_time() / len(gv.extractor_list))

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
    print(f"Total number of jobs to run: {total_job_num}")

    for feature_job in list_feature_computation_job:
        instance_path = Path(feature_job[0])
        extractor_list = feature_job[1]

        for extractor_str in extractor_list:
            extractor_path = Path(extractor_str)
            basic_part = (f"{gv.sparkle_tmp_path}/"
                          f"{extractor_path.name}_"
                          f"{instance_path.name}_"
                          f"{gv.get_time_pid_random_string()}")
            result_path = f"{basic_part}.rawres"
            err_path = f"{basic_part}.err"
            runsolver_watch_data_path = f"{basic_part}.log"
            runsolver_watch_data_path_option = f"-w {runsolver_watch_data_path}"
            runsolver_value_data_path = result_path.replace(".rawres", ".val")
            runsolver_value_data_path_option = f"-v {runsolver_value_data_path}"

            command_line = (f"{runsolver_path} {cutoff_time_each_run_option} "
                            f"{runsolver_watch_data_path_option} "
                            f"{runsolver_value_data_path_option} {extractor_path}/"
                            f"{gv.sparkle_run_default_wrapper} {extractor_path}/ "
                            f"{instance_path} {result_path} 2> {err_path}")

            print(f"Extractor {extractor_path.name} computing feature vector of instance"
                  f" {instance_path.name} ...")

            try:
                runsolver = subprocess.run(command_line.split(" "), capture_output=True)
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
                print(f"****** Run solver Output:\n{runsolver.stderr}")
                Path(result_path).unlink(missing_ok=True)
                tmp_fdcsv = generate_missing_value_csv_like_feature_data_csv(
                    feature_data_csv, instance_path, extractor_path,
                    Path(result_path))

            feature_data_csv.combine(tmp_fdcsv)

            Path(result_path).unlink(missing_ok=True)
            Path(err_path).unlink(missing_ok=True)
            Path(runsolver_watch_data_path).unlink(missing_ok=True)
            Path(runsolver_value_data_path).unlink(missing_ok=True)

            print(f"Executing Progress: {str(current_job_num)} out of "
                  f"{str(total_job_num)}")
            current_job_num += 1

            feature_data_csv.save_csv()

            print(f"Extractor {extractor_path.name}"
                  " computation of feature vector of instance "
                  f"{instance_path.name} done!\n")


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
    total_job_list = sjh.expand_total_job_from_list(list_feature_computation_job)

    if run_on == Runner.LOCAL:
        print("Running the solvers locally")
    elif run_on == Runner.SLURM:
        print("Running the solvers through Slurm")

    # Generate the sbatch script
    parallel_jobs = min(n_jobs, gv.settings.get_slurm_number_of_runs_in_parallel())
    cmd_list = [f"CLI/core/compute_features.py --instance {inst_path} "
                f"--extractor {ex_path} --feature-csv {feature_data_csv_path}"
                for inst_path, ex_path in total_job_list]
    sbatch_options = ssh.get_slurm_options_list()
    srun_options = ["-N1", "-n1"] + ssh.get_slurm_options_list()
    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=CommandName.COMPUTE_FEATURES,
        parallel_jobs=parallel_jobs,
        base_dir=gv.sparkle_tmp_path,
        sbatch_options=sbatch_options,
        srun_options=srun_options)

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
    # Get the incremented fd_id
    fd_id = get_feature_data_id() + 1
    # Write it
    with Path(gv.feature_data_id_path).open("w") as fd_id_file:
        fd_id_file.write(str(fd_id))


def get_feature_data_id() -> int:
    """Returns the current feature data ID.

    Returns:
        An int containing the current feature data ID.
    """
    fd_id_path = Path(gv.feature_data_id_path)
    if not fd_id_path.exists():
        return 0
    return int(Path(fd_id_path).open("r").readline())
