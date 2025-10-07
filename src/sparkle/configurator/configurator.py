"""Configurator class to use different algorithm configurators."""

from __future__ import annotations
import re
import shutil
import decimal
from pathlib import Path
from datetime import datetime
from typing import Optional
import random

import runrunner as rrr
from runrunner import Runner, Run

from sparkle.solver import Solver
from sparkle.instance import InstanceSet, Instance_Set
from sparkle.structures import PerformanceDataFrame
from sparkle.types import SparkleObjective


class Configurator:
    """Abstact class to use different configurators like SMAC."""

    configurator_cli_path = Path(__file__).parent.resolve() / "configurator_cli.py"

    full_name = "Configurator Abstract Class"
    version = "NaN"

    def __init__(self: Configurator, multi_objective_support: bool = False) -> None:
        """Initialize Configurator.

        Args:
            multi_objective_support: Whether the configurator supports
                multi objective optimization for solvers.
        """
        self.multiobjective = multi_objective_support

    @property
    def name(self: Configurator) -> str:
        """Return the name of the configurator."""
        return self.__class__.__name__

    @staticmethod
    def scenario_class() -> ConfigurationScenario:
        """Return the scenario class of the configurator."""
        return ConfigurationScenario

    @staticmethod
    def check_requirements(verbose: bool = False) -> bool:
        """Check if the configurator is installed."""
        raise NotImplementedError

    @staticmethod
    def download_requirements() -> None:
        """Download the configurator."""
        raise NotImplementedError

    def configure(
        self: Configurator,
        configuration_commands: list[str],
        data_target: PerformanceDataFrame,
        output: Path,
        scenario: ConfigurationScenario,
        configuration_ids: list[str] = None,
        validate_after: bool = True,
        sbatch_options: list[str] = None,
        slurm_prepend: str | list[str] | Path = None,
        num_parallel_jobs: int = None,
        base_dir: Path = None,
        run_on: Runner = Runner.SLURM,
    ) -> Run:
        """Start configuration job.

        This method is shared by the configurators and should be called by the
        implementation/subclass of the configurator.

        Args:
            configuration_commands: List of configurator commands to execute
            data_target: Performance data to store the results.
            output: Output directory.
            scenario: ConfigurationScenario to execute.
            configuration_ids: List of configuration ids that are to be created
            validate_after: Whether the configurations should be validated
            sbatch_options: List of slurm batch options to use
            slurm_prepend: Slurm script to prepend to the sbatch
            num_parallel_jobs: The maximum number of jobs to run in parallel
            base_dir: The base_dir of RunRunner where the sbatch scripts will be placed
            run_on: On which platform to run the jobs. Default: Slurm.

        Returns:
            A RunRunner Run object.
        """
        if not self.check_requirements(verbose=True):
            raise RuntimeError(
                f"{self.name} is not installed. Please install {self.name} and try again."
            )
        # Add the configuration IDs to the dataframe with empty configurations
        data_target.add_configuration(
            str(scenario.solver.directory),
            configuration_ids,
            [{}] * len(configuration_ids),
        )
        data_target.save_csv()
        # Submit the configuration job
        runs = [
            rrr.add_to_queue(
                runner=run_on,
                cmd=configuration_commands,
                name=f"{self.name}: {scenario.solver.name} on {scenario.instance_set.name}",
                base_dir=base_dir,
                output_path=output,
                parallel_jobs=num_parallel_jobs,
                sbatch_options=sbatch_options,
                prepend=slurm_prepend,
            )
        ]

        if validate_after:
            validate = scenario.solver.run_performance_dataframe(
                scenario.instance_set,
                config_ids=configuration_ids,
                performance_dataframe=data_target,
                cutoff_time=scenario.solver_cutoff_time,
                sbatch_options=sbatch_options,
                slurm_prepend=slurm_prepend,
                log_dir=scenario.validation,
                base_dir=base_dir,
                dependencies=runs,
                job_name=f"{self.name}: Validating {len(configuration_ids)} "
                f"{scenario.solver.name} Configurations on "
                f"{scenario.instance_set.name}",
                run_on=run_on,
            )
            runs.append(validate)

        if run_on == Runner.LOCAL:
            print(f"[{self.name}] Running {len(runs)} jobs locally...")
            for run in runs:
                run.wait()
            print(f"[{self.name}] Finished running {len(runs)} jobs locally.")
        return runs

    @staticmethod
    def organise_output(
        output_source: Path,
        output_target: Path,
        scenario: ConfigurationScenario,
        configuration_id: str,
    ) -> None | str:
        """Method to restructure and clean up after a single configurator call.

        Args:
            output_source: Path to the output file of the configurator run.
            output_target: Path to the Performance DataFrame to store result.
            scenario: ConfigurationScenario of the configuration.
            configuration_id: ID (of the run) of the configuration.
        """
        raise NotImplementedError

    @staticmethod
    def save_configuration(
        scenario: ConfigurationScenario,
        configuration_id: str,
        configuration: dict,
        output_target: Path,
    ) -> dict | None:
        """Method to save a configuration to a file.

        If the output_target is None, return the configuration.

        Args:
            scenario: ConfigurationScenario of the configuration. Should be removed.
            configuration_id: ID (of the run) of the configuration.
            configuration: Configuration to save.
            output_target: Path to the Performance DataFrame to store result.
        """
        if output_target is None or not output_target.exists():
            return configuration
        # Save result to Performance DataFrame
        from filelock import FileLock

        lock = FileLock(f"{output_target}.lock")
        with lock.acquire(timeout=600):
            performance_data = PerformanceDataFrame(output_target)
            # Resolve absolute path to Solver column
            solver = [
                s
                for s in performance_data.solvers
                if Path(s).name == scenario.solver.name
            ][0]
            # Update the configuration ID by adding the configuration
            performance_data.add_configuration(
                solver=solver,
                configuration_id=configuration_id,
                configuration=configuration,
            )
            performance_data.save_csv()

    def get_status_from_logs(self: Configurator) -> None:
        """Method to scan the log files of the configurator for warnings."""
        raise NotImplementedError


