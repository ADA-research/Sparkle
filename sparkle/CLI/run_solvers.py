#!/usr/bin/env python3
"""Sparkle command to run solvers to get their performance data."""

from __future__ import annotations
import random
import sys
import argparse
from pathlib import Path

from runrunner.base import Runner, Run

from sparkle.solver import Solver
from sparkle.instance import Instance_Set
from sparkle.structures import PerformanceDataFrame
from sparkle.types import SparkleObjective, resolve_objective
from sparkle.instance import InstanceSet
from sparkle.platform.settings_objects import Settings
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help.nicknames import resolve_object_name, resolve_instance_name
from sparkle.CLI.initialise import check_for_initialise


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run solvers on instances to get their performance data."
    )
    parser.add_argument(*ac.SolversArgument.names, **ac.SolversArgument.kwargs)
    parser.add_argument(
        *ac.InstanceSetPathsArgument.names, **ac.InstanceSetPathsArgument.kwargs
    )

    # Mutually exclusive: specific configuration or best configuration
    configuration_group = parser.add_mutually_exclusive_group()
    configuration_group.add_argument(
        *ac.ConfigurationArgument.names, **ac.ConfigurationArgument.kwargs
    )
    configuration_group.add_argument(
        *ac.BestConfigurationArgument.names, **ac.BestConfigurationArgument.kwargs
    )
    configuration_group.add_argument(
        *ac.AllConfigurationArgument.names, **ac.AllConfigurationArgument.kwargs
    )
    parser.add_argument(*ac.ObjectiveArgument.names, **ac.ObjectiveArgument.kwargs)
    parser.add_argument(
        *ac.PerformanceDataJobsArgument.names, **ac.PerformanceDataJobsArgument.kwargs
    )
    # This one is only relevant if the argument above is given
    parser.add_argument(
        *ac.RecomputeRunSolversArgument.names, **ac.RecomputeRunSolversArgument.kwargs
    )
    # Settings arguments
    parser.add_argument(*ac.SettingsFileArgument.names, **ac.SettingsFileArgument.kwargs)
    parser.add_argument(
        *Settings.OPTION_solver_cutoff_time.args,
        **Settings.OPTION_solver_cutoff_time.kwargs,
    )
    parser.add_argument(*Settings.OPTION_run_on.args, **Settings.OPTION_run_on.kwargs)
    return parser


def run_solvers(
    solvers: list[Solver],
    instances: list[str] | list[InstanceSet],
    objectives: list[SparkleObjective],
    seed: int,
    cutoff_time: int,
    configurations: list[list[dict[str, str]]],
    sbatch_options: list[str] = None,
    slurm_prepend: str | list[str] | Path = None,
    log_dir: Path = None,
    run_on: Runner = Runner.SLURM,
) -> list[Run]:
    """Run the solvers.

    Parameters
    ----------
    solvers: list[solvers]
        The solvers to run
    instances: list[str] | list[InstanceSet]
        The instances to run the solvers on
    objectives: list[SparkleObjective]
        The objective values to retrieve from the solvers
    seed: int
        The seed to use
    cutoff_time: int
        The cut off time for the solvers
    configurations: list[list[str]]
        The configurations to use for each solver
    sbatch_options: list[str]
        The sbatch options to use for the solvers
    slurm_prepend: str | list[str] | Path
        The script to prepend to a slurm script
    log_dir: Path
        The directory to use for the logs
    run_on: Runner
        Where to execute the solvers.

    Returns
    -------
    run: runrunner.LocalRun or runrunner.SlurmRun
    """
    runs = []
    # Run the solvers
    for solver, solver_confs in zip(solvers, configurations):
        for conf_index, conf in enumerate(solver_confs):
            if "configuration_id" in conf.keys():
                conf_name = conf["configuration_id"]
            else:
                conf_name = conf_index
            run = solver.run(
                instances=instances,
                objectives=objectives,
                seed=seed,
                configuration=conf,
                cutoff_time=cutoff_time,
                run_on=run_on,
                sbatch_options=sbatch_options,
                slurm_prepend=slurm_prepend,
                log_dir=log_dir,
            )
            if run_on == Runner.LOCAL:
                if isinstance(run, dict):
                    run = [run]
                # TODO: Refactor resolving objective keys
                status_key = [key for key in run[0] if key.lower().startswith("status")][
                    0
                ]
                time_key = [key for key in run[0] if key.lower().startswith("cpu_time")][
                    0
                ]
                for i, solver_output in enumerate(run):
                    print(
                        f"Execution of {solver.name} ({conf_name}) on instance "
                        f"{instances[i]} completed with status "
                        f"{solver_output[status_key]} in {solver_output[time_key]} "
                        f"seconds."
                    )
                print("Running configured solver done!")
            else:
                runs.append(run)
    return runs


