#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for interaction with Slurm."""

from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_job_help as sjh
from Commands.sparkle_help.sparkle_command_help import CommandName

from runrunner.base import Runner
import runrunner as rrr


def get_slurm_options_list(path_modifier: str = None) -> list[str]:
    """Return a list with the Slurm options given in the Slurm settings file.

    Args:
      path_modifier: An optional prefix path for the sparkle Slurm settings.
        Default is None which is interpreted as an empty prefix.

    Returns:
      List of strings (the actual Slurm settings, e.g., ['--mem-per-cpu=3000']).
    """
    if path_modifier is None:
        path_modifier = ""

    slurm_options_list = []
    sparkle_slurm_settings_path = Path(path_modifier) / sgh.sparkle_slurm_settings_path
    with Path(sparkle_slurm_settings_path).open("r") as settings_file:
        slurm_options_list.extend([line.strip() for line in settings_file.readlines()
                                   if line.startswith("-")])

    return slurm_options_list


def get_slurm_sbatch_user_options_list(path_modifier: str = None) -> list[str]:
    """Return a list with Slurm batch options given by the user.

    Args:
      path_modifier: An optional prefix path for the sparkle Slurm settings.
        Default is None which is interpreted as an empty prefix.

    Returns:
      List of strings (the actual Slurm settings, e.g., ['--mem-per-cpu=3000']).
    """
    return get_slurm_options_list(path_modifier)


def get_slurm_sbatch_default_options_list() -> list[str]:
    """Return the default list of Slurm batch options.

    Returns:
      List of strings. Currently, this is the empty list.
    """
    return list()


def get_slurm_srun_user_options_list(path_modifier: str = None) -> list[str]:
    """Return a list with the Slurm run options given by the user.

    Args:
      path_modifier: An optional prefix path for the sparkle Slurm settings.
        Default is None which is interpreted as an empty prefix.

    Returns:
      List of strings (the actual Slurm settings, e.g., ['--mem-per-cpu=3000']).
    """
    return get_slurm_options_list(path_modifier)


def check_slurm_option_compatibility(srun_option_string: str) -> tuple[bool, str]:
    """Check if the given srun_option_string is compatible with the Slurm cluster.

    Args:
      srun_option_string: Specific run option string.

    Returns:
      A 2-tuple of type (combatible, message). The first entry is a Boolean
      incidating the compatibility and the second is a additional informative
      string message.
    """
    args = shlex.split(srun_option_string)
    kwargs = {}

    # Loop through arguments of srun. Split option and specification of each
    # argument on seperator "=".
    # TODO: Argument without value could lead to elif statement going out of
    # bounds -> Needs refactoring
    for i in range(len(args)):
        arg = args[i]
        if "=" in arg:
            splitted = arg.split("=")
            kwargs[splitted[0]] = splitted[1]
        elif i < len(args) - 1 and "-" not in args[i + 1]:
            kwargs[arg] = args[i + 1]

    if not ("--partition" in kwargs.keys() or "-p" in kwargs.keys()):
        print("###Could not check slurm compatibility because no partition was "
              "specified; continuing###")
        return True, "Could not Check"

    partition = kwargs.get("--partition", kwargs.get("-p", None))

    output = str(subprocess.check_output(["sinfo", "--nohead", "--format", '"%c;%m"',
                                          "--partition", partition]))
    # we expect a string of the form b'"{};{}"\n'
    cpus, memory = output[3:-4].split(";")
    cpus = int(cpus)
    memory = float(memory)

    if "--cpus-per-task" in kwargs.keys() or "-c" in kwargs.keys():
        requested_cpus = int(kwargs.get("--cpus-per-task", kwargs.get("-c", 0)))
        if requested_cpus > cpus:
            return False, f"ERROR: CPU specification of {requested_cpus} cannot be " \
                          f"satisfied for {partition}, only got {cpus}"

    if "--mem-per-cpu" in kwargs.keys() or "-m" in kwargs.keys():
        requested_memory = float(kwargs.get("--mem-per-cpu", kwargs.get("-m", 0))) * \
            int(kwargs.get("--cpus-per-task", kwargs.get("-c", cpus)))
        if requested_memory > memory:
            return False, f"ERROR: Memory specification {requested_memory}MB can " \
                          f"not be satisfied for {partition}, only got {memory}MB"

    return True, "Check successful"


def run_callback(solver: Path,
                 instance_set_train: Path,
                 instance_set_test: Path,
                 dependency: rrr.SlurmRun | rrr.LocalRun,
                 command: CommandName,
                 run_on: Runner = Runner.SLURM) -> rrr.SlurmRun | rrr.LocalRun:
    """Add a command callback to RunRunner queue for validation and run it.

    Args:
      solver: Path (object) to solver.
      instance_set_train: Path (object) to instances used for training.
      instance_set_test: Path (object) to instances used for testing.
      dependency: String of job dependencies.
      command: The command to run. Currently supported: Validation and Ablation.
      run_on: Whether the job is executed on Slurm or locally.

    Returns:
      RunRunner Run object regarding the callback
    """
    cmd_file = "validate_configured_vs_default.py"
    if command == CommandName.RUN_ABLATION:
        cmd_file = "run_ablation.py"

    command_line = f"./Commands/{cmd_file} --settings-file Settings/latest.ini "\
                   f"--solver {solver.name} --instance-set-train {instance_set_train}"\
                   f" --run-on {run_on}"
    if instance_set_test is not None:
        command_line += f" --instance-set-test {instance_set_test}"

    run = rrr.add_to_queue(runner=run_on,
                           cmd=command_line,
                           name=command,
                           dependencies=dependency,
                           base_dir=sgh.sparkle_tmp_path,
                           srun_options=["-N1", "-n1"],
                           sbatch_options=get_slurm_sbatch_user_options_list())

    if run_on == Runner.LOCAL:
        print("Waiting for the local calculations to finish.")
        run.wait()
    else:
        sjh.write_active_job(run.run_id, command)
    return run
