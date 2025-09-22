"""Configurator classes to implement IRACE in Sparkle."""

from __future__ import annotations
import shutil
import subprocess
import random
from pathlib import Path

from sparkle.configurator.configurator import Configurator, ConfigurationScenario
from sparkle.solver import Solver
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.instance import InstanceSet, Instance_Set
from sparkle.types import SparkleObjective, resolve_objective

from runrunner import Runner, Run


class IRACE(Configurator):
    """Class for IRACE configurator."""

    configurator_path = Path(__file__).parent.resolve() / "IRACE"
    configurator_target = configurator_path / "irace_target_algorithm.py"

    full_name = "Iterated Racing for Automatic Algorithm Configuration"

    r_regex = r'\[\d+\]\s*["‘](?P<data>[^"`]+)["’]'

    def __init__(self: IRACE) -> None:
        """Initialize IRACE configurator."""
        self._version: str = None
        super().__init__(multi_objective_support=False)

    @property
    def name(self: IRACE) -> str:
        """Returns the name of the configurator."""
        return IRACE.__name__

    @property
    def version(self: IRACE) -> str:
        """Returns the version of the configurator."""
        if self._version is None:
            import re

            version_call = subprocess.run(
                ["Rscript", "-e", "packageVersion('irace')"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if version_call.returncode == 0:
                r_data = re.search(IRACE.r_regex, version_call.stdout.decode().strip())
                if r_data is not None and r_data.group("data") is not None:
                    self._version = r_data.group("data")
        return self._version

    @staticmethod
    def configurator_executable() -> Path:
        """Returns the path to the IRACE executable.

        # NOTE: For the base class this is a class property.
        However as it must be calculated in this case, it is a class method as calculated
        class properties do not exist in Python.

        Returns:
            Path to the executable if it can be found, else None.
        """
        if shutil.which("R") is None:
            return None  # Not installed
        r_call = subprocess.run(
            ["Rscript", "-e", "find.package('irace')"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if r_call.returncode != 0:
            return None  # Not installed
        import re

        r_path = re.search(IRACE.r_regex, r_call.stdout.decode().strip())
        if r_path is None or r_path.group("data") is None:
            return  # Could not find IRACE?
        path = Path(r_path.group("data"))
        return path / "bin" / "irace"

    @staticmethod
    def scenario_class() -> ConfigurationScenario:
        """Returns the IRACE scenario class."""
        return IRACEScenario

    @staticmethod
    def check_requirements(verbose: bool = False) -> bool:
        """Check that IRACE is installed."""
        import warnings

        if shutil.which("R") is None:
            if verbose:
                warnings.warn(
                    "IRACE requires R, but R is not installed. "
                    "Please ensure R is installed."
                )
            return False
        if not IRACE.configurator_executable():
            if verbose:
                warnings.warn(
                    "IRACE executable not found. Please ensure IRACE is installed "
                    f"in the expected Path ({IRACE.configurator_path})."
                )
            return False
        return True

    @staticmethod
    def download_requirements() -> None:
        """Download IRACE."""
        if shutil.which("R") is None:
            raise RuntimeError("IRACE requires R, but R is not installed.")
        # Ensure personal library exists, do not raise warnings
        subprocess.run(
            [
                "Rscript",
                "-e",
                "dir.create(path = Sys.getenv('R_LIBS_USER'), "
                "showWarnings = FALSE, recursive = TRUE)",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        install_irace = subprocess.run(
            [
                "Rscript",
                "-e",
                # Install R
                "install.packages('irace', "
                "lib=Sys.getenv('R_LIBS_USER'), "  # Install in user library
                "dependencies = TRUE, "  # Ensure dependencies are installed
                "repos='https://cloud.r-project.org')",
            ],  # Set source
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(f"{install_irace.stdout.decode()}\n\n{install_irace.stderr.decode()}")
        if install_irace.returncode != 0:
            import warnings

            warnings.warn(
                "IRACE had a non-zero return code during installation!\n\n"
                f"{install_irace.stdout.decode()}\n\n"
                f"{install_irace.stderr.decode()}"
            )

    def configure(
        self: IRACE,
        scenario: ConfigurationScenario,
        data_target: PerformanceDataFrame,
        validate_after: bool = True,
        sbatch_options: list[str] = [],
        slurm_prepend: str | list[str] | Path = None,
        num_parallel_jobs: int = None,
        base_dir: Path = None,
        run_on: Runner = Runner.SLURM,
    ) -> Run:
        """Start configuration job.

        Args:
            scenario: ConfigurationScenario to execute.
            data_target: PerformanceDataFrame where to store the found configurations
            validate_after: Whether to validate the configuration on the training set
                afterwards or not.
            sbatch_options: List of slurm batch options to use
            slurm_prepend: Slurm script to prepend to the sbatch
            num_parallel_jobs: The maximum number of jobs to run in parallel
            base_dir: The base_dir of RunRunner where the sbatch scripts will be placed
            run_on: On which platform to run the jobs. Default: Slurm.

        Returns:
            A RunRunner Run object.
        """
        scenario.create_scenario()
        configuration_ids = scenario.configuration_ids
        # Create command to call IRACE. Create plural based on number of runs
        seeds = [random.randint(0, 2**32 - 1) for _ in range(scenario.number_of_runs)]
        output_files = [
            scenario.results_directory.absolute() / f"output_{job_idx}.Rdata"
            for job_idx in configuration_ids
        ]
        cmds = [
            f"python3 {Configurator.configurator_cli_path.absolute()} "
            f"{IRACE.__name__} {output_path} {data_target.csv_filepath} "
            f"{scenario.scenario_file_path} {configuration_id} "
            f"{IRACE.configurator_executable().absolute()} "
            f"--scenario {scenario.scenario_file_path} "
            f"--log-file {output_path} "
            f"--seed {seed}"
            for seed, configuration_id, output_path in zip(
                seeds, configuration_ids, output_files
            )
        ]
        return super().configure(
            configuration_commands=cmds,
            data_target=data_target,
            output=output_files,
            scenario=scenario,
            configuration_ids=configuration_ids,
            sbatch_options=sbatch_options,
            slurm_prepend=slurm_prepend,
            validate_after=validate_after,
            num_parallel_jobs=num_parallel_jobs,
            base_dir=base_dir,
            run_on=run_on,
        )

    @staticmethod
    def organise_output(
        output_source: Path,
        output_target: Path,
        scenario: IRACEScenario,
        configuration_id: str,
    ) -> None | dict:
        """Method to restructure and clean up after a single configurator call."""
        get_config = subprocess.run(
            [
                "Rscript",
                "-e",
                'library("irace"); '
                f'load("{output_source}"); '
                "last <- length(iraceResults$iterationElites); "
                "id <- iraceResults$iterationElites[last]; "
                "print(getConfigurationById(iraceResults, ids = id))",
            ],
            capture_output=True,
        )
        r_table = get_config.stdout.decode()
        if get_config.returncode != 0 or r_table.strip() == "":
            raise RuntimeError(
                "Failed to get configuration from IRACE file "
                f"{output_source}:\n"
                f"{get_config.stdout.decode()}\n"
                f"{get_config.stderr.decode()}"
            )

        # Join the table header and content together
        header = ""
        content = ""
        for i, line in enumerate(r_table.splitlines()):
            if i & 1 == 0:  # Even lines are headers
                header += line
            else:  # Odd lines are parameter values
                # First element is the ID
                line = " ".join(line.split(" ")[1:])
                content += line
        # First header item is the ID
        header = [x for x in header.split(" ") if x != ""][1:]
        content = [x for x in content.split(" ") if x != ""][1:]
        configuration = ""
        for parameter, value in zip(header, content):
            if not parameter == ".PARENT." and value != "NA" and value != "<NA>":
                configuration += f"--{parameter} {value} "
        configuration = Solver.config_str_to_dict(configuration)
        return Configurator.save_configuration(
            scenario, configuration_id, configuration, output_target
        )

    def get_status_from_logs(self: Configurator) -> None:
        """Method to scan the log files of the configurator for warnings."""
        raise NotImplementedError


class IRACEScenario(ConfigurationScenario):
    """Class for IRACE scenario."""

    def __init__(
        self: IRACEScenario,
        solver: Solver,
        instance_set: InstanceSet,
        sparkle_objectives: list[SparkleObjective],
        number_of_runs: int,
        parent_directory: Path,
        solver_calls: int = None,
        solver_cutoff_time: int = None,
        max_time: int = None,
        budget_estimation: float = None,
        first_test: int = None,
        mu: int = None,
        max_iterations: int = None,
        feature_data: FeatureDataFrame = None,
        timestamp: str = None,
    ) -> None:
        """Initialize scenario paths and names.

        Args:
            solver: Solver that should be configured.
            instance_set: Instances object for the scenario.
            sparkle_objectives: SparkleObjectives used for each run of the configuration.
                Will be simplified to the first objective.
            number_of_runs: The number of configurator runs to perform
                for configuring the solver.
            parent_directory: Path where the scenario files will be placed.
            solver_calls: The number of times the solver is called for each
                configuration run. [MaxExperiments]
            solver_cutoff_time: The maximum time allowed for each individual run during
                configuration.
            max_time: The time budget (CPU) allocated for the sum of solver calls
                done by the configurator in seconds. [MaxTime]
            budget_estimation: Fraction (smaller than 1) of the budget used to estimate
                the mean computation time of a configuration. Only used when maxTime > 0.
                Default: Computed as cutoff_time / max_time. [BudgetEstimation]
            first_test: Specifies how many instances are evaluated before the first
                elimination test. IRACE Default: 5. [firstTest]
            mu: Parameter used to define the number of configurations sampled and
                evaluated at each iteration. IRACE Default: 5. [mu]
            max_iterations: Maximum number of iterations to be executed. Each iteration
                involves the generation of new configurations and the use of racing to
                select the best configurations. By default (with 0), irace calculates a
                minimum number of iterations as N^iter = ⌊2 + log2 N param⌋, where
                N^param is the number of non-fixed parameters to be tuned.
                Setting this parameter may make irace stop sooner than it should without
                using all the available budget. We recommend to use the default value.
            feature_data: FeatureDataFrame object with the feature data.
                Currently not supported by IRACE.
            timestamp: An optional timestamp for the directory name.
        """
        """
        Other possible arguments that are not added yet to Sparkle:
        --test-num-elites     Number of elite configurations returned by irace that
                                will be tested if test instances are provided.
                                Default: 1.
        --test-iteration-elites  Enable/disable testing the elite configurations
                                found at each iteration. Default: 0.
        --test-type           Statistical test used for elimination. The default
                                value selects t-test if capping is enabled or F-test,
                                otherwise. Valid values are: F-test (Friedman test),
                                t-test (pairwise t-tests with no correction),
                                t-test-bonferroni (t-test with Bonferroni's correction
                                for multiple comparisons), t-test-holm (t-test with
                                Holm's correction for multiple comparisons).
        --each-test           Number of instances evaluated between elimination
                                tests. Default: 1.
        --load-balancing      Enable/disable load-balancing when executing
                                experiments in parallel. Load-balancing makes better
                                use of computing resources, but increases
                                communication overhead. If this overhead is large,
                                disabling load-balancing may be faster. Default: 1.
        --mpi                 Enable/disable MPI. Use Rmpi to execute targetRunner
                                in parallel (parameter parallel is the number of
                                slaves). Default: 0.
        --batchmode           Specify how irace waits for jobs to finish when
                                targetRunner submits jobs to a batch cluster: sge,
                                pbs, torque, slurm or htcondor. targetRunner must
                                submit jobs to the cluster using, for example, qsub.
                                Default: 0.
        --digits              Maximum number of decimal places that are significant
                                for numerical (real) parameters. Default: 4.
        --soft-restart        Enable/disable the soft restart strategy that avoids
                                premature convergence of the probabilistic model.
                                Default: 1.
        --soft-restart-threshold  Soft restart threshold value for numerical
                                parameters. If NA, NULL or "", it is computed as
                                10^-digits.
        -e,--elitist             Enable/disable elitist irace. Default: 1.
        --elitist-new-instances  Number of instances added to the execution list
                                before previous instances in elitist irace. Default:
                                1.
        --elitist-limit       In elitist irace, maximum number per race of
                                elimination tests that do not eliminate a
                                configuration. Use 0 for no limit. Default: 2.
        --capping             Enable the use of adaptive capping, a technique
                                designed for minimizing the computation time of
                                configurations. This is only available when elitist is
                                active. Default: 0.
        --capping-type        Measure used to obtain the execution bound from the
                                performance of the elite configurations: median, mean,
                                worst, best. Default: median.
        --bound-type          Method to calculate the mean performance of elite
                                configurations: candidate or instance. Default:
                                candidate.
        --bound-max           Maximum execution bound for targetRunner. It must be
                                specified when capping is enabled. Default: 0.
        --bound-digits        Precision used for calculating the execution time. It
                                must be specified when capping is enabled. Default: 0.
        --bound-par           Penalization constant for timed out executions
                                (executions that reach boundMax execution time).
                                Default: 1.
        --bound-as-timeout    Replace the configuration cost of bounded executions
                                with boundMax. Default: 1.
        --postselection       Percentage of the configuration budget used to perform
                                a postselection race of the best configurations of
                                each iteration after the execution of irace. Default:
                                0.
        --iterations          Maximum number of iterations. Default: 0.
        --experiments-per-iteration  Number of runs of the target algorithm per
                                iteration. Default: 0.
        --min-survival        Minimum number of configurations needed to continue
                                the execution of each race (iteration). Default: 0.
        --num-configurations  Number of configurations to be sampled and evaluated
                                at each iteration. Default: 0.
        --confidence          Confidence level for the elimination test. Default:
                                0.95."""
        super().__init__(
            solver,
            instance_set,
            sparkle_objectives,
            number_of_runs,
            parent_directory,
            timestamp,
        )
        self.solver = solver
        self.instance_set = instance_set
        if sparkle_objectives is not None:
            self.sparkle_objective = sparkle_objectives[0]
        else:
            self.sparkle_objective = None

        if feature_data is not None:
            print("WARNING: Instance features currently not supported by IRACE.")

        self.solver_calls = solver_calls if solver_calls and solver_calls > 0 else None
        self.max_time = max_time if max_time and max_time > 0 else None
        self.solver_cutoff_time = solver_cutoff_time
        self.budget_estimation = budget_estimation
        self.first_test = first_test
        self.mu = mu
        self.max_iterations = max_iterations

    @property
    def instance_file_path(self: IRACEScenario) -> Path:
        """Return the path of the instance file."""
        if self.directory:
            return self.directory / f"{self.instance_set.name}.txt"
        return None

    @property
    def configurator(self: IRACEScenario) -> IRACE:
        """Return the type of configurator the scenario belongs to."""
        return IRACE

    def create_scenario(self: IRACEScenario) -> None:
        """Create scenario with solver and instances in the parent directory.

        This prepares all the necessary subdirectories related to configuration.
        Removes any existing directory if it overlaps with the scenario name.

        Args:
            parent_directory: Directory in which the scenario should be created.
        """
        super().create_scenario()
        with self.instance_file_path.open("w+") as file:
            for instance_path in self.instance_set._instance_paths:
                file.write(f"{instance_path.name}\n")
        self.create_scenario_file()

    def create_scenario_file(self: IRACEScenario) -> Path:
        """Create a file from the IRACE scenario.

        Returns:
            Path to the created file.
        """
        from sparkle.tools.parameters import PCSConvention

        solver_path = self.solver.directory.absolute()
        pcs_path = self.solver.get_pcs_file(port_type=PCSConvention.IRACE).absolute()
        with self.scenario_file_path.open("w") as file:
            file.write(
                f'execDir = "{self.directory.absolute()}"\n'
                'targetRunnerLauncher = "python3"\n'
                f'targetRunner = "{IRACE.configurator_target.absolute()}"\n'
                'targetCmdline = "{targetRunner} '
                f"{solver_path} {self.sparkle_objective} {self.solver_cutoff_time} "
                '{configurationID} {instanceID} {seed} {instance} {targetRunnerArgs}"\n'
                f"deterministic = {1 if self.solver.deterministic else 0}\n"
                f'parameterFile = "{pcs_path.absolute()}"\n'
                f'trainInstancesDir = "{self.instance_set.directory.absolute()}"\n'
                f'trainInstancesFile = "{self.instance_file_path.absolute()}"\n'
                "debugLevel = 1\n"  # The verbosity level of IRACE
            )
            if self.solver_calls is not None:
                file.write(f"maxExperiments = {self.solver_calls}\n")
            elif self.max_time is not None:
                file.write(f"maxTime = {self.max_time}\n")
            if self.solver_calls is not None and self.max_time is not None:
                print(
                    "WARNING: Both solver calls and max time specified for scenario. "
                    "This is not supported by IRACE, defaulting to solver calls."
                )
            elif self.solver_calls is None and self.max_time is None:
                print(
                    "WARNING: Neither solver calls nor max time specified. "
                    "Either budget is required for the IRACE scenario."
                )
            if self.max_time is not None and self.budget_estimation is None:
                # Auto Estimate
                if self.solver_cutoff_time < self.max_time:
                    self.budget_estimation = self.solver_cutoff_time / self.max_time
                    file.write(f"budgetEstimation = {self.budget_estimation}\n")
            if self.first_test is not None:
                file.write(f"firstTest = {self.first_test}\n")
            if self.mu is not None:
                file.write(f"mu = {self.mu}\n")
            if self.max_iterations is not None:
                file.write(f"nbIterations = {self.max_iterations}\n")
        print("Verifying contents of IRACE scenario file and testing solver call...")
        check_file = subprocess.run(
            [
                f"{IRACE.configurator_executable().absolute()}",
                "-s",
                f"{self.scenario_file_path.absolute()}",
                "--check",
            ],
            capture_output=True,
        )
        if check_file.returncode != 0:
            stdout_msg = "\n".join(
                [
                    line
                    for line in check_file.stdout.decode().splitlines()
                    if not line.startswith("#")
                ]
            )
            print(
                "An error occured in the IRACE scenario file:\n",
                self.scenario_file_path.open("r").read(),
                stdout_msg,
                "\n",
                check_file.stderr.decode(),
            )
            return None
        print("IRACE scenario file is valid.")
        return self.scenario_file_path

    def serialise(self: IRACEScenario) -> dict:
        """Serialize the IRACE scenario."""
        return {
            "number_of_runs": self.number_of_runs,
            "solver_calls": self.solver_calls,
            "max_time": self.max_time,
            "solver_cutoff_time": self.solver_cutoff_time,
            "budget_estimation": self.budget_estimation,
            "first_test": self.first_test,
            "mu": self.mu,
            "max_iterations": self.max_iterations,
        }

    @staticmethod
    def from_file(scenario_file: Path) -> IRACEScenario:
        """Reads scenario file and initalises IRACEScenario."""
        scenario_dict = {
            keyvalue[0]: keyvalue[1]
            for keyvalue in (
                line.split(" = ", maxsplit=1)
                for line in scenario_file.open().readlines()
                if line.strip() != ""
            )
        }
        _, solver_path, objective, cutoff, _, _, _, _, _ = scenario_dict.pop(
            "targetCmdline"
        ).split(" ")
        scenario_dict["sparkle_objectives"] = [resolve_objective(objective)]
        scenario_dict["solver_cutoff_time"] = int(cutoff)
        scenario_dict["parent_directory"] = scenario_file.parent.parent
        scenario_dict["number_of_runs"] = len(
            [p for p in (scenario_file.parent / "results").iterdir()]
        )
        scenario_dict.pop("targetRunner")
        scenario_dict.pop("execDir")
        scenario_dict.pop("targetRunnerLauncher")
        scenario_dict.pop("deterministic")
        scenario_dict.pop("parameterFile")
        scenario_dict.pop("debugLevel")
        instance_set_path = Path(
            scenario_dict.pop("trainInstancesDir").strip().strip('"')
        )
        instance_set = Instance_Set(instance_set_path)
        solver_path = Path(solver_path.strip())
        if solver_path.is_absolute():
            solver_path = solver_path.relative_to(Path.cwd())
        solver = Solver(solver_path)
        scenario_dict.pop("trainInstancesFile")
        # Replace keys with scenario variable names
        if "budgetEstimation" in scenario_dict:
            scenario_dict["budget_estimation"] = float(
                scenario_dict.pop(("budgetEstimation"))
            )
        if "firstTest" in scenario_dict:
            scenario_dict["first_test"] = int(scenario_dict.pop("firstTest"))
        if "mu" in scenario_dict:
            scenario_dict["mu"] = int(scenario_dict.pop("mu"))
        if "nbIterations" in scenario_dict:
            scenario_dict["max_iterations"] = int(scenario_dict.pop("nbIterations"))
        if "maxExperiments" in scenario_dict:
            scenario_dict["solver_calls"] = int(scenario_dict.pop("maxExperiments"))
        if "maxTime" in scenario_dict:
            scenario_dict["max_time"] = int(scenario_dict.pop("maxTime"))

        timestamp = scenario_file.parent.name.split("_")[-1]
        return IRACEScenario(solver, instance_set, **scenario_dict, timestamp=timestamp)
