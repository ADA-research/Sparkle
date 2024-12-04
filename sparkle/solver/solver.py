"""File to handle a solver and its directories."""
from __future__ import annotations
import sys
import itertools
from typing import Any
import shlex
import ast
import json
from pathlib import Path

from ConfigSpace import ConfigurationSpace

import runrunner as rrr
from runrunner.local import LocalRun
from runrunner.slurm import Run, SlurmRun
from runrunner.base import Status, Runner

from sparkle.tools import pcsparser, RunSolver
from sparkle.types import SparkleCallable, SolverStatus
from sparkle.solver.verifier import SolutionVerifier
from sparkle.instance import InstanceSet
from sparkle.structures import PerformanceDataFrame
from sparkle.types import resolve_objective, SparkleObjective, UseTime


class Solver(SparkleCallable):
    """Class to handle a solver and its directories."""
    meta_data = "solver_meta.txt"
    wrapper = "sparkle_solver_wrapper.py"
    solver_cli = Path(__file__).parent / "solver_cli.py"

    def __init__(self: Solver,
                 directory: Path,
                 raw_output_directory: Path = None,
                 runsolver_exec: Path = None,
                 deterministic: bool = None,
                 verifier: SolutionVerifier = None) -> None:
        """Initialize solver.

        Args:
            directory: Directory of the solver.
            raw_output_directory: Directory where solver will write its raw output.
            runsolver_exec: Path to the runsolver executable.
                By default, runsolver in directory.
            deterministic: Bool indicating determinism of the algorithm.
                Defaults to False.
            verifier: The solution verifier to use. If None, no verifier is used.
        """
        super().__init__(directory, runsolver_exec, raw_output_directory)
        self.deterministic = deterministic
        self.verifier = verifier
        self.meta_data_file = self.directory / Solver.meta_data

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

    def __str__(self: Solver) -> str:
        """Return the sting representation of the solver."""
        return self.name

    def _get_pcs_file(self: Solver, port_type: str = None) -> Path | bool:
        """Get path of the parameter file.

        Returns:
            Path to the parameter file or False if the parameter file does not exist.
        """
        pcs_files = [p for p in self.directory.iterdir() if p.suffix == ".pcs"
                     and (port_type is None or port_type in p.name)]

        if len(pcs_files) == 0:
            return False
        if len(pcs_files) != 1:
            # Generated PCS files present, this is a quick fix to take the original
            pcs_files = sorted(pcs_files, key=lambda p: len(p.name))
        return pcs_files[0]

    def get_pcs_file(self: Solver, port_type: str = None) -> Path:
        """Get path of the parameter file.

        Returns:
            Path to the parameter file. None if it can not be resolved.
        """
        if not (file_path := self._get_pcs_file(port_type)):
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

    def get_pcs(self: Solver) -> dict[str, tuple[str, str, str]]:
        """Get the parameter content of the PCS file."""
        if not (pcs_file := self.get_pcs_file()):
            return None
        parser = pcsparser.PCSParser()
        parser.load(str(pcs_file), convention="smac")
        return [p for p in parser.pcs.params if p["type"] == "parameter"]

    def port_pcs(self: Solver, port_type: pcsparser.PCSConvention) -> None:
        """Port the parameter file to the given port type."""
        pcs_file = self.get_pcs_file()
        parser = pcsparser.PCSParser()
        parser.load(str(pcs_file), convention="smac")
        target_pcs_file = pcs_file.parent / f"{pcs_file.stem}_{port_type}.pcs"
        if target_pcs_file.exists():  # Already exists, possibly user defined
            return
        parser.export(convention=port_type,
                      destination=target_pcs_file)

    def get_configspace(self: Solver) -> ConfigurationSpace:
        """Get the parameter content of the PCS file."""
        if not (pcs_file := self.get_pcs_file()):
            return None
        parser = pcsparser.PCSParser()
        parser.load(str(pcs_file), convention="smac")
        return parser.get_configspace()

    def get_forbidden(self: Solver, port_type: pcsparser.PCSConvention) -> Path:
        """Get the path to the file containing forbidden parameter combinations."""
        if port_type == "IRACE":
            forbidden = [p for p in self.directory.iterdir()
                         if p.name.endswith("forbidden.txt")]
            if len(forbidden) > 0:
                return forbidden[0]
        return None

    def build_cmd(self: Solver,
                  instance: str | list[str],
                  objectives: list[SparkleObjective],
                  seed: int,
                  cutoff_time: int = None,
                  configuration: dict = None,
                  log_dir: Path = None) -> list[str]:
        """Build the solver call on an instance with a configuration.

        Args:
            instance: Path to the instance.
            seed: Seed of the solver.
            cutoff_time: Cutoff time for the solver.
            configuration: Configuration of the solver.

        Returns:
            List of commands and arguments to execute the solver.
        """
        if configuration is None:
            configuration = {}
        # Ensure configuration contains required entries for each wrapper
        configuration["solver_dir"] = str(self.directory.absolute())
        configuration["instance"] = instance
        configuration["seed"] = seed
        configuration["objectives"] = ",".join([str(obj) for obj in objectives])
        configuration["cutoff_time"] =\
            cutoff_time if cutoff_time is not None else sys.maxsize
        if "configuration_id" in configuration:
            del configuration["configuration_id"]
        # Ensure stringification of dictionary will go correctly for key value pairs
        configuration = {key: str(configuration[key]) for key in configuration}
        solver_cmd = [str((self.directory / Solver.wrapper)),
                      f"'{json.dumps(configuration)}'"]
        if log_dir is None:
            log_dir = Path()
        if cutoff_time is not None:  # Use RunSolver
            log_name_base = f"{Path(instance).name}_{self.name}"
            return RunSolver.wrap_command(self.runsolver_exec,
                                          solver_cmd,
                                          cutoff_time,
                                          log_dir,
                                          log_name_base=log_name_base)
        return solver_cmd

    def run(self: Solver,
            instance: str | list[str] | InstanceSet,
            objectives: list[SparkleObjective],
            seed: int,
            cutoff_time: int = None,
            configuration: dict = None,
            run_on: Runner = Runner.LOCAL,
            sbatch_options: list[str] = None,
            log_dir: Path = None,
            ) -> SlurmRun | list[dict[str, Any]] | dict[str, Any]:
        """Run the solver on an instance with a certain configuration.

        Args:
            instance: The instance(s) to run the solver on, list in case of multi-file.
                In case of an instance set, will run on all instances in the set.
            seed: Seed to run the solver with. Fill with abitrary int in case of
                determnistic solver.
            cutoff_time: The cutoff time for the solver, measured through RunSolver.
                If None, will be executed without RunSolver.
            configuration: The solver configuration to use. Can be empty.
            log_dir: Path where to place output files. Defaults to
                self.raw_output_directory.

        Returns:
            Solver output dict possibly with runsolver values.
        """
        if log_dir is None:
            log_dir = self.raw_output_directory
        cmds = []
        if isinstance(instance, InstanceSet):
            for inst in instance.instance_paths:
                solver_cmd = self.build_cmd(inst.absolute(),
                                            objectives=objectives,
                                            seed=seed,
                                            cutoff_time=cutoff_time,
                                            configuration=configuration,
                                            log_dir=log_dir)
                cmds.append(" ".join(solver_cmd))
        else:
            solver_cmd = self.build_cmd(instance,
                                        objectives=objectives,
                                        seed=seed,
                                        cutoff_time=cutoff_time,
                                        configuration=configuration,
                                        log_dir=log_dir)
            cmds.append(" ".join(solver_cmd))
        commandname = f"Run Solver: {self.name} on {instance}"
        run = rrr.add_to_queue(runner=run_on,
                               cmd=cmds,
                               name=commandname,
                               base_dir=log_dir,
                               sbatch_options=sbatch_options)

        if isinstance(run, LocalRun):
            run.wait()
            import time
            time.sleep(5)
            # Subprocess resulted in error
            if run.status == Status.ERROR:
                print(f"WARNING: Solver {self.name} execution seems to have failed!\n")
                for i, job in enumerate(run.jobs):
                    print(f"[Job {i}] The used command was: {cmds[i]}\n"
                          "The error yielded was:\n"
                          f"\t-stdout: '{run.jobs[0]._process.stdout}'\n"
                          f"\t-stderr: '{run.jobs[0]._process.stderr}'\n")
                return {"status": SolverStatus.ERROR, }

            solver_outputs = []
            for i, job in enumerate(run.jobs):
                solver_cmd = cmds[i].split(" ")
                runsolver_configuration = None
                if solver_cmd[0] == str(self.runsolver_exec.absolute()):
                    runsolver_configuration = solver_cmd[:11]
                solver_output = Solver.parse_solver_output(run.jobs[i].stdout,
                                                           runsolver_configuration,
                                                           objectives=objectives)
                if self.verifier is not None:
                    solver_output["status"] = self.verifier.verifiy(
                        instance, Path(runsolver_configuration[-1]))
                solver_outputs.append(solver_output)
            return solver_outputs if len(solver_outputs) > 1 else solver_output
        return run

    def run_performance_dataframe(self: Solver,
                                  instances: str | list[str] | InstanceSet,
                                  run_ids: int | list[int],
                                  performance_dataframe: PerformanceDataFrame,
                                  cutoff_time: int = None,
                                  train_set: InstanceSet = None,
                                  sbatch_options: list[str] = None,
                                  dependencies: list[SlurmRun] = None,
                                  log_dir: Path = None,
                                  base_dir: Path = None,
                                  run_on: Runner = Runner.SLURM,
                                  ) -> Run:
        """Run the solver from and place the results in the performance dataframe.

        This in practice actually runs Solver.run, but has a little script before/after,
        to read and write to the performance dataframe.

        Args:
            instance: The instance(s) to run the solver on. In case of an instance set,
                or list, will create a job for all instances in the set/list.
            run_ids: The run indices to use in the performance dataframe.
            performance_dataframe: The performance dataframe to use.
            cutoff_time: The cutoff time for the solver, measured through RunSolver.
            train_set: The training set to use. If present, will determine the best
                configuration of the solver using these instances and run with it on
                all instances in the instance argument.
            sbatch_options: List of slurm batch options to use
            dependencies: List of slurm runs to use as dependencies
            log_dir: Path where to place output files. Defaults to
                self.raw_output_directory.
            base_dir: Path where to place output files.
            run_on: On which platform to run the jobs. Default: Slurm.

        Returns:
            SlurmRun or Local run of the job.
        """
        instances = [instances] if isinstance(instances, str) else instances
        run_ids = [run_ids] if isinstance(run_ids, int) else run_ids
        set_name = "instances"
        if isinstance(instances, InstanceSet):
            set_name = instances.name
            instances = [str(i) for i in instances.instance_paths]
        train_arg =\
            ",".join([str(i) for i in train_set.instance_paths]) if train_set else ""
        cmds = [f"{Solver.solver_cli} "
                f"--solver {self.directory} "
                f"--instance {instance} "
                f"--run-index {run_index} "
                f"--performance-dataframe {performance_dataframe.csv_filepath} "
                f"--cutoff-time {cutoff_time} "
                f"--log-dir {log_dir} "
                f"{'--use-verifier' if self.verifier else ' '}"
                f"{'--best-configuration-instances' if train_set else ''} {train_arg}"
                for instance, run_index in itertools.product(instances, run_ids)]
        r = rrr.add_to_queue(
            runner=run_on,
            cmd=cmds,
            name=f"Run: {self.name} on {set_name}",
            base_dir=base_dir,
            sbatch_options=sbatch_options,
            dependencies=dependencies
        )
        if run_on == Runner.LOCAL:
            r.wait()
        return r

    @staticmethod
    def config_str_to_dict(config_str: str) -> dict[str, str]:
        """Parse a configuration string to a dictionary."""
        # First we filter the configuration of unwanted characters
        config_str = config_str.strip().replace("-", "")
        # Then we split the string by spaces, but conserve substrings
        config_list = shlex.split(config_str)
        # We return empty for empty input OR uneven input
        if config_str == "" or config_str == r"{}" or len(config_list) & 1:
            return {}
        config_dict = {}
        for index in range(0, len(config_list), 2):
            # As the value will already be a string object, no quotes are allowed in it
            value = config_list[index + 1].strip('"').strip("'")
            config_dict[config_list[index]] = value
        return config_dict

    @staticmethod
    def parse_solver_output(
            solver_output: str,
            runsolver_configuration: list[str | Path] = None,
            objectives: list[SparkleObjective] = None) -> dict[str, Any]:
        """Parse the output of the solver.

        Args:
            solver_output: The output of the solver run which needs to be parsed
            runsolver_configuration: The runsolver configuration to wrap the solver
                with. If runsolver was not used this should be None.
            objectives: The objectives to apply to the solver output

        Returns:
            Dictionary representing the parsed solver output
        """
        if runsolver_configuration is not None:
            parsed_output = RunSolver.get_solver_output(runsolver_configuration,
                                                        solver_output)
        else:
            parsed_output = ast.literal_eval(solver_output)
        # cast status attribute from str to Enum
        # TODO: Setup status as an objective class with a post process mapping
        parsed_output["status"] = SolverStatus(parsed_output["status"])
        if objectives:  # Create objective map
            objectives = {o.stem: o for o in objectives}
        removable_keys = ["cutoff_time"]  # Keys to remove
        # Apply objectives to parsed output, runtime based objectives added here
        for key, value in parsed_output.items():
            if objectives and key in objectives:
                objective = objectives[key]
                removable_keys.append(key)  # We translate it into the full name
            else:
                objective = resolve_objective(key)
            # If not found in objectives, resolve to which objective the output belongs
            if objective is None:  # Could not parse, skip
                continue
            if objective.use_time == UseTime.NO:
                if objective.post_process is not None:
                    parsed_output[key] = objective.post_process(value)
            else:
                if runsolver_configuration is None:
                    continue
                if objective.use_time == UseTime.CPU_TIME:
                    parsed_output[key] = parsed_output["cpu_time"]
                else:
                    parsed_output[key] = parsed_output["wall_time"]
                if objective.post_process is not None:
                    parsed_output[key] = objective.post_process(
                        parsed_output[key], parsed_output["cutoff_time"])

        # Replace or remove keys based on the objective names
        for key in removable_keys:
            if key in parsed_output:
                if key in objectives:
                    # Map the result to the objective
                    parsed_output[objectives[key].name] = parsed_output[key]
                    if key != objectives[key].name:  # Only delete actual mappings
                        del parsed_output[key]
                else:
                    del parsed_output[key]
        return parsed_output
