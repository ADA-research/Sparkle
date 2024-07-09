#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for feature data computation."""
from __future__ import annotations
import sys
from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner, Status

import global_variables as gv
from sparkle.structures import FeatureDataFrame
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
    feature_dataframe = FeatureDataFrame(feature_data_csv_path)
    if recompute:
        feature_dataframe.reset_dataframe()
    jobs = feature_dataframe.remaining_jobs()

    # If there are no jobs, stop
    if jobs == {}:
        print("No feature computation jobs to run; stopping execution! To recompute "
              "feature values use the --recompute flag.")
        sys.exit()
    cutoff = gv.settings.get_general_extractor_cutoff_time()
    cmd_list = ["CLI/core/compute_features.py "
                f"--instance {inst_path} "
                f"--extractor {ex_path} "
                f"--feature-csv {feature_data_csv_path}"
                f"--cutoff {cutoff}"
                for inst_path in jobs.keys() for ex_path in jobs[inst_path]]

    print(f"The number of total running jobs: {len(cmd_list)}")
    if run_on == Runner.LOCAL:
        print("Running the solvers locally")
    elif run_on == Runner.SLURM:
        print("Running the solvers through Slurm")

    # Generate the sbatch script
    parallel_jobs = min(len(cmd_list), gv.settings.get_number_of_jobs_in_parallel())
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
