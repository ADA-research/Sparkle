#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Sparkle command to execute a parallel algorithm portfolio."""

import sys
import argparse
import random
import time
import shutil
import itertools
from operator import mod
from pathlib import Path

from tqdm import tqdm

import runrunner as rrr
from runrunner.base import Runner, Run
from runrunner.slurm import Status, SlurmRun

from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help.nicknames import resolve_object_name
from sparkle.platform.settings_objects import Settings
from sparkle.solver import Solver
from sparkle.instance import Instance_Set, InstanceSet
from sparkle.types import SolverStatus, resolve_objective, UseTime
from sparkle.structures import PerformanceDataFrame


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments.

    Returns:
        parser: The parser with the parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Run a portfolio of solvers on an instance set in parallel."
    )
    parser.add_argument(
        *ac.InstanceSetPathsArgument.names, **ac.InstanceSetPathsArgument.kwargs
    )
    parser.add_argument(
        *ac.NicknamePortfolioArgument.names, **ac.NicknamePortfolioArgument.kwargs
    )
    parser.add_argument(*ac.SolversArgument.names, **ac.SolversArgument.kwargs)
    # Settings arguments
    parser.add_argument(*ac.SettingsFileArgument.names, **ac.SettingsFileArgument.kwargs)
    parser.add_argument(
        *Settings.OPTION_objectives.args, **Settings.OPTION_objectives.kwargs
    )
    parser.add_argument(
        *Settings.OPTION_solver_cutoff_time.args,
        **Settings.OPTION_solver_cutoff_time.kwargs,
    )
    parser.add_argument(
        *Settings.OPTION_parallel_portfolio_number_of_seeds_per_solver.args,
        **Settings.OPTION_parallel_portfolio_number_of_seeds_per_solver.kwargs,
    )
    parser.add_argument(*Settings.OPTION_run_on.args, **Settings.OPTION_run_on.kwargs)
    return parser


def create_performance_dataframe(
    solvers: list[Solver], instances_set: InstanceSet, portfolio_path: Path
) -> PerformanceDataFrame:
    """Create a PerformanceDataFrame for the given solvers and instances.

    Args:
        solvers: List of solvers to include in the PerformanceDataFrame.
        instances_set: Set of instances to include in the PerformanceDataFrame.
        portfolio_path: Path to save the CSV file.

    Returns:
        pdf: PerformanceDataFrame object initialized with solvers and instances.
    """
    instances = instances_set.instance_names
    solvers = [str(s.directory) for s in solvers]
    objectives = gv.settings().objectives
    csv_path = portfolio_path / "results.csv"
    return PerformanceDataFrame(
        csv_filepath=csv_path,
        solvers=solvers,
        objectives=objectives,
        instances=instances,
    )


def init_default_objectives() -> list:
    """Initialize default objective values and key names.

    Returns:
        default_objective_values: Dictionary with default values for each objective.
        cpu_time_key: Key for CPU time in the default values.
        status_key: Key for status in the default values.
        wall_time_key: Key for wall clock time in the default values.
    """
    # We record the 'best' of all seed results per solver-instance,
    # setting start values for objectives that are always present
    objectives = gv.settings().objectives
    cutoff = gv.settings().solver_cutoff_time
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
    default_objective_values[status_key] = SolverStatus.UNKNOWN  # Overwrite status
    return default_objective_values, cpu_time_key, status_key, wall_time_key