class ConfigurationScenario:
    """Template class to handle a configuration scenarios."""

    def __init__(
        self: ConfigurationScenario,
        solver: Solver,
        instance_set: InstanceSet,
        sparkle_objectives: list[SparkleObjective],
        number_of_runs: int,
        parent_directory: Path,
        timestamp: str = None,
    ) -> None:
        """Initialize scenario paths and names.

        Args:
            solver: Solver that should be configured.
            instance_set: Instances object for the scenario.
            sparkle_objectives: Sparkle Objectives to optimize.
            number_of_runs: The number of configurator runs to perform.
            parent_directory: Directory in which the scenario should be placed.
            timestamp: The timestamp of the scenario directory/file creation.
                Only set when read from file, otherwise generated at time of creation.
        """
        self.solver = solver
        self.instance_set = instance_set
        self.sparkle_objectives = sparkle_objectives
        self.number_of_runs = number_of_runs
        self.parent_directory = parent_directory
        self._timestamp = timestamp
        self._ablation_scenario: AblationScenario = None

    @property
    def configurator(self: ConfigurationScenario) -> Configurator:
        """Return the type of configurator the scenario belongs to."""
        return Configurator

    @property
    def name(self: ConfigurationScenario) -> str:
        """Return the name of the scenario."""
        return f"{self.solver.name}_{self.instance_set.name}_{self.timestamp}"

    @property
    def timestamp(self: ConfigurationScenario) -> str:
        """Return the timestamp."""
        return self._timestamp

    @property
    def directory(self: ConfigurationScenario) -> Path:
        """Return the path of the scenario directory."""
        return None if self.timestamp is None else self.parent_directory / self.name

    @property
    def scenario_file_path(self: ConfigurationScenario) -> Path:
        """Return the path of the scenario file."""
        if self.directory:
            return self.directory / "scenario.txt"
        return None

    @property
    def validation(self: ConfigurationScenario) -> Path:
        """Return the path of the validation directory."""
        if self.directory:
            return self.directory / "validation"
        return None

    @property
    def tmp(self: ConfigurationScenario) -> Path:
        """Return the path of the tmp directory."""
        if self.directory:
            return self.directory / "tmp"
        return None

    @property
    def results_directory(self: ConfigurationScenario) -> Path:
        """Return the path of the results directory."""
        if self.directory:
            return self.directory / "results"
        return None

    @property
    def configuration_ids(self: ConfigurationScenario) -> list[str]:
        """Return the IDs of the configurations for the scenario.

        Only exists after the scenario has been created.

        Returns:
            List of configuration IDs, one for each run.
        """
        return [
            f"{self.configurator.__name__}_{self.timestamp}_{i}"
            for i in range(self.number_of_runs)
        ]

    @property
    def ablation_scenario(self: ConfigurationScenario) -> AblationScenario:
        """Return the ablation scenario for the scenario if it exists."""
        if self._ablation_scenario is not None:
            return self._ablation_scenario
        for scenario in self.directory.glob("*/ablation_config.txt"):
            self._ablation_scenario = AblationScenario.from_file(scenario, self)
            return self._ablation_scenario
        return None

    def create_scenario(self: ConfigurationScenario) -> None:
        """Create scenario with solver and instances in the parent directory.

        This prepares all the necessary subdirectories related to configuration.

        Args:
            parent_directory: Directory in which the scenario should be created.
        """
        self._timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        # Prepare scenario directory
        shutil.rmtree(self.directory, ignore_errors=True)
        self.directory.mkdir(parents=True)
        # Create empty directories as needed
        self.tmp.mkdir(exist_ok=True)
        self.validation.mkdir(exist_ok=True)
        self.results_directory.mkdir(exist_ok=True)

    def create_scenario_file(self: ConfigurationScenario) -> Path:
        """Create a file with the configuration scenario."""
        raise NotImplementedError

    def serialise(self: ConfigurationScenario) -> dict:
        """Serialize the configuration scenario."""
        raise NotImplementedError

    @classmethod
    def find_scenario(
        cls: ConfigurationScenario,
        directory: Path,
        solver: Solver,
        instance_set: InstanceSet,
        timestamp: str = None,
    ) -> ConfigurationScenario:
        """Resolve a scenario from a directory and Solver / Training set."""
        if timestamp is None:
            # Get the newest timestamp
            timestamp_list: list[datetime] = []
            for subdir in directory.iterdir():
                if subdir.is_dir():
                    dir_timestamp = subdir.name.split("_")[-1]
                    try:
                        dir_timestamp = datetime.strptime(dir_timestamp, "%Y%m%d-%H%M")
                        timestamp_list.append(dir_timestamp)
                    except ValueError:
                        continue

            if timestamp_list == []:
                return None
            timestamp = max(timestamp_list).strftime("%Y%m%d-%H%M")

        scenario_name = f"{solver.name}_{instance_set.name}_{timestamp}"
        path = directory / f"{scenario_name}" / "scenario.txt"
        if not path.exists():
            return None
        return cls.from_file(path)

    @staticmethod
    def from_file(scenario_file: Path) -> ConfigurationScenario:
        """Reads scenario file and initalises ConfigurationScenario."""
        raise NotImplementedError


