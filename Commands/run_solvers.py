#!/usr/bin/env python3

import sys
import argparse
from typing import List
from pathlib import Path

from sparkle_help import sparkle_record_help as srh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_run_solvers_parallel_help as srsp
from sparkle_help import sparkle_job_parallel_help as sjph
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings
from sparkle_help.sparkle_settings import PerformanceMeasure
from sparkle_help.sparkle_settings import SolutionVerifier
from sparkle_help.sparkle_settings import SettingState
from sparkle_help.sparkle_command_help import CommandName

import runrunner as rrr


def run_solvers_on_instances(
        parallel: bool = False,
        recompute: bool = False,
        run_on: str = None,
        also_construct_selector_and_report: bool = False):
    """ Run all the solvers on all the instances that were not not previously run. If
        recompute is True, rerun everything even if previously run. Where the solvers are
        executed can be controlled with 'run_on'.

        Parameters
        ----------
        parallel: bool
            Run the solvers in parallel or one at a time. Default: False
        recompute: bool
            If True, recompute all solver-instance pairs even if they were run before.
            Default: False
        run_on: str
            On which computer or cluster environment to run the solvers.
            Available: local, slurm. Default: slurm
        also_construct_selector_and_report: bool
            If True, the selector will be constructed and a report will be produced.
     """
    if recompute:
        spdcsv.Sparkle_Performance_Data_CSV(sgh.performance_data_csv_path).clean_csv()

    # Write used settings to file
    sgh.settings.write_used_settings()

    if parallel:
        num_job_in_parallel = sgh.settings.get_slurm_number_of_runs_in_parallel()
    else:
        num_job_in_parallel = 1

    # Run the solvers
    runs = [srsp.running_solvers_parallel(
        performance_data_csv_path=sgh.performance_data_csv_path,
        num_job_in_parallel=num_job_in_parallel,
        rerun=recompute,
        run_on=run_on
    )]

    # Update performance data csv after the last job is done
    runs.append(rrr.add_to_queue(
        runner=run_on,
        cmd="Commands/sparkle_help/sparkle_csv_merge_help.py",
        name="sprkl_csv_merge",
        dependencies=runs[-1],
        base_dir="Tmp"
    ))

    if also_construct_selector_and_report:
        runs.append(rrr.add_to_queue(
            runner=run_on,
            cmd="Commands/construct_sparkle_portfolio_selector.py",
            name="sprkl_portfolio_selector",
            dependencies=runs[-1],
            base_dir="Tmp"
        ))

        runs.append(rrr.add_to_queue(
            runner=run_on,
            cmd="Commands/generate_report.py",
            name="sprkl_report",
            dependencies=runs[-1],
            base_dir="Tmp"
        ))

    if run_on == "local":
        print("c Waiting for the local calculations to finish.")
        for run in runs:
            run.wait()
        print("c Running solvers done!")
    elif run_on == "slurm":
        print("c Running solvers in parallel. Waiting for Slurm job(s) with id(s): "
              f"{','.join(r.run_id for r in runs if r is not None)}")

    return


def construct_selector_and_report(dependency_jobid_list: List[str] = []):
    job_script = "Commands/construct_sparkle_portfolio_selector.py"
    run_job_parallel_jobid = sjph.running_job_parallel(
        job_script,
        dependency_jobid_list,
        CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR,
    )

    if run_job_parallel_jobid:
        dependency_jobid_list.append(run_job_parallel_jobid)
    job_script = "Commands/generate_report.py"
    run_job_parallel_jobid = sjph.running_job_parallel(
        job_script, dependency_jobid_list, CommandName.GENERATE_REPORT
    )

    return run_job_parallel_jobid


if __name__ == r"__main__":
    # Initialise settings
    global settings
    sgh.settings = sparkle_settings.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--recompute",
        action="store_true",
        help="recompute the performance of all solvers on all instances",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="run the solver on multiple instances in parallel",
    )
    parser.add_argument(
        "--performance-measure",
        choices=PerformanceMeasure.__members__,
        help="the performance measure, e.g. runtime",
    )
    parser.add_argument(
        "--target-cutoff-time",
        type=int,
        help="cutoff time per target algorithm run in seconds",
    )
    parser.add_argument(
        "--also-construct-selector-and-report",
        action="store_true",
        help=("after running the solvers also construct the selector and generate"
              " the report"),
    )
    parser.add_argument(
        "--verifier",
        choices=SolutionVerifier.__members__,
        help=("problem specific verifier that should be used to verify solutions found"
              " by a target algorithm"),
    )

    parser.add_argument(
        "--run-on",
        default="slurm",
        help=("On which computer or cluster environment to execute the calculation."
              "Available: local, slurm. Default: slurm"),
    )

    parser.add_argument(
        "--settings-file",
        type=Path,
        help=("specify the settings file to use in case you want to use one other than"
              " the default"),
    )

    # Process command line arguments
    args = parser.parse_args()

    if args.settings_file is not None:
        sgh.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file

    if args.performance_measure is not None:
        sgh.settings.set_general_performance_measure(
            PerformanceMeasure.from_str(args.performance_measure), SettingState.CMD_LINE
        )

    if args.verifier is not None:
        sgh.settings.set_general_solution_verifier(
            SolutionVerifier.from_str(args.verifier), SettingState.CMD_LINE
        )

    if args.target_cutoff_time:
        sgh.settings.set_general_target_cutoff_time(
            args.target_cutoff_time, SettingState.CMD_LINE
        )

    if not srh.detect_current_sparkle_platform_exists():
        print("c No Sparkle platform found; please first run the initialise command")
        exit()

    print("c Start running solvers ...")

    run_solvers_on_instances(
        parallel=args.parallel,
        recompute=args.recompute,
        also_construct_selector_and_report=args.also_construct_selector_and_report,
        run_on=args.run_on,
    )
