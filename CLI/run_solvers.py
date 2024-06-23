#!/usr/bin/env python3
"""Sparkle command to run solvers to get their performance data."""
from __future__ import annotations


import sys
import argparse
from pathlib import PurePath

import runrunner as rrr
from runrunner.base import Runner

import global_variables as gv
from sparkle.structures.performance_dataframe import PerformanceDataFrame
from CLI.help import slurm_help as ssh
import sparkle_logging as sl
from sparkle.platform import settings_help
from sparkle.platform.settings_help import SolutionVerifier
from sparkle.platform.settings_help import SettingState, Settings
from CLI.help.command_help import CommandName
from CLI.help import command_help as sch
from CLI.initialise import check_for_initialise
from CLI.help import argparse_custom as ac
from CLI.support import run_solvers_help as srs


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument(*ac.RecomputeRunSolversArgument.names,
                        **ac.RecomputeRunSolversArgument.kwargs)
    parser.add_argument(*ac.ParallelArgument.names,
                        **ac.ParallelArgument.kwargs)
    parser.add_argument(*ac.PerformanceMeasureSimpleArgument.names,
                        **ac.PerformanceMeasureSimpleArgument.kwargs)
    parser.add_argument(*ac.TargetCutOffTimeRunSolversArgument.names,
                        **ac.TargetCutOffTimeRunSolversArgument.kwargs)
    parser.add_argument(*ac.AlsoConstructSelectorAndReportArgument.names,
                        **ac.AlsoConstructSelectorAndReportArgument.kwargs)
    parser.add_argument(*ac.VerifierArgument.names,
                        **ac.VerifierArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)

    return parser


def running_solvers_performance_data(
        performance_data_csv_path: str,
        num_job_in_parallel: int,
        rerun: bool = False,
        run_on: Runner = Runner.SLURM) -> rrr.SlurmRun | rrr.LocalRun:
    """Run the solvers for the performance data.

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
    performance_dataframe = PerformanceDataFrame(performance_data_csv_path)
    print(performance_dataframe.dataframe)
    # List of jobs to do
    jobs = performance_dataframe.get_job_list(rerun=rerun)
    num_jobs = len(jobs)

    cutoff_time_str = str(gv.settings.get_general_target_cutoff_time())

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
    cmd_base = "CLI/core/run_solvers_core.py"
    perf_m = gv.settings.get_general_sparkle_objectives()[0].PerformanceMeasure
    cmd_list = [f"{cmd_base} --performance-data {performance_data_csv_path} "
                f"--instance {inst_p} --solver {solver_p} "
                f"--performance-measure {perf_m.name}" for inst_p, solver_p in jobs]

    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        parallel_jobs=num_job_in_parallel,
        name=CommandName.RUN_SOLVERS,
        base_dir=gv.sparkle_tmp_path,
        sbatch_options=sbatch_options,
        srun_options=srun_options)

    return run


def run_solvers_on_instances(
        parallel: bool = False,
        recompute: bool = False,
        run_on: Runner = Runner.SLURM,
        also_construct_selector_and_report: bool = False) -> None:
    """Run all the solvers on all the instances that were not not previously run.

    If recompute is True, rerun everything even if previously run. Where the solvers are
    executed can be controlled with "run_on".

    Parameters
    ----------
    parallel: bool
        Run the solvers in parallel or one at a time. Default: False
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
        PerformanceDataFrame(gv.performance_data_csv_path).clean_csv()
    num_job_in_parallel = 1
    if parallel:
        num_job_in_parallel = gv.settings.get_slurm_number_of_runs_in_parallel()

    runs = [running_solvers_performance_data(
        performance_data_csv_path=gv.performance_data_csv_path,
        num_job_in_parallel=num_job_in_parallel,
        rerun=recompute,
        run_on=run_on)]

    # If there are no jobs return
    if all(run is None for run in runs):
        print("Running solvers done!")
        return

    sbatch_user_options = ssh.get_slurm_options_list()
    if also_construct_selector_and_report:
        runs.append(rrr.add_to_queue(
            runner=run_on,
            cmd="CLI/construct_sparkle_portfolio_selector.py",
            name=CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR,
            dependencies=runs[-1],
            base_dir=gv.sparkle_tmp_path,
            sbatch_options=sbatch_user_options))

        runs.append(rrr.add_to_queue(
            runner=run_on,
            cmd="CLI/generate_report.py",
            name=CommandName.GENERATE_REPORT,
            dependencies=runs[-1],
            base_dir=gv.sparkle_tmp_path,
            sbatch_options=sbatch_user_options))

    if run_on == Runner.LOCAL:
        print("Waiting for the local calculations to finish.")
        for run in runs:
            if run is not None:
                run.wait()
        print("Running solvers done!")
    elif run_on == Runner.SLURM:
        print("Running solvers in parallel. Waiting for Slurm job(s) with id(s): "
              f'{",".join(r.run_id for r in runs if r is not None)}')


if __name__ == "__main__":
    # Initialise settings
    global settings
    gv.settings = settings_help.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    if args.settings_file is not None:
        # Do first, so other command line options can override settings from the file
        gv.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)

    if args.performance_measure is not None:
        gv.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE
        )

    if args.verifier is not None:
        gv.settings.set_general_solution_verifier(
            SolutionVerifier.from_str(args.verifier), SettingState.CMD_LINE)

    if args.target_cutoff_time:
        gv.settings.set_general_target_cutoff_time(
            args.target_cutoff_time, SettingState.CMD_LINE)

    check_for_initialise(sys.argv,
                         sch.COMMAND_DEPENDENCIES[sch.CommandName.RUN_SOLVERS])

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings, prev_settings)

    print("Start running solvers ...")

    # Write settings to file before starting, since they are used in callback scripts
    gv.settings.write_used_settings()

    run_solvers_on_instances(
        parallel=args.parallel,
        recompute=args.recompute,
        also_construct_selector_and_report=args.also_construct_selector_and_report,
        run_on=args.run_on)