class AblationScenario:
    """Class for ablation analysis."""

    # We use the SMAC2 target algorithm for solver output handling
    configurator_target = (
        Path(__file__).parent.resolve()
        / "implementations"
        / "SMAC2"
        / "smac2_target_algorithm.py"
    )

    ablation_dir = Path(__file__).parent / "implementations" / "ablationAnalysis-0.9.4"
    ablation_executable = ablation_dir / "ablationAnalysis"
    ablation_validation_executable = ablation_dir / "ablationValidation"

    def __init__(
        self: AblationScenario,
        configuration_scenario: ConfigurationScenario,
        test_set: InstanceSet,
        cutoff_length: str,
        concurrent_clis: int,
        best_configuration: dict,
        ablation_racing: bool = False,
    ) -> None:
        """Initialize ablation scenario.

        Args:
            solver: Solver object
            configuration_scenario: Configuration scenario
            train_set: The training instance
            test_set: The test instance
            cutoff_length: The cutoff length for ablation analysis
            concurrent_clis: The maximum number of concurrent jobs on a single node
            best_configuration: The configuration to ablate from.
            ablation_racing: Whether to use ablation racing
        """
        self.config_scenario = configuration_scenario
        self.solver = configuration_scenario.solver
        self.train_set = configuration_scenario.instance_set
        self.test_set = test_set
        self.cutoff_time = configuration_scenario.solver_cutoff_time
        self.cutoff_length = cutoff_length
        self.concurrent_clis = concurrent_clis
        self.best_configuration = best_configuration
        self.ablation_racing = ablation_racing
        self.scenario_name = f"ablation_{configuration_scenario.name}"
        self._table_file: Optional[Path] = None
        if self.test_set is not None:
            self.scenario_name += f"_{self.test_set.name}"

    @property
    def scenario_dir(self: AblationScenario) -> Path:
        """Return the path of the scenario directory."""
        if self.config_scenario.directory:
            return self.config_scenario.directory / self.scenario_name
        return None

    @property
    def tmp_dir(self: AblationScenario) -> Path:
        """Return the path of the tmp directory."""
        if self.scenario_dir:
            return self.scenario_dir / "tmp"
        return None

    @property
    def validation_dir(self: AblationScenario) -> Path:
        """Return the path of the validation directory."""
        if self.scenario_dir:
            return self.scenario_dir / "validation"
        return None

    @property
    def validation_dir_tmp(self: AblationScenario) -> Path:
        """Return the path of the validation tmp directory."""
        if self.validation_dir:
            return self.validation_dir / "tmp"
        return None

    @property
    def table_file(self: AblationScenario) -> Path:
        """Return the path of the table file."""
        if self._table_file:
            return self._table_file
        elif self.validation_dir:
            return self.validation_dir / "log" / "ablation-validation-run1234.txt"
        else:
            return None

    @staticmethod
    def check_requirements(verbose: bool = False) -> bool:
        """Check if Ablation Analysis is installed."""
        import warnings

        if no_java := shutil.which("java") is None:
            if verbose:
                warnings.warn(
                    "AblationAnalysis requires Java 1.8.0_402, but Java is not installed"
                    ". Please ensure Java is installed."
                )
        if no_exec := not AblationScenario.ablation_executable.exists():
            if verbose:
                warnings.warn(
                    "AblationAnalysis executable not found. Please ensure Ablation"
                    " Analysis is installed in the expected Path "
                    f"({AblationScenario.ablation_executable})."
                )
        if no_validation := not AblationScenario.ablation_validation_executable.exists():
            if verbose:
                warnings.warn(
                    "AblationAnalysis Validation executable not found. Please ensure "
                    "Ablation Analysis is installed in the expected Path "
                    f"({AblationScenario.ablation_validation_executable})."
                )
        return not (no_java or no_exec or no_validation)

    @staticmethod
    def download_requirements(
        ablation_url: str = "https://github.com/ADA-research/Sparkle/raw/refs/heads/development"
        "/Resources/Other/ablationAnalysis-0.9.4.zip",
    ) -> None:
        """Download Ablation Analysis executable."""
        if AblationScenario.ablation_executable.exists():
            return  # Already installed
        from urllib.request import urlopen
        import zipfile
        import io

        AblationScenario.ablation_dir.mkdir(parents=True, exist_ok=True)
        r = urlopen(ablation_url, timeout=60)
        z = zipfile.ZipFile(io.BytesIO(r.read()))
        z.extractall(AblationScenario.ablation_dir)
        # Ensure execution rights
        AblationScenario.ablation_executable.chmod(0o755)
        AblationScenario.ablation_validation_executable.chmod(0o755)

    def create_configuration_file(self: AblationScenario) -> Path:
        """Create a configuration file for ablation analysis.

        Returns:
            Path to the created configuration file.
        """
        objective = self.config_scenario.sparkle_objectives[0]
        pcs = self.solver.get_configuration_space()
        parameter_names = [p.name for p in pcs.values()]
        # We need to remove any redundant keys that are not in PCS
        best_configuration = self.best_configuration.copy()
        removable_keys = [
            key for key in best_configuration if key not in parameter_names
        ]
        for key in removable_keys:
            del best_configuration[key]
        opt_config_str = " ".join([f"-{k} {v}" for k, v in best_configuration.items()])
        # We need to check which params are missing and supplement with default values
        for p in list(pcs.values()):
            if p.name not in opt_config_str:
                opt_config_str += f" -{p.name} {p.default_value}"

        # Ablation cannot deal with E scientific notation in floats
        ctx = decimal.Context(prec=16)
        for config in opt_config_str.split(" -"):
            _, value = config.strip().split(" ")
            if "e" in value.lower():
                value = value.strip("'")
                float_value = float(value.lower())
                formatted = format(ctx.create_decimal(float_value), "f")
                opt_config_str = opt_config_str.replace(value, formatted)

        smac_run_obj = "RUNTIME" if objective.time else "QUALITY"
        objective_str = "MEAN10" if objective.time else "MEAN"
        pcs_file_path = f"{self.config_scenario.solver.pcs_file.absolute()}"

        # Create config file
        config_file = self.scenario_dir / "ablation_config.txt"
        config = (
            f'algo = "{AblationScenario.configurator_target.absolute()} '
            f"{self.config_scenario.solver.directory.absolute()} "
            f'{self.tmp_dir.absolute()} {objective}"\n'
            f"execdir = {self.tmp_dir.absolute()}\n"
            "experimentDir = ./\n"
            f"deterministic = {1 if self.solver.deterministic else 0}\n"
            f"run_obj = {smac_run_obj}\n"
            f"overall_obj = {objective_str}\n"
            f"cutoffTime = {self.cutoff_time}\n"
            f"cutoff_length = {self.cutoff_length}\n"
            f"cli-cores = {self.concurrent_clis}\n"
            f"useRacing = {self.ablation_racing}\n"
            f"seed = {random.randint(0, 2**32 - 1)}\n"
            f"paramfile = {pcs_file_path}\n"
            "instance_file = instances_train.txt\n"
            "test_instance_file = instances_test.txt\n"
            "sourceConfiguration = DEFAULT\n"
            f'targetConfiguration = "{opt_config_str}"'
        )
        config_file.open("w").write(config)
        # Write config to validation directory
        conf_valid = config.replace(
            f"execdir = {self.tmp_dir.absolute()}\n",
            f"execdir = {self.validation_dir_tmp.absolute()}\n",
        )
        (self.validation_dir / config_file.name).open("w").write(conf_valid)
        return self.validation_dir / config_file.name

    def create_instance_file(self: AblationScenario, test: bool = False) -> Path:
        """Create an instance file for ablation analysis."""
        file_suffix = "_train.txt"
        instance_set = self.train_set
        if test:
            file_suffix = "_test.txt"
            instance_set = self.test_set if self.test_set is not None else self.train_set
        # We give the Ablation script the paths of the instances
        file_instance = self.scenario_dir / f"instances{file_suffix}"
        with file_instance.open("w") as fh:
            for instance in instance_set._instance_paths:
                # We need to unpack the multi instance file paths in quotes
                if isinstance(instance, list):
                    joined_instances = " ".join(
                        [str(file.absolute()) for file in instance]
                    )
                    fh.write(f"{joined_instances}\n")
                else:
                    fh.write(f"{instance.absolute()}\n")
        # Copy to validation directory
        shutil.copyfile(file_instance, self.validation_dir / file_instance.name)
        return file_instance

    def create_scenario(self: AblationScenario, override_dirs: bool = False) -> None:
        """Create scenario directory and files."""
        if self.scenario_dir.exists():
            print("WARNING: Found existing ablation scenario.")
            if not override_dirs:
                print("Set override to True to overwrite existing scenario.")
                return
            print("Overwriting existing scenario...")
            shutil.rmtree(self.scenario_dir)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.validation_dir_tmp.mkdir(parents=True, exist_ok=True)
        self.create_instance_file()
        self.create_instance_file(test=True)
        self.create_configuration_file()

    def check_for_ablation(self: AblationScenario) -> bool:
        """Checks if ablation has terminated successfully."""
        if not self.table_file.is_file():
            return False
        # First line in the table file should be "Ablation analysis validation complete."
        table_line = self.table_file.open().readline().strip()
        return table_line == "Ablation analysis validation complete."

    def read_ablation_table(self: AblationScenario) -> list[list[str]]:
        """Read from ablation table of a scenario."""
        if not self.check_for_ablation():
            # No ablation table exists for this solver-instance pair
            return []
        results = [
            [
                "Round",
                "Flipped parameter",
                "Source value",
                "Target value",
                "Validation result",
            ]
        ]

        for line in self.table_file.open().readlines():
            # Pre-process lines from the ablation file and add to the results dictionary.
            # Sometimes ablation rounds switch multiple parameters at once.
            # EXAMPLE: 2 EDR, EDRalpha   0, 0.1   1, 0.1013241633106732 486.31691
            # To split the row correctly, we remove the space before the comma separated
            # parameters and add it back.
            # T.S. 30-01-2024: the results object is a nested list not dictionary?
            values = re.sub(r"\s+", " ", line.strip())
            values = re.sub(r", ", ",", values)
            values = [val.replace(",", ", ") for val in values.split(" ")]
            if len(values) == 5:
                results.append(values)
        return results

    def submit_ablation(
        self: AblationScenario,
        log_dir: Path,
        sbatch_options: list[str] = [],
        slurm_prepend: str | list[str] | Path = None,
        run_on: Runner = Runner.SLURM,
    ) -> list[Run]:
        """Submit an ablation job.

        Args:
            log_dir: Directory to store job logs
            sbatch_options: Options to pass to sbatch
            slurm_prepend: Script to prepend to sbatch script
            run_on: Determines to which RunRunner queue the job is added

        Returns:
            A  list of Run objects. Empty when running locally.
        """
        if not self.check_requirements(verbose=True):
            raise RuntimeError(
                "Ablation Analysis is not available. Please ensure Java and Ablation "
                "Analysis is installed and try again."
            )
        # 1. submit the ablation to the runrunner queue
        cmd = (
            f"{AblationScenario.ablation_executable.absolute()} "
            "--optionFile ablation_config.txt"
        )
        srun_options = ["-N1", "-n1", f"-c{self.concurrent_clis}"]
        sbatch_options += [f"--cpus-per-task={self.concurrent_clis}"]
        run_ablation = rrr.add_to_queue(
            runner=run_on,
            cmd=cmd,
            name=f"Ablation analysis: {self.solver.name} on {self.train_set.name}",
            base_dir=log_dir,
            path=self.scenario_dir,
            sbatch_options=sbatch_options,
            srun_options=srun_options,
            prepend=slurm_prepend,
        )

        runs = []
        if run_on == Runner.LOCAL:
            run_ablation.wait()
        runs.append(run_ablation)

        # 2. Run ablation validation run if we have a test set to run on
        if self.test_set is not None:
            # Validation dir should have a copy of all needed files, except for the
            # output of the ablation run, which is stored in ablation-run[seed].txt
            cmd = (
                f"{AblationScenario.ablation_validation_executable.absolute()} "
                "--optionFile ablation_config.txt "
                "--ablationLogFile ../log/ablation-run1234.txt"
            )

            run_ablation_validation = rrr.add_to_queue(
                runner=run_on,
                cmd=cmd,
                name=f"Ablation validation: Test set {self.test_set.name}",
                path=self.validation_dir,
                base_dir=log_dir,
                dependencies=run_ablation,
                sbatch_options=sbatch_options,
                prepend=slurm_prepend,
            )

            if run_on == Runner.LOCAL:
                run_ablation_validation.wait()
            runs.append(run_ablation_validation)
        return runs

    @staticmethod
    def from_file(
        path: Path, config_scenario: ConfigurationScenario
    ) -> AblationScenario:
        """Reads scenario file and initalises AblationScenario."""
        variables = {}
        for line in path.open().readlines():
            if line.strip() == "":
                continue
            key, value = line.strip().split(" = ", maxsplit=1)
            variables[key] = value
        best_conf = {}
        for keyvalue in variables["targetConfiguration"].replace('"', "").split("-"):
            keyvalue = keyvalue.strip()
            if keyvalue:
                key, value = keyvalue.strip().split(" ", maxsplit=1)
                best_conf[key] = value
        test_set = None
        if (path.parent / "instances_test.txt").exists():
            test_path = (path.parent / "instances_test.txt").open().readline().strip()
            test_path = Path(test_path).parent
            if test_path != config_scenario.instance_set.directory:
                test_set = Instance_Set(test_path)
        return AblationScenario(
            config_scenario,
            test_set,
            variables["cutoff_length"],
            int(variables["cli-cores"]),
            best_conf,
            ablation_racing=bool(variables["useRacing"]),
        )
