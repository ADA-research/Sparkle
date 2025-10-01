"""Classes and Enums to control settings."""

from __future__ import annotations
import configparser
import argparse
from enum import Enum
from pathlib import Path
from typing import Any, NamedTuple, Optional

from runrunner import Runner

from sparkle.types import SparkleObjective, resolve_objective
from sparkle.configurator.configurator import Configurator
from sparkle.configurator import implementations as cim
from sparkle.platform.cli_types import VerbosityLevel


class Option(NamedTuple):
    """Class to define an option in the Settings."""

    name: str
    section: str
    type: Any
    default_value: Any
    alternatives: tuple[str, ...]
    help: str = ""
    cli_kwargs: dict[str, Any] = {}

    def __str__(self: Option) -> str:
        """Return the option name."""
        return self.name

    def __eq__(self: Option, other: Any) -> bool:
        """Check if two options are equal."""
        if isinstance(other, Option):
            return (
                self.name == other.name
                and self.section == other.section
                and self.type == other.type
                and self.default_value == other.default_value
                and self.alternatives == other.alternatives
            )
        if isinstance(other, str):
            return self.name == other or other in self.alternatives
        return False

    @property
    def args(self: Option) -> list[str]:
        """Return the option names as a command line arguments."""
        return [
            f"--{name.replace('_', '-')}"
            for name in [self.name] + list(self.alternatives)
        ]

    @property
    def kwargs(self: Option) -> dict[str, Any]:
        """Return the option attributes as kwargs."""
        kw = {"help": self.help, **self.cli_kwargs}

        # If this option uses a boolean flag action, argparse must NOT receive 'type'
        action = kw.get("action")
        if action in ("store_true", "store_false"):
            return kw

        # Otherwise include the base 'type'
        return {"type": self.type, **kw}


