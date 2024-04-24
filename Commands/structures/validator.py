"""File containing the Validator class."""

from __future__ import annotations

import os
import sys
from pathlib import Path, PurePath
import ast
import csv
import glob
import re
import runrunner as rrr
from runrunner import Runner

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_basic_help as sbh
from Commands.sparkle_help import sparkle_slurm_help as ssh
from Commands.sparkle_help.sparkle_command_help import CommandName
from Commands.sparkle_help import sparkle_file_help as sfh
from Commands.sparkle_help import sparkle_run_configured_solver_help as srcsh
from Commands.sparkle_help import sparkle_run_solvers_help as srsh


class Validator():
    def __init__(self: Validator) -> None:
        """Construct the validator"""
        pass

    def get_validation_results(self, solver, instance_set, config: str = None):
        '''
        Query the results of the validation of solver on instance_set.

        Parameters
        ----------
        solver: Path to the validated solver
        instance_set: Path to validation set
        config: Path to the configuration if the solver was configured, None
                otherwise

        Returns
        -------
        csv_file: Path to csv file where the validation results can be found
        '''
        out_dir = sgh.validation_output_general / f"{solver}_{instance_set}"
        csv_file = out_dir / "validation.csv"
        csv_data = [line for line in csv.reader(csv_file.open("r"))]
        if config is not None:
            # We filter on the config string, but are flexible with:
            # - Surrounding white space
            # - Singular quotes, double qoutes
            config = config.strip().replace("'", "").replace('"', "")
            csv_data = [line for line in csv_data if
                        csv_data[1].strip().replace("'", "") == config]
        return csv_data

    def validate(self: Validator, solvers: list[Path], config_str_list: list[str] | str,
                 instance_sets: list[Path], run_on: Runner=Runner.LOCAL):
        """
        Validate a list of solvers (with corresponding configurations) on a set
        of instances.

        Parameters
        ----------
        solvers: list of solvers to validate
        config_str_list: list of parameters for each solver we validate
        instance_sets: set of instance sets on which we want to validate each solver
        run_on: whether to run on SLURM or local
        """
        # if there is only one configuration, we extend it to a list of the same
        #   length as the solver list
        if isinstance(config_str_list, str):
            config_str_list = [config_str_list] * len(solvers)
        elif len(config_str_list) != len(solvers):
            print("Error: Number of solvers and configurations does not match!")
            sys.exit(-1)

        for solver, config_str in zip(solvers, config_str_list):
            # run a configured solver
            if config_str is None:
                config_str = ""
            for instance_set in instance_sets:
                instance_path_list = list(p.absolute() for p in instance_set.iterdir())
                _, solver_name = os.path.split(solver)
                srcsh.run_configured_solver(instance_path_list=instance_path_list,
                                            solver_name=solver_name,
                                            config_str=config_str)
                raw_res_files = glob.glob(f"{sgh.sparkle_tmp_path }/*.rawres")
                for res in raw_res_files:
                    first_underscore_index = res.find('_')
                    second_underscore_index = res.find('_', first_underscore_index + 1)
                    solver_name = solver.name
                    instance_name = res[first_underscore_index+1:second_underscore_index]
                    out_dict = srsh.get_solver_output_dict(Path(res))
                    if out_dict is None:
                        # Wrong file
                        continue
                    runtime, wc_time = srsh.get_runtime_from_runsolver(res.replace(".rawres", ".val"))
                    if runtime == -1.0:
                        runtime = wc_time
                    status, quality = out_dict["status"], out_dict["quality"]
                    Validator.write_csv(solver.name, config_str,
                                        instance_set.name, instance_name,
                                        status, quality, runtime)
                    # Clean up .rawres files from this loop iteration?
    
    def append_entry_to_csv(solver: str,
                            config_str: str,
                            instance_set: str,
                            instance: str,
                            status: str,
                            quality: str,
                            runtime: str):
        """Append a validation result to a CSV file."""
        out_dir = sgh.validation_output_general / f"{solver}_{instance_set}"
        if not out_dir.exists():
            out_dir.mkdir(parents=True)
        csv_file = out_dir / "validation.csv"
        if not csv_file.exists():
           # Write header
           with csv_file.open("w") as out:
               csv.writer(out).write(("Solver", "Configuration", "InstanceSet",
                                      "Instance", "Status", "Quality", "Runtime"))
        with csv_file.open("a") as out:
            writer = csv.writer(out)
            writer.writerow((solver, config_str, instance_set, instance, status,
                             quality, runtime))
