#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for parallel feature computation."""

import sys

try:
    from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
    from sparkle_help import sparkle_job_help
    from sparkle_help import sparkle_compute_features_help as scf
    from sparkle_help import sparkle_slurm_help as ssh
    from sparkle_help import sparkle_logging as sl
    from sparkle_help.sparkle_command_help import CommandName
except ImportError:
    import sparkle_feature_data_csv_help as sfdcsv
    import sparkle_job_help
    import sparkle_compute_features_help as scf
    import sparkle_slurm_help as ssh
    import sparkle_logging as sl
    from sparkle_command_help import CommandName


def computing_features_parallel(feature_data_csv_path: str, mode: int) -> int:
    """Compute features for all instance and feature extractor combinations in parallel.

    An sbatch job is submitted for the computation of the features. The results are then
    stored in the csv file specified by feature_data_csv_path.

    Args:
        feature_data_csv_path: Create a new feature data CSV file in the path
            specified by this parameter.
        mode: If mode is set to 1 features will be computed only for instances for which
            they are not available yet.
            If mode = 2 features will be computed for all instances, including
            recomputing any that were previously saved.
            If mode has any other value an error message is printed.

    Returns:
        The Slurm job ID of the sbatch job will be returned as an int.
    """
    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(feature_data_csv_path)

    if mode == 1:
        list_feature_computation_job = (
            feature_data_csv.get_list_remaining_feature_computation_job())
    elif mode == 2:
        list_feature_computation_job = (
            feature_data_csv.get_list_recompute_feature_computation_job())
    else:  # The abnormal case, exit
        print("Computing features mode error!")
        print("Do not compute features")
        sys.exit()

    n_jobs = sparkle_job_help.get_num_of_total_job_from_list(
        list_feature_computation_job)

    # If there are no jobs, stop
    if n_jobs < 1:
        print("No feature computation jobs to run; stopping execution! To recompute "
              "feature values use the --recompute flag.")
        sys.exit()
    # If there are jobs update feature data ID
    else:
        scf.update_feature_data_id()

    print("The number of total running jobs: " + str(n_jobs))
    total_job_list = (
        sparkle_job_help.expand_total_job_from_list(list_feature_computation_job))

    # Generate the sbatch script
    n_jobs = len(total_job_list)
    sbatch_script_name, sbatch_script_dir = (
        ssh.generate_sbatch_script_for_feature_computation(n_jobs, feature_data_csv_path,
                                                           total_job_list))

    # Execute the sbatch script via slurm
    execution_dir = "./"
    sbatch_script_path = sbatch_script_dir + sbatch_script_name
    jobid = ssh.submit_sbatch_script(sbatch_script_path, CommandName.COMPUTE_FEATURES,
                                     execution_dir)

    # Log output paths
    sl.add_output(sbatch_script_path,
                  "Slurm batch script to compute features in parallel")

    return jobid
