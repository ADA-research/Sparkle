"""File to handle a solver and its directories."""

from __future__ import annotations
import sys
from typing import Any
import shlex
import ast
import json
import random
from pathlib import Path

from ConfigSpace import ConfigurationSpace

import runrunner as rrr
from runrunner.local import LocalRun
from runrunner.slurm import Run, SlurmRun
from runrunner.base import Status, Runner

from sparkle.tools.parameters import PCSConverter, PCSConvention
from sparkle.tools import RunSolver
from sparkle.types import SparkleCallable, SolverStatus
from sparkle.solver import verifiers
from sparkle.instance import InstanceSet
from sparkle.structures import PerformanceDataFrame
from sparkle.types import resolve_objective, SparkleObjective, UseTime


class Solver(SparkleCallable):
    """Class to handle a solver and its directories."""

    meta_data = "solver_meta.txt"
    _wrapper_file = "sparkle_solver_wrapper"
    solver_cli = Path(__file__).parent / "solver_cli.py"

    def __init__(
        self: Solver,
        directory: Path,
        runsolver_exec: Path = None,
        deterministic: bool = None,
        verifier: verifiers.SolutionVerifier = None,
    ) -> None:
        """Initialize solver.

        Args:
            directory: Directory of the solver.
            runsolver_exec: Path to the runsolver executable.
                By default, runsolver in directory.
            deterministic: Bool indicating determinism of the algorithm.
                Defaults to False.
            verifier: The solution verifier to use. If None, no verifier is used.
        """
        super().__init__(directory, runsolver_exec)
        self.deterministic = deterministic
        self.verifier = verifier
        self._pcs_file: Path = None
        self._interpreter: str = None
        self._wrapper_extension: str = None

        meta_data_file = self.directory / Solver.meta_data
        if meta_data_file.exists():
            meta_data = ast.literal_eval(meta_data_file.open().read())
            # We only override the deterministic and verifier from file if not set
            if self.deterministic is None:
                if (
                    "deterministic" in meta_data
                    and meta_data["deterministic"] is not None
                ):
                    self.deterministic = meta_data["deterministic"]
            if self.verifier is None and "verifier" in meta_data:
                if isinstance(meta_data["verifier"], tuple):  # File verifier
                    self.verifier = verifiers.mapping[meta_data["verifier"][0]](
                        Path(meta_data["verifier"][1])
                    )
                elif meta_data["verifier"] in verifiers.mapping:
                    self.verifier = verifiers.mapping[meta_data["verifier"]]
        if self.deterministic is None:  # Default to False
            self.deterministic = False

    def __str__(self: Solver) -> str:
        """Return the string representation of the solver."""
        return self.name

    def __repr__(self: Solver) -> str:
        """Return detailed representation of the solver."""
        return (
            f"{self.name}:\n"
            f"\t- Directory: {self.directory}\n"
            f"\t- Deterministic: {self.deterministic}\n"
            f"\t- Verifier: {self.verifier}\n"
            f"\t- PCS File: {self.pcs_file}\n"
            f"\t- Wrapper: {self.wrapper}"
        )

    @property
    def pcs_file(self: Solver) -> Path:
        """Get path of the parameter file."""
        if self._pcs_file is None:
            files = sorted([p for p in self.directory.iterdir() if p.suffix == ".pcs"])
            if len(files) == 0:
                return None
            self._pcs_file = files[0]
        return self._pcs_file

    @property
    def wrapper_extension(self: Solver) -> str:
        """Get the extension of the wrapper file."""
        if self._wrapper_extension is None:
            # Determine which file is the wrapper by sorting alphabetically
            wrapper = sorted(
                [p for p in self.directory.iterdir() if p.stem == Solver._wrapper_file]
            )[0]
            self._wrapper_extension = wrapper.suffix
        return self._wrapper_extension

    @property
    def wrapper(self: Solver) -> str:
        """Get name of the wrapper file."""
        return f"{Solver._wrapper_file}{self.wrapper_extension}"

    @property
    def wrapper_file(self: Solver) -> Path:
        """Get path of the wrapper file."""
        return self.directory / self.wrapper

    def get_pcs_file(self: Solver, port_type: PCSConvention) -> Path:
        """Get path of the parameter file of a specific convention.

        Args:
            port_type: Port type of the parameter file. If None, will return the
                file with the shortest name.

        Returns:
            Path to the parameter file. None if it can not be resolved.
        """
        pcs_files = sorted([p for p in self.directory.iterdir() if p.suffix == ".pcs"])
        if port_type is None:
            return pcs_files[0]
        for file in pcs_files:
            if port_type == PCSConverter.get_convention(file):
                return file
        return None

    def read_pcs_file(self: Solver) -> bool:
        """Checks if the pcs file can be read."""
        # TODO: Should be a .validate method instead
        return PCSConverter.get_convention(self.pcs_file) is not None

    def get_configuration_space(self: Solver) -> ConfigurationSpace:
        """Get the ConfigurationSpace of the PCS file."""
        if not self.pcs_file:
            return None
        return PCSConverter.parse(self.pcs_file)

    def port_pcs(self: Solver, port_type: PCSConvention) -> None:
        """Port the parameter file to the given port type."""
        target_pcs_file = (
            self.pcs_file.parent / f"{self.pcs_file.stem}_{port_type.name}.pcs"
        )
        if target_pcs_file.exists():  # Already exists, possibly user defined
            return
        PCSConverter.export(self.get_configuration_space(), port_type, target_pcs_file)

    def build_cmd(
        self: Solver,
        instance: str | list[str],
        objectives: list[SparkleObjective],
        seed: int,
        cutoff_time: int = None,
        configuration: dict = None,
        log_dir: Path = None,
    ) -> list[str]:
        """Build the solver call on an instance with a configuration.

        Args:
            instance: Path to the instance.
            objectives: List of sparkle objectives.
            seed: Seed of the solver.
            cutoff_time: Cutoff time for the solver.
            configuration: Configuration of the solver.
            log_dir: Directory path for logs.

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
        configuration["cutoff_time"] = (
            cutoff_time if cutoff_time is not None else sys.maxsize
        )
        if "configuration_id" in configuration:
            del configuration["configuration_id"]
        # Ensure stringification of dictionary will go correctly for key value pairs
        configuration = {key: str(configuration[key]) for key in configuration}
        solver_cmd = [
            str(self.directory / self.wrapper),
            f"'{json.dumps(configuration)}'",
        ]
        if log_dir is None:
            log_dir = Path()
        if cutoff_time is not None:  # Use RunSolver
            log_path_str = instance[0] if isinstance(instance, list) else instance
            log_name_base = f"{Path(log_path_str).name}_{self.name}"
            return RunSolver.wrap_command(
                self.runsolver_exec,
                solver_cmd,
                cutoff_time,
                log_dir,
                log_name_base=log_name_base,
            )
        return solver_cmd

    def run(
        self: Solver,
        instances: str | list[str] | InstanceSet | list[InstanceSet],
        objectives: list[SparkleObjective],
        seed: int,
        cutoff_time: int = None,
        configuration: dict = None,
        run_on: Runner = Runner.LOCAL,
        sbatch_options: list[str] = None,
        slurm_prepend: str | list[str] | Path = None,
        log_dir: Path = None,
    ) -> SlurmRun | list[dict[str, Any]] | dict[str, Any]:
        """Run the solver on an instance with a certain configuration.

        Args:
            instances: The instance(s) to run the solver on, list in case of multi-file.
                In case of an instance set, will run on all instances in the set.
            objectives: List of sparkle objectives.
            seed: Seed to run the solver with. Fill with abitrary int in case of
                determnistic solver.
            cutoff_time: The cutoff time for the solver, measured through RunSolver.
                If None, will be executed without RunSolver.
            configuration: The solver configuration to use. Can be empty.
            run_on: Whether to run on slurm or locally.
            sbatch_options: The sbatch options to use.
            slurm_prepend: The script to prepend to a slurm script.
            log_dir: The log directory to use.

        Returns:
            Solver output dict possibly with runsolver values.
        """
        cmds = []
        set_label = instances.name if isinstance(instances, InstanceSet) else "instances"
        instances = [instances] if not isinstance(instances, list) else instances
        log_dir = Path() if log_dir is None else log_dir
        for instance in instances:
            paths = (
                instance.instance_paths
                if isinstance(instance, InstanceSet)
                else [instance]
            )
            for instance_path in paths:
                instance_path = (
                    [str(p) for p in instance_path]
                    if isinstance(instance_path, list)
                    else instance_path
                )
                solver_cmd = self.build_cmd(
                    instance_path,
                    objectives=objectives,
                    seed=seed,
                    cutoff_time=cutoff_time,
                    configuration=configuration,
                    log_dir=log_dir,
                )
                cmds.append(" ".join(solver_cmd))

        commandname = f"Run Solver: {self.name} on {set_label}"
        run = rrr.add_to_queue(
            runner=run_on,
            cmd=cmds,
            name=commandname,
            base_dir=log_dir,
            sbatch_options=sbatch_options,
            prepend=slurm_prepend,
        )

        if isinstance(run, LocalRun):
            run.wait()
            if run.status == Status.ERROR:  # Subprocess resulted in error
                print(f"WARNING: Solver {self.name} execution seems to have failed!\n")
                for i, job in enumerate(run.jobs):
                    print(
                        f"[Job {i}] The used command was: {cmds[i]}\n"
                        "The error yielded was:\n"
                        f"\t-stdout: '{job.stdout}'\n"
                        f"\t-stderr: '{job.stderr}'\n"
                    )
                return {
                    "status": SolverStatus.ERROR,
                }

            solver_outputs = []
            for i, job in enumerate(run.jobs):
                solver_cmd = cmds[i].split(" ")
                solver_output = Solver.parse_solver_output(
                    run.jobs[i].stdout,
                    solver_call=solver_cmd,
                    objectives=objectives,
                    verifier=self.verifier,
                )
                solver_outputs.append(solver_output)
            return solver_outputs if len(solver_outputs) > 1 else solver_output
        return run

    def run_performance_dataframe(
        self: Solver,
        instances: str | list[str] | InstanceSet,
        performance_dataframe: PerformanceDataFrame,
        config_ids: str | list[str] = None,
        run_ids: list[int] | list[list[int]] = None,
        cutoff_time: int = None,
        objective: SparkleObjective = None,
        train_set: InstanceSet = None,
        sbatch_options: list[str] = None,
        slurm_prepend: str | list[str] | Path = None,
        dependencies: list[SlurmRun] = None,
        log_dir: Path = None,
        base_dir: Path = None,
        job_name: str = None,
        run_on: Runner = Runner.SLURM,
    ) -> Run:
        """Run the solver from and place the results in the performance dataframe.

        This in practice actually runs Solver.run, but has a little script before/after,
        to read and write to the performance dataframe.

        Args:
            instances: The instance(s) to run the solver on. In case of an instance set,
                or list, will create a job for all instances in the set/list.
            config_ids: The config indices to use in the performance dataframe.
            performance_dataframe: The performance dataframe to use.
            run_ids: List of run ids to use. If list of list, a list of runs is given
                per instance. Otherwise, all runs are used for each instance.
            cutoff_time: The cutoff time for the solver, measured through RunSolver.
            objective: The objective to use, only relevant when determining the best
                configuration.
            train_set: The training set to use. If present, will determine the best
                configuration of the solver using these instances and run with it on
                all instances in the instance argument.
            sbatch_options: List of slurm batch options to use
            slurm_prepend: Slurm script to prepend to the sbatch
            dependencies: List of slurm runs to use as dependencies
            log_dir: Path where to place output files. Defaults to CWD.
            base_dir: Path where to place output files.
            job_name: Name of the job
                If None, will generate a name based on Solver and Instances
            run_on: On which platform to run the jobs. Default: Slurm.

        Returns:
            SlurmRun or Local run of the job.
        """
        instances = [instances] if isinstance(instances, str) else instances
        set_name = "instances"
        if isinstance(instances, InstanceSet):
            set_name = instances.name
            instances = [str(i) for i in instances.instance_paths]
        if not isinstance(config_ids, list):
            config_ids = [config_ids]
        configurations = [
            performance_dataframe.get_full_configuration(str(self.directory), config_id)
            if config_id
            else None
            for config_id in config_ids
        ]
        if run_ids is None:
            run_ids = performance_dataframe.run_ids
        if isinstance(run_ids[0], list):  # Runs per instance
            combinations = []
            for index, instance in enumerate(instances):
                for run_id in run_ids[index]:
                    combinations.extend(
                        [
                            (instance, config_id, config, run_id)
                            for config_id, config in zip(config_ids, configurations)
                        ]
                    )
        else:  # Runs for all instances
            import itertools

            combinations = [
                (instance, config_data[0], config_data[1], run_id)
                for instance, config_data, run_id in itertools.product(
                    instances,
                    zip(config_ids, configurations),
                    performance_dataframe.run_ids,
                )
            ]
        objective_arg = f"--target-objective {objective.name}" if objective else ""
        train_arg = (
            "--best-configuration-instances "
            + " ".join([str(i) for i in train_set.instance_paths])
            if train_set
            else ""
        )
        configuration_args = [
            ""
            if not config_id and not config
            else f"--configuration-id {config_id}"
            if not config
            else f"--configuration '{json.dumps(config)}'"
            for _, config_id, config, _ in combinations
        ]

        # We run all instances/configs/runs combinations
        # For each value we try to resolve from the PDF, to avoid high read loads during executions
        cmds = [
            f"python3 {Solver.solver_cli} "
            f"--solver {self.directory} "
            f"--instance {instance} "
            f"{config_arg} "
            # f"{'--configuration-id ' + config_id if not config else '--configuration"' + str(config) + '\"'} "
            f"--run-index {run_id} "
            f"--objectives {' '.join([obj.name for obj in performance_dataframe.objectives])} "
            f"--performance-dataframe {performance_dataframe.csv_filepath} "
            f"--cutoff-time {cutoff_time} "
            f"--log-dir {log_dir} "
            f"--seed {random.randint(0, 2**32 - 1)} "
            f"{objective_arg} "
            f"{train_arg}"
            for (instance, _, _, run_id), config_arg in zip(
                combinations, configuration_args
            )
        ]
        job_name = f"Run: {self.name} on {set_name}" if job_name is None else job_name
        r = rrr.add_to_queue(
            runner=run_on,
            cmd=cmds,
            name=job_name,
            base_dir=base_dir,
            sbatch_options=sbatch_options,
            prepend=slurm_prepend,
            dependencies=dependencies,
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
        solver_call: list[str | Path] = None,
        objectives: list[SparkleObjective] = None,
        verifier: verifiers.SolutionVerifier = None,
    ) -> dict[str, Any]:
        """Parse the output of the solver.

        Args:
            solver_output: The output of the solver run which needs to be parsed
            solver_call: The solver call used to run the solver
            objectives: The objectives to apply to the solver output
            verifier: The verifier to check the solver output

        Returns:
            Dictionary representing the parsed solver output
        """
        used_runsolver = False
        if solver_call is not None and len(solver_call) > 2:
            used_runsolver = True
            parsed_output = RunSolver.get_solver_output(solver_call, solver_output)
        else:
            parsed_output = ast.literal_eval(solver_output)
        # cast status attribute from str to Enum
        parsed_output["status"] = SolverStatus(parsed_output["status"])
        # Apply objectives to parsed output, runtime based objectives added here
        if verifier is not None and used_runsolver:
            # Horrible hack to get the instance from the solver input
            solver_call_str: str = " ".join(solver_call)
            solver_input_str = solver_call_str.split(Solver._wrapper_file, maxsplit=1)[1]
            solver_input_str = solver_input_str.split(" ", maxsplit=1)[1]
            solver_input_str = solver_input_str[
                solver_input_str.index("{") : solver_input_str.index("}") + 1
            ]
            solver_input = ast.literal_eval(solver_input_str)
            target_instance = Path(solver_input["instance"])
            parsed_output["status"] = verifier.verify(
                target_instance, parsed_output, solver_call
            )

        # Create objective map
        objectives = {o.stem: o for o in objectives} if objectives else {}
        removable_keys = ["cutoff_time"]  # Keys to remove

        # apply objectives to parsed output, runtime based objectives added here
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
                if not used_runsolver:
                    continue
                if objective.use_time == UseTime.CPU_TIME:
                    parsed_output[key] = parsed_output["cpu_time"]
                else:
                    parsed_output[key] = parsed_output["wall_time"]
                if objective.post_process is not None:
                    parsed_output[key] = objective.post_process(
                        parsed_output[key],
                        parsed_output["cutoff_time"],
                        parsed_output["status"],
                    )

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