class Settings:
    """Class to read, write, set, and get settings."""

    # CWD Prefix
    cwd_prefix = Path()  # Empty for now

    # Library prefix
    lib_prefix = Path(__file__).parent.parent.resolve()

    # Default directory names
    rawdata_dir = Path("Raw_Data")
    analysis_dir = Path("Analysis")
    DEFAULT_settings_dir = Path("Settings")
    __settings_file = Path("sparkle_settings.ini")
    __latest_settings_file = Path("latest.ini")

    # Default settings path
    DEFAULT_settings_path = Path(cwd_prefix / DEFAULT_settings_dir / __settings_file)
    DEFAULT_previous_settings_path = Path(
        cwd_prefix / DEFAULT_settings_dir / __latest_settings_file
    )
    DEFAULT_reference_dir = DEFAULT_settings_dir / "Reference_Lists"

    # Default library pathing
    DEFAULT_components = lib_prefix / "Components"

    # Report Component: Bilbiography
    bibliography_path = DEFAULT_components / "latex_source" / "report.bib"

    # Example settings path
    DEFAULT_example_settings_path = Path(DEFAULT_components / "sparkle_settings.ini")

    # Runsolver component
    DEFAULT_runsolver_dir = DEFAULT_components / "runsolver" / "src"
    DEFAULT_runsolver_exec = DEFAULT_runsolver_dir / "runsolver"

    # Ablation component
    DEFAULT_ablation_dir = DEFAULT_components / "ablationAnalysis-0.9.4"
    DEFAULT_ablation_exec = DEFAULT_ablation_dir / "ablationAnalysis"
    DEFAULT_ablation_validation_exec = DEFAULT_ablation_dir / "ablationValidation"

    # Default input directory pathing
    DEFAULT_solver_dir = cwd_prefix / "Solvers"
    DEFAULT_instance_dir = cwd_prefix / "Instances"
    DEFAULT_extractor_dir = cwd_prefix / "Extractors"
    DEFAULT_snapshot_dir = cwd_prefix / "Snapshots"

    # Default output directory pathing
    DEFAULT_tmp_output = cwd_prefix / "Tmp"
    DEFAULT_output = cwd_prefix / "Output"
    DEFAULT_configuration_output = DEFAULT_output / "Configuration"
    DEFAULT_selection_output = DEFAULT_output / "Selection"
    DEFAULT_parallel_portfolio_output = DEFAULT_output / "Parallel_Portfolio"
    DEFAULT_ablation_output = DEFAULT_output / "Ablation"
    DEFAULT_log_output = DEFAULT_output / "Log"

    # Default output subdirs
    DEFAULT_output_analysis = DEFAULT_output / analysis_dir

    # Old default output dirs which should be part of something else
    DEFAULT_feature_data = DEFAULT_output / "Feature_Data"
    DEFAULT_performance_data = DEFAULT_output / "Performance_Data"

    # Collection of all working dirs for platform
    DEFAULT_working_dirs = [
        DEFAULT_solver_dir,
        DEFAULT_instance_dir,
        DEFAULT_extractor_dir,
        DEFAULT_output,
        DEFAULT_configuration_output,
        DEFAULT_selection_output,
        DEFAULT_output_analysis,
        DEFAULT_tmp_output,
        DEFAULT_log_output,
        DEFAULT_feature_data,
        DEFAULT_performance_data,
        DEFAULT_settings_dir,
        DEFAULT_reference_dir,
    ]

    # Old default file paths from GV which should be turned into variables
    DEFAULT_feature_data_path = DEFAULT_feature_data / "feature_data.csv"
    DEFAULT_performance_data_path = DEFAULT_performance_data / "performance_data.csv"

    # Define sections and options
    # GENERAL Options
    SECTION_general: str = "general"
    OPTION_objectives = Option(
        "objectives",
        SECTION_general,
        str,
        None,
        ("sparkle_objectives",),
        "A list of Sparkle objectives.",
        cli_kwargs={"nargs": "+"},
    )
    OPTION_configurator = Option(
        "configurator",
        SECTION_general,
        str,
        None,
        tuple(),
        "Name of the configurator to use.",
    )
    OPTION_solver_cutoff_time = Option(
        "solver_cutoff_time",
        SECTION_general,
        int,
        None,
        ("target_cutoff_time", "cutoff_time_each_solver_call"),
        "Solver cutoff time in seconds.",
    )
    OPTION_extractor_cutoff_time = Option(
        "extractor_cutoff_time",
        SECTION_general,
        int,
        None,
        tuple("cutoff_time_each_feature_computation"),
        "Extractor cutoff time in seconds.",
    )
    OPTION_run_on = Option(
        "run_on",
        SECTION_general,
        Runner,
        None,
        tuple(),
        "On which compute resource to execute.",
        cli_kwargs={"choices": [Runner.LOCAL, Runner.SLURM]},
    )
    OPTION_verbosity = Option(
        "verbosity",
        SECTION_general,
        VerbosityLevel,
        VerbosityLevel.STANDARD,
        ("verbosity_level",),
        "Verbosity level.",
    )
    OPTION_seed = Option(
        "seed",
        SECTION_general,
        int,
        None,
        tuple(),
        "Seed to use for pseudo-random number generators.",
    )
    OPTION_appendices = Option(
        "appendices",
        SECTION_general,
        bool,
        False,
        tuple(),
        "Include the appendix section in the generated report.",
        cli_kwargs={
            "action": "store_true",
            "default": None,
        },
    )

    # CONFIGURATION Options
    SECTION_configuration = "configuration"
    OPTION_configurator_number_of_runs = Option(
        "number_of_runs",
        SECTION_configuration,
        int,
        None,
        tuple(),
        "The number of independent configurator jobs/runs.",
    )
    OPTION_configurator_solver_call_budget = Option(
        "solver_calls",
        SECTION_configuration,
        int,
        None,
        tuple(),
        "The maximum number of calls (evaluations) a configurator can do in a single "
        "run of the solver.",
    )
    OPTION_configurator_max_iterations = Option(
        "max_iterations",
        SECTION_configuration,
        int,
        None,
        ("maximum_iterations",),
        "The maximum number of iterations a configurator can do in a single job.",
    )

    # ABLATION Options
    SECTION_ablation = "ablation"
    OPTION_ablation_racing = Option(
        "racing",
        SECTION_ablation,
        bool,
        False,
        ("ablation_racing",),
        "Set a flag indicating whether racing should be used for ablation.",
    )
    OPTION_ablation_clis_per_node = Option(
        "clis_per_node",
        SECTION_ablation,
        int,
        None,
        (
            "max_parallel_runs_per_node",
            "maximum_parallel_runs_per_node",
        ),
        "The maximum number of ablation analysis jobs to run in parallel on a single "
        "node.",
    )

    # SELECTION Options
    SECTION_selection = "selection"
    OPTION_selection_class = Option(
        "selector_class",
        SECTION_selection,
        str,
        None,
        ("class",),
        "Can contain any of the class names as defined in asf.selectors.",
    )
    OPTION_selection_model = Option(
        "selector_model",
        SECTION_selection,
        str,
        None,
        ("model",),
        "Can be any of the sklearn.ensemble models.",
    )
    OPTION_minimum_marginal_contribution = Option(
        "minimum_marginal_contribution",
        SECTION_selection,
        float,
        0.01,
        (
            "minimum_marginal_contribution",
            "minimum_contribution",
            "contribution_threshold",
        ),
        "The minimum marginal contribution a solver (configuration) must have to be used for the selector.",
    )

    # SMAC2 Options
    SECTION_smac2 = "smac2"
    OPTION_smac2_wallclock_time_budget = Option(
        "wallclock_time_budget",
        SECTION_smac2,
        int,
        None,
        ("wallclock_time",),
        "The wallclock time budget in seconds for each SMAC2 run.",
    )
    OPTION_smac2_cpu_time_budget = Option(
        "cpu_time_budget",
        SECTION_smac2,
        int,
        None,
        ("cpu_time",),
        "The cpu time budget in seconds for each SMAC2 run.",
    )
    OPTION_smac2_target_cutoff_length = Option(
        "target_cutoff_length",
        SECTION_smac2,
        str,
        None,
        ("cutoff_length", "solver_cutoff_length"),
        "The target cutoff length for SMAC2 solver call.",
    )
    OPTION_smac2_count_tuner_time = Option(
        "use_cpu_time_in_tunertime",
        SECTION_smac2,
        bool,
        None,
        ("countSMACTimeAsTunerTime",),
        "Whether to count and deducted SMAC2 CPU time from the CPU time budget.",
    )
    OPTION_smac2_cli_cores = Option(
        "cli_cores",
        SECTION_smac2,
        int,
        None,
        tuple(),
        "Number of cores to use to execute SMAC2 runs.",
    )
    OPTION_smac2_max_iterations = Option(
        "max_iterations",
        SECTION_smac2,
        int,
        None,
        (
            "iteration_limit",
            "numIterations",
            "numberOfIterations",
        ),
        "The maximum number of iterations SMAC2 configurator can do in a single job.",
    )

    # SMAC3 Options
    SECTION_smac3 = "smac3"
    OPTION_smac3_number_of_trials = Option(
        "n_trials",
        SECTION_smac3,
        int,
        None,
        ("n_trials", "number_of_trials", "solver_calls"),
        "Maximum calls SMAC3 is allowed to make to the Solver in a single run/job.",
    )
    OPTION_smac3_facade = Option(
        "facade",
        SECTION_smac3,
        str,
        "AlgorithmConfigurationFacade",
        ("facade", "smac_facade", "smac3_facade"),
        "The SMAC3 Facade to use. See the SMAC3 documentation for more options.",
    )
    OPTION_smac3_facade_max_ratio = Option(
        "facade_max_ratio",
        SECTION_smac3,
        float,
        None,
        ("facade_max_ratio", "smac3_facade_max_ratio", "smac3_facade_max_ratio"),
        "The SMAC3 Facade max ratio. See the SMAC3 documentation for more options.",
    )
    OPTION_smac3_crash_cost = Option(
        "crash_cost",
        SECTION_smac3,
        float,
        None,
        tuple(),
        "Defines the cost for a failed trial, defaults in SMAC3 to np.inf.",
    )
    OPTION_smac3_termination_cost_threshold = Option(
        "termination_cost_threshold",
        SECTION_smac3,
        float,
        None,
        tuple(),
        "Defines a cost threshold when the SMAC3 optimization should stop.",
    )
    OPTION_smac3_wallclock_time_budget = Option(
        "walltime_limit",
        SECTION_smac3,
        float,
        None,
        ("wallclock_time", "wallclock_budget", "wallclock_time_budget"),
        "The maximum time in seconds that SMAC3 is allowed to run per job.",
    )
    OPTION_smac3_cpu_time_budget = Option(
        "cputime_limit",
        SECTION_smac3,
        float,
        None,
        ("cpu_time", "cpu_budget", "cpu_time_budget"),
        "The maximum CPU time in seconds that SMAC3 is allowed to run per job.",
    )
    OPTION_smac3_use_default_config = Option(
        "use_default_config",
        SECTION_smac3,
        bool,
        None,
        tuple(),
        "If True, the configspace's default configuration is evaluated in the initial "
        "design. For historic benchmark reasons, this is False by default. Notice, that "
        "this will result in n_configs + 1 for the initial design. Respecting n_trials, "
        "this will result in one fewer evaluated configuration in the optimization.",
    )
    OPTION_smac3_min_budget = Option(
        "min_budget",
        SECTION_smac3,
        float,
        None,
        ("minimum_budget",),
        "The minimum budget (epochs, subset size, number of instances, ...) that is used"
        " for the optimization. Use this argument if you use multi-fidelity or instance "
        "optimization.",
    )
    OPTION_smac3_max_budget = Option(
        "max_budget",
        SECTION_smac3,
        float,
        None,
        ("maximum_budget",),
        "The maximum budget (epochs, subset size, number of instances, ...) that is used"
        " for the optimization. Use this argument if you use multi-fidelity or instance "
        "optimization.",
    )

    # IRACE Options
    SECTION_irace = "irace"
    OPTION_irace_max_time = Option(
        "max_time",
        SECTION_irace,
        int,
        0,
        ("maximum_time",),
        "The maximum time in seconds for each IRACE run/job.",
    )
    OPTION_irace_max_experiments = Option(
        "max_experiments",
        SECTION_irace,
        int,
        0,
        ("maximum_experiments",),
        "The maximum number of experiments for each IRACE run/job.",
    )
    OPTION_irace_first_test = Option(
        "first_test",
        SECTION_irace,
        int,
        None,
        tuple(),
        "Specifies how many instances are evaluated before the first elimination test. "
        "IRACE Default: 5.",
    )
    OPTION_irace_mu = Option(
        "mu",
        SECTION_irace,
        int,
        None,
        tuple(),
        "Parameter used to define the number of configurations sampled and evaluated at "
        "each iteration. IRACE Default: 5.",
    )
    OPTION_irace_max_iterations = Option(
        "max_iterations",
        SECTION_irace,
        int,
        None,
        ("nb_iterations", "iterations", "max_iterations"),
        "Maximum number of iterations to be executed. Each iteration involves the "
        "generation of new configurations and the use of racing to select the best "
        "configurations. By default (with 0), irace calculates a minimum number of "
        "iterations as N^iter = ⌊2 + log2 N param⌋, where N^param is the number of "
        "non-fixed parameters to be tuned. Setting this parameter may make irace stop "
        "sooner than it should without using all the available budget. IRACE recommends"
        " to use the default value (Empty).",
    )

    # ParamILS Options
    SECTION_paramils = "paramils"
    OPTION_paramils_min_runs = Option(
        "min_runs",
        SECTION_paramils,
        int,
        None,
        ("minimum_runs",),
        "Set the minimum number of runs for ParamILS for each run/job.",
    )
    OPTION_paramils_max_runs = Option(
        "max_runs",
        SECTION_paramils,
        int,
        None,
        ("maximum_runs",),
        "Set the maximum number of runs for ParamILS for each run/job.",
    )
    OPTION_paramils_cpu_time_budget = Option(
        "cputime_budget",
        SECTION_paramils,
        int,
        None,
        (
            "cputime_limit",
            "cputime_limit",
            "tunertime_limit",
            "tuner_timeout",
            "tunerTimeout",
        ),
        "The maximum CPU time for each ParamILS run/job.",
    )
    OPTION_paramils_random_restart = Option(
        "random_restart",
        SECTION_paramils,
        float,
        None,
        tuple(),
        "Set the random restart chance for ParamILS.",
    )
    OPTION_paramils_focused = Option(
        "focused_approach",
        SECTION_paramils,
        bool,
        False,
        ("focused",),
        "Set the focused approach for ParamILS.",
    )
    OPTION_paramils_count_tuner_time = Option(
        "use_cpu_time_in_tunertime",
        SECTION_paramils,
        bool,
        None,
        tuple(),
        "Whether to count and deducted ParamILS CPU time from the CPU time budget.",
    )
    OPTION_paramils_cli_cores = Option(
        "cli_cores",
        SECTION_paramils,
        int,
        None,
        tuple(),
        "Number of cores to use for ParamILS runs.",
    )
    OPTION_paramils_max_iterations = Option(
        "max_iterations",
        SECTION_paramils,
        int,
        None,
        (
            "iteration_limit",
            "numIterations",
            "numberOfIterations",
            "maximum_iterations",
        ),
        "The maximum number of ParamILS iterations per run/job.",
    )
    OPTION_paramils_number_initial_configurations = Option(
        "initial_configurations",
        SECTION_paramils,
        int,
        None,
        "The number of initial configurations ParamILS should evaluate.",
    )

    SECTION_parallel_portfolio = "parallel_portfolio"
    OPTION_parallel_portfolio_check_interval = Option(
        "check_interval",
        SECTION_parallel_portfolio,
        int,
        None,
        tuple(),
        "The interval time in seconds when Solvers are checked for their status.",
    )
    OPTION_parallel_portfolio_number_of_seeds_per_solver = Option(
        "num_seeds_per_solver",
        SECTION_parallel_portfolio,
        int,
        None,
        ("solver_seeds",),
        "The number of seeds per solver.",
    )

    SECTION_slurm = "slurm"
    OPTION_slurm_parallel_jobs = Option(
        "number_of_jobs_in_parallel",
        SECTION_slurm,
        int,
        None,
        ("num_job_in_parallel",),
        "The number of jobs to run in parallel.",
    )
    OPTION_slurm_prepend_script = Option(
        "prepend_script",
        SECTION_slurm,
        str,
        None,
        ("job_prepend", "prepend"),
        "Slurm script to prepend to the sbatch.",
    )

    sections_options: dict[str, list[Option]] = {
        SECTION_general: [
            OPTION_objectives,
            OPTION_configurator,
            OPTION_solver_cutoff_time,
            OPTION_extractor_cutoff_time,
            OPTION_run_on,
            OPTION_appendices,
            OPTION_verbosity,
            OPTION_seed,
        ],
        SECTION_configuration: [
            OPTION_configurator_number_of_runs,
            OPTION_configurator_solver_call_budget,
            OPTION_configurator_max_iterations,
        ],
        SECTION_ablation: [
            OPTION_ablation_racing,
            OPTION_ablation_clis_per_node,
        ],
        SECTION_selection: [
            OPTION_selection_class,
            OPTION_selection_model,
            OPTION_minimum_marginal_contribution,
        ],
        SECTION_smac2: [
            OPTION_smac2_wallclock_time_budget,
            OPTION_smac2_cpu_time_budget,
            OPTION_smac2_target_cutoff_length,
            OPTION_smac2_count_tuner_time,
            OPTION_smac2_cli_cores,
            OPTION_smac2_max_iterations,
        ],
        SECTION_smac3: [
            OPTION_smac3_number_of_trials,
            OPTION_smac3_facade,
            OPTION_smac3_facade_max_ratio,
            OPTION_smac3_crash_cost,
            OPTION_smac3_termination_cost_threshold,
            OPTION_smac3_wallclock_time_budget,
            OPTION_smac3_cpu_time_budget,
            OPTION_smac3_use_default_config,
            OPTION_smac3_min_budget,
            OPTION_smac3_max_budget,
        ],
        SECTION_irace: [
            OPTION_irace_max_time,
            OPTION_irace_max_experiments,
            OPTION_irace_first_test,
            OPTION_irace_mu,
            OPTION_irace_max_iterations,
        ],
        SECTION_paramils: [
            OPTION_paramils_min_runs,
            OPTION_paramils_max_runs,
            OPTION_paramils_cpu_time_budget,
            OPTION_paramils_random_restart,
            OPTION_paramils_focused,
            OPTION_paramils_count_tuner_time,
            OPTION_paramils_cli_cores,
            OPTION_paramils_max_iterations,
            OPTION_paramils_number_initial_configurations,
        ],
        SECTION_parallel_portfolio: [
            OPTION_parallel_portfolio_check_interval,
            OPTION_parallel_portfolio_number_of_seeds_per_solver,
        ],
        SECTION_slurm: [OPTION_slurm_parallel_jobs, OPTION_slurm_prepend_script],
    }

    def __init__(
        self: Settings, file_path: Path, argsv: argparse.Namespace = None
    ) -> None:
        """Initialise a settings object.

        Args:
            file_path (Path): Path to the settings file.
            argsv: The CLI arguments to process.
        """
        # Settings 'dictionary' in configparser format
        self.__settings = configparser.ConfigParser()
        for section in self.sections_options.keys():
            self.__settings.add_section(section)
            self.__settings[section] = {}

        # General attributes
        self.__sparkle_objectives: list[SparkleObjective] = None
        self.__general_sparkle_configurator: Configurator = None
        self.__solver_cutoff_time: int = None
        self.__extractor_cutoff_time: int = None
        self.__run_on: Runner = None
        self.__appendices: bool = False
        self.__verbosity_level: VerbosityLevel = None
        self.__seed: Optional[int] = None

        # Configuration attributes
        self.__configurator_solver_call_budget: int = None
        self.__configurator_number_of_runs: int = None
        self.__configurator_max_iterations: int = None

        # Ablation attributes
        self.__ablation_racing_flag: bool = None
        self.__ablation_max_parallel_runs_per_node: int = None

        # Selection attributes
        self.__selection_model: str = None
        self.__selection_class: str = None
        self.__minimum_marginal_contribution: float = None

        # SMAC2 attributes
        self.__smac2_wallclock_time_budget: int = None
        self.__smac2_cpu_time_budget: int = None
        self.__smac2_target_cutoff_length: str = None
        self.__smac2_use_tunertime_in_cpu_time_budget: bool = None
        self.__smac2_cli_cores: int = None
        self.__smac2_max_iterations: int = None

        # SMAC3 attributes
        self.__smac3_number_of_trials: int = None
        self.__smac3_facade: str = None
        self.__smac3_facade_max_ratio: float = None
        self.__smac3_crash_cost: float = None
        self.__smac3_termination_cost_threshold: float = None
        self.__smac3_wallclock_time_limit: int = None
        self.__smac3_cputime_limit: int = None
        self.__smac3_use_default_config: bool = None
        self.__smac3_min_budget: float = None
        self.__smac3_max_budget: float = None

        # IRACE attributes
        self.__irace_max_time: int = None
        self.__irace_max_experiments: int = None
        self.__irace_first_test: int = None
        self.__irace_mu: int = None
        self.__irace_max_iterations: int = None

        # ParamILS attributes
        self.__paramils_cpu_time_budget: int = None
        self.__paramils_min_runs: int = None
        self.__paramils_max_runs: int = None
        self.__paramils_random_restart: float = None
        self.__paramils_focused_approach: bool = None
        self.__paramils_use_cpu_time_in_tunertime: bool = None
        self.__paramils_cli_cores: int = None
        self.__paramils_max_iterations: int = None
        self.__paramils_number_initial_configurations: int = None

        # Parallel portfolio attributes
        self.__parallel_portfolio_check_interval: int = None
        self.__parallel_portfolio_num_seeds_per_solver: int = None

        # Slurm attributes
        self.__slurm_jobs_in_parallel: int = None
        self.__slurm_job_prepend: str = None

        # The seed that has been used to set the random state
        self.random_state: Optional[int] = None

        if file_path and file_path.exists():
            self.read_settings_ini(file_path)

        if argsv:
            self.apply_arguments(argsv)

    def read_settings_ini(self: Settings, file_path: Path) -> None:
        """Read the settings from an INI file."""
        if not file_path.exists():
            raise ValueError(f"Settings file {file_path} does not exist.")
        # Read file
        file_settings = configparser.ConfigParser()
        file_settings.read(file_path)

        # Set internal settings based on data read from FILE if they were read
        # successfully
        if file_settings.sections() == []:
            # Print error if unable to read the settings
            print(
                f"ERROR: Failed to read settings from {file_path} The file may "
                "have been empty or be in another format than INI."
            )
            return

        for section in file_settings.sections():
            if section not in self.__settings.sections():
                print(f'Unrecognised section: "{section}" in file {file_path} ignored')
                continue
            for option_name in file_settings.options(section):
                if option_name not in self.sections_options[section]:
                    if section == Settings.SECTION_slurm:  # Flexible section
                        self.__settings.set(
                            section,
                            option_name,
                            file_settings.get(section, option_name),
                        )
                    else:
                        print(
                            f'Unrecognised section - option combination: "{section} '
                            f'{option_name}" in file {file_path} ignored'
                        )
                    continue
                option_index = self.sections_options[section].index(option_name)
                option = self.sections_options[section][option_index]
                self.__settings.set(
                    section, option.name, file_settings.get(section, option_name)
                )
        del file_settings

    def write_settings_ini(self: Settings, file_path: Path) -> None:
        """Write the settings to an INI file."""
        # Create needed directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        # We don't write empty sections
        for s in self.__settings.sections():
            if not self.__settings[s]:
                self.__settings.remove_section(s)
        with file_path.open("w") as fout:
            self.__settings.write(fout)
        for s in self.sections_options.keys():
            if s not in self.__settings.sections():
                self.__settings.add_section(s)

    def write_used_settings(self: Settings) -> None:
        """Write the used settings to the default locations."""
        # Write to latest settings file
        self.write_settings_ini(self.DEFAULT_previous_settings_path)

    def apply_arguments(self: Settings, argsv: argparse.Namespace) -> None:
        """Apply the arguments to the settings."""
        # Read a possible second file, that overwrites the first, where applicable
        # e.g. settings are not deleted, but overwritten where applicable
        if hasattr(argsv, "settings_file") and argsv.settings_file:
            self.read_settings_ini(argsv.settings_file)
        # Match all possible arguments to the settings
        for argument in argsv.__dict__.keys():
            value = argsv.__dict__[argument]
            if value is None:
                continue  # Skip None
            value = value.name if isinstance(value, Enum) else str(value)
            for section in self.sections_options.keys():
                if argument in self.sections_options[section]:
                    index = self.sections_options[section].index(argument)
                    option = self.sections_options[section][index]
                    self.__settings.set(option.section, option.name, value)
                    break

    def _abstract_getter(self: Settings, option: Option) -> Any:
        """Abstract getter method."""
        if self.__settings.has_option(option.section, option.name):
            if option.type is bool:
                return self.__settings.getboolean(option.section, option.name)
            value = self.__settings.get(option.section, option.name)
            if not isinstance(value, option.type):
                if issubclass(option.type, Enum):
                    return option.type[value.upper()]
                return option.type(value)  # Attempt to resolve str to type
            return value
        return option.default_value

    # General settings ###
    @property
    def objectives(self: Settings) -> list[SparkleObjective]:
        """Get the objectives for Sparkle."""
        if self.__sparkle_objectives is None and self.__settings.has_option(
            Settings.SECTION_general, "objectives"
        ):
            objectives = self.__settings[Settings.SECTION_general]["objectives"]
            if "status" not in objectives:
                objectives += ",status:metric"
            if "cpu_time" not in objectives:
                objectives += ",cpu_time:metric"
            if "wall_time" not in objectives:
                objectives += ",wall_time:metric"
            if "memory" not in objectives:
                objectives += ",memory:metric"
            self.__sparkle_objectives = [
                resolve_objective(obj) for obj in objectives.split(",")
            ]
        return self.__sparkle_objectives

    @property
    def configurator(self: Settings) -> Configurator:
        """Get the configurator class (instance)."""
        if self.__general_sparkle_configurator is None and self.__settings.has_option(
            Settings.OPTION_configurator.section, Settings.OPTION_configurator.name
        ):
            self.__general_sparkle_configurator = cim.resolve_configurator(
                self.__settings.get(
                    Settings.OPTION_configurator.section,
                    Settings.OPTION_configurator.name,
                )
            )()
        return self.__general_sparkle_configurator

    @property
    def solver_cutoff_time(self: Settings) -> int:
        """Solver cutoff time in seconds."""
        if self.__solver_cutoff_time is None:
            self.__solver_cutoff_time = self._abstract_getter(
                Settings.OPTION_solver_cutoff_time
            )
        return self.__solver_cutoff_time

    @property
    def extractor_cutoff_time(self: Settings) -> int:
        """Extractor cutoff time in seconds."""
        if self.__extractor_cutoff_time is None:
            self.__extractor_cutoff_time = self._abstract_getter(
                Settings.OPTION_extractor_cutoff_time
            )
        return self.__extractor_cutoff_time

    @property
    def run_on(self: Settings) -> Runner:
        """On which compute to run (Local or Slurm)."""
        if self.__run_on is None:
            self.__run_on = self._abstract_getter(Settings.OPTION_run_on)
        return self.__run_on

    @property
    def appendices(self: Settings) -> bool:
        """Whether to include appendices in the report."""
        return self._abstract_getter(Settings.OPTION_appendices)

    @property
    def verbosity_level(self: Settings) -> VerbosityLevel:
        """Verbosity level to use in CLI commands."""
        if self.__verbosity_level is None:
            if self.__settings.has_option(
                Settings.OPTION_verbosity.section, Settings.OPTION_verbosity.name
            ):
                self.__verbosity_level = VerbosityLevel[
                    self.__settings.get(
                        Settings.OPTION_verbosity.section,
                        Settings.OPTION_verbosity.name,
                    )
                ]
            else:
                self.__verbosity_level = Settings.OPTION_verbosity.default_value
        return self.__verbosity_level

    @property
    def seed(self: Settings) -> int:
        """Seed to use in CLI commands."""
        if self.__seed is not None:
            return self.__seed

        section, name = Settings.OPTION_seed.section, Settings.OPTION_seed.name
        if self.__settings.has_option(section, name):
            value = self.__settings.get(section, name)
            self.__seed = int(value)
        else:
            self.__seed = Settings.OPTION_seed.default_value

        return self.__seed

    @seed.setter
    def seed(self: Settings, value: int) -> None:
        """Set the seed value (overwrites settings)."""
        self.__seed = value
        self.__settings.set(
            Settings.OPTION_seed.section, Settings.OPTION_seed.name, str(self.__seed)
        )

    # Configuration settings ###
    @property
    def configurator_solver_call_budget(self: Settings) -> int:
        """The amount of calls a configurator can do to the solver."""
        if self.__configurator_solver_call_budget is None:
            self.__configurator_solver_call_budget = self._abstract_getter(
                Settings.OPTION_configurator_solver_call_budget
            )
        return self.__configurator_solver_call_budget

    @property
    def configurator_number_of_runs(self: Settings) -> int:
        """Get the amount of configurator runs to do."""
        if self.__configurator_number_of_runs is None:
            self.__configurator_number_of_runs = self._abstract_getter(
                Settings.OPTION_configurator_number_of_runs
            )
        return self.__configurator_number_of_runs

    @property
    def configurator_max_iterations(self: Settings) -> int:
        """Get the amount of configurator iterations to do."""
        if self.__configurator_max_iterations is None:
            self.__configurator_max_iterations = self._abstract_getter(
                Settings.OPTION_configurator_max_iterations
            )
        return self.__configurator_max_iterations

    # Ablation settings ###
    @property
    def ablation_racing_flag(self: Settings) -> bool:
        """Get the ablation racing flag."""
        if self.__ablation_racing_flag is None:
            self.__ablation_racing_flag = self._abstract_getter(
                Settings.OPTION_ablation_racing
            )
        return self.__ablation_racing_flag

    @property
    def ablation_max_parallel_runs_per_node(self: Settings) -> int:
        """Get the ablation max parallel runs per node."""
        if self.__ablation_max_parallel_runs_per_node is None:
            self.__ablation_max_parallel_runs_per_node = self._abstract_getter(
                Settings.OPTION_ablation_clis_per_node
            )
        return self.__ablation_max_parallel_runs_per_node

    # Selection settings ###
    @property
    def selection_model(self: Settings) -> str:
        """Get the selection model."""
        if self.__selection_model is None:
            self.__selection_model = self._abstract_getter(
                Settings.OPTION_selection_model
            )
        return self.__selection_model

    @property
    def selection_class(self: Settings) -> str:
        """Get the selection class."""
        if self.__selection_class is None:
            self.__selection_class = self._abstract_getter(
                Settings.OPTION_selection_class
            )
        return self.__selection_class

    @property
    def minimum_marginal_contribution(self: Settings) -> float:
        """Get the minimum marginal contribution."""
        if self.__minimum_marginal_contribution is None:
            self.__minimum_marginal_contribution = self._abstract_getter(
                Settings.OPTION_minimum_marginal_contribution
            )
        return self.__minimum_marginal_contribution

    # Configuration: SMAC2 specific settings ###
    @property
    def smac2_wallclock_time_budget(self: Settings) -> int:
        """Return the SMAC2 wallclock budget per configuration run in seconds."""
        if self.__smac2_wallclock_time_budget is None:
            self.__smac2_wallclock_time_budget = self._abstract_getter(
                Settings.OPTION_smac2_wallclock_time_budget
            )
        return self.__smac2_wallclock_time_budget

    @property
    def smac2_cpu_time_budget(self: Settings) -> int:
        """Return the SMAC2 CPU budget per configuration run in seconds."""
        if self.__smac2_cpu_time_budget is None:
            self.__smac2_cpu_time_budget = self._abstract_getter(
                Settings.OPTION_smac2_cpu_time_budget
            )
        return self.__smac2_cpu_time_budget

    @property
    def smac2_target_cutoff_length(self: Settings) -> str:
        """Return the SMAC2 target cutoff length."""
        if self.__smac2_target_cutoff_length is None:
            self.__smac2_target_cutoff_length = self._abstract_getter(
                Settings.OPTION_smac2_target_cutoff_length
            )
        return self.__smac2_target_cutoff_length

    @property
    def smac2_use_tunertime_in_cpu_time_budget(self: Settings) -> bool:
        """Return whether SMAC2 time should be used in CPU time budget."""
        if self.__smac2_use_tunertime_in_cpu_time_budget is None:
            self.__smac2_use_tunertime_in_cpu_time_budget = self._abstract_getter(
                Settings.OPTION_smac2_count_tuner_time
            )
        return self.__smac2_use_tunertime_in_cpu_time_budget

    @property
    def smac2_cli_cores(self: Settings) -> int:
        """Return the SMAC2 CLI cores."""
        if self.__smac2_cli_cores is None:
            self.__smac2_cli_cores = self._abstract_getter(
                Settings.OPTION_smac2_cli_cores
            )
        return self.__smac2_cli_cores

    @property
    def smac2_max_iterations(self: Settings) -> int:
        """Return the SMAC2 max iterations."""
        if self.__smac2_max_iterations is None:
            self.__smac2_max_iterations = self._abstract_getter(
                Settings.OPTION_smac2_max_iterations
            )
        return self.__smac2_max_iterations

    # SMAC3 attributes ###
    @property
    def smac3_number_of_trials(self: Settings) -> int:
        """Return the SMAC3 number of trials."""
        if self.__smac3_number_of_trials is None:
            self.__smac3_number_of_trials = self._abstract_getter(
                Settings.OPTION_smac3_number_of_trials
            )
        return self.__smac3_number_of_trials

    @property
    def smac3_facade(self: Settings) -> str:
        """Return the SMAC3 facade."""
        if self.__smac3_facade is None:
            self.__smac3_facade = self._abstract_getter(Settings.OPTION_smac3_facade)
        return self.__smac3_facade

    @property
    def smac3_facade_max_ratio(self: Settings) -> float:
        """Return the SMAC3 facade max ratio."""
        if self.__smac3_facade_max_ratio is None:
            self.__smac3_facade_max_ratio = self._abstract_getter(
                Settings.OPTION_smac3_facade_max_ratio
            )
        return self.__smac3_facade_max_ratio

    @property
    def smac3_crash_cost(self: Settings) -> float:
        """Return the SMAC3 crash cost."""
        if self.__smac3_crash_cost is None:
            self.__smac3_crash_cost = self._abstract_getter(
                Settings.OPTION_smac3_crash_cost
            )
        return self.__smac3_crash_cost

    @property
    def smac3_termination_cost_threshold(self: Settings) -> float:
        """Return the SMAC3 termination cost threshold."""
        if self.__smac3_termination_cost_threshold is None:
            self.__smac3_termination_cost_threshold = self._abstract_getter(
                Settings.OPTION_smac3_termination_cost_threshold
            )
        return self.__smac3_termination_cost_threshold

    @property
    def smac3_wallclock_time_budget(self: Settings) -> int:
        """Return the SMAC3 walltime budget in seconds."""
        if self.__smac3_wallclock_time_limit is None:
            self.__smac3_wallclock_time_limit = self._abstract_getter(
                Settings.OPTION_smac3_wallclock_time_budget
            )
        return self.__smac3_wallclock_time_limit

    @property
    def smac3_cpu_time_budget(self: Settings) -> int:
        """Return the SMAC3 cputime budget in seconds."""
        if self.__smac3_cputime_limit is None:
            self.__smac3_cputime_limit = self._abstract_getter(
                Settings.OPTION_smac3_cpu_time_budget
            )
        return self.__smac3_cputime_limit

    @property
    def smac3_use_default_config(self: Settings) -> bool:
        """Return whether SMAC3 should use the default config."""
        if self.__smac3_use_default_config is None:
            self.__smac3_use_default_config = self._abstract_getter(
                Settings.OPTION_smac3_use_default_config
            )
        return self.__smac3_use_default_config

    @property
    def smac3_min_budget(self: Settings) -> int:
        """Return the SMAC3 min budget."""
        if self.__smac3_min_budget is None:
            self.__smac3_min_budget = self._abstract_getter(
                Settings.OPTION_smac3_min_budget
            )
        return self.__smac3_min_budget

    @property
    def smac3_max_budget(self: Settings) -> int:
        """Return the SMAC3 max budget."""
        if self.__smac3_max_budget is None:
            self.__smac3_max_budget = self._abstract_getter(
                Settings.OPTION_smac3_max_budget
            )
        return self.__smac3_max_budget

    # IRACE settings ###
    @property
    def irace_max_time(self: Settings) -> int:
        """Return the max time in seconds for IRACE."""
        if self.__irace_max_time is None:
            self.__irace_max_time = self._abstract_getter(Settings.OPTION_irace_max_time)
        return self.__irace_max_time

    @property
    def irace_max_experiments(self: Settings) -> int:
        """Return the max experiments for IRACE."""
        if self.__irace_max_experiments is None:
            self.__irace_max_experiments = self._abstract_getter(
                Settings.OPTION_irace_max_experiments
            )
        return self.__irace_max_experiments

    @property
    def irace_first_test(self: Settings) -> int:
        """Return the first test for IRACE."""
        if self.__irace_first_test is None:
            self.__irace_first_test = self._abstract_getter(
                Settings.OPTION_irace_first_test
            )
        return self.__irace_first_test

    @property
    def irace_mu(self: Settings) -> int:
        """Return the mu for IRACE."""
        if self.__irace_mu is None:
            self.__irace_mu = self._abstract_getter(Settings.OPTION_irace_mu)
        return self.__irace_mu

    @property
    def irace_max_iterations(self: Settings) -> int:
        """Return the max iterations for IRACE."""
        if self.__irace_max_iterations is None:
            self.__irace_max_iterations = self._abstract_getter(
                Settings.OPTION_irace_max_iterations
            )
        return self.__irace_max_iterations

    # ParamILS settings ###
    @property
    def paramils_cpu_time_budget(self: Settings) -> int:
        """Return the CPU time budget for ParamILS."""
        if self.__paramils_cpu_time_budget is None:
            self.__paramils_cpu_time_budget = self._abstract_getter(
                Settings.OPTION_paramils_cpu_time_budget
            )
        return self.__paramils_cpu_time_budget

    @property
    def paramils_min_runs(self: Settings) -> int:
        """Return the min runs for ParamILS."""
        if self.__paramils_min_runs is None:
            self.__paramils_min_runs = self._abstract_getter(
                Settings.OPTION_paramils_min_runs
            )
        return self.__paramils_min_runs

    @property
    def paramils_max_runs(self: Settings) -> int:
        """Return the max runs for ParamILS."""
        if self.__paramils_max_runs is None:
            self.__paramils_max_runs = self._abstract_getter(
                Settings.OPTION_paramils_max_runs
            )
        return self.__paramils_max_runs

    @property
    def paramils_random_restart(self: Settings) -> float:
        """Return the random restart for ParamILS."""
        if self.__paramils_random_restart is None:
            self.__paramils_random_restart = self._abstract_getter(
                Settings.OPTION_paramils_random_restart
            )
        return self.__paramils_random_restart

    @property
    def paramils_focused_approach(self: Settings) -> bool:
        """Return the focused approach for ParamILS."""
        if self.__paramils_focused_approach is None:
            self.__paramils_focused_approach = self._abstract_getter(
                Settings.OPTION_paramils_focused
            )
        return self.__paramils_focused_approach

    @property
    def paramils_use_cpu_time_in_tunertime(self: Settings) -> bool:
        """Return the use cpu time for ParamILS."""
        if self.__paramils_use_cpu_time_in_tunertime is None:
            self.__paramils_use_cpu_time_in_tunertime = self._abstract_getter(
                Settings.OPTION_paramils_count_tuner_time
            )
        return self.__paramils_use_cpu_time_in_tunertime

    @property
    def paramils_cli_cores(self: Settings) -> int:
        """The number of CPU cores to use for ParamILS."""
        if self.__paramils_cli_cores is None:
            self.__paramils_cli_cores = self._abstract_getter(
                Settings.OPTION_paramils_cli_cores
            )
        return self.__paramils_cli_cores

    @property
    def paramils_max_iterations(self: Settings) -> int:
        """Return the max iterations for ParamILS."""
        if self.__paramils_max_iterations is None:
            self.__paramils_max_iterations = self._abstract_getter(
                Settings.OPTION_paramils_max_iterations
            )
        return self.__paramils_max_iterations

    @property
    def paramils_number_initial_configurations(self: Settings) -> int:
        """Return the number of initial configurations for ParamILS."""
        if self.__paramils_number_initial_configurations is None:
            self.__paramils_number_initial_configurations = self._abstract_getter(
                Settings.OPTION_paramils_number_initial_configurations
            )
        return self.__paramils_number_initial_configurations

    # Parallel Portfolio settings ###
    @property
    def parallel_portfolio_check_interval(self: Settings) -> int:
        """Return the check interval for the parallel portfolio."""
        if self.__parallel_portfolio_check_interval is None:
            self.__parallel_portfolio_check_interval = self._abstract_getter(
                Settings.OPTION_parallel_portfolio_check_interval
            )
        return self.__parallel_portfolio_check_interval

    @property
    def parallel_portfolio_num_seeds_per_solver(self: Settings) -> int:
        """Return the number of seeds per solver for the parallel portfolio."""
        if self.__parallel_portfolio_num_seeds_per_solver is None:
            self.__parallel_portfolio_num_seeds_per_solver = self._abstract_getter(
                Settings.OPTION_parallel_portfolio_number_of_seeds_per_solver
            )
        return self.__parallel_portfolio_num_seeds_per_solver

    # Slurm settings ###
    @property
    def slurm_jobs_in_parallel(self: Settings) -> int:
        """Return the (maximum) number of jobs to run in parallel."""
        if self.__slurm_jobs_in_parallel is None:
            self.__slurm_jobs_in_parallel = self._abstract_getter(
                Settings.OPTION_slurm_parallel_jobs
            )
        return self.__slurm_jobs_in_parallel

    @property
    def slurm_job_prepend(self: Settings) -> str:
        """Return the slurm job prepend."""
        if self.__slurm_job_prepend is None and self.__settings.has_option(
            Settings.OPTION_slurm_prepend_script.section,
            Settings.OPTION_slurm_prepend_script.name,
        ):
            value = self.__settings[Settings.OPTION_slurm_prepend_script.section][
                Settings.OPTION_slurm_prepend_script.name
            ]
            try:
                path = Path(value)
                if path.is_file():
                    with path.open() as f:
                        value = f.read()
                        f.close()
                self.__slurm_job_prepend = str(value)
            except TypeError:
                pass
        return self.__slurm_job_prepend

    @property
    def sbatch_settings(self: Settings) -> list[str]:
        """Return the sbatch settings."""
        sbatch_options = self.__settings[Settings.SECTION_slurm]
        # Return all non-predefined keys
        return [
            f"--{key}={sbatch_options[key]}"
            for key in sbatch_options.keys()
            if key not in Settings.sections_options[Settings.SECTION_slurm]
        ]

    # General functionalities ###

    def get_configurator_output_path(self: Settings, configurator: Configurator) -> Path:
        """Return the configurator output path."""
        return self.DEFAULT_configuration_output / configurator.name

    def get_configurator_settings(
        self: Settings, configurator_name: str
    ) -> dict[str, any]:
        """Return the settings of a specific configurator."""
        configurator_settings = {
            "solver_calls": self.configurator_solver_call_budget,
            "solver_cutoff_time": self.solver_cutoff_time,
            "max_iterations": self.configurator_max_iterations,
        }
        # In the settings below, we default to the configurator general settings if no
        # specific configurator settings are given, by using the [None] or [Value]
        if configurator_name == cim.SMAC2.__name__:
            # Return all settings from the SMAC2 section
            configurator_settings.update(
                {
                    "cpu_time": self.smac2_cpu_time_budget,
                    "wallclock_time": self.smac2_wallclock_time_budget,
                    "target_cutoff_length": self.smac2_target_cutoff_length,
                    "use_cpu_time_in_tunertime": self.smac2_use_tunertime_in_cpu_time_budget,
                    "cli_cores": self.smac2_cli_cores,
                    "max_iterations": self.smac2_max_iterations
                    or configurator_settings["max_iterations"],
                }
            )
        elif configurator_name == cim.SMAC3.__name__:
            # Return all settings from the SMAC3 section
            del configurator_settings["max_iterations"]  # SMAC3 does not have this?
            configurator_settings.update(
                {
                    "smac_facade": self.smac3_facade,
                    "max_ratio": self.smac3_facade_max_ratio,
                    "crash_cost": self.smac3_crash_cost,
                    "termination_cost_threshold": self.smac3_termination_cost_threshold,
                    "walltime_limit": self.smac3_wallclock_time_budget,
                    "cputime_limit": self.smac3_cpu_time_budget,
                    "use_default_config": self.smac3_use_default_config,
                    "min_budget": self.smac3_min_budget,
                    "max_budget": self.smac3_max_budget,
                    "solver_calls": self.smac3_number_of_trials
                    or configurator_settings["solver_calls"],
                }
            )
            # Do not pass None values to SMAC3, its Scenario resolves default settings
            configurator_settings = {
                key: value
                for key, value in configurator_settings.items()
                if value is not None
            }
        elif configurator_name == cim.IRACE.__name__:
            # Return all settings from the IRACE section
            configurator_settings.update(
                {
                    "solver_calls": self.irace_max_experiments,
                    "max_time": self.irace_max_time,
                    "first_test": self.irace_first_test,
                    "mu": self.irace_mu,
                    "max_iterations": self.irace_max_iterations
                    or configurator_settings["max_iterations"],
                }
            )
            if (
                configurator_settings["solver_calls"] == 0
                and configurator_settings["max_time"] == 0
            ):  # Default to base
                configurator_settings["solver_calls"] = (
                    self.configurator_solver_call_budget
                )
        elif configurator_name == cim.ParamILS.__name__:
            configurator_settings.update(
                {
                    "tuner_timeout": self.paramils_cpu_time_budget,
                    "min_runs": self.paramils_min_runs,
                    "max_runs": self.paramils_max_runs,
                    "focused_ils": self.paramils_focused_approach,
                    "initial_configurations": self.paramils_number_initial_configurations,
                    "random_restart": self.paramils_random_restart,
                    "cli_cores": self.paramils_cli_cores,
                    "use_cpu_time_in_tunertime": self.paramils_use_cpu_time_in_tunertime,
                    "max_iterations": self.paramils_max_iterations
                    or configurator_settings["max_iterations"],
                }
            )
        return configurator_settings

    @staticmethod
    def check_settings_changes(
        cur_settings: Settings, prev_settings: Settings, verbose: bool = True
    ) -> bool:
        """Check if there are changes between the previous and the current settings.

        Prints any section changes, printing None if no setting was found.

        Args:
          cur_settings: The current settings
          prev_settings: The previous settings
          verbose: Verbosity of the function

        Returns:
          True iff there are changes.
        """
        cur_dict = cur_settings.__settings._sections
        prev_dict = prev_settings.__settings._sections

        cur_sections_set = set(cur_dict.keys())
        prev_sections_set = set(prev_dict.keys())

        sections_remained = cur_sections_set & prev_sections_set
        option_changed = False
        for section in sections_remained:
            printed_section = False
            names = set(cur_dict[section].keys()) | set(prev_dict[section].keys())
            if (
                section == "general" and "seed" in names
            ):  # Do not report on the seed, is supposed to change
                names.remove("seed")
            for name in names:
                # if name is not present in one of the two dicts, get None as placeholder
                cur_val = cur_dict[section].get(name, None)
                prev_val = prev_dict[section].get(name, None)

                # If cur val is None, it is default
                if cur_val is not None and cur_val != prev_val:
                    if not option_changed and verbose:  # Print the initial
                        print("[INFO] The following attributes/options have changed:")
                        option_changed = True

                    # do we have yet to print the section?
                    if not printed_section and verbose:
                        print(f"  - In the section '{section}':")
                        printed_section = True

                    # print actual change
                    if verbose:
                        print(f"    · '{name}' changed from '{prev_val}' to '{cur_val}'")

        return option_changed
