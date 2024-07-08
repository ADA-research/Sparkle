#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for feature data computation."""
from __future__ import annotations
import sys
from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner, Status

import global_variables as gv
from CLI.support import sparkle_job_help as sjh
from sparkle.structures import FeatureDataFrame
from CLI.support import sparkle_job_help
from CLI.help.command_help import CommandName


def compute_features(
        feature_data_csv_path: Path,
        recompute: bool,
        run_on: Runner = Runner.SLURM) -> rrr.SlurmRun | rrr.LocalRun:
    """Compute features for all instance and feature extractor combinations.

    A RunRunner run is submitted for the computation of the features.
    The results are then stored in the csv file specified by feature_data_csv_path.

    Args:
        feature_data_csv_path: Create or load feature data CSV file in the path
            specified by this parameter.
        recompute: Specifies if features should be recomputed.
        run_on: Runner
            On which computer or cluster environment to run the solvers.
            Available: Runner.LOCAL, Runner.SLURM. Default: Runner.SLURM

    Returns:
        The Slurm job or Local job
    """
    feature_dataframe = FeatureDataFrame(feature_data_csv_path,
                                         gv.extractor_list)
    if recompute:
        feature_dataframe.reset_dataframe()
    list_feature_computation_job = feature_dataframe.remaining_feature_computation_job()
    n_jobs = sparkle_job_help.get_num_of_total_job_from_list(
        list_feature_computation_job)
    #print(len(list_feature_computation_job))
    #input()
    # If there are no jobs, stop
    if n_jobs < 1:
        print("No feature computation jobs to run; stopping execution! To recompute "
              "feature values use the --recompute flag.")
        sys.exit()

    print("The number of total running jobs: " + str(n_jobs))
    total_job_list = sjh.expand_total_job_from_list(list_feature_computation_job)
    #print(total_job_list)
    #input()
    if run_on == Runner.LOCAL:
        print("Running the solvers locally")
    elif run_on == Runner.SLURM:
        print("Running the solvers through Slurm")

    # Generate the sbatch script
    parallel_jobs = min(n_jobs, gv.settings.get_number_of_jobs_in_parallel())
    cmd_list = [f"CLI/core/compute_features.py --instance {inst_path} "
                f"--extractor {ex_path} --feature-csv {feature_data_csv_path}"
                for inst_path, ex_path in total_job_list]
    sbatch_options = gv.settings.get_slurm_extra_options(as_args=True)
    srun_options = ["-N1", "-n1"] + sbatch_options
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
