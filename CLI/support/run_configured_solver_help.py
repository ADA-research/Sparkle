#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for the execution of a configured solver."""
from __future__ import annotations

import sys
from pathlib import Path

import runrunner as rrr
from runrunner.base import Runner

import global_variables as sgh
from CLI.help.command_help import CommandName
from CLI.support import configure_solver_help as scsh
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
        job_id_str = call_configured_solver_parallel(instances_list,
                                                     solver,
                                                     config_str,
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
    custom_cutoff = sgh.settings.get_general_target_cutoff_time()
    solver_params = Solver.config_str_to_dict(config_str)
    solver_params["specifics"] = "rawres"
    solver_params["cutoff_time"] = custom_cutoff
    solver_params["run_length"] = "2147483647"  # Arbitrary, not used by SMAC wrapper
    solver_params["seed"] = sgh.get_seed()

    for instance_path_list in instances_list:
        # Use original path for output string
        instance_path_str = " ".join([str(path) for path in instance_path_list])

        # Run the configured solver
        print(f"Start running the latest configured solver to solve instance "
              f"{instance_path_str} ...")

        for instance_path in instance_path_list:
            raw_result_path = Path(f"{solver.name}_{Path(instance_path).name}"
                                   f"_{sgh.get_time_pid_random_string()}.rawres")
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
            print("Raw output can be found at:"
                  f"{solver.raw_output_directory / raw_result_path}.\n")


def call_configured_solver_parallel(
        instances_list: list[list[Path]], solver: Solver, config_str: str,
        run_on: Runner = Runner.SLURM) -> rrr.SlurmRun | rrr.LocalRun:
    """Run the configured solver in parallel on all given instances.

    Args:
        instance_list: A list of all paths in a directory of instances.
        run_on: Whether the command is run with Slurm or not.

    Returns:
        str: The Slurm job id str, SlurmJob if RunRunner Slurm or empty string if local
    """
    # Create an instance list[str] keeping in mind possible multi-file instances
    for index, value in enumerate(instances_list):
        # Flatten the second dimension
        if isinstance(value, list):
            instances_list[index] = " ".join([str(path) for path in value])

    num_jobs = len(instances_list)
    custom_cutoff = sgh.settings.get_general_target_cutoff_time()
    cmd_list = []
    for instance_path in instances_list:
        instance_path = Path(instance_path)
        raw_result_path = Path(f"{solver.name}_{instance_path.name}"
                               f"_{sgh.get_time_pid_random_string()}.rawres")
        runsolver_watch_data_path = raw_result_path.with_suffix(".log")
        runsolver_values_path = raw_result_path.with_suffix(".val")

        runsolver_args = ["--timestamp", "--use-pty",
                          "--cpu-limit", str(custom_cutoff),
                          "-w", runsolver_watch_data_path,
                          "-v", runsolver_values_path,
                          "-o", raw_result_path]
        solver_params = solver.config_str_to_dict(config_str)
        solver_params["specifics"] = "rawres"
        solver_params["cutoff_time"] = custom_cutoff
        solver_params["run_length"] = "2147483647"  # Arbitrary, not used by SMAC wrapper
        solver_params["seed"] = sgh.get_seed()
        solver_cmd = [str(item) for item in
                      solver.build_solver_cmd(instance_path.absolute(),
                                              solver_params, runsolver_args)]
        # Replace dictionary quotes so RunRunner can handle it
        solver_cmd[-1] = solver_cmd[-1].replace("'", '"')
        cmd_list.append(" ".join(solver_cmd))

    sbatch_options = ssh.get_slurm_options_list()
    srun_options = ["-N1", "-n1"]
    srun_options.extend(ssh.get_slurm_options_list())
    # Make sure the executable dir exists
    solver.raw_output_directory.mkdir(exist_ok=True)
    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=CommandName.RUN_CONFIGURED_SOLVER,
        parallel_jobs=num_jobs,
        base_dir=sgh.sparkle_tmp_path,
        path=solver.raw_output_directory,
        sbatch_options=sbatch_options,
        srun_options=srun_options)

    if run_on == Runner.LOCAL:
        run.wait()
    else:
        print(f"Configured solver added to {run_on} queue.")

    return run


def get_latest_configured_solver_and_configuration() -> tuple[str, str]:
    """Return the name and parameter string of the latest configured solver.

    Returns:
        Tuple(str, str): A tuple containing the solver name and its configuration string.
    """
    # Get latest configured solver + instance set
    solver = sgh.latest_scenario().get_config_solver()
    instance_set = sgh.latest_scenario().get_config_instance_set_train()

    if solver is None or instance_set is None:
        # Print error and stop execution
        print("ERROR: No configured solver found! Stopping execution.")
        sys.exit(-1)

    # Get optimised configuration
    config_str = scsh.get_optimised_configuration_params(solver.name, instance_set.name)
    return solver.name, config_str
