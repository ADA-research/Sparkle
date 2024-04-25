#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Class to handle a solver and its directories."""


from __future__ import annotations
import sys
import fcntl
import shlex
import ast
from pathlib import Path
import subprocess
from tools.runsolver_parsing import get_solver_output

class Solver:
    """Class to handle a solver and its directories."""
    solver_dir = Path("Solvers/")
    solver_list_path = Path("Reference_Lists/") / "sparkle_solver_list.txt"

    def __init__(self: Solver,
                 solver_directory: Path, 
                 raw_output_directory: Path = None,
                 runsolver_exec: Path = None) -> None:
        """Initialize solver.

        Args:
            solver_directory: Directory of the solver.
            raw_output_directory: Directory where solver will write its raw output.
                Defaults to solver_directory / tmp
            runsolver_exec: Path to the runsolver executable.
                By default, runsolver in solver_directory.
        """
        self.directory = solver_directory
        self.name = solver_directory.name
        self.raw_output_directory = raw_output_directory
        if self.raw_output_directory is None:
            self.raw_output_directory = self.directory / "tmp"
            self.raw_output_directory.mkdir(exist_ok=True)
        self.runsolver_exec = runsolver_exec
        if self.runsolver_exec is None:
            self.runsolver_exec = self.directory / "runsolver"
        

    def get_pcs_file(self: Solver) -> Path:
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
            sys.exit(-1)

        return self.directory / file_name

    # TODO: This information should be stored in the solver as an attribute too.
    # That will allow us to at least skip this method.
    def is_deterministic(self: Solver) -> str:
        """Return a string indicating whether a given solver is deterministic or not.

        Returns:
            A string containing 0 or 1 indicating whether solver is deterministic.
        """
        deterministic = ""
        target_solver_path = "Solvers/" + self.name
        for solver in Solver.get_solver_list():
            solver_line = solver.strip().split()
            if (solver_line[0] == target_solver_path):
                deterministic = solver_line[1]
                break

        return deterministic

    @staticmethod
    def get_solver_by_name(name: str) -> Solver:
        """Attempt to resolve the solver object by name.

        Args:
            name: The name of the solver

        Returns:
            A Solver object if found, None otherwise
        """
        if (Solver.solver_dir / name).exists():
            return Solver(Solver.solver_dir / name)
        return None

    @staticmethod
    def get_solver_list() -> list[str]:
        """Get solver list from file."""
        if Solver.solver_list_path.exists():
            with Solver.solver_list_path.open("r+") as fo:
                fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
                return ast.literal_eval(fo.read())
        return []

    @staticmethod
    def config_str_to_dict(configuration: str) -> dict[str, str]:
        """Parse a configuration string to a dictionary."""
        # First we filter the configuration of unwanted characters
        configuration = configuration.strip().replace("-", "")
        # Then we split the string by spaces, but conserve substrings
        config_list = shlex.split(configuration)
        config = {}
        for index in range(0, len(config_list), 2):
            # As the value will already be a string object, no quotes are allowed in it
            value = config[config_list[index + 1]].strip('"').strip("'")
            config[config_list[index]] = value
        return config


    def build_solver_cmd(self, instance: str, configuration: dict = None,
                         runsolver_configuration: list[str] = None) -> list[str]:
        """Build the solver call on an instance with a certain configuration."""
        if isinstance(configuration, str):
            configuration = Solver.config_str_to_dict(configuration)
            if "instance" not in configuration:
                configuration["instance"] = instance
        solver_cmd = []
        if runsolver_configuration is not None:
            # We wrap the solver call in the runsolver executable, by placing it in front
            solver_cmd += [self.runsolver_exec] + runsolver_configuration
        solver_cmd += [self.directory / "solver_wrapper.py", str(configuration)]
        return solver_cmd

    def run_solver(self, instance: str, configuration: dict = None,
                   runsolver_configuration: list[str] = None) -> dict[str, str]:
        """Run the solver on an instance with a certain configuration.

        Args:
            instance:
            configuration:
            runsolver_configuration:

        Returns:
            Solver output dict possibly with runsolver values.
        """
        solver_cmd = self.build_solver_cmd(instance,
                                           configuration=configuration,
                                           runsolver_configuration=runsolver_configuration)
        process = subprocess.run(solver_cmd,
                                 cwd=self.raw_output_directory,
                                 capture_output=True)
        if process.returncode != 0:
            print(f"WARNING: Solver {self.solver_name} execution seems to have failed!\n"
                  f"The used command was: {solver_cmd}", flush=True)
            return {"status": "ERROR", }
        # Resolving solver output
        if runsolver_configuration is not None:
            solver_output = get_solver_output(runsolver_configuration,
                                              process.stdout.decode())
        else:
            # Ran without runsolver, can read solver output directly
            solver_output = ast.literal_eval(process.stdout.decode())
        return solver_output
