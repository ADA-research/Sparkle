"""File containing the Validator class."""

from __future__ import annotations

import os
import sys
from pathlib import Path, PurePath
import csv
import glob
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

    def get_validation_results(self, solver, instance_set, config=None):
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
        csv_file = f"Output/validation/{solver}_{instance_set.name}/validation.csv"
        solver_name = solver.name
        solver_wrapper_path = solver/sgh.sparkle_solver_wrapper
        for instance in instance_set:
            instance_name = instance.name
            raw_results = glob.glob(f"Tmp/{solver_name}_{instance_name}*")
            if not raw_results:
                print(f"Error: No validation results found for {solver} and "
                      f"{instance}.")
            else:
                tuple_list = []
                for res in raw_results:
                    cpu_time, wc_time, quality, status = \
                        srsh.process_results(res, solver_wrapper_path, 
                                            res.replace(".rawres", ".val"))
                    tuple_list.append((quality, cpu_time))
                with open(csv_file, 'wb') as out:        
                    csv_out=csv.writer(out)
                    for row in tuple_list:
                        csv_out.writerow((solver_name, config, instance_set.name)
                                         + (instance_name,) + row)

        return csv_file

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

        # gather slurm information for the non-configured solvers which are run
        #   directly via runrunner
        num_job_in_parallel = sgh.settings.get_slurm_number_of_runs_in_parallel()
        # TODO: determine number of CPU cores we should use
        srun_options = ["-N1", "-n1"] + ssh.get_slurm_options_list()
        sbatch_options = ssh.get_slurm_options_list()
        perf_m = sgh.settings.get_general_sparkle_objectives()[0].PerformanceMeasure

        for solver, config_str in zip(solvers, config_str_list):
            # run a configured solver
            if config_str is not None:
                for instance_set in instance_sets:
                    instance_path_list = list(instance_set.iterdir())
                    _, solver_name = os.path.split(solver)
                    srcsh.run_configured_solver(instance_path_list=instance_path_list,
                                                solver_name=solver_name,
                                                config_str=config_str)

            # run a non-configured solver
            else:
                cmd_base = "Commands/sparkle_help/run_solvers_core.py"
                for instance_set in instance_sets.iterdir():
                    cmd_list = [f"{cmd_base} --instance {instance} --solver {solver} "
                                f"--performance-measure {perf_m.name}" for instance in instance_set]
                    
                    run = rrr.add_to_queue(
                        runner=run_on,
                        cmd=cmd_list,
                        parallel_jobs=num_job_in_parallel,
                        name=CommandName.RUN_SOLVERS,
                        base_dir=sgh.sparkle_tmp_path,
                        sbatch_options=sbatch_options,
                        srun_options=srun_options)
                    

        if run_on == Runner.LOCAL:
            print("Waiting for the local calculations to finish.")
            run.wait()
    