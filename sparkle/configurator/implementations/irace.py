"""Configurator classes to implement IRACE in Sparkle."""
from __future__ import annotations
from pathlib import Path

import pandas as pd

from sparkle.configurator.configurator import Configurator, ConfigurationScenario
from sparkle.solver import Solver, Validator
from sparkle.instance import InstanceSet
from sparkle.types import SparkleObjective

# import runrunner as rrr
from runrunner import Runner, Run


class IRACE(Configurator):
    """Class for IRACE configurator."""
    configurator_path = Path(__file__).parent.parent.parent.resolve() /\
        "Components/irace-v3.5"
    configurator_package = configurator_path / "irace_3.5.tar.gz"
    configurator_executable = configurator_path / "irace" / "bin" / "irace"
    configurator_ablation_executable = configurator_path / "irace" / "bin" / "ablation"
    target_algorithm = configurator_path / "irace_target_algorithm.py"

    def __init__(self: Configurator, validator: Validator, output_path: Path,
                 objectives: list[SparkleObjective], base_dir: Path, tmp_path: Path,
                 ) -> None:
        """Initialize IRACE configurator."""
        output_path = output_path / IRACE.__name__
        output_path.mkdir(parents=True, exist_ok=True)
        super().__init__(validator, output_path,
                         objectives, base_dir, tmp_path, multi_objective_support=False)

    def __str__(self: IRACE) -> str:
        """Returns the name of the configurator."""
        return IRACE.__name__

    @property
    def scenario(self: Configurator) -> ConfigurationScenario:
        """Returns the IRACE scenario class."""
        return IRACEScenario

    def configure(self: Configurator,
                  scenario: ConfigurationScenario,
                  validate_after: bool = True,
                  sbatch_options: list[str] = [],
                  num_parallel_jobs: int = None,
                  base_dir: Path = None,
                  run_on: Runner = Runner.SLURM) -> Run:
        """Start configuration job.

        Args:
            scenario: ConfigurationScenario to execute.
            validate_after: Whether to validate the configuration on the training set
                afterwards or not.
            sbatch_options: List of slurm batch options to use
            num_parallel_jobs: The maximum number of jobs to run in parallel
            base_dir: The base_dir of RunRunner where the sbatch scripts will be placed
            run_on: On which platform to run the jobs. Default: Slurm.

        Returns:
            A RunRunner Run object.
        """
        # TODO: Create scenario
        self.scenario = scenario
        scenario_path = self.scenario.create_scenario(parent_directory=self.output_path)
        output_csv = self.scenario.validation / "configurations.csv"
        output_csv.parent.mkdir(exist_ok=True, parents=True)
        # TODO Create command to call IRACE. Create plural ? based on number of runs var
        # NOTE: Possible arguments listed below.
        # Some are also placed in scenario file so can be omitted ?, marked with [sf]
        # Some are not relevant and should be ignored [i]
        # Should be hard defined by Sparkle to work [h]
        """
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
        --first-test          Number of instances evaluated before the first
                                elimination test. It must be a multiple of eachTest.
                                Default: 5.
        --each-test           Number of instances evaluated between elimination
                                tests. Default: 1.
        --max-experiments     Maximum number of runs (invocations of targetRunner)
                                that will be performed. It determines the maximum
                                budget of experiments for the tuning. Default: 0.
        --budget-estimation   Fraction (smaller than 1) of the budget used to
                                estimate the mean computation time of a configuration.
                                Only used when maxTime > 0 Default: 0.02.
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
        --mu                  Parameter used to define the number of configurations
                                sampled and evaluated at each iteration. Default: 5.
        --confidence          Confidence level for the elimination test. Default:
                                0.95."""
        output = []  # List of output files for each seed
        cmds = [f"python3 {Configurator.configurator_cli_path.absolute()} "
                f"{IRACE.__name__} {output[seed]} {output_csv.absolute()} "
                f"{IRACE.configurator_executable.absolute()} "
                f"--scenario-file {scenario_path.absolute()} "
                f"--parallel {num_parallel_jobs} "
                for seed in range(self.scenario.number_of_runs)]
        return cmds
        raise NotImplementedError

    def get_optimal_configuration(self: Configurator,
                                  solver: Solver,
                                  instance_set: InstanceSet,
                                  objective: SparkleObjective) -> tuple[float, str]:
        """Returns the optimal configuration string for a solver on an instance set."""
        raise NotImplementedError

    @staticmethod
    def organise_output(output_source: Path, output_target: Path) -> None | str:
        """Method to restructure and clean up after a single configurator call."""
        raise NotImplementedError

    def set_scenario_dirs(self: Configurator,
                          solver: Solver, instance_set: InstanceSet) -> None:
        """Patching method to allow the rebuilding of configuration scenario."""
        raise NotImplementedError

    def get_status_from_logs(self: Configurator) -> None:
        """Method to scan the log files of the configurator for warnings."""
        raise NotImplementedError


