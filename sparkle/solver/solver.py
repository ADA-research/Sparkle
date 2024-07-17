#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""File to handle a solver and its directories."""

from __future__ import annotations
import sys
from typing import Any
import shlex
import ast
from pathlib import Path
import subprocess
from tools import runsolver_parsing
import pcsparser
from sparkle.types import SparkleCallable, SolverStatus


class Solver(SparkleCallable):
    """Class to handle a solver and its directories."""
    meta_data = "solver_meta.txt"
    wrapper = "sparkle_solver_wrapper.py"

    def __init__(self: Solver,
                 directory: Path,
                 raw_output_directory: Path = None,
                 runsolver_exec: Path = None,
                 deterministic: bool = None) -> None:
        """Initialize solver.

        Args:
            directory: Directory of the solver.
            raw_output_directory: Directory where solver will write its raw output.
                Defaults to directory / tmp
            runsolver_exec: Path to the runsolver executable.
                By default, runsolver in directory.
            deterministic: Bool indicating determinism of the algorithm.
                Defaults to False.
        """
        super().__init__(directory, runsolver_exec, raw_output_directory)
        self.deterministic = deterministic
        self.meta_data_file = self.directory / Solver.meta_data

        if self.raw_output_directory is None:
            self.raw_output_directory = self.directory / "tmp"
            self.raw_output_directory.mkdir(exist_ok=True)
        if self.runsolver_exec is None:
            self.runsolver_exec = self.directory / "runsolver"
        if not self.meta_data_file.exists():
            self.meta_data_file = None
        if self.deterministic is None:
            if self.meta_data_file is not None:
                # Read the parameter from file
                meta_dict = ast.literal_eval(self.meta_data_file.open().read())
                self.deterministic = meta_dict["deterministic"]
            else:
                self.deterministic = False

    def _get_pcs_file(self: Solver) -> Path | bool:
        """Get path of the parameter file.

        Returns:
            Path to the parameter file or False if the parameter file does not exist.
        """
        pcs_files = [p for p in self.directory.iterdir() if p.suffix == ".pcs"]
        if len(pcs_files) != 1:
            # We only consider one PCS file per solver
            return False
        return pcs_files[0]

    def get_pcs_file(self: Solver) -> Path:
        """Get path of the parameter file.

        Returns:
            Path to the parameter file. None if it can not be resolved.
        """
        if not (file_path := self._get_pcs_file()):
            return None
        return file_path

    def read_pcs_file(self: Solver) -> bool:
        """Checks if the pcs file can be read."""
        pcs_file = self._get_pcs_file()
        try:
            parser = pcsparser.PCSParser()
            parser.load(str(pcs_file), convention="smac")
            return True
        except SyntaxError:
            pass
        return False

    def build_cmd(self: Solver, instance: str | list[str], configuration: dict = None,
                  runsolver_configuration: list[str] = None) -> list[str]:
        """Build the solver call on an instance with a configuration."""
        if isinstance(configuration, str):
            configuration = Solver.config_str_to_dict(configuration)
        if configuration is None:
            configuration = {}
        # Ensure configuration contains required entries for each wrapper
        if "instance" not in configuration:
            configuration["instance"] = instance
        if "solver_dir" not in configuration:
            configuration["solver_dir"] = str(self.directory.absolute())
        if "specifics" not in configuration:
            configuration["specifics"] = ""
        if "run_length" not in configuration:
            configuration["run_length"] = ""
        if "cutoff_time" not in configuration:
            configuration["cutoff_time"] = sys.maxsize
        # Ensure stringification of dictionary will go correctly
        configuration = {key: str(configuration[key]) for key in configuration}
        # Ensure stringifcation of cmd call will go correctly
        solver_cmd = []
        if runsolver_configuration is not None:
            # Ensure stringification of runsolver configuration is done correctly
            runsolver_configuration = [str(runsolver_config) for runsolver_config in
                                       runsolver_configuration]
            # We wrap the solver call in the runsolver executable, by placing it in front
            solver_cmd += [str(self.runsolver_exec.absolute())] + runsolver_configuration
        solver_cmd += [str((self.directory / Solver.wrapper).absolute()),
                       str(configuration)]
        return solver_cmd

    def run(self: Solver, instance: str | list[str],
            configuration: dict = None,
            runsolver_configuration: list[str] = None,
            cwd: Path = None) -> dict[str, str]:
        """Run the solver on an instance with a certain configuration.

        Args:
            instance: The instance to run the solver on, list in case of multi-file
            configuration: The solver configuration to use. Can be empty.
            runsolver_configuration: The runsolver configuration to wrap the solver
                with. If None (default), runsolver will not be used.
            cwd: Path where to execute. Defaults to self.raw_output_directory.

        Returns:
            Solver output dict possibly with runsolver values.
        """
        if cwd is None:
            cwd = self.raw_output_directory
        solver_cmd = self.build_cmd(instance,
                                    configuration,
                                    runsolver_configuration)
        process = subprocess.run(solver_cmd,
                                 cwd=cwd,
                                 capture_output=True)

        # Subprocess resulted in error
        if process.returncode != 0:
            print(f"WARNING: Solver {self.name} execution seems to have failed!\n"
                  f"The used command was: {solver_cmd}\n The error yielded was: \n"
                  f"\t-stdout: '{process.stdout.decode()}'\n"
                  f"\t-stderr: '{process.stderr.decode()}'\n")
            return {"status": SolverStatus.ERROR, }

        return Solver.parse_solver_output(process.stdout.decode(),
                                          runsolver_configuration,
                                          cwd)

    @staticmethod
    def config_str_to_dict(config_str: str) -> dict[str, str]:
        """Parse a configuration string to a dictionary."""
        # First we filter the configuration of unwanted characters
        config_str = config_str.strip().replace("-", "")
        if config_str == "" or config_str == r"{}":
            return {}
        # Then we split the string by spaces, but conserve substrings
        config_list = shlex.split(config_str)
        config_dict = {}
        for index in range(0, len(config_list), 2):
            # As the value will already be a string object, no quotes are allowed in it
            value = config_list[index + 1].strip('"').strip("'")
            config_dict[config_list[index]] = value
        return config_dict

    @staticmethod
    def parse_solver_output(solver_output: str,
                            runsolver_configuration: list[str] = None,
                            cwd: Path = None) -> dict[str, Any]:
        """Parse the output of the solver."""
        if runsolver_configuration is not None:
            parsed_output = runsolver_parsing.get_solver_output(runsolver_configuration,
                                                                solver_output,
                                                                cwd)
        else:
            parsed_output = ast.literal_eval(solver_output)

        # cast status attribute from str to Enum
        parsed_output["status"] = SolverStatus(parsed_output["status"])

        return parsed_output
