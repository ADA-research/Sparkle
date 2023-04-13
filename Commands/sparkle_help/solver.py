#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Class to handle a solver and its directories."""

import sys

from pathlib import Path

from sparkle_help import sparkle_global_help as sgh


class Solver:
    """Class to handle a solver and its directories."""
    def __init__(self, solver_directory: Path) -> None:
        """Initialize solver.

        Args:
            solver_directory: Directory of the solver.
        """
        self.directory = solver_directory
        self.name = solver_directory.name

    def get_pcs_file(self) -> Path:
        """Get path of the parameter file.

        Returns:
            Path to the parameter file.
        """
        file_count = 0
        file_name = ""
        for file_path in self.directory.iterdir():
            file_extension = "".join(file_path.suffixes)

            if file_extension == ".pcs":
                file_name = file_path.name
                file_count += 1

        if file_count != 1:
            print("None or multiple .pcs files found. Solver "
                  "is not valid for configuration.")
            sys.exit()

        return self.directory / file_name

    def is_deterministic(self) -> str:
        """Return a string indicating whether a given solver is deterministic or not.

        Returns:
            A string containing 0 or 1 indicating whether solver is deterministic.
        """
        deterministic = ""
        target_solver_path = "Solvers/" + self.name
        solver_list_path = sgh.solver_list_path

        fin = open(solver_list_path, "r+")

        while True:
            myline = fin.readline()
            if not myline:
                break
            myline = myline.strip()
            mylist = myline.split()

            if (mylist[0] == target_solver_path):
                deterministic = mylist[1]
                break

        return deterministic
