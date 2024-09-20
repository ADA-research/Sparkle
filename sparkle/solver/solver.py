"""File to handle a solver and its directories."""

from __future__ import annotations
import sys
from typing import Any
import shlex
import ast
import json
from pathlib import Path

import runrunner as rrr
from runrunner.local import LocalRun
from runrunner.slurm import SlurmRun
from runrunner.base import Status, Runner

from sparkle.tools import runsolver_parsing, general as tg
from sparkle.tools import pcsparser
from sparkle.types import SparkleCallable, SolverStatus
from sparkle.solver.verifier import SolutionVerifier
from sparkle.instance import InstanceSet
from sparkle.types import resolve_objective, SparkleObjective, UseTime


class Solver(SparkleCallable):
    """Class to handle a solver and its directories."""
    meta_data = "solver_meta.txt"
    wrapper = "sparkle_solver_wrapper.py"

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
                Defaults to directory / tmp
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

    def get_pcs(self: Solver) -> dict[str, tuple[str, str, str]]:
        """Get the parameter content of the PCS file."""
        if not (pcs_file := self.get_pcs_file()):
            return None
        parser = pcsparser.PCSParser()
        parser.load(str(pcs_file), convention="smac")
        return [p for p in parser.pcs.params if p["type"] == "parameter"]

    def build_cmd(self: Solver,
                  instance: str | list[str],
                  objectives: list[SparkleObjective],
                  seed: int,
                  cutoff_time: int = None,
                  configuration: dict = None) -> list[str]:
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
        if cutoff_time is not None:  # Use RunSolver
            configuration["cutoff_time"] = cutoff_time
            # Create RunSolver Logs
            # --timestamp
            #  instructs to timestamp each line of the solver standard output and
            #  error files (which are then redirected to stdout)

            # --use-pty
            # use a pseudo-terminal to collect the solver output. Currently only
            # available when lines are timestamped. Some I/O libraries (including
            # the C library) automatically flushes the output after each line when
            # the standard output is a terminal. There's no automatic flush when
            # the standard output is a pipe or a plain file. See setlinebuf() for
            # some details. This option instructs runsolver to use a
            # pseudo-terminal instead of a pipe/file to collect the solver
            # output. This fools the solver which will line-buffer its output.

            # -w filename or --watcher-data filename
            # sends the watcher informations to filename

            # -v filename or --var filename
            # save the most relevant information (times,...)
            # in an easy to parse VAR=VALUE file

            # -o filename or --solver-data filename
            # redirects the solver output (both stdout and stderr) to filename
            inst_name = Path(instance).name
            raw_result_path =\
                Path(f"{self.name}_{inst_name}_{tg.get_time_pid_random_string()}.rawres")
            runsolver_watch_data_path = raw_result_path.with_suffix(".log")
            runsolver_values_path = raw_result_path.with_suffix(".val")

            solver_cmd = [str(self.runsolver_exec.absolute()),
                          "--timestamp", "--use-pty",
                          "--cpu-limit", str(cutoff_time),
                          "-w", str(runsolver_watch_data_path),
                          "-v", str(runsolver_values_path),
                          "-o", str(raw_result_path)]
        else:
            configuration["cutoff_time"] = sys.maxsize
            solver_cmd = []

        # Ensure stringification of dictionary will go correctly for key value pairs
        configuration = {key: str(configuration[key]) for key in configuration}
        solver_cmd += [str((self.directory / Solver.wrapper).absolute()),
                       f"'{json.dumps(configuration)}'"]
        return solver_cmd

    def run(self: Solver,
            instance: str | list[str] | InstanceSet,
            objectives: list[SparkleObjective],
            seed: int,
            cutoff_time: int = None,
            configuration: dict = None,
            run_on: Runner = Runner.LOCAL,
            commandname: str = "run_solver",
            sbatch_options: list[str] = None,
            cwd: Path = None) -> SlurmRun | list[dict[str, Any]] | dict[str, Any]:
        """Run the solver on an instance with a certain configuration.

        Args:
            instance: The instance(s) to run the solver on, list in case of multi-file.
                In case of an instance set, will run on all instances in the set.
            seed: Seed to run the solver with. Fill with abitrary int in case of
                determnistic solver.
            cutoff_time: The cutoff time for the solver, measured through RunSolver.
                If None, will be executed without RunSolver.
            configuration: The solver configuration to use. Can be empty.
            cwd: Path where to execute. Defaults to self.raw_output_directory.

        Returns:
            Solver output dict possibly with runsolver values.
        """
        if cwd is None:
            cwd = self.raw_output_directory
        cmds = []
        if isinstance(instance, InstanceSet):
            for inst in instance.instance_paths:
                solver_cmd = self.build_cmd(inst.absolute(),
                                            objectives=objectives,
                                            seed=seed,
                                            cutoff_time=cutoff_time,
                                            configuration=configuration)
                cmds.append(" ".join(solver_cmd))
        else:
            solver_cmd = self.build_cmd(instance,
                                        objectives=objectives,
                                        seed=seed,
                                        cutoff_time=cutoff_time,
                                        configuration=configuration)
            cmds.append(" ".join(solver_cmd))
        run = rrr.add_to_queue(runner=run_on,
                               cmd=cmds,
                               name=commandname,
                               base_dir=cwd,
                               path=cwd,
                               sbatch_options=sbatch_options)

        if isinstance(run, LocalRun):
            run.wait()
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
                                                           cwd)
                if self.verifier is not None:
                    solver_output["status"] = self.verifier.verifiy(
                        instance, Path(runsolver_configuration[-1]))
                solver_outputs.append(solver_output)
            return solver_outputs if len(solver_outputs) > 1 else solver_output
        return run

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
        """Parse the output of the solver.

        Args:
            solver_output: The output of the solver run which needs to be parsed
            runsolver_configuration: The runsolver configuration to wrap the solver
                with. If runsolver was not used this should be None.
            cwd: Path where to execute. Defaults to self.raw_output_directory.

        Returns:
            Dictionary representing the parsed solver output
        """
        if runsolver_configuration is not None:
            parsed_output = runsolver_parsing.get_solver_output(runsolver_configuration,
                                                                solver_output,
                                                                cwd)
        else:
            parsed_output = ast.literal_eval(solver_output)

        # cast status attribute from str to Enum
        parsed_output["status"] = SolverStatus(parsed_output["status"])
        # apply objectives to parsed output, runtime based objectives added here
        for key, value in parsed_output.items():
            if key == "status":
                continue
            objective = resolve_objective(key)
            if objective is None:
                continue
            if objective.use_time == UseTime.NO:
                if objective.post_process is not None:
                    parsed_output[objective] = objective.post_process(value)
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
        if "cutoff_time" in parsed_output:
            del parsed_output["cutoff_time"]
        return parsed_output
