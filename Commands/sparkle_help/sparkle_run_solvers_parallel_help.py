#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for parallel execution of solvers."""

import os

import runrunner.local
from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_basic_help as sbh
from Commands.sparkle_help import sparkle_performance_data_csv_help as spdcsv
from Commands.sparkle_help import sparkle_job_help as sjh
from Commands.sparkle_help import sparkle_run_solvers_help as srs
from Commands.sparkle_help import sparkle_slurm_help as ssh
from Commands.sparkle_help import sparkle_logging as sl
from Commands.sparkle_help.sparkle_command_help import CommandName

from sparkle.slurm_parsing import SlurmBatch
import runrunner as rrr
from runrunner.base import Runner


def generate_running_solvers_sbatch_shell_script(total_job_num: int,
                                                 num_job_in_parallel: int,
                                                 total_job_list: list[tuple[str, str]],
                                                 ) -> (str, str, str):
    """Generate a Slurm shell script to run the solvers."""
    sbatch_script_name = ("running_solvers_sbatch_shell_script_"
                          f"{sbh.get_time_pid_random_string()}.sh")
    sbatch_script_path = f"{sgh.sparkle_tmp_path}{sbatch_script_name}"
    job_name = "--job-name=" + sbatch_script_name
    std_out_path = sbatch_script_path + ".txt"
    std_err_path = sbatch_script_path + ".err"
    output = "--output=" + std_out_path
    error = "--error=" + std_err_path
    array = "--array=0-" + str(total_job_num - 1) + "%" + str(num_job_in_parallel)

    sbatch_options_list = [job_name, output, error, array]
    sbatch_options_list.extend(ssh.get_slurm_sbatch_default_options_list())
    sbatch_options_list.extend(ssh.get_slurm_sbatch_user_options_list())
    job_params_list = []

    for job in total_job_list:
        instance_path = job[0]
        solver_path = job[1]
        performance_measure = sgh.settings.get_general_performance_measure()
        job_params_list.append(f"--instance {instance_path} --solver {solver_path}"
                               f" --performance-measure {performance_measure.name}")

    srun_options_str = "-N1 -n1"
    srun_options_str = srun_options_str + " " + ssh.get_slurm_srun_user_options_str()
    target_call_str = "Commands/sparkle_help/run_solvers_core.py"

    ssh.generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list,
                                       job_params_list, srun_options_str,
                                       target_call_str)

    return sbatch_script_path, std_out_path, std_err_path


def running_solvers_parallel(
        performance_data_csv_path: str,
        num_job_in_parallel: int,
        rerun: bool = False,
        run_on: Runner = Runner.SLURM) -> str:
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
    run: runrunner.local.QueuedRun or runrunner.slurm.SlurmRun or None
        If the run is local return a QueuedRun object with the information concerning
        the run. If the run is executed on Slurm, return the ID of the run.
    """
    # Open the performance data csv file
    performance_data_csv = spdcsv.SparklePerformanceDataCSV(performance_data_csv_path)

    # List of jobs to do
    jobs = performance_data_csv.get_job_list(rerun=rerun)
    num_jobs = len(jobs)

    cutoff_time_str = str(sgh.settings.get_general_target_cutoff_time())

    print(f"Cutoff time for each solver run: {cutoff_time_str} seconds")
    print(f"Total number of jobs to run: {num_jobs}")

    # If there are no jobs, stop
    if num_jobs == 0:
        return "" if run_on == Runner.SLURM else None
    # If there are jobs update performance data ID
    else:
        srs.update_performance_data_id()

    sbatch_script_path, std_out_path, std_err_path = (
        generate_running_solvers_sbatch_shell_script(
            num_jobs, num_job_in_parallel, jobs))

    # Log output paths
    sl.add_output(sbatch_script_path, "Slurm batch script to run solvers in parallel")
    sl.add_output(std_out_path,
                  "Standard output of Slurm batch script to run solvers in parallel")
    sl.add_output(std_err_path,
                  "Error output of Slurm batch script to run solvers in parallel")

    if run_on == Runner.LOCAL:
        print("Running the solvers locally")
    elif run_on == Runner.SLURM:
        print("Running the solvers through Slurm")

    # NOTE: Remove everything under the if once Slurm through runrunner works
    # satisfactorily. Keep everything in the else.
    if run_on == Runner.SLURM:
        # Execute the sbatch script via slurm
        command_line = f"sbatch {sbatch_script_path}"
        output_list = os.popen(command_line).readlines()
        run = ""
        if len(output_list) > 0 and len(output_list[0].strip().split()) > 0:
            run = output_list[0].strip().split()[-1]
            # Add job to active job CSV
            sjh.write_active_job(run, CommandName.RUN_SOLVERS)
    else:
        batch = SlurmBatch(sbatch_script_path)

        # Remove the below if block once runrunner works satisfactorily
        if run_on == Runner.SLURM_RR:
            run_on = Runner.SLURM

        cmd_list = [f"{batch.cmd} {param}" for param in batch.cmd_params]
        run = rrr.add_to_queue(
            runner=run_on,
            cmd=cmd_list,
            name=CommandName.RUN_SOLVERS,
            base_dir=sgh.sparkle_tmp_path,
            sbatch_options=batch.sbatch_options,
            srun_options=batch.srun_options)

        # Remove the below if block once runrunner works satisfactorily
        if run_on == Runner.SLURM:
            run_on = Runner.SLURM_RR

    if run_on == Runner.SLURM_RR:  # Change to SLURM once runrunner works satisfactorily
        # Add the run to the list of active job.
        sjh.write_active_job(run.run_id, CommandName.RUN_SOLVERS)

    return run
