#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for parallel execution of solvers."""
#Team2
from __future__ import annotations

import runrunner as rrr
from runrunner.base import Runner

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.structures.sparkle_performance_dataframe import PerformanceDataFrame
from Commands.sparkle_help import sparkle_run_solvers_help as srs
from Commands.sparkle_help import sparkle_slurm_help as ssh
from Commands.sparkle_help.sparkle_command_help import CommandName


def running_solvers_parallel(
        performance_data_csv_path: str,
        num_job_in_parallel: int,
        rerun: bool = False,
        run_on: Runner = Runner.SLURM) -> rrr.SlurmRun | rrr.LocalRun:
    """Run the solvers in parallel.

    Parameters
    ----------
    performance_data_csv_path: str
        The path to the performance data file
    num_job_in_parallel: int
        The maximum number of jobs to run in parallel
    rerun: bool
        Run only solvers for which no data is available yet (False) or (re)run all
        solvers to get (new) performance data for them (True)
    run_on: Runner
        Where to execute the solvers. For available values see runrunner.base.Runner
        enum. Default: "Runner.SLURM".

    Returns
    -------
    run: runrunner.LocalRun or runrunner.SlurmRun
        If the run is local return a QueuedRun object with the information concerning
        the run.
    """
    # Open the performance data csv file
    performance_data_csv = PerformanceDataFrame(performance_data_csv_path)

    # List of jobs to do
    jobs = performance_data_csv.get_job_list(rerun=rerun)
    num_jobs = len(jobs)

    cutoff_time_str = str(sgh.settings.get_general_target_cutoff_time())

    print(f"Cutoff time for each solver run: {cutoff_time_str} seconds")
    print(f"Total number of jobs to run: {num_jobs}")

    # If there are no jobs, stop
    if num_jobs == 0:
        return None
    # If there are jobs update performance data ID
    else:
        srs.update_performance_data_id()

    if run_on == Runner.LOCAL:
        print("Running the solvers locally")
    elif run_on == Runner.SLURM:
        print("Running the solvers through Slurm")

    srun_options = ["-N1", "-n1"] + ssh.get_slurm_options_list()
    sbatch_options = ssh.get_slurm_options_list()
    cmd_base = "Commands/sparkle_help/run_solvers_core.py"
    perf_m = sgh.settings.get_general_sparkle_objectives()[0].PerformanceMeasure
    cmd_list = [f"{cmd_base} --instance {inst_p} --solver {solver_p} "
                f"--performance-measure {perf_m.name}" for inst_p, solver_p in jobs]

    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        parallel_jobs=num_job_in_parallel,
        name=CommandName.RUN_SOLVERS,
        base_dir=sgh.sparkle_tmp_path,
        sbatch_options=sbatch_options,
        srun_options=srun_options)

    return run
