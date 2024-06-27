#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for feature data computation."""
from __future__ import annotations
import sys
from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner, Status

import global_variables as gv
from CLI.help import slurm_help as ssh
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
    zero_value_csv = sfdcsv.SparkleFeatureDataCSV(result_path,
                                                  gv.extractor_list)

    # add as many columns as feature_data_csv has
    for column_name in feature_data_csv.list_columns():
        zero_value_csv.add_column(column_name)

    # Add missing values based on the number of features this extractor computes.
    # WARNING: This currently does not correctly handle which columns should be set in
    # case of multiple feature extractors.
    length = int(gv.extractor_feature_vector_size_mapping[str(extractor_path)])
    value_list = [sfdcsv.SparkleFeatureDataCSV.missing_value] * length

    zero_value_csv.add_row(instance_path, value_list)

    return zero_value_csv


def computing_features_parallel(
        feature_data_csv_path: Path,
        recompute: bool,
        run_on: Runner = Runner.SLURM) -> rrr.SlurmRun | rrr.LocalRun:
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
    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(feature_data_csv_path,
                                                    gv.extractor_list)
    list_feature_computation_job = get_feature_computation_job_list(
        feature_data_csv, recompute)
    n_jobs = sparkle_job_help.get_num_of_total_job_from_list(
        list_feature_computation_job)

    # If there are no jobs, stop
    if n_jobs < 1:
        print("No feature computation jobs to run; stopping execution! To recompute "
              "feature values use the --recompute flag.")
        sys.exit()

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

    if run_on == Runner.LOCAL:
        print("Waiting for the local calculations to finish.")
        run.wait()
        for job in run.jobs:
            jobs_done = sum(j.status == Status.COMPLETED for j in run.jobs)
            print(f"Executing Progress: {jobs_done} out of {len(run.jobs)}")
            if jobs_done == len(run.jobs):
                break
            job.wait()
        print("Computing features done!")

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