def monitor_jobs(
    run: Run,
    instances_set: InstanceSet,
    solvers: list[Solver],
    default_objective_values: dict,
    run_on: Runner = Runner.SLURM,
) -> dict:
    """Monitor job progress and update job output dictionary.

    Args:
        run: The run object containing the submitted jobs.
        instances_set: Set of instances to run on.
        solvers: List of solvers to run on the instances.
        default_objective_values: Default objective values for each solver-instance.
        run_on: Unused

    Returns:
        job_output_dict: Dictionary containing the job output for each instance-solver
                            combination.
    """
    num_solvers, num_instances = len(solvers), len(instances_set._instance_paths)
    seeds_per_solver = gv.settings().parallel_portfolio_num_seeds_per_solver
    n_instance_jobs = num_solvers * seeds_per_solver

    job_output_dict = {
        instance_name: {
            solver.name: default_objective_values.copy() for solver in solvers
        }
        for instance_name in instances_set._instance_names
    }

    check_interval = gv.settings().parallel_portfolio_check_interval
    instances_done = [False] * num_instances

    with tqdm(total=len(instances_done)) as pbar:
        pbar.set_description("Instances done")
        while not all(instances_done):
            prev_done = sum(instances_done)
            time.sleep(check_interval)
            job_status_list = [r.status for r in run.jobs]
            job_status_completed = [
                status == Status.COMPLETED for status in job_status_list
            ]
            # The jobs are sorted by instance
            for i, instance in enumerate(instances_set._instance_paths):
                if instances_done[i]:
                    continue
                instance_job_slice = slice(
                    i * n_instance_jobs, (i + 1) * n_instance_jobs
                )
                if any(job_status_completed[instance_job_slice]):
                    instances_done[i] = True
                    # Kill remaining jobs for this instance.
                    solver_kills = [0] * num_solvers
                    for job_index in range(
                        i * n_instance_jobs, (i + 1) * n_instance_jobs
                    ):
                        if not job_status_completed[job_index]:
                            run.jobs[job_index].kill()
                            solver_index = int(
                                (mod(job_index, n_instance_jobs)) // seeds_per_solver
                            )
                            solver_kills[solver_index] += 1
                    for solver_index in range(num_solvers):
                        # All seeds of a solver were killed on instance, set status kill
                        if solver_kills[solver_index] == seeds_per_solver:
                            solver_name = solvers[solver_index].name
                            job_output_dict[instance.stem][solver_name]["status"] = (
                                SolverStatus.KILLED
                            )
            pbar.update(sum(instances_done) - prev_done)
    return job_output_dict


def wait_for_logs(cmd_list: list[str]) -> None:
    """Wait for all log files to be written.

    Args:
        cmd_list: List of command strings for all instance-solver-seed combinations.
    """
    # Attempt to verify that all logs have been written (Slurm I/O latency)
    check_interval = gv.settings().parallel_portfolio_check_interval
    for cmd in cmd_list:
        runsolver_configuration = cmd.split(" ")[:11]
        logs = [
            Path(p)
            for p in runsolver_configuration
            if Path(p).suffix in [".log", ".val", ".rawres"]
        ]
        if not all(p.exists() for p in logs):
            time.sleep(check_interval)