def run_solvers_performance_data(
    performance_data: PerformanceDataFrame,
    cutoff_time: int,
    rerun: bool = False,
    solvers: list[Solver] = None,
    instances: list[str] = None,
    sbatch_options: list[str] = None,
    slurm_prepend: str | list[str] | Path = None,
    run_on: Runner = Runner.SLURM,
) -> list[Run]:
    """Run the solvers for the performance data.

    Parameters
    ----------
    performance_data: PerformanceDataFrame
        The performance data
    cutoff_time: int
        The cut off time for the solvers
    rerun: bool
        Run only solvers for which no data is available yet (False) or (re)run all
        solvers to get (new) performance data for them (True)
    solvers: list[solvers]
        The solvers to run. If None, run all found solvers.
    instances: list[str]
        The instances to run the solvers on. If None, run all found instances.
    sbatch_options: list[str]
        The sbatch options to use
    slurm_prepend: str | list[str] | Path
        The script to prepend to a slurm script
    run_on: Runner
        Where to execute the solvers. For available values see runrunner.base.Runner
        enum. Default: "Runner.SLURM".

    Returns
    -------
    run: runrunner.LocalRun or runrunner.SlurmRun
        If the run is local return a QueuedRun object with the information concerning
        the run.
    """
    # List of jobs to do
    jobs = performance_data.get_job_list(rerun=rerun)

    # Edit jobs to incorporate file paths
    jobs_with_paths = []
    for solver, config, instance, run in jobs:
        instance_path = resolve_instance_name(
            instance, gv.settings().DEFAULT_instance_dir
        )
        jobs_with_paths.append((solver, config, instance_path, run))
    jobs = jobs_with_paths

    print(f"Total number of jobs to run: {len(jobs)}")
    # If there are no jobs, stop
    if len(jobs) == 0:
        return None

    if run_on == Runner.LOCAL:
        print("Running the solvers locally")
    elif run_on == Runner.SLURM:
        print("Running the solvers through Slurm")

    solvers = performance_data.solvers if solvers is None else solvers
    if solvers is None:
        solver_keys = performance_data.solvers
        solvers = [Solver(Path(s)) for s in solver_keys]
    else:  # Filter the Solvers
        solver_keys = [str(s.directory) for s in solvers]
        jobs = [j for j in jobs if j[0] in solver_keys]
    # Filter the instances
    if instances is not None:
        jobs = [j for j in jobs if j[2] in instances]
    # Sort the jobs per solver
    solver_jobs = {p_solver: {} for p_solver, _, _, _ in jobs}
    for p_solver, p_config, p_instance, p_run in jobs:
        if p_config not in solver_jobs[p_solver]:
            solver_jobs[p_solver][p_config] = {}
        if p_instance not in solver_jobs[p_solver][p_config]:
            solver_jobs[p_solver][p_config][p_instance] = [p_run]
        else:
            solver_jobs[p_solver][p_config][p_instance].append(p_run)
    runrunner_runs = []
    if run_on == Runner.LOCAL:
        print(f"Cutoff time for each solver run: {cutoff_time} seconds")
    for solver, solver_key in zip(solvers, solver_keys):
        for solver_config in solver_jobs[solver_key].keys():
            solver_instances = solver_jobs[solver_key][solver_config].keys()
            run_ids = [
                solver_jobs[solver_key][solver_config][instance]
                for instance in solver_instances
            ]
            if solver_instances == []:
                print(f"Warning: No jobs for instances found for solver {solver_key}")
                continue
            run = solver.run_performance_dataframe(
                solver_instances,
                performance_data,
                solver_config,
                run_ids=run_ids,
                cutoff_time=cutoff_time,
                sbatch_options=sbatch_options,
                slurm_prepend=slurm_prepend,
                log_dir=sl.caller_log_dir,
                base_dir=sl.caller_log_dir,
                run_on=run_on,
            )
            runrunner_runs.append(run)
            if run_on == Runner.LOCAL:
                # Do some printing?
                pass
    if run_on == Runner.SLURM:
        num_jobs = sum(len(r.jobs) for r in runrunner_runs)
        print(f"Total number of jobs submitted: {num_jobs}")

    return runrunner_runs


