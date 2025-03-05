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

from tqdm import tqdm

import runrunner as rrr
from runrunner.base import Runner
from runrunner.slurm import Status

from sparkle.CLI.help.reporting_scenario import Scenario
from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help.nicknames import resolve_object_name
from sparkle.platform.settings_objects import Settings, SettingState
from sparkle.solver import Solver
from sparkle.instance import Instance_Set, InstanceSet
from sparkle.types import SolverStatus, resolve_objective, UseTime


def run_parallel_portfolio(instances_set: InstanceSet,
                           portfolio_path: Path,
                           solvers: list[Solver],
                           run_on: Runner = Runner.SLURM) -> None:
    """Run the parallel algorithm portfolio.

    Args:
        instances_set: Set of instances to run on.
        portfolio_path: Path to the parallel portfolio.
        solvers: List of solvers to run on the instances.
        run_on: Currently only supports Slurm.
    """
    num_solvers, num_instances = len(solvers), len(instances_set._instance_paths)
    seeds_per_solver = gv.settings().get_parallel_portfolio_number_of_seeds_per_solver()
    num_jobs = num_solvers * num_instances * seeds_per_solver
    parallel_jobs = min(gv.settings().get_number_of_jobs_in_parallel(), num_jobs)
    if parallel_jobs > num_jobs:
        print("WARNING: Not all jobs will be started at the same time due to the "
              "limitation of number of Slurm jobs that can be run in parallel. Check"
              " your Sparkle Slurm Settings.")
    print(f"Sparkle parallel portfolio is running {seeds_per_solver} seed(s) per solver "
          f"on {num_solvers} solvers for {num_instances} instances ...")
    cmd_list = []
    cutoff = gv.settings().get_general_target_cutoff_time()
    objectives = gv.settings().get_general_sparkle_objectives()
    # Create a command for each instance-solver-seed combination
    for instance, solver in itertools.product(instances_set._instance_paths, solvers):
        for _ in range(seeds_per_solver):
            seed = int(random.getrandbits(32))
            solver_call_list = solver.build_cmd(
                instance.absolute(),
                objectives=objectives,
                seed=seed,
                cutoff_time=cutoff,
                log_dir=portfolio_path)
            cmd_list.append((" ".join(solver_call_list)).replace("'", '"'))
    # Jobs are added in to the runrunner object in the same order they are provided
    sbatch_options = gv.settings().get_slurm_extra_options(as_args=True)
    solver_names = ", ".join([s.name for s in solvers])
    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=f"Parallel Portfolio: {solver_names}",
        parallel_jobs=parallel_jobs,
        base_dir=sl.caller_log_dir,
        srun_options=["-N1", "-n1"] + sbatch_options,
        sbatch_options=sbatch_options,
        prepend=gv.settings().get_slurm_job_prepend(),
    )
    check_interval = gv.settings().get_parallel_portfolio_check_interval()
    instances_done = [False] * num_instances
    # We record the 'best' of all seed results per solver-instance,
    # setting start values for objectives that are always present
    cpu_time_key = [o.name for o in objectives if o.name.startswith("cpu_time")][0]
    status_key = [o.name for o in objectives if o.name.startswith("status")][0]
    wall_time_key = [o.name for o in objectives if o.name.startswith("wall_time")][0]
    default_objective_values = {}
    for o in objectives:
        default_value = float(sys.maxsize) if o.minimise else 0
        # Default values for time objectives can be linked to cutoff time
        if o.time and o.post_process:
            default_value = o.post_process(default_value, cutoff, SolverStatus.KILLED)
        default_objective_values[o.name] = default_value
    default_objective_values[status_key] = SolverStatus.UNKNOWN  # Overwrite Status
    job_output_dict = {instance_name: {solver.name: default_objective_values.copy()
                                       for solver in solvers}
                       for instance_name in instances_set._instance_names}
    n_instance_jobs = num_solvers * seeds_per_solver

    with tqdm(total=len(instances_done)) as pbar:
        pbar.set_description("Instances done")
        while not all(instances_done):
            prev_done = sum(instances_done)
            time.sleep(check_interval)
            job_status_list = [r.status for r in run.jobs]
            job_status_completed = [status == Status.COMPLETED
                                    for status in job_status_list]
            # The jobs are sorted by instance
            for i, instance in enumerate(instances_set._instance_paths):
                if instances_done[i]:
                    continue
                instance_job_slice = slice(i * n_instance_jobs,
                                           (i + 1) * n_instance_jobs)
                if any(job_status_completed[instance_job_slice]):
                    instances_done[i] = True
                    # Kill all running jobs for this instance
                    solver_kills = [0] * num_solvers
                    for job_index in range(i * n_instance_jobs,
                                           (i + 1) * n_instance_jobs):
                        if not job_status_completed[job_index]:
                            run.jobs[job_index].kill()
                            solver_index = int(
                                (job_index % n_instance_jobs) / seeds_per_solver)
                            solver_kills[solver_index] += 1
                    for solver_index in range(num_solvers):
                        # All seeds of a solver were killed on instance, set status kill
                        if solver_kills[solver_index] == seeds_per_solver:
                            solver_name = solvers[solver_index].name
                            job_output_dict[instance.name][solver_name]["status"] =\
                                SolverStatus.KILLED
            pbar.update(sum(instances_done) - prev_done)

    # Attempt to verify that all logs have been written (Slurm I/O latency)
    for index, cmd in enumerate(cmd_list):
        runsolver_configuration = cmd.split(" ")[:11]
        logs = [Path(p) for p in runsolver_configuration
                if Path(p).suffix in [".log", ".val", ".rawres"]]
        if not all([p.exists() for p in logs]):
            time.sleep(check_interval)

    # Now iterate over runsolver logs to get runtime, get the lowest value per seed
    for index, cmd in enumerate(cmd_list):
        solver_index = int((index % n_instance_jobs) / seeds_per_solver)
        runsolver_configuration = cmd.split(" ")[:11]
        solver_obj = solvers[solver_index]
        solver_output = Solver.parse_solver_output(run.jobs[i].stdout,
                                                   cmd.split(" "),
                                                   objectives=objectives,
                                                   verifier=solver_obj.verifier)
        instance_name = instances_set._instance_names[int(index / n_instance_jobs)]
        cpu_time = solver_output[cpu_time_key]
        cmd_output = job_output_dict[instance_name][solver_obj.name]
        if cpu_time > 0.0 and cpu_time < cmd_output[cpu_time_key]:
            for key, value in solver_output.items():
                if key in [o.name for o in objectives]:
                    job_output_dict[instance_name][solver_obj.name][key] = value
            if (status_key not in cmd_output
                    or cmd_output[status_key] != SolverStatus.KILLED):
                cmd_output[status_key] = solver_output[status_key]

    # Fix the CPU/WC time for non existent logs to instance min time + check_interval
    for instance in job_output_dict.keys():
        no_log_solvers = []
        min_time = cutoff
        for solver in job_output_dict[instance].keys():
            cpu_time = job_output_dict[instance][solver][cpu_time_key]
            if cpu_time == -1.0 or cpu_time == float(sys.maxsize):
                no_log_solvers.append(solver)
            elif cpu_time < min_time:
                min_time = cpu_time
        for solver in no_log_solvers:
            job_output_dict[instance][solver][cpu_time_key] = min_time + check_interval
            job_output_dict[instance][solver][wall_time_key] = min_time + check_interval
            # Fix runtime objectives with resolved CPU/Wall times
            for key, value in job_output_dict[instance][solver].items():
                objective = resolve_objective(key)
                if objective is not None and objective.time:
                    print(key, value)
                    if objective.use_time == UseTime.CPU_TIME:
                        value = job_output_dict[instance][solver][cpu_time_key]
                    else:
                        value = job_output_dict[instance][solver][wall_time_key]
                    if objective.post_process is not None:
                        status = job_output_dict[instance][solver][status_key]
                        value = objective.post_process(value, cutoff, status)
                    job_output_dict[instance][solver][key] = value

    for index, instance_name in enumerate(instances_set._instance_names):
        index_str = f"[{index + 1}/{num_instances}] "
        instance_output = job_output_dict[instance_name]
        if all([instance_output[k][status_key] == SolverStatus.TIMEOUT
                for k in instance_output.keys()]):
            print(f"\n{index_str}{instance_name} was not solved within the cutoff-time.")
            continue
        print(f"\n{index_str}{instance_name} yielded the following Solver results:")
        for sindex in range(index * num_solvers, (index + 1) * num_solvers):
            solver_name = solvers[sindex % num_solvers].name
            job_info = job_output_dict[instance_name][solver_name]
            print(f"\t- {solver_name} ended with status {job_info[status_key]} in "
                  f"{job_info[cpu_time_key]}s CPU-Time ({job_info[wall_time_key]}s "
                  "Wall clock time)")

    # Write the results to a CSV
    csv_path = portfolio_path / "results.csv"
    values_header = [o.name for o in objectives]
    header = ["Instance", "Solver"] + values_header
    result_rows = [header]
    for instance_name in job_output_dict.keys():
        for solver_name in job_output_dict[instance_name].keys():
            job_o = job_output_dict[instance_name][solver_name]
            values = [instance_name, solver_name] + [
                job_o[key] if key in job_o else "None"
                for key in values_header]
            result_rows.append(values)
    with csv_path.open("w") as out:
        writer = csv.writer(out)
        writer.writerows(result_rows)


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments.

    Returns:
        parser: The parser with the parsed command line arguments
    """
    parser = argparse.ArgumentParser(description="Run a portfolio of solvers on an "
                                                 "instance set in parallel.")
    parser.add_argument(*ac.InstanceSetPathsArgument.names,
                        **ac.InstanceSetPathsArgument.kwargs)
    parser.add_argument(*ac.NicknamePortfolioArgument.names,
                        **ac.NicknamePortfolioArgument.kwargs)
    parser.add_argument(*ac.SolversArgument.names,
                        **ac.SolversArgument.kwargs)
    parser.add_argument(*ac.ObjectivesArgument.names,
                        **ac.ObjectivesArgument.kwargs)
    parser.add_argument(*ac.CutOffTimeArgument.names,
                        **ac.CutOffTimeArgument.kwargs)
    parser.add_argument(*ac.SolverSeedsArgument.names,
                        **ac.SolverSeedsArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    return parser


def main(argv: list[str]) -> None:
    """Main method of run parallel portfolio command."""
    # Log command call
    sl.log_command(sys.argv)
    check_for_initialise()

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)
    if args.solvers is not None:
        solver_paths = [resolve_object_name("".join(s),
                                            target_dir=gv.settings().DEFAULT_solver_dir)
                        for s in args.solvers]
        if None in solver_paths:
            print("Some solvers not recognised! Check solver names:")
            for i, name in enumerate(solver_paths):
                if solver_paths[i] is None:
                    print(f'\t- "{solver_paths[i]}" ')
            sys.exit(-1)
        solvers = [Solver(p) for p in solver_paths]
    else:
        solvers = [Solver(p) for p in
                   gv.settings().DEFAULT_solver_dir.iterdir() if p.is_dir()]

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings(), prev_settings)

    # Do first, so other command line options can override settings from the file
    if args.settings_file is not None:
        gv.settings().read_settings_ini(args.settings_file, SettingState.CMD_LINE)

    portfolio_path = args.portfolio_name

    if args.run_on is not None:
        gv.settings().set_run_on(
            args.run_on.value, SettingState.CMD_LINE)
    run_on = gv.settings().get_run_on()

    if args.solver_seeds is not None:
        gv.settings().set_parallel_portfolio_number_of_seeds_per_solver(
            args.solver_seeds, SettingState.CMD_LINE)

    if run_on == Runner.LOCAL:
        print("Parallel Portfolio is not fully supported yet for Local runs. Exiting.")
        sys.exit(-1)

    # Retrieve instance sets
    instances = [resolve_object_name(instance_path,
                 gv.file_storage_data_mapping[gv.instances_nickname_path],
                 gv.settings().DEFAULT_instance_dir, Instance_Set)
                 for instance_path in args.instance_path]
    # Join them into one
    if len(instances) > 1:
        print("WARNING: More than one instance set specified. "
              "Currently only supporting one.")
    instances = instances[0]

    print(f"Running on {instances.size} instance(s)...")

    if args.cutoff_time is not None:
        gv.settings().set_general_target_cutoff_time(args.cutoff_time,
                                                     SettingState.CMD_LINE)

    if args.objectives is not None:
        gv.settings().set_general_sparkle_objectives(
            args.objectives, SettingState.CMD_LINE)
    if not gv.settings().get_general_sparkle_objectives()[0].time:
        print("ERROR: Parallel Portfolio is currently only relevant for "
              "RunTime objectives. In all other cases, use validation")
        sys.exit(-1)

    if args.portfolio_name is not None:  # Use a nickname
        portfolio_path = gv.settings().DEFAULT_parallel_portfolio_output_raw /\
            args.portfolio_name
    else:  # Generate a timestamped nickname
        timestamp = time.strftime("%Y-%m-%d-%H:%M:%S", time.gmtime(time.time()))
        randintstamp = int(random.getrandbits(32))
        portfolio_path = gv.settings().DEFAULT_parallel_portfolio_output_raw /\
            f"{timestamp}_{randintstamp}"
    if portfolio_path.exists():
        print(f"[WARNING] Portfolio path {portfolio_path} already exists! "
              "Overwrite? [y/n] ", end="")
        user_input = input()
        if user_input != "y":
            sys.exit()
        shutil.rmtree(portfolio_path)
    portfolio_path.mkdir(parents=True)
    run_parallel_portfolio(instances, portfolio_path, solvers, run_on=run_on)

    # Update latest scenario
    gv.latest_scenario().set_parallel_portfolio_path(portfolio_path)
    gv.latest_scenario().set_latest_scenario(Scenario.PARALLEL_PORTFOLIO)
    gv.latest_scenario().set_parallel_portfolio_instance_path(instances.directory)
    # Write used scenario to file
    gv.latest_scenario().write_scenario_ini()
    # Write used settings to file
    gv.settings().write_used_settings()
    print("Running Sparkle parallel portfolio is done!")
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