def update_results_from_logs(
    cmd_list: list[str],
    run: Run,
    solvers: list[Solver],
    job_output_dict: dict,
    cpu_time_key: str,
) -> dict:
    """Parse logs to update job output dictionary with best objective values.

    Args:
        cmd_list: List of command strings for all instance-solver-seed combinations.
        run: The run object containing the submitted jobs.
        solvers: List of solvers to run on the instances.
        job_output_dict: Dictionary containing the job output for each intsance-solver
                         combination.
        cpu_time_key: Key for CPU time in the job output dictionary.

    Returns:
        job_output_dict: Updated job output dictionary with best objective values.
    """
    seeds_per_solver = gv.settings().parallel_portfolio_num_seeds_per_solver
    num_solvers = len(solvers)
    n_instance_jobs = num_solvers * seeds_per_solver
    objectives = gv.settings().objectives

    for index, cmd in enumerate(cmd_list):
        solver_index = (mod(index, n_instance_jobs)) // seeds_per_solver
        solver_obj = solvers[solver_index]
        solver_output = Solver.parse_solver_output(
            run.jobs[index].stdout,
            cmd.split(" "),
            objectives=objectives,
            verifier=solver_obj.verifier,
        )
        instance_name = list(job_output_dict.keys())[index // n_instance_jobs]
        cpu_time = solver_output[cpu_time_key]
        cmd_output = job_output_dict[instance_name][solver_obj.name]
        if cpu_time > 0.0 and cpu_time < cmd_output[cpu_time_key]:
            for key, value in solver_output.items():
                if key in [o.name for o in objectives]:
                    job_output_dict[instance_name][solver_obj.name][key] = value
            if cmd_output.get("status") != SolverStatus.KILLED:
                cmd_output["status"] = solver_output.get("status")
    return job_output_dict


def fix_missing_times(
    job_output_dict: dict, status_key: str, cpu_time_key: str, wall_time_key: str
) -> dict:
    """Fix CPU and wall clock times for solvers that did not produce logs.

    Args:
        job_output_dict: Dictionary containing the job output for each instance-solver
                            combination.
        status_key: Key for status in the job output dictionary.
        cpu_time_key: Key for CPU time in the job output dictionary.
        wall_time_key: Key for wall clock time in the job output dictionary.

    Returns:
        job_output_dict: Updated job output dictionary with fixed CPU and wall clock
                            times.
    """
    cutoff = gv.settings().solver_cutoff_time
    check_interval = gv.settings().parallel_portfolio_check_interval

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
                    value = (
                        job_output_dict[instance][solver][cpu_time_key]
                        if objective.use_time == UseTime.CPU_TIME
                        else job_output_dict[instance][solver][wall_time_key]
                    )
                    if objective.post_process is not None:
                        status = job_output_dict[instance][solver][status_key]
                        value = objective.post_process(value, cutoff, status)
                    job_output_dict[instance][solver][key] = value
    return job_output_dict


def print_and_write_results(
    job_output_dict: dict,
    solvers: list[Solver],
    instances_set: InstanceSet,
    portfolio_path: Path,
    status_key: str,
    cpu_time_key: str,
    wall_time_key: str,
    pdf: PerformanceDataFrame,
) -> None:
    """Print results to console and write the CSV file."""
    num_instances = len(job_output_dict)
    num_solvers = len(solvers)
    objectives = gv.settings().objectives
    for index, instance_name in enumerate(job_output_dict.keys()):
        index_str = f"[{index + 1}/{num_instances}] "
        instance_output = job_output_dict[instance_name]
        if all(
            instance_output[k][status_key] == SolverStatus.TIMEOUT
            for k in instance_output
        ):
            print(f"\n{index_str}{instance_name} was not solved within the cutoff-time.")
            continue
        print(f"\n{index_str}{instance_name} yielded the following Solver results:")
        for sindex in range(index * num_solvers, (index + 1) * num_solvers):
            solver_name = solvers[mod(sindex, num_solvers)].name
            job_info = job_output_dict[instance_name][solver_name]
            print(
                f"\t- {solver_name} ended with status {job_info[status_key]} in "
                f"{job_info[cpu_time_key]}s CPU-Time ({job_info[wall_time_key]}s "
                "Wall clock time)"
            )

    instance_map = {Path(p).name: p for p in pdf.instances}
    solver_map = {Path(s).name: s for s in pdf.solvers}
    for instance, instance_dict in job_output_dict.items():
        instance_name = Path(instance).name
        instance_full_path = instance_map.get(instance_name, instance)
        for solver, objective_dict in instance_dict.items():
            solver_name = Path(solver).name
            solver_full_path = solver_map.get(solver_name, solver)
            for objective in objectives:
                obj_name = objective.name
                obj_val = objective_dict.get(
                    obj_name, PerformanceDataFrame.missing_value
                )
                pdf.set_value(
                    value=obj_val,
                    solver=solver_full_path,
                    instance=instance_full_path,
                    objective=obj_name,
                )
    pdf.save_csv()


def build_command_list(
    instances_set: InstanceSet,
    solvers: list[Solver],
    portfolio_path: Path,
    performance_data: PerformanceDataFrame,
) -> list[str]:
    """Build the list of command strings for all instance-solver-seed combinations.

    Args:
        instances_set: Set of instances to run on.
        solvers: List of solvers to run on the instances.
        portfolio_path: Path to the parallel portfolio.
        performance_data: PerformanceDataFrame object.

    Returns:
        cmd_list: List of command strings for all instance-solver-seed combinations.
    """
    cutoff = gv.settings().solver_cutoff_time
    objectives = gv.settings().objectives
    seeds_per_solver = gv.settings().parallel_portfolio_num_seeds_per_solver
    cmd_list = []

    # Create a command for each instance-solver-seed combination
    for instance, solver in itertools.product(instances_set._instance_paths, solvers):
        for _ in range(seeds_per_solver):
            seed = int(random.getrandbits(32))
            solver_call_list = solver.build_cmd(
                instance.absolute(),
                objectives=objectives,
                seed=seed,
                cutoff_time=cutoff,
                log_dir=portfolio_path,
            )

            cmd_list.append(" ".join(solver_call_list))
            for objective in objectives:
                performance_data.set_value(
                    value=seed,
                    solver=str(solver.directory),
                    instance=instance.stem,
                    objective=objective.name,
                    solver_fields=["Seed"],
                )
    return cmd_list


def submit_jobs(
    cmd_list: list[str],
    solvers: list[Solver],
    instances_set: InstanceSet,
    run_on: Runner = Runner.SLURM,
) -> SlurmRun:
    """Submit jobs to the runner and return the run object.

    Args:
        cmd_list: List of command strings for all instance-solver-seed combinations.
        solvers: List of solvers to run on the instances.
        instances_set: Set of instances to run on.
        run_on: Runner to use for submitting the jobs.

    Returns:
        run: The run object containing the submitted jobs.
    """
    seeds_per_solver = gv.settings().parallel_portfolio_num_seeds_per_solver
    num_solvers, num_instances = len(solvers), len(instances_set._instance_paths)
    num_jobs = num_solvers * num_instances * seeds_per_solver
    parallel_jobs = min(gv.settings().slurm_jobs_in_parallel, num_jobs)
    if parallel_jobs > num_jobs:
        print(
            "WARNING: Not all jobs will be started at the same time due to the "
            "limitation of number of Slurm jobs that can be run in parallel. Check"
            " your Sparkle Slurm Settings."
        )
    print(
        f"Sparkle parallel portfolio is running {seeds_per_solver} seed(s) per solver "
        f"on {num_solvers} solvers for {num_instances} instances ..."
    )

    sbatch_options = gv.settings().sbatch_settings
    solver_names = ", ".join([s.name for s in solvers])
    # Jobs are added in to the runrunner object in the same order they are provided
    return rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=f"Parallel Portfolio: {solver_names}",
        parallel_jobs=parallel_jobs,
        base_dir=sl.caller_log_dir,
        srun_options=["-N1", "-n1"] + sbatch_options,
        sbatch_options=sbatch_options,
        prepend=gv.settings().slurm_job_prepend,
    )


