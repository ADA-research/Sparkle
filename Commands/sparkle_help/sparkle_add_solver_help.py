#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for adding solvers."""

import os

try:
    from sparkle_help import sparkle_file_help as sfh
except ImportError:
    import sparkle_file_help as sfh


def get_solver_directory(solver_name: str) -> str:
    """Return the directory a solver is stored at as str."""
    return 'Solvers/' + solver_name


def check_adding_solver_contain_pcs_file(solver_directory: str) -> bool:
    """Return whether the directory of the solver being added contains a PCS file."""
    list_files = os.listdir(solver_directory)

    pcs_count = 0
    for file_name in list_files:
        file_extension = sfh.get_file_least_extension(file_name)

        if file_extension == 'pcs':
            pcs_count += 1

    return False if pcs_count != 1 else True


def get_pcs_file_from_solver_directory(solver_directory: str) -> str:
    """Return the name of the PCS file in a solver directory.

    If not found, return an empty str.
    """
    list_files = os.listdir(solver_directory)

    for file_name in list_files:
        file_extension = sfh.get_file_full_extension(file_name)

        if file_extension == 'pcs':
            return file_name

    return ''


def create_necessary_files_for_configured_solver(smac_solver_dir: str) -> None:
    """Create directories needed for configuration of a solver."""
    outdir_dir = smac_solver_dir + '/' + 'outdir_train_configuration/'
    command_line = 'mkdir -p ' + outdir_dir
    os.system(command_line)

    tmp_dir = smac_solver_dir + '/' + 'tmp/'
    command_line = 'mkdir -p ' + tmp_dir
    os.system(command_line)

    return
