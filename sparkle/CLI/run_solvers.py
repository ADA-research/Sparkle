#!/usr/bin/env python3
"""Sparkle command to run solvers to get their performance data."""
from __future__ import annotations
import random
import sys
import ast
import argparse
from pathlib import PurePath, Path

from runrunner.base import Runner, Run

from sparkle.solver import Solver
from sparkle.instance import Instance_Set
from sparkle.structures import PerformanceDataFrame
from sparkle.types import SparkleObjective, resolve_objective
from sparkle.platform.settings_objects import Settings, SettingState
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help.nicknames import resolve_object_name
from sparkle.CLI.initialise import check_for_initialise


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run solvers on instances to get their performance data.")
    parser.add_argument(*ac.SolversArgument.names,
                        **ac.SolversArgument.kwargs)
    parser.add_argument(*ac.InstanceSetPathsArgument.names,
                        **ac.InstanceSetPathsArgument.kwargs)

    # Mutually exclusive: specific configuration or best configuration
    configuration_group = parser.add_mutually_exclusive_group()
    configuration_group.add_argument(*ac.ConfigurationArgument.names,
                                     **ac.ConfigurationArgument.kwargs)
    configuration_group.add_argument(*ac.BestConfigurationArgument.names,
                                     **ac.BestConfigurationArgument.kwargs)

    parser.add_argument(*ac.ObjectiveArgument.names,
                        **ac.ObjectiveArgument.kwargs)
    parser.add_argument(*ac.PerformanceDataJobsArgument.names,
                        **ac.PerformanceDataJobsArgument.kwargs)
    # This one is only relevant if the argument above is given
    parser.add_argument(*ac.RecomputeRunSolversArgument.names,
                        **ac.RecomputeRunSolversArgument.kwargs)
    parser.add_argument(*ac.TargetCutOffTimeArgument.names,
                        **ac.TargetCutOffTimeArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    return parser


def run_solvers(
        solvers: list[Solver],
        instances: list[str],
        objectives: list[SparkleObjective],
        seed: int,
        cutoff_time: int,
        configuration: list[dict] = None,
        sbatch_options: list[str] = None,
        slurm_prepend: str | list[str] | Path = None,
        log_dir: Path = None,
        run_on: Runner = Runner.SLURM,) -> list[Run]:
    """Run the solvers.

    Parameters
    ----------
    solvers: list[solvers]
        The solvers to run
    instances: list[str]
        The instances to run the solvers on
    objectives: list[SparkleObjective]
        The objective values to retrieve from the solvers
    seed: int
        The seed to use
    cutoff_time: int
        The cut off time for the solvers
    configuration: list[dict]
        The configuration to use for the solvers
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
    for solver, configuration in zip(solvers, configuration):
        run = solver.run(instances=instances,
                         objectives=objectives,
                         seed=seed,
                         configuration=configuration,
                         cutoff_time=cutoff_time,
                         run_on=run_on,
                         sbatch_options=sbatch_options,
                         slurm_prepend=slurm_prepend,
                         log_dir=log_dir)
        if run_on == Runner.LOCAL:
            if isinstance(run, dict):
                run = [run]
            # Resolve objective keys
            status_key = [key for key in run[0] if key.lower().startswith("status")][0]
            time_key = [key for key in run[0] if key.lower().startswith("cpu_time")][0]
            for i, solver_output in enumerate(run):
                print(f"Execution of {solver.name} on instance {instances[i]} "
                      f"completed with status {solver_output[status_key]} "
                      f"in {solver_output[time_key]} seconds.")
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
        run_on: Runner = Runner.SLURM) -> list[Run]:
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
    num_jobs = len(jobs)

    print(f"Total number of jobs to run: {num_jobs}")

    # If there are no jobs, stop
    if num_jobs == 0:
        return None

    if run_on == Runner.LOCAL:
        print("Running the solvers locally")
    elif run_on == Runner.SLURM:
        print("Running the solvers through Slurm")

    # Sort the jobs per solver
    solver_jobs = {p_solver: {} for _, _, p_solver in jobs}
    for p_instance, p_run, p_solver in jobs:
        if p_instance not in solver_jobs[p_solver]:
            solver_jobs[p_solver][p_instance] = [p_run]
        else:
            solver_jobs[p_solver][p_instance].append(p_run)
    runrunner_runs = []
    solvers = [Solver(Path(p))
               for p in performance_data.solvers] if solvers is None else solvers
    if run_on == Runner.LOCAL:
        print(f"Cutoff time for each solver run: {cutoff_time} seconds")
    for solver in solvers:
        solver_key = str(solver.directory)
        solver_instances = solver_jobs[solver_key].keys()
        if instances:  # Filter
            solver_instances = [i for i in solver_instances if i in instances]
        runs = list(solver_jobs[solver_key][i] for i in solver_instances)
        if solver_instances == []:
            print(f"Warning: No jobs for instances found for solver {solver_key}")
            continue
        run = solver.run_performance_dataframe(
            solver_instances, runs, performance_data, cutoff_time=cutoff_time,
            sbatch_options=sbatch_options, slurm_prepend=slurm_prepend,
            log_dir=sl.caller_log_dir, base_dir=sl.caller_log_dir, run_on=run_on)
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
    # Log command call
    sl.log_command(sys.argv)
    check_for_initialise()

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)
    if args.settings_file is not None:
        # Do first, so other command line options can override settings from the file
        gv.settings().read_settings_ini(args.settings_file, SettingState.CMD_LINE)
    if args.target_cutoff_time is not None:
        gv.settings().set_general_target_cutoff_time(
            args.target_cutoff_time, SettingState.CMD_LINE)
    if args.run_on is not None:
        gv.settings().set_run_on(
            args.run_on.value, SettingState.CMD_LINE)
    if args.best_configuration or args.configuration:
        if not args.objective:
            objective = gv.settings().get_general_sparkle_objectives()[0]
            print("WARNING: Best configuration requested, but no objective specified. "
                  f"Revert to first objective ({objective}).")
        else:
            objective = resolve_objective(args.objective)

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings(), prev_settings)

    if args.solvers:
        solvers = [resolve_object_name(solver_path,
                   gv.file_storage_data_mapping[gv.solver_nickname_list_path],
                   gv.settings().DEFAULT_solver_dir, Solver)
                   for solver_path in args.solvers]
    else:
        solvers = [Solver(p) for p in
                   gv.settings().DEFAULT_solver_dir.iterdir() if p.is_dir()]

    if args.instance_path:
        instances = [resolve_object_name(instance_path,
                     gv.file_storage_data_mapping[gv.instances_nickname_path],
                     gv.settings().DEFAULT_instance_dir, Instance_Set)
                     for instance_path in args.instance_path]
        # Unpack the sets into instance strings
        instances = [str(path) for set in instances for path in set.instance_paths]
    else:
        instances = None  # TODO: Fix? Or its good like this

    sbatch_options = gv.settings().get_slurm_extra_options(as_args=True)
    slurm_prepend = gv.settings().get_slurm_job_prepend()
    # Write settings to file before starting, since they are used in callback scripts
    gv.settings().write_used_settings()
    run_on = gv.settings().get_run_on()
    cutoff_time = gv.settings().get_general_target_cutoff_time()
    # Open the performance data csv file
    performance_dataframe = PerformanceDataFrame(
        gv.settings().DEFAULT_performance_data_path)

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
            run_on=run_on)
    else:
        configurations = [None] * len(solvers)
        if args.best_configuration:
            train_instances = None
            if isinstance(args.best_configuration, list):
                train_instances = [resolve_object_name(
                    instance_path,
                    gv.file_storage_data_mapping[gv.instances_nickname_path],
                    gv.settings().DEFAULT_instance_dir, Instance_Set)
                    for instance_path in args.best_configuration]
                # Unpack the sets into instance strings
                instances = [str(path) for set in train_instances
                             for path in set.instance_paths]
            # Determine best configuration
            configurations = [performance_dataframe.best_configuration(
                str(solver.directory), objective, train_instances)[0]
                for solver in solvers]
        elif args.configuration:
            # Use given configurations
            # Hotfix: We take the first instance in the DF. Might not work in some cases
            instance = performance_dataframe.instances[0]
            configurations = [ast.literal_eval(performance_dataframe.get_value(
                str(solver.directory), instance, objective.name, run=args.configuration,
                solver_fields=[PerformanceDataFrame.column_configuration]))
                for solver in solvers]
        if instances is None:
            instances = performance_dataframe.instances
        runs = run_solvers(
            solvers=solvers,
            configuration=configurations,
            instances=instances,
            objectives=gv.settings().get_general_sparkle_objectives(),
            seed=random.randint(0, sys.maxsize),
            cutoff_time=cutoff_time,
            sbatch_options=sbatch_options,
            slurm_prepend=slurm_prepend,
            log_dir=sl.caller_log_dir,
            run_on=gv.settings().get_run_on(),
        )

    # If there are no jobs return
    if runs is None or all(run is None for run in runs):
        print("Running solvers done!")
    elif run_on == Runner.SLURM:
        print("Running solvers through Slurm with job id(s): "
              f'{",".join(r.run_id for r in runs if r is not None)}')
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