class IRACEScenario(ConfigurationScenario):
    """Class for IRACE scenario."""

    def __init__(self: ConfigurationScenario, solver: Solver,
                 instance_set: InstanceSet, number_of_runs: int = None,
                 solver_calls: int = None, cpu_time: int = None,
                 wallclock_time: int = None, cutoff_time: int = None,
                 cutoff_length: int = None,
                 sparkle_objectives: list[SparkleObjective] = None,
                 feature_data_df: pd.DataFrame = None)\
            -> None:
        """Initialize scenario paths and names.

        Args:
            solver: Solver that should be configured.
            instance_set: Instances object for the scenario.
            number_of_runs: The number of configurator runs to perform
                for configuring the solver.
            solver_calls: The number of times the solver is called for each
                configuration run
            cpu_time: The time budget allocated for each configuration run. (cpu)
            wallclock_time: The time budget allocated for each configuration run.
                (wallclock)
            cutoff_time: The maximum time allowed for each individual run during
                configuration.
            cutoff_length: The maximum number of iterations allowed for each
                individual run during configuration.
            sparkle_objectives: SparkleObjectives used for each run of the configuration.
                Will be simplified to the first objective.
            use_features: Boolean indicating if features should be used.
            feature_data_df: If features are used, this contains the feature data.
                Defaults to None.
        """
        super().__init__(solver, instance_set, sparkle_objectives)
        self.solver = solver
        self.instance_set = instance_set
        self.name = f"{self.solver.name}_{self.instance_set.name}"
        self.sparkle_objective = sparkle_objectives[0] if sparkle_objectives else None

        self.number_of_runs = number_of_runs
        self.solver_calls = solver_calls
        self.cpu_time = cpu_time
        self.wallclock_time = wallclock_time
        self.cutoff_time = cutoff_time
        self.cutoff_length = cutoff_length
        self.feature_data = feature_data_df

        self.parent_directory = Path()
        self.directory = Path()
        self.result_directory = Path()
        self.scenario_file_path = Path()
        self.feature_file_path = Path()
        self.instance_file_path = Path()

    def create_scenario(self: IRACEScenario, parent_directory: Path) -> None:
        """Create scenario with solver and instances in the parent directory.

        This prepares all the necessary subdirectories related to configuration.

        Args:
            parent_directory: Directory in which the scenario should be created.
        """
        # Set up directories
        self.tmp = self.directory / "tmp"
        self.tmp.mkdir(exist_ok=True)
        # Create instance files
        self.instance_file_path = self.directory / "instances.txt"
        self.instance_file_path.parent.mkdir(exist_ok=True, parents=True)
        with self.instance_file_path.open("w+") as file:
            for instance_path in self.instance_set._instance_paths:
                file.write(f"{instance_path.name}\n")
        self.create_scenario_file()

    def create_scenario_file(self: ConfigurationScenario) -> Path:
        """Create a file from the IRACE scenario.

        Returns:
            Path to the created file.
        """
        # File that contains the description of the parameters.
        # parameterFile = "./parameters-acotsp.txt"

        # Directory where the programs will be run.
        # execDir = "./acotsp-arena"

        # Directory where tuning instances are located, either absolute path or
        # relative to current directory.
        # trainInstancesDir = "./Instances"

        # The maximum number of runs (invocations of targetRunner) that will performed.
        # It determines the (maximum) budget of experiments for the tuning.
        # maxExperiments = 5000

        # File that contains a set of initial configurations. If empty or NULL,
        # all initial configurations are randomly generated.
        # configurationsFile = ""
        # File that contains a list of logical expressions that cannot be TRUE
        # for any evaluated configuration. If empty or NULL, do not use forbidden
        # expressions.
        # forbiddenFile = "forbidden.txt"

        # Indicates the number of decimal places to be considered for the
        # real parameters.
        # digits = 2

        # A value of 0 silences all debug messages. Higher values provide
        # more verbose debug messages.
        # debugLevel = 0 [0, 3] -> Should probably be set to 1

        # TODO: Write to the file
        self.scenario_file_path = self.directory / f"{self.name}_scenario.txt"
        solver_path = self.solver.directory.absolute()
        with self.scenario_file_path.open("w") as file:
            file.write(
                f'execDir = "{self.tmp.absolute()}"\n'
                'targetRunnerLauncher = "python3"\n'
                f'targetRunner = "{IRACE.target_algorithm.absolute()}"\n'
                'targetRunnerLauncherArgs = "{targetRunner} '
                f"{solver_path} {self.sparkle_objective} {self.cutoff_time} "
                '{targetRunnerArgs}"\n'
                f"deterministic = {1 if self.solver.deterministic else 0}\n"
                "parameterFile = "
                f'"{self.solver.get_pcs_file(port_type="""IRACE""").absolute()}"\n'
                # TODO: forbidden-file = self.solver.get_forbidden_file()
                # TODO: configurations-file = ?
                f'trainInstancesDir = "{self.instance_set.directory.absolute()}"\n'
                f'trainInstancesFile = "{self.instance_file_path.absolute()}"\n'
                # TODO: This is SMAC2 workflow, is it correct? Can it be ommited?
                f'testInstancesDir = "{self.instance_set.directory.absolute()}"\n'
                f'testInstancesFile = "{self.instance_file_path.absolute()}"\n'
                # 'batchmode = "slurm"'  # TODO:  run_on variable to set this
                # TODO: Log file, or default good enough?
                "debugLevel = 1\n"
            )
            if self.solver_calls is not None:
                file.write(f"maxExperiments = {self.solver_calls}\n")
            elif self.cpu_time is not None or self.wallclock_time is not None:

                # Time specified by user, but IRACE does not differentiate CPU from WALL
                maxtime = max(self.cpu_time if self.cpu_time is not None else 0,
                              self.wallclock_time if self.cpu_time is not None else 0)
                file.write(f"maxTime = {int(maxtime)}\n")
            if self.solver_calls is not None and (
                    self.cpu_time is not None or self.wallclock_time is not None):
                print("WARNING: Both solver calls and time limit specified for scenario."
                      " This is not supported by IRACE, defaulting to solver calls.")
        import subprocess
        check_file = subprocess.run(
            [f"{IRACE.configurator_executable.absolute()}",
             "-s", f"{self.scenario_file_path.absolute()}", "--check"],
            capture_output=True)
        if check_file.returncode != 0:
            stdout_msg = "\n".join([
                line for line in check_file.stdout.decode().splitlines()
                if not line.startswith("#")])
            print("An error occured in the IRACE scenario file:\n",
                  self.scenario_file_path.open("r").read(),
                  stdout_msg, "\n",
                  check_file.stderr.decode())
        return self.scenario_file_path

    @staticmethod
    def from_file(scenario_file: Path, solver: Solver, instance_set: InstanceSet,
                  ) -> ConfigurationScenario:
        """Reads scenario file and initalises IRACEScenario."""
        raise NotImplementedError
