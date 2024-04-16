"""File containing the Validator class."""

from __future__ import annotations

import sys
from pathlib import Path, PurePath
import json
import runrunner as rrr
from runrunner import Runner

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_basic_help as sbh
from Commands.sparkle_help import sparkle_slurm_help as ssh
from Commands.sparkle_help.sparkle_command_help import CommandName
from Commands.sparkle_help import sparkle_file_help as sfh


class Validator():
    def __init__(self: Validator) -> None:
        """Construct the validator"""
        # TODO: what attributes should the validator have?
        pass

    def validate(self: Validator, solvers: list[Path], config_str_list: list[str] | str, instance_sets: list[Path], run_on: Runner=Runner.SLURM):
        """
        TODO

        Parameters
        ----------
        solvers: list of solvers to validate
        config_str_list: list of parameters for each solver we validate
        instance_sets: set of instance sets on which we want to validate each solver
        run_on: whether to run on SLURM or local
        """
        # if there is only one configuration, we extend it to a list of the same length as the solver list
        if isinstance(config_str_list, str):
            config_str_list = [config_str_list] * len(solvers)
        elif len(config_str_list) != len(solvers):
            print("Error: Length of solver list and configuration string list does not match!")
            sys.exit(-1)

        num_job_in_parallel = sgh.settings.get_slurm_number_of_runs_in_parallel()
        # TODO: determine number of CPU cores we should use
        srun_options = ["-N1", "-n1"] + ssh.get_slurm_options_list()
        sbatch_options = ssh.get_slurm_options_list()
        cmd_base = "Commands/sparkle_help/run_solvers_core.py"
        perf_m = sgh.settings.get_general_sparkle_objectives()[0].PerformanceMeasure

        for solver in solvers:
            for instance_set in instance_sets:
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
                