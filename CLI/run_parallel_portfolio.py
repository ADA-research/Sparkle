#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Sparkle command to execute a parallel algorithm portfolio."""

import sys
import argparse
import random
import time
import shutil
import csv
import itertools
from pathlib import Path, PurePath

import runrunner as rrr
from runrunner.base import Runner
from runrunner.slurm import Status

from CLI.help.reporting_scenario import Scenario
import sparkle_logging as sl
from sparkle.platform import settings_help
from sparkle.types.objective import PerformanceMeasure
import global_variables as gv
from sparkle.platform.settings_help import SettingState, Settings
from sparkle.solver import Solver
from sparkle.instance import Instances
from CLI.help import command_help as sch
from CLI.initialise import check_for_initialise
from CLI.help import argparse_custom as ac
from CLI.help.command_help import CommandName
from tools.runsolver_parsing import get_runtime, get_status
from CLI.help.nicknames import resolve_object_name


def run_parallel_portfolio(instances: Instances,
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
    num_solvers, num_instances = len(solvers), len(instances.instance_paths)
    seeds_per_solver = gv.settings.get_parallel_portfolio_number_of_seeds_per_solver()
    num_jobs = num_solvers * num_instances * seeds_per_solver
    parallel_jobs = min(gv.settings.get_number_of_jobs_in_parallel(), num_jobs)
    if parallel_jobs > num_jobs:
        print("WARNING: Not all jobs will be started at the same time due to the "
              "limitation of number of Slurm jobs that can be run in parallel. Check"
              " your Sparkle Slurm Settings.")
    print(f"Sparkle parallel portfolio is running {seeds_per_solver} seed(s) of "
          f"{num_solvers} solvers on {num_instances} instances ...")
    cmd_list, runsolver_logs = [], []
    cutoff = gv.settings.get_general_target_cutoff_time()
    log_timestamp = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(time.time()))
    log_path = portfolio_path / "run-status-path"
    log_path.mkdir()
    # Create a command for each instance-solver-seed combination
    for instance, solver in itertools.product(instances.instance_paths, solvers):
        for _ in range(seeds_per_solver):
            seed = int(random.getrandbits(32))
            runsolver_watch_log =\
                log_path / f"{solver.name}_{instance.name}_{seed}_{log_timestamp}.log"
            runsolver_values_log =\
                log_path / f"{solver.name}_{instance.name}_{seed}_{log_timestamp}.var"
            raw_result_path =\
                log_path / f"{solver.name}_{instance.name}_{seed}_{log_timestamp}.raw"
            solver_call_list = solver.build_cmd(
                str(instance),
                configuration={"specifics": "",
                               "seed": seed,
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
    sbatch_options = gv.settings.get_slurm_extra_options(as_args=True)
    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=CommandName.RUN_PARALLEL_PORTFOLIO,
        parallel_jobs=parallel_jobs,
        path=".",
        base_dir=gv.sparkle_tmp_path,
        srun_options=["-N1", "-n1"] + sbatch_options,
        sbatch_options=sbatch_options
    )
    check_interval = gv.settings.get_parallel_portfolio_check_interval()
    instances_done = [False] * num_instances
    # We record the 'best' of all seed results per solver-instance
    job_output_dict = {instance_name: {solver.name: {"killed": False,
                                                     "cpu-time": float(sys.maxsize),
                                                     "wc-time": float(sys.maxsize),
                                                     "status": "UNKNOWN"}
                                       for solver in solvers}
                       for instance_name in instances.instance_names}
    n_instance_jobs = num_solvers * seeds_per_solver
    while not all(instances_done):
        time.sleep(check_interval)
        job_status_list = [r.status for r in run.jobs]
        job_status_completed = [status == Status.COMPLETED for status in job_status_list]
        # The jobs are sorted by instance
        for i, instance in enumerate(instances):
            if instances_done[i]:
                continue
            instance_job_slice = slice(i * n_instance_jobs, (i + 1) * n_instance_jobs)
            if any(job_status_completed[instance_job_slice]):
                instances_done[i] = True
                # Kill all running jobs for this instance
                solver_kills = [0] * num_solvers
                for job_index in range(i * n_instance_jobs, (i + 1) * n_instance_jobs):
                    if not job_status_completed[job_index]:
                        run.jobs[job_index].kill()
                        solver_index = int(
                            (job_index % n_instance_jobs) / seeds_per_solver)
                        solver_kills[solver_index] += 1
                for solver_index in range(num_solvers):
                    # All seeds of a solver were killed on instance, set state to killed
                    if solver_kills[solver_index] == seeds_per_solver:
                        solver_name = solvers[solver_index].name
                        job_output_dict[instance.name][solver_name]["killed"] = True
                        job_output_dict[instance.name][solver_name]["status"] = "KILLED"

    # Now iterate over runsolver logs to get runtime, get the lowest value per seed
    for index, solver_logs in enumerate(runsolver_logs):
        solver_index = int((index % n_instance_jobs) / seeds_per_solver)
        solver_name = solvers[solver_index].name
        instance_name = instances.instance_names[int(index / n_instance_jobs)]
        if not solver_logs[1].exists():
            # NOTE: Runsolver is still wrapping up, not a pretty solution
            time.sleep(5)
        if not solver_logs[2].exists():
            # NOTE: Runsolver is still wrapping up, not a pretty solution
            time.sleep(5)
        cpu_time, wallclock_time = get_runtime(solver_logs[1])
        if cpu_time < job_output_dict[instance_name][solver_name]["cpu-time"]:
            job_output_dict[instance_name][solver_name]["cpu-time"] = cpu_time
            job_output_dict[instance_name][solver_name]["wc-time"] = wallclock_time
            if not job_output_dict[instance_name][solver_name]["killed"]:
                job_output_dict[instance_name][solver_name]["status"] =\
                    get_status(solver_logs[1], solver_logs[2])

    # Fix the CPU/WC time for non existent logs to instance min time + check_interval
    for instance in job_output_dict.keys():
        no_log_solvers = []
        min_time = cutoff
        for solver in job_output_dict[instance].keys():
            if job_output_dict[instance][solver]["cpu-time"] == -1.0:
                no_log_solvers.append(solver)
            elif job_output_dict[instance][solver]["cpu-time"] < min_time:
                min_time = job_output_dict[instance][solver]["cpu-time"]
        for solver in no_log_solvers:
            job_output_dict[instance][solver]["cpu-time"] = min_time + cutoff
            job_output_dict[instance][solver]["wc-time"] = min_time + cutoff

    for index, instance in enumerate(instances):
        index_str = f"[{index + 1}/{num_instances}] "
        instance_output = job_output_dict[instance.name]
        if all([instance_output[k]["status"] == "TIMEOUT"
                for k in instance_output.keys()]):
            print(f"\n{index_str}{instance.name} was not solved within the cutoff-time.")
            continue
        print(f"\n{index_str}{instance.name} yielded the following Solver results:")
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
        solver_paths = [resolve_object_name("".join(s), target_dir=gv.solver_dir)
                        for s in args.solvers]
        if None in solver_paths:
            print("Some solvers not recognised! Check solver names:")
            for i, name in enumerate(solver_paths):
                if solver_paths[i] is None:
                    print(f'\t- "{solver_paths[i]}" ')
            sys.exit(-1)
        solvers = [Solver(p) for p in solver_paths]
    else:
        solvers = [Solver(p) for p in gv.solver_dir.iterdir() if p.is_dir()]



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

    # Retrieve instance set
    
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
