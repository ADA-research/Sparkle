#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for adding solvers."""

import os

try:
    from sparkle_help import sparkle_file_help as sfh
except ImportError:
    import sparkle_file_help as sfh


def get_solver_directory(solver_name: str) -> str:
    """ A helper function that returs the path to a solver

    Args:
        solver_name (str): the name of the solver for which the path is needed

    Returns:
        str: the relative path of the solver as a string
    """
    return "Solvers/" + solver_name


def check_adding_solver_contain_pcs_file(solver_directory: str) -> bool:
    """Returns whether the directory of the solver being added contains a PCS file. 
    Args:
        solver_directory (str): the directory to be checked if it contains a PCS file
    Returns:
        bool: A Boolean that is true if and only if solver_directory contains exactly one PCS file
    """
    list_files = os.listdir(solver_directory)

    pcs_count = 0
    for file_name in list_files:
        file_extension = sfh.get_file_least_extension(file_name)

        if file_extension == "pcs":
            pcs_count += 1

    return False if pcs_count != 1 else True
