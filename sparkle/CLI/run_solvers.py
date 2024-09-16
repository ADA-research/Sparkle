#!/usr/bin/env python3
"""Sparkle command to run solvers to get their performance data."""
from __future__ import annotations

import sys
import argparse
from pathlib import PurePath, Path

import runrunner as rrr
from runrunner.base import Runner, Run

from sparkle.CLI.help import global_variables as gv
from sparkle.structures import PerformanceDataFrame
from sparkle.CLI.help import logging as sl
from sparkle.platform.settings_objects import Settings, SettingState
from sparkle.platform import CommandName, COMMAND_DEPENDENCIES
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as ac


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument(*ac.RecomputeRunSolversArgument.names,
                        **ac.RecomputeRunSolversArgument.kwargs)
    parser.add_argument(*ac.SparkleObjectiveArgument.names,
                        **ac.SparkleObjectiveArgument.kwargs)
    parser.add_argument(*ac.TargetCutOffTimeRunSolversArgument.names,
                        **ac.TargetCutOffTimeRunSolversArgument.kwargs)
    parser.add_argument(*ac.AlsoConstructSelectorAndReportArgument.names,
                        **ac.AlsoConstructSelectorAndReportArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)

    return parser


def running_solvers_performance_data(
        performance_data_csv_path: Path,
        num_job_in_parallel: int,
        rerun: bool = False,
        run_on: Runner = Runner.SLURM) -> Run:
    """Run the solvers for the performance data.

    Parameters
    ----------
    performance_data_csv_path: Path
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
    performance_dataframe = PerformanceDataFrame(performance_data_csv_path)
    # List of jobs to do
    jobs = performance_dataframe.get_job_list(rerun=rerun)
    num_jobs = len(jobs)

    cutoff_time_str = str(gv.settings().get_general_target_cutoff_time())

    print(f"Cutoff time for each solver run: {cutoff_time_str} seconds")
    print(f"Total number of jobs to run: {num_jobs}")

    # If there are no jobs, stop
    if num_jobs == 0:
        return None

    if run_on == Runner.LOCAL:
        print("Running the solvers locally")
    elif run_on == Runner.SLURM:
        print("Running the solvers through Slurm")

    sbatch_options = gv.settings().get_slurm_extra_options(as_args=True)
    srun_options = ["-N1", "-n1"] + sbatch_options
    objectives = gv.settings().get_general_sparkle_objectives()
    run_solvers_core = Path(__file__).parent.resolve() / "core" / "run_solvers_core.py"
    cmd_list = [f"{run_solvers_core} "
                f"--performance-data {performance_data_csv_path} "
                f"--instance {inst_p} --solver {solver_p} "
                f"--objectives {','.join([str(o) for o in objectives])} "
                f"--log-dir {sl.caller_log_dir}" for inst_p, _, solver_p in jobs]

    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        parallel_jobs=num_job_in_parallel,
        name=CommandName.RUN_SOLVERS,
        base_dir=sl.caller_log_dir,
        sbatch_options=sbatch_options,
        srun_options=srun_options)

    if run_on == Runner.LOCAL:
        # TODO: It would be nice to extract some info per job and print it
        # As the user now only sees jobs starting and completing without their results
        run.wait()

    return run


def run_solvers_on_instances(
        recompute: bool = False,
        run_on: Runner = Runner.SLURM,
        also_construct_selector_and_report: bool = False) -> None:
    """Run all the solvers on all the instances that were not not previously run.

    If recompute is True, rerun everything even if previously run. Where the solvers are
    executed can be controlled with "run_on".

    Parameters
    ----------
    recompute: bool
        If True, recompute all solver-instance pairs even if they were run before.
        Default: False
    run_on: Runner
        On which computer or cluster environment to run the solvers.
        Available: Runner.LOCAL, Runner.SLURM. Default: Runner.SLURM
    also_construct_selector_and_report: bool
        If True, the selector will be constructed and a report will be produced.
    """
    if recompute:
        PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path).clean_csv()
    num_job_in_parallel = gv.settings().get_number_of_jobs_in_parallel()

    runs = [running_solvers_performance_data(
        performance_data_csv_path=gv.settings().DEFAULT_performance_data_path,
        num_job_in_parallel=num_job_in_parallel,
        rerun=recompute,
        run_on=run_on)]

    # If there are no jobs return
    if all(run is None for run in runs):
        print("Running solvers done!")
        return

    sbatch_user_options = gv.settings().get_slurm_extra_options(as_args=True)
    if also_construct_selector_and_report:
        runs.append(rrr.add_to_queue(
            runner=run_on,
            cmd="sparkle/CLI/construct_portfolio_selector.py",
            name=CommandName.CONSTRUCT_PORTFOLIO_SELECTOR,
            dependencies=runs[-1],
            base_dir=sl.caller_log_dir,
            sbatch_options=sbatch_user_options))

        runs.append(rrr.add_to_queue(
            runner=run_on,
            cmd="sparkle/CLI/generate_report.py",
            name=CommandName.GENERATE_REPORT,
            dependencies=runs[-1],
            base_dir=sl.caller_log_dir,
            sbatch_options=sbatch_user_options))

    if run_on == Runner.LOCAL:
        print("Waiting for the local calculations to finish.")
        for run in runs:
            if run is not None:
                run.wait()
        print("Running solvers done!")
    elif run_on == Runner.SLURM:
        print("Running solvers. Waiting for Slurm job(s) with id(s): "
              f'{",".join(r.run_id for r in runs if r is not None)}')


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    if args.settings_file is not None:
        # Do first, so other command line options can override settings from the file
        gv.settings().read_settings_ini(args.settings_file, SettingState.CMD_LINE)

    if args.objectives is not None:
        gv.settings().set_general_sparkle_objectives(
            args.objectives, SettingState.CMD_LINE
        )

    if args.target_cutoff_time is not None:
        gv.settings().set_general_target_cutoff_time(
            args.target_cutoff_time, SettingState.CMD_LINE)

    if args.run_on is not None:
        gv.settings().set_run_on(
            args.run_on.value, SettingState.CMD_LINE)
    run_on = gv.settings().get_run_on()

    check_for_initialise(COMMAND_DEPENDENCIES[CommandName.RUN_SOLVERS])

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings(), prev_settings)

    print("Start running solvers ...")

    # Write settings to file before starting, since they are used in callback scripts
    gv.settings().write_used_settings()

    run_solvers_on_instances(
        recompute=args.recompute,
        also_construct_selector_and_report=args.also_construct_selector_and_report,
        run_on=run_on)
