"""File containing the Validator class."""

from __future__ import annotations

import sys
from pathlib import Path
import csv
import ast
from runrunner import Runner
from runrunner import SlurmRun, LocalRun

from CLI.help.command_help import CommandName
from sparkle.solver import Solver
from sparkle.instance import Instances
from CLI.help import run_solver_help as rcsh
from tools.runsolver_parsing import get_solver_output, get_solver_args


class Validator():
    """Class to handle the validation of solvers on instance sets."""
    def __init__(self: Validator, out_dir: Path = Path()) -> None:
        """Construct the validator."""
        self.out_dir = out_dir

    def validate(self: Validator,
                 solvers: list[Path] | list[Solver] | Solver | Path,
                 configurations: list[str] | str | Path,
                 instance_sets: list[Instances],
                 subdir: Path = None,
                 dependency: list[SlurmRun | LocalRun] | SlurmRun | LocalRun = None,
                 run_on: Runner = Runner.SLURM) -> list[SlurmRun | LocalRun]:
        """Validate a list of solvers (with configurations) on a set of instances.

        Args:
            solvers: list of solvers to validate
            configurations: list of configurations for each solver we validate.
                If a path is supplied, will use each line as a configuration.
            instance_sets: set of instance sets on which we want to validate each solver
            subdir: The subdir where to place the output in the outputdir. If None,
                a semi-unique combination of solver_instanceset is created.
            dependency: Jobs to wait for before executing the validation.
            run_on: whether to run on SLURM or local
        """
        # Seed only relevant when reading from file (Used as line index)
        use_seed = isinstance(configurations, Path)
        if not isinstance(solvers, list) and isinstance(configurations, list):
            # If we receive one solver but multiple configurations, we cas the
            # Solvers to a list of the same length
            solvers = [solvers] * len(configurations)
        elif not isinstance(configurations, list) and isinstance(solvers, list):
            # If there is only one configuration, we cast it to a list of the same
            # length as the solver list
            configurations = [configurations] * len(solvers)
        if not isinstance(solvers, list) or len(configurations) != len(solvers):
            print("Error: Number of solvers and configurations does not match!")
            sys.exit(-1)
        # Ensure we have the object representation of solvers
        solvers = [Solver(s) if isinstance(s, Path) else s for s in solvers]
        jobs = []
        for index, (solver, config) in enumerate(zip(solvers, configurations)):
            # run a configured solver
            if config is None:
                config = ""

            for instance_set in instance_sets:
                instance_path_list = [p.absolute() for p in instance_set.instance_paths]
                if subdir is None:
                    out_path = self.out_dir / f"{solver.name}_{instance_set.name}"
                else:
                    out_path = self.out_dir / subdir
                run = rcsh.call_solver(instance_path_list,
                                       solver,
                                       config=config,
                                       seed=index if use_seed else None,
                                       outdir=out_path,
                                       commandname=CommandName.VALIDATION,
                                       dependency=dependency,
                                       run_on=run_on)
                jobs.append(run)
        return jobs

    def retrieve_raw_results(self: Validator,
                             solver: Solver,
                             instance_sets: Instances | list[Instances],
                             subdir: Path = None,
                             log_dir: Path = None) -> None:
        """Checks the raw results of a given solver for a specific instance_set.

        Writes the raw results to a unified CSV file for the resolve/instance_set
        combination.

        Args:
            solver: The solver for which to check the raw result path
            instance_set: The set of instances for which to retrieve the results
            subdir: Subdir where the CSV is to be placed, passed to the append method.
            log_dir: The directory to search for log files. If none, defaults to
                the log directory of the Solver.
        """
        if isinstance(instance_sets, Instances):
            instance_sets = [instance_sets]
        if log_dir is None:
            log_dir = solver.raw_output_directory
        for res in log_dir.iterdir():
            if res.suffix != ".rawres":
                continue
            solver_args = get_solver_args(res.with_suffix(".log"))
            solver_args = ast.literal_eval(solver_args.strip())
            instance_path = Path(solver_args["instance"])
            # Remove default args
            if "config_path" in solver_args:
                # The actual solver configuration can be found elsewhere
                row_idx = int(solver_args["seed"])
                config_path = Path(solver_args["config_path"])
                if not config_path.exists():
                    config_path = log_dir / config_path
                config_str = config_path.open("r").readlines()[row_idx]
                solver_args = Solver.config_str_to_dict(config_str)
            else:
                for def_arg in ["instance", "solver_dir", "cutoff_time",
                                "seed", "specifics", "run_length"]:
                    if def_arg in solver_args:
                        del solver_args[def_arg]
            solver_args = str(solver_args).replace('"', "'")
            for instance_set in instance_sets:
                if instance_path.name in instance_set.instance_names:
                    out_dict = get_solver_output(
                        ["-o", res.name, "-v", res.with_suffix(".val").name],
                        "", log_dir)
                    self.append_entry_to_csv(solver.name,
                                            solver_args,
                                            instance_set,
                                            instance_path.name,
                                            out_dict["status"],
                                            out_dict["quality"],
                                            out_dict["runtime"],
                                            subdir=subdir)
                    res.unlink()
                    res.with_suffix(".val").unlink(missing_ok=True)
                    res.with_suffix(".log").unlink(missing_ok=True)

    def get_validation_results(self: Validator,
                               solver: Solver,
                               instance_set: Instances,
                               source_dir: Path = None,
                               subdir: Path = None,
                               config: str = None) -> list[list[str]]:
        """Query the results of the validation of solver on instance_set.

        Args:
            solver: Solver object
            instance_set: Instance set
            source_dir: Path where to look for any unprocessed output.
                By default, look in the solver's tmp dir.
            subdir: Path where to place the .csv file subdir. By default will be
                'self.outputdir/solver.name_instanceset.name/validation.csv'
            config: Path to the configuration if the solver was configured, None
                    otherwise
        Returns
            A list of row lists with string values
        """
        if source_dir is None:
            source_dir = self.out_dir / f"{solver.name}_{instance_set.name}"
        if any(x.suffix == ".rawres" for x in source_dir.iterdir()):
            self.retrieve_raw_results(
                solver, instance_set, subdir=subdir, log_dir=source_dir)
        if subdir is None:
            subdir = Path(f"{solver.name}_{instance_set.name}")
        csv_file = self.out_dir / subdir / "validation.csv"
        # We skip the header when returning results
        csv_data = [line for line in csv.reader(csv_file.open("r"))][1:]
        if config is not None:
            # We filter on the config string by subdict
            if isinstance(config, str):
                config_dict = Solver.config_str_to_dict(config)
            csv_data = [line for line in csv_data if
                        config_dict.items() == ast.literal_eval(line[1]).items()]
        return csv_data

    def append_entry_to_csv(self: Validator,
                            solver: str,
                            config_str: str,
                            instance_set: Instances,
                            instance: str,
                            status: str,
                            quality: str,
                            runtime: str,
                            subdir: Path = None) -> None:
        """Append a validation result as a row to a CSV file."""
        if subdir is None:
            subdir = Path(f"{solver}_{instance_set.name}")
        out_dir = self.out_dir / subdir
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
            writer.writerow((solver, config_str, instance_set.name, instance, status,
                             quality, runtime))