def main(argv: list[str]) -> None:
    """Main function of the run solvers command."""
    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)
    settings = gv.settings(args)

    # Log command call
    sl.log_command(sys.argv, seed=settings.random_state)
    check_for_initialise()

    if args.best_configuration:
        if not args.objective:
            objective = settings.objectives[0]
            print(
                "WARNING: Best configuration requested, but no objective specified. "
                f"Defaulting to first objective: {objective}"
            )
        else:
            objective = resolve_objective(args.objective)

    # Compare current settings to latest.ini
    prev_settings = Settings(Settings.DEFAULT_previous_settings_path)
    Settings.check_settings_changes(settings, prev_settings)

    if args.solvers:
        solvers = [
            resolve_object_name(
                solver_path,
                gv.file_storage_data_mapping[gv.solver_nickname_list_path],
                settings.DEFAULT_solver_dir,
                Solver,
            )
            for solver_path in args.solvers
        ]
    else:
        solvers = [
            Solver(p) for p in settings.DEFAULT_solver_dir.iterdir() if p.is_dir()
        ]

    if args.instance_path:
        instances = [
            resolve_object_name(
                instance_path,
                gv.file_storage_data_mapping[gv.instances_nickname_path],
                settings.DEFAULT_instance_dir,
                Instance_Set,
            )
            for instance_path in args.instance_path
        ]
        # Unpack the sets into instance strings
        instances = [str(path) for set in instances for path in set.instance_paths]
    else:
        instances = None  # TODO: Fix? Or its good like this

    sbatch_options = settings.sbatch_settings
    slurm_prepend = settings.slurm_job_prepend
    # Write settings to file before starting, since they are used in callback scripts
    settings.write_used_settings()
    run_on = settings.run_on
    cutoff_time = settings.solver_cutoff_time
    # Open the performance data csv file
    performance_dataframe = PerformanceDataFrame(settings.DEFAULT_performance_data_path)

    print("Start running solvers ...")
    if args.performance_data_jobs:
        runs = run_solvers_performance_data(
            performance_data=performance_dataframe,
            solvers=solvers,
            instances=instances,
            cutoff_time=cutoff_time,
            rerun=args.recompute,
            sbatch_options=sbatch_options,
            slurm_prepend=slurm_prepend,
            run_on=run_on,
        )
    else:
        if args.best_configuration:
            train_instances = None
            if isinstance(args.best_configuration, list):
                train_instances = [
                    resolve_object_name(
                        instance_path,
                        gv.file_storage_data_mapping[gv.instances_nickname_path],
                        settings.DEFAULT_instance_dir,
                        Instance_Set,
                    )
                    for instance_path in args.best_configuration
                ]
                # Unpack the sets into instance strings
                instances = [
                    str(path) for set in train_instances for path in set.instance_paths
                ]
            # Determine best configuration
            configurations = [
                [
                    performance_dataframe.best_configuration(
                        str(solver.directory), objective, train_instances
                    )[0]
                ]
                for solver in solvers
            ]
        elif args.configuration:
            # Sort the configurations to the solvers
            # TODO: Add a better check that the id could only match this solver
            configurations = []
            for solver in solvers:
                configurations.append([])
                for c in args.configuration:
                    if c not in performance_dataframe.configuration_ids:
                        raise ValueError(f"Configuration id {c} not found.")
                    if c in performance_dataframe.get_configurations(
                        str(solver.directory)
                    ):
                        configurations[-1].append(c)
        elif args.all_configurations:  # All known configurations
            configurations = [
                performance_dataframe.get_configurations(str(solver.directory))
                for solver in solvers
            ]
        else:  # Only default configurations
            configurations = [
                [PerformanceDataFrame.default_configuration] for _ in solvers
            ]
        # Look up and replace with the actual configurations
        for solver_index, configs in enumerate(configurations):
            for config_index, config in enumerate(configs):
                configurations[solver_index][config_index] = (
                    performance_dataframe.get_full_configuration(
                        str(solvers[solver_index].directory), config
                    )
                )
        if instances is None:
            instances = []
            for instance_dir in settings.DEFAULT_instance_dir.iterdir():
                if instance_dir.is_dir():
                    instances.append(Instance_Set(instance_dir))

        # TODO Objective arg not used in Multi-file-instances case?
        runs = run_solvers(
            solvers=solvers,
            configurations=configurations,
            instances=instances,
            objectives=settings.objectives,
            seed=random.randint(0, 2**32 - 1),
            cutoff_time=cutoff_time,
            sbatch_options=sbatch_options,
            slurm_prepend=slurm_prepend,
            log_dir=sl.caller_log_dir,
            run_on=run_on,
        )

    # If there are no jobs return
    if runs is None or all(run is None for run in runs):
        print("Running solvers done!")
    elif run_on == Runner.SLURM:
        print(
            "Running solvers through Slurm with job id(s): "
            f"{','.join(r.run_id for r in runs if r is not None)}"
        )
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
