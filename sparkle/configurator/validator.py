"""File containing the Validator class."""

from __future__ import annotations

import sys
from pathlib import Path
import csv
from runrunner import Runner

import global_variables as sgh
from sparkle.solver.solver import Solver
from CLI.support import run_configured_solver_help as rcsh
from tools.runsolver_parsing import get_solver_output

class Validator():
    def __init__(self: Validator) -> None:
        """Construct the validator"""
        pass

    def validate(self: Validator, solvers: list[Path], config_str_list: list[str] | str,
                 instance_sets: list[Path], run_on: Runner=Runner.SLURM):
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

        for solver_path, config_str in zip(solvers, config_str_list):
            # run a configured solver
            if config_str is None:
                config_str = ""
            for instance_set in instance_sets:
                instance_path_list = list(p.absolute() for p in instance_set.iterdir())
                solver = Solver.get_solver_by_name(solver_path.name)
                rcsh.call_configured_solver_parallel(instance_path_list, solver, config_str, run_on=run_on)
                """instance_path_list = list(p.absolute() for p in instance_set.iterdir())
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
                    runtime, wc_time = get_runtime(res.replace(".rawres", ".val"))
                    if runtime == -1.0:
                        runtime = wc_time
                    status, quality = out_dict["status"], out_dict["quality"]
                    Validator.write_csv(solver.name, config_str,
                                        instance_set.name, instance_name,
                                        status, quality, runtime)"""
                    # Clean up .rawres files from this loop iteration?

    def get_validation_results(solver: Solver | str, instance_set: str, config: str = None) -> list[list[str]]:
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
        if isinstance(solver, str):
            solver = Solver.get_solver_by_name(solver)
        # Check if we still have to collect results for this combination
        if any(x.suffix == ".rawres" for x in solver.raw_output_directory.iterdir()):
            relevant_instances = [p.name for p in (sgh.instance_dir / instance_set).iterdir()]
            for res in solver.raw_output_directory.iterdir():
                if res.suffix != ".rawres":
                    continue
                res_str = str(res)
                first_underscore_index = res_str.find('_')
                second_underscore_index = res_str.find('_', first_underscore_index + 1)
                instance_name = res_str[first_underscore_index+1:second_underscore_index]
                if instance_name in relevant_instances:
                    out_dict = get_solver_output(["-o", res.name, "-v", res.with_suffix('.val').name],
                                                 "", solver.raw_output_directory)
                    Validator.append_entry_to_csv(solver.name,
                                                  config,
                                                  instance_set,
                                                  instance_name,
                                                  out_dict["status"],
                                                  out_dict["quality"],
                                                  out_dict["runtime"])
                    res.unlink()
                    res.with_suffix(".val").unlink()
                    res.with_suffix(".log").unlink()

        out_dir = sgh.validation_output_general / f"{solver.name}_{instance_set}"
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
               csv.writer(out).writerow(("Solver", "Configuration", "InstanceSet",
                                      "Instance", "Status", "Quality", "Runtime"))
        with csv_file.open("a") as out:
            writer = csv.writer(out)
            writer.writerow((solver, config_str, instance_set, instance, status,
                             quality, runtime))
