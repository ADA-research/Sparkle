#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for adding solvers."""
import global_variables as gv


def get_solver_directory(solver_name: str) -> str:
    """Return the directory a solver is stored in as str.

    Args:
        solver_name: Name of the solver.

    Returns:
        A str of the path to the solver.
    """
    return str(gv.solver_dir / solver_name)
