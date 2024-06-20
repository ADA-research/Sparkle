#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for the execution of a configured solver."""
from __future__ import annotations

from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner

import global_variables as gv
from CLI.help.command_help import CommandName
from sparkle.platform import slurm_help as ssh
from sparkle.instance import instances_help as sih
from sparkle.solver.solver import Solver


def call_configured_solver(instance_path_list: list[Path],
                           solver_name: str,
                           config_str: str,
                           parallel: bool,
                           run_on: Runner = Runner.SLURM) -> str:
    """Create list of instance path lists, and call solver in parallel or sequential.

    Args:
        instance_path_list: List of paths to all the instances.
        solver_name: Name of the solver to be used.
        config_str: Configuration to be used.
        parallel: Boolean indicating a parallel call if True. Sequential otherwise.
        run_on: Whether the command is run with Slurm or not.

    Returns:
        str: The Slurm job id, or empty string if local run.
    """
    job_id_str = ""

    # If directory, get instance list from directory as list[list[Path]]
    if len(instance_path_list) == 1 and instance_path_list[0].is_dir():
        instance_directory_path = instance_path_list[0]
        list_all_filename = sih.get_instance_list_from_path(instance_directory_path)

        # Create an instance list keeping in mind possible multi-file instances
        instances_list = []
        for filename_str in list_all_filename:
            instances_list.append([instance_directory_path / name
                                  for name in filename_str.split()])
    # Else single instance turn it into list[list[Path]]
    else:
        instances_list = [instance_path_list]
    solver = Solver.get_solver_by_name(solver_name)
    # If parallel, pass instances list to parallel function
    if parallel:
        job_id_str = call_solver_parallel(instances_list,
                                          solver,
                                          config_str,
                                          commandname=CommandName.RUN_CONFIGURED_SOLVER,
                                          run_on=run_on)
    # Else, pass instances list to sequential function
    else:
        call_configured_solver_sequential(instances_list, solver, config_str)

    return job_id_str


def call_configured_solver_sequential(instances_list: list[list[Path]],
                                      solver: Solver,
                                      config_str: str) -> None:
    """Prepare to run and run the configured solver sequentially on instances.

    Args:
        instances_list: The paths to all the instances
        solver: Solver to be called.
        config_str: Configuration to be used.
    """
    # Prepare runsolver call
    custom_cutoff = gv.settings.get_general_target_cutoff_time()
    solver_params = Solver.config_str_to_dict(config_str)
    solver_params["specifics"] = "rawres"
    solver_params["cutoff_time"] = custom_cutoff
    solver_params["run_length"] = "2147483647"  # Arbitrary, not used by SMAC wrapper
    solver_params["seed"] = gv.get_seed()

    for instance_path_list in instances_list:
        # Use original path for output string
        instance_path_str = " ".join([str(path) for path in instance_path_list])

        # Run the configured solver
        print(f"Start running the latest configured solver to solve instance "
              f"{instance_path_str} ...")

        for instance_path in instance_path_list:
            raw_result_path = Path(f"{solver.name}_{Path(instance_path).name}"
                                   f"_{gv.get_time_pid_random_string()}.rawres")
            runsolver_watch_data_path = raw_result_path.with_suffix(".log")
            runsolver_values_path = raw_result_path.with_suffix(".val")

            runsolver_args = ["--timestamp", "--use-pty",
                              "--cpu-limit", str(custom_cutoff),
                              "-w", runsolver_watch_data_path,
                              "-v", runsolver_values_path,
                              "-o", raw_result_path]
            solver_output = solver.run_solver(instance_path.absolute(),
                                              configuration=solver_params,
                                              runsolver_configuration=runsolver_args)
            # Output results to user, including path to rawres_solver (e.g. SAT solution)
            print(f"Execution on instance {Path(instance_path).name} completed with "
                  f"status {solver_output['status']}"
                  f" in {solver_output['runtime']} seconds.")
            print("Raw output can be found at: "
                  f"{solver.raw_output_directory / raw_result_path}.\n")


def call_solver_parallel(
        instances_list: list[list[Path]],
        solver: Solver,
        config: str | Path,
        seed: int = None,
        outdir: Path = None,
        commandname: CommandName = CommandName.RUN_SOLVERS,
        dependency: rrr.SlurmRun | list[rrr.SlurmRun] = None,
        run_on: Runner = Runner.SLURM) -> rrr.SlurmRun | rrr.LocalRun:
    """Run a solver in parallel on all given instances.

    Args:
        instance_list: A list of all paths in a directory of instances.
        run_on: Whether the command is run with Slurm or not.
        config: The configuration with which to run. Can be direct configuration string,
            or file from which to read. If specific line from file is needed, seed
            should be specified.
        dependency: The jobs it depends on to finish before starting.

    Returns:
        str: The Slurm job id str, SlurmJob if RunRunner Slurm or empty string if local
    """
    # Create an instance list[str] keeping in mind possible multi-file instances
    for index, value in enumerate(instances_list):
        # Flatten the second dimension
        if isinstance(value, list):
            instances_list[index] = " ".join([str(path) for path in value])

    num_jobs = len(instances_list)
    custom_cutoff = gv.settings.get_general_target_cutoff_time()
    cmd_list = []
    for instance_path in instances_list:
        instance_path = Path(instance_path)
        raw_result_path = Path(f"{solver.name}_{instance_path.name}"
                               f"_{gv.get_time_pid_random_string()}.rawres")
        runsolver_watch_data_path = raw_result_path.with_suffix(".log")
        runsolver_values_path = raw_result_path.with_suffix(".val")

        runsolver_args = ["--timestamp", "--use-pty",
                          "--cpu-limit", str(custom_cutoff),
                          "-w", runsolver_watch_data_path,
                          "-v", runsolver_values_path,
                          "-o", raw_result_path]
        if isinstance(config, str):
            solver_params = solver.config_str_to_dict(config)
        else:
            solver_params = {"config_path": config}
        solver_params["specifics"] = "rawres"
        solver_params["cutoff_time"] = custom_cutoff
        solver_params["run_length"] = "2147483647"  # Arbitrary, not used by SMAC wrapper
        if seed is None:
            solver_params["seed"] = gv.get_seed()
        else:
            # Use the seed to determine the configuration line in the file
            solver_params["seed"] = seed
        solver_cmd = solver.build_solver_cmd(instance_path.absolute(),
                                             solver_params, runsolver_args)
        cmd_list.append(" ".join(solver_cmd))

    sbatch_options = ssh.get_slurm_options_list()
    srun_options = ["-N1", "-n1"]
    srun_options.extend(ssh.get_slurm_options_list())
    # Make sure the executable dir exists
    if outdir is None:
        outdir = solver.raw_output_directory
    outdir.mkdir(exist_ok=True, parents=True)
    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=commandname,
        parallel_jobs=num_jobs,
        base_dir=gv.sparkle_tmp_path,
        path=outdir,
        dependencies=dependency,
        sbatch_options=sbatch_options,
        srun_options=srun_options)

    if run_on == Runner.LOCAL:
        run.wait()

    return run
