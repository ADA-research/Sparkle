#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for adding solvers."""

import os

try:
    from sparkle_help import sparkle_file_help as sfh
except ImportError:
    import sparkle_file_help as sfh


def get_solver_directory(solver_name: str) -> str:
    """Return the directory a solver is stored in as str.

    Args:
        solver_name: Name of the solver.

    Returns:
        A str of the path to the solver.
    """
    return f"Solvers/{solver_name}"


def check_adding_solver_contain_pcs_file(solver_directory: str) -> bool:
    """Return whether the directory of the solver being added contains a PCS file."""
    list_files = os.listdir(solver_directory)

    pcs_count = 0

    for file_name in list_files:
        file_extension = sfh.get_file_least_extension(file_name)

        if file_extension == "pcs":
            pcs_count += 1

    return False if pcs_count != 1 else True
