#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Sparkle command to execute a parallel algorithm portfolio.."""

import sys
import argparse
import random
import time
import shutil
import csv
from pathlib import Path, PurePath

import runrunner as rrr
from runrunner.base import Runner
from runrunner.slurm import Status

from CLI.help.reporting_scenario import Scenario
import sparkle_logging as sl
from sparkle.platform import settings_help
from sparkle.types.objective import PerformanceMeasure
import global_variables as gv
from sparkle.platform import slurm_help as ssh
from sparkle.platform.settings_help import SettingState, Settings
from sparkle.solver.solver import Solver
from CLI.help import command_help as sch
from CLI.initialise import check_for_initialise
from CLI.help import argparse_custom as ac
from CLI.help.command_help import CommandName
from tools.runsolver_parsing import get_runtime, get_status


def run_parallel_portfolio(instances: list[Path],
                           portfolio_path: Path,
                           solvers: list[Solver],
                           run_on: Runner = Runner.SLURM) -> None:
    """Run the parallel algorithm portfolio.

    Args:
        instances: List of instance Paths.
        portfolio_path: Path to the parallel portfolio.
        solvers: List of solvers to run on the instances.
        run_on: Currently only supports Slurm.
    """
    num_solvers, num_instances = len(solvers), len(instances)
    num_jobs = num_solvers * num_instances
    parallel_jobs = min(gv.settings.get_slurm_number_of_runs_in_parallel(), num_jobs)
    if parallel_jobs > num_jobs:
        print("WARNING: Not all jobs will be started at the same time due to the "
              "limitation of number of Slurm jobs that can be run in parallel. Check"
              " your Sparkle Slurm Settings.")
    cmd_list, runsolver_logs = [], []
    cutoff = gv.settings.get_general_target_cutoff_time()
    log_timestamp = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(time.time()))
    run_status_path = portfolio_path / "run-status-path"
    run_status_path.mkdir()
    # Create a command for each instance-solver combination
    for instance in instances:
        for solver in solvers:
            runsolver_watch_log =\
                run_status_path / f"{solver.name}_{instance.name}_{log_timestamp}.log"
            runsolver_values_log =\
                run_status_path / f"{solver.name}_{instance.name}_{log_timestamp}.var"
            raw_result_path =\
                run_status_path / f"{solver.name}_{instance.name}_{log_timestamp}.raw"
            print(runsolver_values_log)
            solver_call_list = solver.build_solver_cmd(
                str(instance),
                configuration={"specifics": "",
                               "seed": 1,
                               "cutoff_time": cutoff,
                               "run_length": cutoff},
                runsolver_configuration=["--timestamp", "--use-pty",
                                         "--cpu-limit", str(cutoff),
                                         "-w", runsolver_watch_log,
                                         "-v", runsolver_values_log,
                                         "-o", raw_result_path])

            cmd_list.append((" ".join(solver_call_list)).replace("'", '"'))
            runsolver_logs.append([runsolver_watch_log,
                                   runsolver_values_log,
                                   raw_result_path])

    # Jobs are added in to the runrunner object in the same order they are provided
    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=CommandName.RUN_PARALLEL_PORTFOLIO,
        parallel_jobs=parallel_jobs,
        path=".",
        base_dir=gv.sparkle_tmp_path,
        srun_options=["-N1", "-n1"] + ssh.get_slurm_options_list(),
        sbatch_options=ssh.get_slurm_options_list()
    )
    check_interval = gv.settings.get_parallel_portfolio_check_interval()
    instances_done = [False] * num_instances
    job_output_dict = {instance.name: {solver.name: {"killed": False,
                                                     "cpu-time": -1.0,
                                                     "wc-time": -1.0,
                                                     "status": "UNKNOWN"}
                                       for solver in solvers}
                       for instance in instances}
    while not all(instances_done):
        time.sleep(check_interval)
        job_status_list = [r.status for r in run.jobs]
        job_status_completed = [status == Status.COMPLETED for status in job_status_list]
        # The jobs are sorted by instance
        for i, instance in enumerate(instances):
            if instances_done[i]:
                continue
            if any(job_status_completed[i * num_solvers:(i + 1) * num_solvers]):
                instances_done[i] = True
                # Kill all running jobs for this instance
                for job_index in range(i * num_solvers, (i + 1) * num_solvers):
                    if not job_status_completed[job_index]:
                        run.jobs[job_index].kill()
                        solver_name = solvers[job_index % num_solvers].name
                        job_output_dict[instance.name][solver_name]["killed"] = True
                        job_output_dict[instance.name][solver_name]["status"] = "KILLED"

    # Now we iterate over the logs to get the runtime values
    for index, solver_logs in enumerate(runsolver_logs):
        solver_name = solvers[index % num_solvers].name
        instance_name = instances[int(index / num_solvers)].name
        if not solver_logs[1].exists():
            # NOTE: Runsolver is still wrapping up, not a pretty solution
            time.sleep(5)
        cpu_time, wallclock_time = get_runtime(solver_logs[1])
        job_output_dict[instance_name][solver_name]["cpu-time"] = cpu_time
        job_output_dict[instance_name][solver_name]["wc-time"] = wallclock_time
        if not job_output_dict[instance_name][solver_name]["killed"]:
            job_output_dict[instance_name][solver_name]["status"] =\
                get_status(solver_logs[1], solver_logs[2])

    for index, instance in enumerate(instances):
        index_print = f"[{index + 1}/{num_instances}] "
        if not instances_done[index]:
            print(f"{index_print}{instance.name} was not solved within the cutoff-time.")
            continue
        print(f"\n{index_print}{instance.name} yielded the following Solver results:")
        for sindex in range(index * num_solvers, (index + 1) * num_solvers):
            solver_name = solvers[sindex % num_solvers].name
            job_info = job_output_dict[instance.name][solver_name]
            print(f"\t- {solver_name} ended with status {job_info['status']} in "
                  f"{job_info['cpu-time']}s CPU-Time ({job_info['wc-time']}s WC-Time)")

    # Write the results to a CSV
    csv_path = portfolio_path / "results.csv"
    with csv_path.open("w") as out:
        writer = csv.writer(out)
        for instance_name in job_output_dict.keys():
            for solver_name in job_output_dict[instance_name].keys():
                job_o = job_output_dict[instance_name][solver_name]
                writer.writerow((instance_name, solver_name,
                                 job_o["status"], job_o["cpu-time"], job_o["wc-time"]))


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments.

    Returns:
        parser: The parser with the parsed command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(*ac.InstancePathsRunParallelPortfolioArgument.names,
                        **ac.InstancePathsRunParallelPortfolioArgument.kwargs)
    parser.add_argument(*ac.NicknamePortfolioArgument.names,
                        **ac.NicknamePortfolioArgument.kwargs)
    parser.add_argument(*ac.SolversArgument.names,
                        **ac.SolversArgument.kwargs)
    parser.add_argument(*ac.PerformanceMeasureSimpleArgument.names,
                        **ac.PerformanceMeasureSimpleArgument.kwargs)
    parser.add_argument(*ac.CutOffTimeArgument.names,
                        **ac.CutOffTimeArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    return parser


if __name__ == "__main__":
    # Initialise settings
    gv.settings = settings_help.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    if args.solvers is not None:
        solver_names = ["".join(s) for s in args.solvers]
        solvers = [Solver.get_solver_by_name(solver) for solver in solver_names]
        if None in solvers:
            print("Some solvers not recognised! Check solver names:")
            for i, name in enumerate(solver_names):
                if solvers[i] is None:
                    print(f'\t- "{solver_names[i]}" ')
            sys.exit(-1)
    else:
        solvers = [Solver.get_solver_by_name(p) for p in gv.solver_dir.iterdir()]

    check_for_initialise(
        sys.argv,
        sch.COMMAND_DEPENDENCIES[sch.CommandName.RUN_PARALLEL_PORTFOLIO]
    )

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings, prev_settings)

    # Do first, so other command line options can override settings from the file
    if args.settings_file is not None:
        gv.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)

    portfolio_path = args.portfolio_name
    run_on = args.run_on

    if run_on == Runner.LOCAL:
        print("Parallel Portfolio is not fully supported yet for Local runs. Exiting.")
        sys.exit(-1)

    # Create list of instance paths
    instance_paths = []

    for instance in args.instance_paths:
        instance_path = Path(instance)
        if not instance_path.exists():
            print(f'Instance "{instance}" not found, aborting the process.')
            sys.exit(-1)
        if instance_path.is_file():
            print(f"Running on instance {instance}")
            instance_paths.append(instance_path)
        elif not instance_path.is_dir():
            instance_path = gv.instance_dir / instance

        if instance_path.is_dir():
            items = [instance_path / p.name for p in Path(instance).iterdir()
                     if p.is_file()]
            print(f"Running on {len(items)} instance(s) from "
                  f"directory {instance}")
            instance_paths.extend(items)

    if args.cutoff_time is not None:
        gv.settings.set_general_target_cutoff_time(args.cutoff_time,
                                                   SettingState.CMD_LINE)

    if args.performance_measure is not None:
        gv.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE)
    if gv.settings.get_general_sparkle_objectives()[0].PerformanceMeasure\
            is not PerformanceMeasure.RUNTIME:
        print("ERROR: Parallel Portfolio is currently only relevant for "
              f"{PerformanceMeasure.RUNTIME} measurement. In all other cases, "
              "use validation")
        sys.exit(-1)
    # Write settings to file before starting, since they are used in callback scripts
    gv.settings.write_used_settings()

    print("Sparkle parallel portfolio is running ...")
    if args.portfolio_name is not None:  # Use a nickname
        portfolio_path = gv.parallel_portfolio_output_raw / args.portfolio_name
    else:  # Generate a timestamped nickname
        timestamp = time.strftime("%Y-%m-%d-%H:%M:%S", time.gmtime(time.time()))
        randintstamp = int(random.getrandbits(32))
        portfolio_path = gv.parallel_portfolio_output_raw / f"{timestamp}_{randintstamp}"
    if portfolio_path.exists():
        print(f"[WARNING] Portfolio path {portfolio_path} already exists! "
              "Overwrite? [y/n] ", end="")
        user_input = input()
        if user_input != "y":
            sys.exit()
        shutil.rmtree(portfolio_path)
    portfolio_path.mkdir(parents=True)
    run_parallel_portfolio(instance_paths, portfolio_path, solvers, run_on=run_on)

    # Update latest scenario
    gv.latest_scenario().set_parallel_portfolio_path(portfolio_path)
    gv.latest_scenario().set_latest_scenario(Scenario.PARALLEL_PORTFOLIO)
    gv.latest_scenario().set_parallel_portfolio_instance_list(instance_paths)
    # NOTE: Patching code to make sure generate report still works
    solvers_file = portfolio_path / "solvers.txt"
    with solvers_file.open("w") as fout:
        for solver in solvers:
            fout.write(f"{solver.directory}\n")
    print("Running Sparkle parallel portfolio is done!")

    # Write used settings to file
    gv.settings.write_used_settings()