def main(argv: list[str]) -> None:
    """Main method of run parallel portfolio command."""
    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)
    settings = gv.settings(args)

    # Log command call
    sl.log_command(sys.argv, settings.random_state)
    check_for_initialise()

    # Compare current settings to latest.ini
    prev_settings = Settings(Settings.DEFAULT_previous_settings_path)
    Settings.check_settings_changes(settings, prev_settings)

    if args.solvers is not None:
        solver_paths = [
            resolve_object_name("".join(s), target_dir=settings.DEFAULT_solver_dir)
            for s in args.solvers
        ]
        if None in solver_paths:
            print("Some solvers not recognised! Check solver names:")
            for i, name in enumerate(solver_paths):
                if solver_paths[i] is None:
                    print(f'\t- "{solver_paths[i]}" ')
            sys.exit(-1)
        solvers = [Solver(p) for p in solver_paths]
    else:
        solvers = [
            Solver(p) for p in settings.DEFAULT_solver_dir.iterdir() if p.is_dir()
        ]

    portfolio_path = args.portfolio_name

    run_on = settings.run_on
    if run_on == Runner.LOCAL:
        print("Parallel Portfolio is not fully supported yet for Local runs. Exiting.")
        sys.exit(-1)

    # Retrieve instance sets
    instances = [
        resolve_object_name(
            instance_path,
            gv.file_storage_data_mapping[gv.instances_nickname_path],
            gv.settings().DEFAULT_instance_dir,
            Instance_Set,
        )
        for instance_path in args.instance_path
    ]
    # Join them into one
    if len(instances) > 1:
        print(
            "WARNING: More than one instance set specified. "
            "Currently only supporting one."
        )
    instances = instances[0]

    print(f"Running on {instances.size} instance(s)...")

    if not settings.objectives[0].time:
        print(
            "ERROR: Parallel Portfolio is currently only relevant for "
            "RunTime objectives. In all other cases, use validation"
        )
        sys.exit(-1)

    if args.portfolio_name is not None:  # Use a nickname
        portfolio_path = settings.DEFAULT_parallel_portfolio_output / args.portfolio_name
    else:  # Generate a timestamped nickname
        timestamp = time.strftime("%Y-%m-%d-%H:%M:%S", time.gmtime(time.time()))
        randintstamp = int(random.getrandbits(32))
        portfolio_path = (
            settings.DEFAULT_parallel_portfolio_output / f"{timestamp}_{randintstamp}"
        )
    if portfolio_path.exists():
        print(
            f"[WARNING] Portfolio path {portfolio_path} already exists! "
            "Overwrite? [y/n] ",
            end="",
        )
        user_input = input()
        if user_input != "y":
            sys.exit()
        shutil.rmtree(portfolio_path)

    portfolio_path.mkdir(parents=True)
    pdf = create_performance_dataframe(solvers, instances, portfolio_path)
    returned_cmd = build_command_list(instances, solvers, portfolio_path, pdf)
    default_objective_values, cpu_time_key, status_key, wall_time_key = (
        init_default_objectives()
    )
    returned_run = submit_jobs(returned_cmd, solvers, instances, Runner.SLURM)
    job_output_dict = monitor_jobs(
        returned_run, instances, solvers, default_objective_values
    )
    wait_for_logs(returned_cmd)
    job_output_dict = update_results_from_logs(
        returned_cmd, returned_run, solvers, job_output_dict, cpu_time_key
    )
    job_output_dict = fix_missing_times(
        job_output_dict, status_key, cpu_time_key, wall_time_key
    )
    print_and_write_results(
        job_output_dict,
        solvers,
        instances,
        portfolio_path,
        status_key,
        cpu_time_key,
        wall_time_key,
        pdf,
    )

    # Write used settings to file
    settings.write_used_settings()
    print("Running Sparkle parallel portfolio is done!")
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
