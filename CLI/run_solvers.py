#!/usr/bin/env python3
"""Sparkle command to run solvers to get their performance data."""

import sys
import argparse
from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner

import global_variables as sgh
from sparkle.structures.performance_dataframe import PerformanceDataFrame
from sparkle.platform import slurm_help as ssh
from CLI.support import run_solvers_parallel_help as srsph
import sparkle_logging as sl
from sparkle.platform import settings_help
from sparkle.types.objective import PerformanceMeasure
from sparkle.platform.settings_help import SolutionVerifier
from sparkle.platform.settings_help import SettingState
from CLI.help.command_help import CommandName
from CLI.help import command_help as sch
from CLI.initialise import check_for_initialise

import functools
print = functools.partial(print, flush=True)


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--recompute",
        action="store_true",
        help="recompute the performance of all solvers on all instances")
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="run the solver on multiple instances in parallel")
    parser.add_argument(
        "--performance-measure",
        choices=PerformanceMeasure.__members__,
        help="the performance measure, e.g. runtime")
    parser.add_argument(
        "--target-cutoff-time",
        type=int,
        help="cutoff time per target algorithm run in seconds")
    parser.add_argument(
        "--also-construct-selector-and-report",
        action="store_true",
        help=("after running the solvers also construct the selector and generate"
              " the report"))
    parser.add_argument(
        "--verifier",
        choices=SolutionVerifier.__members__,
        help=("problem specific verifier that should be used to verify solutions found"
              " by a target algorithm"))
    parser.add_argument(
        "--run-on",
        default=Runner.SLURM,
        choices=[Runner.LOCAL, Runner.SLURM],
        help=("On which computer or cluster environment to execute the calculation."))
    parser.add_argument(
        "--settings-file",
        type=Path,
        help=("specify the settings file to use in case you want to use one other than"
              " the default"))

    return parser


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
        PerformanceDataFrame(sgh.performance_data_csv_path).clean_csv()
    num_job_in_parallel = 1
    if parallel:
        num_job_in_parallel = sgh.settings.get_slurm_number_of_runs_in_parallel()

    runs = [srsph.running_solvers_parallel(
        performance_data_csv_path=sgh.performance_data_csv_path,
        num_job_in_parallel=num_job_in_parallel,
        rerun=recompute,
        run_on=run_on)]

    # If there are no jobs return
    if all(run is None for run in runs):
        print("Running solvers done!")
        return

    sbatch_user_options = ssh.get_slurm_options_list()

    # Update performance data csv after the last job is done
    runs.append(rrr.add_to_queue(
        runner=run_on,
        cmd="sparkle/structures/csv_merge.py",
        name=CommandName.CSV_MERGE,
        dependencies=runs[-1],
        base_dir=sgh.sparkle_tmp_path,
        sbatch_options=sbatch_user_options))

    if also_construct_selector_and_report:
        runs.append(rrr.add_to_queue(
            runner=run_on,
            cmd="CLI/construct_sparkle_portfolio_selector.py",
            name=CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR,
            dependencies=runs[-1],
            base_dir=sgh.sparkle_tmp_path,
            sbatch_options=sbatch_user_options))

        runs.append(rrr.add_to_queue(
            runner=run_on,
            cmd="CLI/generate_report.py",
            name=CommandName.GENERATE_REPORT,
            dependencies=runs[-1],
            base_dir=sgh.sparkle_tmp_path,
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
    sgh.settings = settings_help.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    if args.settings_file is not None:
        # Do first, so other command line options can override settings from the file
        sgh.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)

    if args.performance_measure is not None:
        sgh.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE
        )

    if args.verifier is not None:
        sgh.settings.set_general_solution_verifier(
            SolutionVerifier.from_str(args.verifier), SettingState.CMD_LINE)

    if args.target_cutoff_time:
        sgh.settings.set_general_target_cutoff_time(
            args.target_cutoff_time, SettingState.CMD_LINE)

    check_for_initialise(sys.argv,
                         sch.COMMAND_DEPENDENCIES[sch.CommandName.RUN_SOLVERS])

    print("Start running solvers ...")

    # Write settings to file before starting, since they are used in callback scripts
    sgh.settings.write_used_settings()

    run_solvers_on_instances(
        parallel=args.parallel,
        recompute=args.recompute,
        also_construct_selector_and_report=args.also_construct_selector_and_report,
        run_on=args.run_on)
