"""File containing the Validator class."""

from __future__ import annotations

import sys
from pathlib import Path
import csv
import ast
from runrunner import Runner

import global_variables as sgh
from sparkle.solver.solver import Solver
from CLI.support import run_configured_solver_help as rcsh
from tools.runsolver_parsing import get_solver_output, get_solver_args


class Validator():
    """Class to handle the validation of solvers on instance sets."""
    def __init__(self: Validator) -> None:
        """Construct the validator."""
        pass

    def validate(self: Validator, solvers: list[Path], config_str_list: list[str] | str,
                 instance_sets: list[Path], run_on: Runner = Runner.SLURM) -> None:
        """Validate a list of solvers (with configurations) on a set of instances.

        Args:
            solvers: list of solvers to validate
            config_str_list: list of parameters for each solver we validate
            instance_sets: set of instance sets on which we want to validate each solver
            run_on: whether to run on SLURM or local
        """
        # If there is only one configuration, we cast it to a list of the same
        # length as the solver list
        if isinstance(config_str_list, str):
            config_str_list = [config_str_list] * len(solvers)
        elif len(config_str_list) != len(solvers):
            print("Error: Number of solvers and configurations does not match!")
            sys.exit(-1)

        for solver_path, config_str in zip(solvers, config_str_list):
            # run a configured solver
            if config_str is None:
                config_str = ""
            for instance_set in instance_sets:
                instance_path_list = list(p.absolute() for p in instance_set.iterdir())
                solver = Solver.get_solver_by_name(solver_path.name)
                rcsh.call_configured_solver_parallel(instance_path_list,
                                                     solver,
                                                     config_str,
                                                     run_on=run_on)

    @staticmethod
    def retrieve_raw_results(solver: Solver, instance_set: str) -> None:
        """Checks the raw results of a given solver for a specific instance_set.

        Writes the raw results to a unified CSV file for the resolve/instance_set
        combination.

        Args:
            solver: The solver for which to check the raw result path
            instance_set: The set for which to retrieve the results
        """
        relevant_instances = [p.name for p in
                              (sgh.instance_dir / instance_set).iterdir()]
        for res in solver.raw_output_directory.iterdir():
            if res.suffix != ".rawres":
                continue
            res_str = str(res)
            first_underscore_index = res_str.find("_")
            second_underscore_index = res_str.find("_", first_underscore_index + 1)
            instance_name = res_str[first_underscore_index + 1:second_underscore_index]
            solver_args = get_solver_args(res.with_suffix(".log"))
            # Remove default args
            solver_args = ast.literal_eval(solver_args.strip())
            for def_arg in ["instance", "solver_dir", "cutoff_time",
                            "seed", "specifics", "run_length"]:
                if def_arg in solver_args:
                    del solver_args[def_arg]
            solver_args = str(solver_args).replace('"', "'")
            if instance_name in relevant_instances:
                out_dict = get_solver_output(
                    ["-o", res.name, "-v", res.with_suffix(".val").name],
                    "", solver.raw_output_directory)
                Validator.append_entry_to_csv(solver.name,
                                              solver_args,
                                              instance_set,
                                              instance_name,
                                              out_dict["status"],
                                              out_dict["quality"],
                                              out_dict["runtime"])
                res.unlink()
                res.with_suffix(".val").unlink()
                res.with_suffix(".log").unlink()

    @staticmethod
    def get_validation_results(solver: Solver | str,
                               instance_set: str,
                               config: str = None) -> list[list[str]]:
        """Query the results of the validation of solver on instance_set.

        Args:
            solver: Path to the validated solver
            instance_set: Path to validation set
            config: Path to the configuration if the solver was configured, None
                    otherwise

        Returns
            A list of row lists with string values
        """
        if isinstance(solver, str):
            solver = Solver.get_solver_by_name(solver)
        # Check if we still have to collect results for this combination
        if any(x.suffix == ".rawres" for x in solver.raw_output_directory.iterdir()):
            Validator.retrieve_raw_results(solver, instance_set)

        out_dir = sgh.validation_output_general / f"{solver.name}_{instance_set}"
        csv_file = out_dir / "validation.csv"
        # We skip the header when returning results
        csv_data = [line for line in csv.reader(csv_file.open("r"))][1:]
        if config is not None:
            # We filter on the config string by subdict
            if isinstance(config, str):
                config_dict = Solver.config_str_to_dict(config)
            csv_data = [line for line in csv_data if
                        config_dict.items() == ast.literal_eval(line[1]).items()]
        return csv_data

    @staticmethod
    def append_entry_to_csv(solver: str,
                            config_str: str,
                            instance_set: str,
                            instance: str,
                            status: str,
                            quality: str,
                            runtime: str) -> None:
        """Append a validation result as a row to a CSV file."""
        out_dir = sgh.validation_output_general / f"{solver}_{instance_set}"
        if not out_dir.exists():
            out_dir.mkdir(parents=True)
        csv_file = out_dir / "validation.csv"
        if not csv_file.exists():
            # Write header
            with csv_file.open("w") as out:
                csv.writer(out).writerow(("Solver", "Configuration", "InstanceSet",
                                          "Instance", "Status", "Quality", "Runtime"))
        with csv_file.open("a") as out:
            writer = csv.writer(out)
            writer.writerow((solver, config_str, instance_set, instance, status,
                             quality, runtime))
