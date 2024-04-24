#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for interaction with Slurm."""
from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

import global_variables as sgh


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


def check_slurm_option_compatibility(srun_option_string: str) -> tuple[bool, str]:
    """Check if the given srun_option_string is compatible with the cluster partition.

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
