#!/usr/bin/env python3
"""Sparkle command to run solvers to get their performance data."""
from __future__ import annotations

import sys
import argparse
from pathlib import PurePath, Path

from runrunner.base import Runner, Run

from sparkle.solver import Solver
from sparkle.structures import PerformanceDataFrame
from sparkle.platform.settings_objects import Settings, SettingState
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.initialise import check_for_initialise


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run all solvers on all instances to get their performance data.")
    parser.add_argument(*ac.RecomputeRunSolversArgument.names,
                        **ac.RecomputeRunSolversArgument.kwargs)
    parser.add_argument(*ac.SparkleObjectiveArgument.names,
                        **ac.SparkleObjectiveArgument.kwargs)
    parser.add_argument(*ac.TargetCutOffTimeRunSolversArgument.names,
                        **ac.TargetCutOffTimeRunSolversArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    return parser


def running_solvers_performance_data(
        performance_data_csv_path: Path,
        num_job_in_parallel: int,
        rerun: bool = False,
        run_on: Runner = Runner.SLURM) -> list[Run]:
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

    print("Cutoff time for each solver run: "
          f"{gv.settings().get_general_target_cutoff_time()} seconds")
    print(f"Total number of jobs to run: {num_jobs}")

    # If there are no jobs, stop
    if num_jobs == 0:
        return None

    if run_on == Runner.LOCAL:
        print("Running the solvers locally")
    elif run_on == Runner.SLURM:
        print("Running the solvers through Slurm")

    sbatch_options = gv.settings().get_slurm_extra_options(as_args=True)
    cutoff = gv.settings().get_general_target_cutoff_time()

    # Sort the jobs per solver
    solver_jobs = {solver: [] for _, _, solver in jobs}
    runs = []
    for instance, run, solver in jobs:
        solver_jobs[solver].append((instance, run))
    for solver_path in solver_jobs:
        solver = Solver(Path(solver_path))
        for instance, run in solver_jobs[solver_path]:
            print(instance, run)
            run = solver.run_performance_dataframe(
                instance, run, performance_dataframe, cutoff_time=cutoff,
                sbatch_options=sbatch_options, log_dir=sl.caller_log_dir,
                base_dir=sl.caller_log_dir, run_on=run_on)
            runs.append(run)

    return runs


def main(argv: list[str]) -> None:
    """Main function of the run solvers command."""
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)

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

    check_for_initialise()

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings(), prev_settings)

    print("Start running solvers ...")

    # Write settings to file before starting, since they are used in callback scripts
    gv.settings().write_used_settings()

    run_on = gv.settings().get_run_on()
    if args.recompute:
        PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path).clean_csv()
    num_job_in_parallel = gv.settings().get_number_of_jobs_in_parallel()

    runs = running_solvers_performance_data(
        performance_data_csv_path=gv.settings().DEFAULT_performance_data_path,
        num_job_in_parallel=num_job_in_parallel,
        rerun=args.recompute,
        run_on=run_on)

    # If there are no jobs return
    if all(run is None for run in runs):
        print("Running solvers done!")
        return

    if run_on == Runner.LOCAL:
        print("Waiting for the local calculations to finish.")
        for run in runs:
            if run is not None:
                run.wait()
        print("Running solvers done!")
    elif run_on == Runner.SLURM:
        print("Running solvers. Waiting for Slurm job(s) with id(s): "
              f'{",".join(r.run_id for r in runs if r is not None)}')
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
