#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for adding solvers."""
import os
from pathlib import Path
import global_variables as sgh


def get_solver_directory(solver_name: str) -> str:
    """Return the directory a solver is stored in as str.

    Args:
        solver_name: Name of the solver.

    Returns:
        A str of the path to the solver.
    """
    return str(sgh.solver_dir / solver_name)


def check_adding_solver_contain_pcs_file(solver_directory: str) -> bool:
    """Returns whether the directory of the solver being added contains a PCS file.

    Args:
        solver_directory: The directory to be checked if it contains a PCS file.

    Returns:
        A Boolean that is true if and only if
        solver_directory contains exactly one PCS file.
    """
    list_files = os.listdir(solver_directory)

    pcs_count = 0

    for file_name in list_files:
        file_extension = Path(file_name).suffix

        if file_extension == "pcs":
            pcs_count += 1

    return False if pcs_count != 1 else True
