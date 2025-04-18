"""Classes and Enums to control settings."""
from __future__ import annotations
import configparser
from enum import Enum
import ast
from pathlib import Path
from pathlib import PurePath

from runrunner import Runner

from sparkle.types import SparkleObjective, resolve_objective
from sparkle.types.objective import PAR
from sparkle.configurator.configurator import Configurator
from sparkle.configurator import implementations as cim
from sparkle.platform.cli_types import VerbosityLevel


class SettingState(Enum):
    """Enum of possible setting states."""

    NOT_SET = 0
    DEFAULT = 1
    FILE = 2
    CMD_LINE = 3


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

    # Default settings path
    DEFAULT_settings_path = PurePath(cwd_prefix / DEFAULT_settings_dir / __settings_file)
    DEFAULT_reference_dir = DEFAULT_settings_dir / "Reference_Lists"

    # Default library pathing
    DEFAULT_components = lib_prefix / "Components"

    # Example settings path
    DEFAULT_example_settings_path = PurePath(DEFAULT_components / "sparkle_settings.ini")

    # Runsolver component
    DEFAULT_runsolver_dir = DEFAULT_components / "runsolver" / "src"
    DEFAULT_runsolver_exec = DEFAULT_runsolver_dir / "runsolver"

    # Ablation component
    DEFAULT_ablation_dir = DEFAULT_components / "ablationAnalysis-0.9.4"
    DEFAULT_ablation_exec = DEFAULT_ablation_dir / "ablationAnalysis"
    DEFAULT_ablation_validation_exec = DEFAULT_ablation_dir / "ablationValidation"

    # Report component
    DEFAULT_latex_source = DEFAULT_components / "Sparkle-latex-source"
    DEFAULT_latex_bib = DEFAULT_latex_source / "SparkleReport.bib"

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
    DEFAULT_configuration_output_raw = DEFAULT_configuration_output / rawdata_dir
    DEFAULT_configuration_output_analysis = DEFAULT_configuration_output / analysis_dir
    DEFAULT_selection_output_raw = DEFAULT_selection_output / rawdata_dir
    DEFAULT_selection_output_analysis = DEFAULT_selection_output / analysis_dir
    DEFAULT_parallel_portfolio_output_raw =\
        DEFAULT_parallel_portfolio_output / rawdata_dir
    DEFAULT_parallel_portfolio_output_analysis =\
        DEFAULT_parallel_portfolio_output / analysis_dir

    # Old default output dirs which should be part of something else
    DEFAULT_feature_data = DEFAULT_output / "Feature_Data"
    DEFAULT_performance_data = DEFAULT_output / "Performance_Data"

    # Collection of all working dirs for platform
    DEFAULT_working_dirs = [
        DEFAULT_solver_dir, DEFAULT_instance_dir, DEFAULT_extractor_dir,
        DEFAULT_output, DEFAULT_configuration_output,
        DEFAULT_selection_output,
        DEFAULT_tmp_output, DEFAULT_log_output,
        DEFAULT_feature_data, DEFAULT_performance_data,
        DEFAULT_settings_dir, DEFAULT_reference_dir,
    ]

    # Old default file paths from GV which should be turned into variables
    DEFAULT_feature_data_path =\
        DEFAULT_feature_data / "feature_data.csv"
    DEFAULT_performance_data_path =\
        DEFAULT_performance_data / "performance_data.csv"

    # Constant default values
    DEFAULT_general_sparkle_objective = PAR(10)
    DEFAULT_general_sparkle_configurator = cim.SMAC2.__name__
    DEFAULT_general_target_cutoff_time = 60
    DEFAULT_general_extractor_cutoff_time = 60
    DEFAULT_number_of_jobs_in_parallel = 25
    DEFAULT_general_verbosity = VerbosityLevel.STANDARD
    DEFAULT_general_check_interval = 10
    DEFAULT_general_run_on = "local"

    DEFAULT_configurator_number_of_runs = 25
    DEFAULT_configurator_solver_calls = 100
    DEFAULT_configurator_maximum_iterations = None

    # Default SMAC2 settings
    DEFAULT_smac2_wallclock_time = None
    DEFAULT_smac2_cpu_time = None
    DEFAULT_smac2_target_cutoff_length = "max"
    DEFAULT_smac2_use_cpu_time_in_tunertime = None
    DEFAULT_smac2_cli_cores = None
    DEFAULT_smac2_max_iterations = None

    # Default SMAC3 settings
    DEFAULT_smac3_number_of_runs = None
    DEFAULT_smac3_facade = "AlgorithmConfigurationFacade"
    DEFAULT_smac3_facade_max_ratio = None
    DEFAULT_smac3_crash_cost = None
    DEFAULT_smac3_termination_cost_threshold = None
    DEFAULT_smac3_walltime_limit = None
    DEFAULT_smac3_cputime_limit = None
    DEFAULT_smac3_use_default_config = None
    DEFAULT_smac3_min_budget = None
    DEFAULT_smac3_max_budget = None

    # Default IRACE settings
    DEFAULT_irace_max_time = 0  # IRACE equivalent of None in this case
    DEFAULT_irace_max_experiments = 0
    DEFAULT_irace_first_test = None
    DEFAULT_irace_mu = None
    DEFAULT_irace_max_iterations = None

    # Default ParamILS settings
    DEFAULT_paramils_focused_ils = False
    DEFAULT_paramils_tuner_timeout = None
    DEFAULT_paramils_focused_approach = None
    DEFAULT_paramils_min_runs = None
    DEFAULT_paramils_max_runs = None
    DEFAULT_paramils_random_restart = None
    DEFAULT_paramils_initial_configurations = None
    DEFAULT_paramils_use_cpu_time_in_tunertime = None
    DEFAULT_paramils_cli_cores = None
    DEFAULT_paramils_max_iterations = None

    DEFAULT_slurm_max_parallel_runs_per_node = 8
    DEFAULT_slurm_job_submission_limit = None
    DEFAULT_slurm_job_prepend = ""

    DEFAULT_ablation_racing = False

    DEFAULT_parallel_portfolio_check_interval = 4
    DEFAULT_parallel_portfolio_num_seeds_per_solver = 1

    # Default selection settings
    DEFAULT_selector_class = "MultiClassClassifier"
    DEFAULT_selector_model = "RandomForestClassifier"

    def __init__(self: Settings, file_path: PurePath = None) -> None:
        """Initialise a settings object."""
        # Settings 'dictionary' in configparser format
        self.__settings = configparser.ConfigParser()

        # Setting flags
        self.__general_sparkle_objective_set = SettingState.NOT_SET
        self.__general_sparkle_configurator_set = SettingState.NOT_SET
        self.__general_target_cutoff_time_set = SettingState.NOT_SET
        self.__general_extractor_cutoff_time_set = SettingState.NOT_SET
        self.__general_verbosity_set = SettingState.NOT_SET
        self.__general_check_interval_set = SettingState.NOT_SET

        self.__config_solver_calls_set = SettingState.NOT_SET
        self.__config_number_of_runs_set = SettingState.NOT_SET
        self.__config_max_iterations_set = SettingState.NOT_SET

        self.__smac2_wallclock_time_set = SettingState.NOT_SET
        self.__smac2_cpu_time_set = SettingState.NOT_SET
        self.__smac2_use_cpu_time_in_tunertime_set = SettingState.NOT_SET
        self.__smac2_cli_cores_set = SettingState.NOT_SET
        self.__smac2_max_iterations_set = SettingState.NOT_SET
        self.__smac2_target_cutoff_length_set = SettingState.NOT_SET

        self.__smac3_number_of_trials_set = SettingState.NOT_SET
        self.__smac3_smac_facade_set = SettingState.NOT_SET
        self.__smac3_facade_max_ratio_set = SettingState.NOT_SET
        self.__smac3_crash_cost_set = SettingState.NOT_SET
        self.__smac3_termination_cost_threshold_set = SettingState.NOT_SET
        self.__smac3_walltime_limit_set = SettingState.NOT_SET
        self.__smac3_cputime_limit_set = SettingState.NOT_SET
        self.__smac3_use_default_config_set = SettingState.NOT_SET
        self.__smac3_min_budget_set = SettingState.NOT_SET
        self.__smac3_max_budget_set = SettingState.NOT_SET

        self.__irace_max_time_set = SettingState.NOT_SET
        self.__irace_max_experiments_set = SettingState.NOT_SET
        self.__irace_first_test_set = SettingState.NOT_SET
        self.__irace_mu_set = SettingState.NOT_SET
        self.__irace_max_iterations_set = SettingState.NOT_SET

        self.__paramils_min_runs_set = SettingState.NOT_SET
        self.__paramils_max_runs_set = SettingState.NOT_SET
        self.__paramils_tuner_timeout_set = SettingState.NOT_SET
        self.__paramils_focused_approach_set = SettingState.NOT_SET
        self.__paramils_random_restart_set = SettingState.NOT_SET
        self.__paramils_initial_configurations_set = SettingState.NOT_SET
        self.__paramils_use_cpu_time_in_tunertime_set = SettingState.NOT_SET
        self.__paramils_cli_cores_set = SettingState.NOT_SET
        self.__paramils_max_iterations_set = SettingState.NOT_SET

        self.__run_on_set = SettingState.NOT_SET
        self.__number_of_jobs_in_parallel_set = SettingState.NOT_SET
        self.__ablation_racing_flag_set = SettingState.NOT_SET

        self.__parallel_portfolio_check_interval_set = SettingState.NOT_SET
        self.__parallel_portfolio_num_seeds_per_solver_set = SettingState.NOT_SET

        self.__selection_model_set = SettingState.NOT_SET
        self.__selection_class_set = SettingState.NOT_SET

        self.__slurm_max_parallel_runs_per_node_set = SettingState.NOT_SET
        self.__slurm_job_prepend_set = SettingState.NOT_SET
        self.__slurm_job_submission_limit_set = SettingState.NOT_SET

        self.__general_sparkle_configurator = None

        self.__slurm_extra_options_set = dict()

        if file_path is None:
            # Initialise settings from default file path
            self.read_settings_ini()
        else:
            # Initialise settings from a given file path
            self.read_settings_ini(file_path)

    def read_settings_ini(self: Settings, file_path: PurePath = DEFAULT_settings_path,
                          state: SettingState = SettingState.FILE) -> None:
        """Read the settings from an INI file."""
        # Read file
        file_settings = configparser.ConfigParser()
        file_settings.read(file_path)

        # Set internal settings based on data read from FILE if they were read
        # successfully
        if file_settings.sections() != []:
            section = "general"
            option_names = ("objectives", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = [resolve_objective(obj) for obj in
                             file_settings.get(section, option).split(",")]
                    self.set_general_sparkle_objectives(value, state)
                    file_settings.remove_option(section, option)

            # Comma so python understands it's a tuple...
            option_names = ("configurator", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.get(section, option)
                    self.set_general_sparkle_configurator(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("target_cutoff_time",
                            "cutoff_time_each_solver_call")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_general_target_cutoff_time(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("extractor_cutoff_time",
                            "cutoff_time_each_feature_computation")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_general_extractor_cutoff_time(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("run_on", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.get(section, option)
                    self.set_run_on(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("verbosity", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = VerbosityLevel.from_string(
                        file_settings.get(section, option))
                    self.set_general_verbosity(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("check_interval", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = int(file_settings.get(section, option))
                    self.set_general_check_interval(value, state)
                    file_settings.remove_option(section, option)

            section = "configuration"
            option_names = ("solver_calls", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_configurator_solver_calls(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("number_of_runs", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_configurator_number_of_runs(value, state)
                    file_settings.remove_option(section, option)

            option_name = "max_iterations"
            if file_settings.has_option(section, option_name):
                value = file_settings.getint(section, option_name)
                self.set_configurator_max_iterations(value, state)
                file_settings.remove_option(section, option_name)

            section = "smac2"
            option_names = ("wallclock_time", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_smac2_wallclock_time(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("cpu_time", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_smac2_cpu_time(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("target_cutoff_length", "each_run_cutoff_length")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.get(section, option)
                    self.set_smac2_target_cutoff_length(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("use_cpu_time_in_tunertime", "countSMACTimeAsTunerTime")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getboolean(section, option)
                    self.set_smac2_use_cpu_time_in_tunertime(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("cli_cores", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_smac2_cli_cores(value, state)
                    file_settings.remove_option(section, option)

            options_names = ("iteration_limit", "numIterations", "numberOfIterations",
                             "max_iterations")
            for option in options_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_smac2_max_iterations(value, state)
                    file_settings.remove_option(section, option)

            section = "smac3"

            option_names = ("n_trials", "number_of_trials", "solver_calls")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_smac3_number_of_trials(value, state)
                    file_settings.remove_option(section, option)

            options_names = ("facade", "smac_facade", "smac3_facade")
            for option in options_names:
                if file_settings.has_option(section, option):
                    value = file_settings.get(section, option)
                    self.set_smac3_smac_facade(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("max_ratio", "facade_max_ratio", "initial_trials_max_ratio")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getfloat(section, option)
                    self.set_smac3_facade_max_ratio(value, state)
                    file_settings.remove_option(section, option)

            options_names = ("crash_cost", )
            for option in options_names:
                if file_settings.has_option(section, option):
                    value = file_settings.get(section, option)
                    self.set_smac3_crash_cost(value, state)
                    file_settings.remove_option(section, option)

            options_names = ("termination_cost_threshold", )
            for option in options_names:
                if file_settings.has_option(section, option):
                    value = file_settings.get(section, option)
                    self.set_smac3_termination_cost_threshold(value, state)
                    file_settings.remove_option(section, option)

            options_names = ("walltime_limit", "wallclock_time")
            for option in options_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getfloat(section, option)
                    self.set_smac3_walltime_limit(value, state)
                    file_settings.remove_option(section, option)

            options_names = ("cputime_limit", )
            for option in options_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getfloat(section, option)
                    self.set_smac3_cputime_limit(value, state)
                    file_settings.remove_option(section, option)

            options_names = ("use_default_config", )
            for option in options_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getboolean(section, option)
                    self.set_smac3_use_default_config(value, state)
                    file_settings.remove_option(section, option)

            options_names = ("min_budget", )
            for option in options_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getfloat(section, option)
                    self.set_smac3_min_budget(value, state)
                    file_settings.remove_option(section, option)

            options_names = ("max_budget", )
            for option in options_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getfloat(section, option)
                    self.set_smac3_max_budget(value, state)
                    file_settings.remove_option(section, option)

            section = "irace"
            option_names = ("max_time", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_irace_max_time(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("max_experiments", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_irace_max_experiments(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("first_test", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_irace_first_test(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("mu", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_irace_mu(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("nb_iterations", "iterations", "max_iterations")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_irace_max_iterations(value, state)
                    file_settings.remove_option(section, option)

            section = "paramils"

            option_names = ("min_runs", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_paramils_min_runs(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("max_runs", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_paramils_max_runs(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("cputime_limit", "cputime_limit", "tunertime_limit",
                            "tuner_timeout", "tunerTimeout")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_paramils_tuner_timeout(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("random_restart", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getfloat(section, option)
                    self.set_paramils_random_restart(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("focused_approach", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getboolean(section, option)
                    self.set_paramils_focused_approach(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("use_cpu_time_in_tunertime", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getboolean(section, option)
                    self.set_paramils_use_cpu_time_in_tunertime(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("cli_cores", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_paramils_cli_cores(value, state)
                    file_settings.remove_option(section, option)

            options_names = ("iteration_limit", "numIterations", "numberOfIterations",
                             "max_iterations")
            for option in options_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_paramils_max_iterations(value, state)
                    file_settings.remove_option(section, option)

            section = "selection"

            option_names = ("selector_class", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.get(section, option)
                    self.set_selection_class(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("selector_model")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.get(section, option)
                    self.set_selection_model(value, state)
                    file_settings.remove_option(section, option)

            section = "slurm"
            option_names = ("number_of_jobs_in_parallel", "num_job_in_parallel")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_number_of_jobs_in_parallel(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("max_parallel_runs_per_node", "clis_per_node")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_slurm_max_parallel_runs_per_node(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("job_submission_limit", "max_jobs_submit")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_slurm_job_submission_limit(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("job_prepend", "prepend", "prepend_script")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.get(section, option)
                    self.set_slurm_job_prepend(value, state)
                    file_settings.remove_option(section, option)

            section = "ablation"
            option_names = ("racing", "ablation_racing")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getboolean(section, option)
                    self.set_ablation_racing_flag(value, state)
                    file_settings.remove_option(section, option)

            section = "parallel_portfolio"
            option_names = ("check_interval", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = int(file_settings.get(section, option))
                    self.set_parallel_portfolio_check_interval(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("num_seeds_per_solver", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = int(file_settings.get(section, option))
                    self.set_parallel_portfolio_number_of_seeds_per_solver(value, state)
                    file_settings.remove_option(section, option)

            # TODO: Report on any unknown settings that were read
            sections = file_settings.sections()

            for section in sections:
                for option in file_settings[section]:
                    # TODO: Should check the options are valid Slurm options
                    if section == "slurm":
                        value = file_settings.get(section, option)
                        self.add_slurm_extra_option(option, value, state)
                    else:
                        print(f'Unrecognised section - option combination: "{section} '
                              f'{option}" in file {file_path} ignored')

        # Print error if unable to read the settings
        elif Path(file_path).exists():
            print(f"ERROR: Failed to read settings from {file_path} The file may have "
                  "been empty or be in another format than INI. Default Setting values "
                  "will be used.")

    def write_used_settings(self: Settings) -> None:
        """Write the used settings to the default locations."""
        # Write to latest settings file
        self.write_settings_ini(self.DEFAULT_settings_dir / "latest.ini")

    def write_settings_ini(self: Settings, file_path: Path) -> None:
        """Write the settings to an INI file."""
        # Create needed directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        slurm_extra_section_options = None
        if self.__settings.has_section("slurm_extra"):
            # Slurm extra options are not written as a seperate section
            slurm_extra_section_options = {}
            for key in self.__settings["slurm_extra"]:
                self.__settings["slurm"][key] = self.__settings["slurm_extra"][key]
                slurm_extra_section_options[key] = self.__settings["slurm_extra"][key]
            self.__settings.remove_section("slurm_extra")
        # We do not write None values
        removed = []
        for section in self.__settings.sections():
            for option in self.__settings[section]:
                try:
                    if ast.literal_eval(str(self.__settings[section][option])) is None:
                        del self.__settings[section][option]
                        removed.append((section, option))
                except Exception:
                    pass
        # Write the settings to file
        with file_path.open("w") as settings_file:
            self.__settings.write(settings_file)
        # Rebuild slurm extra if needed
        if slurm_extra_section_options is not None:
            self.__settings.add_section("slurm_extra")
            for key in slurm_extra_section_options:
                self.__settings["slurm_extra"][key] = slurm_extra_section_options[key]
        # Rebuild None if needed
        for section, option in removed:
            self.__settings[section][option] = "None"

    def __init_section(self: Settings, section: str) -> None:
        if section not in self.__settings:
            self.__settings[section] = {}

    @staticmethod
    def __check_setting_state(current_state: SettingState,
                              new_state: SettingState, name: str) -> bool:
        change_setting_ok = True

        if current_state == SettingState.FILE and new_state == SettingState.DEFAULT:
            change_setting_ok = False
            print(f"Warning: Attempting to overwrite setting for {name} with default "
                  "value; keeping the value read from file!")
        elif (current_state == SettingState.CMD_LINE
              and new_state == SettingState.DEFAULT):
            change_setting_ok = False
            print(f"Warning: Attempting to overwrite setting for {name} with default "
                  "value; keeping the value read from command line!")
        elif current_state == SettingState.CMD_LINE and new_state == SettingState.FILE:
            change_setting_ok = False
            print(f"Warning: Attempting to overwrite setting for {name} with value from "
                  "file; keeping the value read from command line!")

        return change_setting_ok

    # General settings ###
    def set_general_sparkle_objectives(
            self: Settings,
            value: list[SparkleObjective] = [DEFAULT_general_sparkle_objective, ],
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the sparkle objective."""
        section = "general"
        name = "objectives"

        if value is not None and self.__check_setting_state(
                self.__general_sparkle_objective_set, origin, name):
            if isinstance(value, list):
                value = ",".join([str(obj) for obj in value])
            else:
                value = str(value)

            # Append standard Sparkle Objectives
            if "status" not in value:
                value += ",status:metric"
            if "cpu_time" not in value:
                value += ",cpu_time:metric"
            if "wall_time" not in value:
                value += ",wall_time:metric"
            if "memory" not in value:
                value += ",memory:metric"

            self.__init_section(section)
            self.__general_sparkle_objective_set = origin
            self.__settings[section][name] = value

    def get_general_sparkle_objectives(
            self: Settings,
            filter_metric: bool = False) -> list[SparkleObjective]:
        """Return the Sparkle objectives."""
        if self.__general_sparkle_objective_set == SettingState.NOT_SET:
            self.set_general_sparkle_objectives()

        objectives = [resolve_objective(obj)
                      for obj in self.__settings["general"]["objectives"].split(",")]

        if filter_metric:
            return [obj for obj in objectives if not obj.metric]

        return objectives

    def set_general_sparkle_configurator(
            self: Settings,
            value: str = DEFAULT_general_sparkle_configurator,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the Sparkle configurator."""
        section = "general"
        name = "configurator"
        if value is not None and self.__check_setting_state(
                self.__general_sparkle_configurator_set, origin, name):
            self.__init_section(section)
            self.__general_sparkle_configurator_set = origin
            self.__settings[section][name] = value

    def get_general_sparkle_configurator(self: Settings) -> Configurator:
        """Return the configurator init method."""
        if self.__general_sparkle_configurator_set == SettingState.NOT_SET:
            self.set_general_sparkle_configurator()
        configurator_var = self.__settings["general"]["configurator"]
        if (self.__general_sparkle_configurator is None
                or self.__general_sparkle_configurator.name != configurator_var):
            configurator_subclass =\
                cim.resolve_configurator(self.__settings["general"]["configurator"])
            if configurator_subclass is not None:
                self.__general_sparkle_configurator = configurator_subclass(
                    base_dir=Path(),
                    output_path=Settings.DEFAULT_configuration_output_raw)
            else:
                print("WARNING: Configurator class name not recognised: "
                      f'{self.__settings["general"]["configurator"]}. '
                      "Configurator not set.")
        return self.__general_sparkle_configurator

    def set_general_target_cutoff_time(
            self: Settings, value: int = DEFAULT_general_target_cutoff_time,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the cutoff time in seconds for target algorithms."""
        section = "general"
        name = "target_cutoff_time"

        if value is not None and self.__check_setting_state(
                self.__general_target_cutoff_time_set, origin, name):
            self.__init_section(section)
            self.__general_target_cutoff_time_set = origin
            self.__settings[section][name] = str(value)

    def get_general_target_cutoff_time(self: Settings) -> int:
        """Return the cutoff time in seconds for target algorithms."""
        if self.__general_target_cutoff_time_set == SettingState.NOT_SET:
            self.set_general_target_cutoff_time()
        return int(self.__settings["general"]["target_cutoff_time"])

    def set_general_extractor_cutoff_time(
            self: Settings, value: int = DEFAULT_general_extractor_cutoff_time,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the cutoff time in seconds for feature extraction."""
        section = "general"
        name = "extractor_cutoff_time"

        if value is not None and self.__check_setting_state(
                self.__general_extractor_cutoff_time_set, origin, name):
            self.__init_section(section)
            self.__general_extractor_cutoff_time_set = origin
            self.__settings[section][name] = str(value)

    def get_general_extractor_cutoff_time(self: Settings) -> int:
        """Return the cutoff time in seconds for feature extraction."""
        if self.__general_extractor_cutoff_time_set == SettingState.NOT_SET:
            self.set_general_extractor_cutoff_time()
        return int(self.__settings["general"]["extractor_cutoff_time"])

    def set_number_of_jobs_in_parallel(
            self: Settings, value: int = DEFAULT_number_of_jobs_in_parallel,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the number of runs Sparkle can do in parallel."""
        section = "slurm"
        name = "number_of_jobs_in_parallel"

        if value is not None and self.__check_setting_state(
                self.__number_of_jobs_in_parallel_set, origin, name):
            self.__init_section(section)
            self.__number_of_jobs_in_parallel_set = origin
            self.__settings[section][name] = str(value)

    def get_number_of_jobs_in_parallel(self: Settings) -> int:
        """Return the number of runs Sparkle can do in parallel."""
        if self.__number_of_jobs_in_parallel_set == SettingState.NOT_SET:
            self.set_number_of_jobs_in_parallel()

        return int(self.__settings["slurm"]["number_of_jobs_in_parallel"])

    def set_general_verbosity(
            self: Settings, value: VerbosityLevel = DEFAULT_general_verbosity,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the general verbosity to use."""
        section = "general"
        name = "verbosity"

        if value is not None and self.__check_setting_state(
                self.__general_verbosity_set, origin, name):
            self.__init_section(section)
            self.__general_verbosity_set = origin
            self.__settings[section][name] = value.name

    def get_general_verbosity(self: Settings) -> VerbosityLevel:
        """Return the general verbosity."""
        if self.__general_verbosity_set == SettingState.NOT_SET:
            self.set_general_verbosity()

        return VerbosityLevel.from_string(
            self.__settings["general"]["verbosity"])

    def set_general_check_interval(
            self: Settings,
            value: int = DEFAULT_general_check_interval,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the general check interval."""
        section = "general"
        name = "check_interval"

        if value is not None and self.__check_setting_state(
                self.__general_check_interval_set, origin, name):
            self.__init_section(section)
            self.__general_check_interval_set = origin
            self.__settings[section][name] = str(value)

    def get_general_check_interval(self: Settings) -> int:
        """Return the general check interval."""
        if self.__general_check_interval_set == SettingState.NOT_SET:
            self.set_general_check_interval()

        return int(self.__settings["general"]["check_interval"])

    # Configuration settings General ###

    def get_configurator_settings(self: Settings,
                                  configurator_name: str) -> dict[str, any]:
        """Return the configurator settings."""
        configurator_settings = {
            "number_of_runs": self.get_configurator_number_of_runs(),
            "solver_calls": self.get_configurator_solver_calls(),
            "cutoff_time": self.get_general_target_cutoff_time(),
            "max_iterations": self.get_configurator_max_iterations()
        }
        # In the settings below, we default to the configurator general settings if no
        # specific configurator settings are given, by using the [None] or [Value]
        if configurator_name == cim.SMAC2.__name__:
            # Return all settings from the SMAC2 section
            configurator_settings.update({
                "cpu_time": self.get_smac2_cpu_time(),
                "wallclock_time": self.get_smac2_wallclock_time(),
                "target_cutoff_length": self.get_smac2_target_cutoff_length(),
                "use_cpu_time_in_tunertime": self.get_smac2_use_cpu_time_in_tunertime(),
                "cli_cores": self.get_smac2_cli_cores(),
                "max_iterations": self.get_smac2_max_iterations()
                or configurator_settings["max_iterations"],
            })
        elif configurator_name == cim.SMAC3.__name__:
            # Return all settings from the SMAC3 section
            del configurator_settings["max_iterations"]  # SMAC3 does not have this?
            configurator_settings.update({
                "smac_facade": self.get_smac3_smac_facade(),
                "max_ratio": self.get_smac3_facade_max_ratio(),
                "crash_cost": self.get_smac3_crash_cost(),
                "termination_cost_threshold":
                self.get_smac3_termination_cost_threshold(),
                "walltime_limit": self.get_smac3_walltime_limit(),
                "cputime_limit": self.get_smac3_cputime_limit(),
                "use_default_config": self.get_smac3_use_default_config(),
                "min_budget": self.get_smac3_min_budget(),
                "max_budget": self.get_smac3_max_budget(),
                "solver_calls": self.get_smac3_number_of_trials()
                or configurator_settings["solver_calls"],
            })
            # Do not pass None values to SMAC3, it Scenario resolves default settings
            configurator_settings = {key: value
                                     for key, value in configurator_settings.items()
                                     if value is not None}
        elif configurator_name == cim.IRACE.__name__:
            # Return all settings from the IRACE section
            configurator_settings.update({
                "solver_calls": self.get_irace_max_experiments(),
                "max_time": self.get_irace_max_time(),
                "first_test": self.get_irace_first_test(),
                "mu": self.get_irace_mu(),
                "max_iterations": self.get_irace_max_iterations()
                or configurator_settings["max_iterations"],
            })
            if (configurator_settings["solver_calls"] == 0
                    and configurator_settings["max_time"] == 0):  # Default to base
                configurator_settings["solver_calls"] =\
                    self.get_configurator_solver_calls()
        elif configurator_name == cim.ParamILS.__name__:
            configurator_settings.update({
                "tuner_timeout": self.get_paramils_tuner_timeout(),
                "min_runs": self.get_paramils_min_runs(),
                "max_runs": self.get_paramils_max_runs(),
                "focused_ils": self.get_paramils_focused_approach(),
                "initial_configurations": self.get_paramils_initial_configurations(),
                "random_restart": self.get_paramils_random_restart(),
                "cli_cores": self.get_paramils_cli_cores(),
                "use_cpu_time_in_tunertime":
                self.get_paramils_use_cpu_time_in_tunertime(),
                "max_iterations": self.set_paramils_max_iterations()
                or configurator_settings["max_iterations"],
            })
        return configurator_settings

    def set_configurator_solver_calls(
            self: Settings, value: int = DEFAULT_configurator_solver_calls,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the number of solver calls."""
        section = "configuration"
        name = "solver_calls"

        if value is not None and self.__check_setting_state(
                self.__config_solver_calls_set, origin, name):
            self.__init_section(section)
            self.__config_solver_calls_set = origin
            self.__settings[section][name] = str(value)

    def get_configurator_solver_calls(self: Settings) -> int | None:
        """Return the maximum number of solver calls the configurator can do."""
        if self.__config_solver_calls_set == SettingState.NOT_SET:
            self.set_configurator_solver_calls()

        return int(self.__settings["configuration"]["solver_calls"])

    def set_configurator_number_of_runs(
            self: Settings, value: int = DEFAULT_configurator_number_of_runs,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the number of configuration runs."""
        section = "configuration"
        name = "number_of_runs"

        if value is not None and self.__check_setting_state(
                self.__config_number_of_runs_set, origin, name):
            self.__init_section(section)
            self.__config_number_of_runs_set = origin
            self.__settings[section][name] = str(value)

    def get_configurator_number_of_runs(self: Settings) -> int:
        """Return the number of configuration runs."""
        if self.__config_number_of_runs_set == SettingState.NOT_SET:
            self.set_configurator_number_of_runs()

        return int(self.__settings["configuration"]["number_of_runs"])

    def set_configurator_max_iterations(
            self: Settings, value: int = DEFAULT_configurator_maximum_iterations,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the number of configuration runs."""
        section = "configuration"
        name = "max_iterations"

        if self.__check_setting_state(
                self.__config_max_iterations_set, origin, name):
            self.__init_section(section)
            self.__config_max_iterations_set = origin
            self.__settings[section][name] = str(value)

    def get_configurator_max_iterations(self: Settings) -> int | None:
        """Get the maximum number of configurator iterations."""
        if self.__config_max_iterations_set == SettingState.NOT_SET:
            self.set_configurator_max_iterations()
        max_iterations = self.__settings["configuration"]["max_iterations"]
        return int(max_iterations) if max_iterations.isdigit() else None

    # Configuration: SMAC2 specific settings ###

    def set_smac2_wallclock_time(
            self: Settings, value: int = DEFAULT_smac2_wallclock_time,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the budget per configuration run in seconds (wallclock)."""
        section = "smac2"
        name = "wallclock_time"

        if self.__check_setting_state(
                self.__smac2_wallclock_time_set, origin, name):
            self.__init_section(section)
            self.__smac2_wallclock_time_set = origin
            self.__settings[section][name] = str(value)

    def get_smac2_wallclock_time(self: Settings) -> int | None:
        """Return the budget per configuration run in seconds (wallclock)."""
        if self.__smac2_wallclock_time_set == SettingState.NOT_SET:
            self.set_smac2_wallclock_time()
        wallclock_time = self.__settings["smac2"]["wallclock_time"]
        return int(wallclock_time) if wallclock_time.isdigit() else None

    def set_smac2_cpu_time(
            self: Settings, value: int = DEFAULT_smac2_cpu_time,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the budget per configuration run in seconds (cpu)."""
        section = "smac2"
        name = "cpu_time"

        if self.__check_setting_state(
                self.__smac2_cpu_time_set, origin, name):
            self.__init_section(section)
            self.__smac2_cpu_time_set = origin
            self.__settings[section][name] = str(value)

    def get_smac2_cpu_time(self: Settings) -> int | None:
        """Return the budget per configuration run in seconds (cpu)."""
        if self.__smac2_cpu_time_set == SettingState.NOT_SET:
            self.set_smac2_cpu_time()
        cpu_time = self.__settings["smac2"]["cpu_time"]
        return int(cpu_time) if cpu_time.isdigit() else None

    def set_smac2_target_cutoff_length(
            self: Settings, value: str = DEFAULT_smac2_target_cutoff_length,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the target algorithm cutoff length."""
        section = "smac2"
        name = "target_cutoff_length"

        if value is not None and self.__check_setting_state(
                self.__smac2_target_cutoff_length_set, origin, name):
            self.__init_section(section)
            self.__smac2_target_cutoff_length_set = origin
            self.__settings[section][name] = str(value)

    def get_smac2_target_cutoff_length(self: Settings) -> str:
        """Return the target algorithm cutoff length.

        'A domain specific measure of when the algorithm should consider itself done.'

        Returns:
            The target algorithm cutoff length.
        """
        if self.__smac2_target_cutoff_length_set == SettingState.NOT_SET:
            self.set_smac2_target_cutoff_length()
        return self.__settings["smac2"]["target_cutoff_length"]

    def set_smac2_use_cpu_time_in_tunertime(
            self: Settings, value: bool = DEFAULT_smac2_use_cpu_time_in_tunertime,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set whether to use CPU time in tunertime."""
        section = "smac2"
        name = "use_cpu_time_in_tunertime"

        if self.__check_setting_state(
                self.__smac2_use_cpu_time_in_tunertime_set, origin, name):
            self.__init_section(section)
            self.__smac2_use_cpu_time_in_tunertime_set = origin
            self.__settings[section][name] = str(value)

    def get_smac2_use_cpu_time_in_tunertime(self: Settings) -> bool:
        """Return whether to use CPU time in tunertime."""
        if self.__smac2_use_cpu_time_in_tunertime_set == SettingState.NOT_SET:
            self.set_smac2_use_cpu_time_in_tunertime()
        return ast.literal_eval(self.__settings["smac2"]["use_cpu_time_in_tunertime"])

    def set_smac2_cli_cores(
            self: Settings, value: int = DEFAULT_smac2_cli_cores,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the number of cores to use for SMAC2 CLI."""
        section = "smac2"
        name = "cli_cores"

        if self.__check_setting_state(
                self.__smac2_cli_cores_set, origin, name):
            self.__init_section(section)
            self.__smac2_cli_cores_set = origin
            self.__settings[section][name] = str(value)

    def get_smac2_cli_cores(self: Settings) -> int | None:
        """Number of cores to use to execute runs.

        In other words, the number of requests to run at a given time.
        """
        if self.__smac2_cli_cores_set == SettingState.NOT_SET:
            self.set_smac2_cli_cores()
        cli_cores = self.__settings["smac2"]["cli_cores"]
        return int(cli_cores) if cli_cores.isdigit() else None

    def set_smac2_max_iterations(
            self: Settings, value: int = DEFAULT_smac2_max_iterations,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the maximum number of SMAC2 iterations."""
        section = "smac2"
        name = "max_iterations"

        if self.__check_setting_state(
                self.__smac2_max_iterations_set, origin, name):
            self.__init_section(section)
            self.__smac2_max_iterations_set = origin
            self.__settings[section][name] = str(value)

    def get_smac2_max_iterations(self: Settings) -> int | None:
        """Get the maximum number of SMAC2 iterations."""
        if self.__smac2_max_iterations_set == SettingState.NOT_SET:
            self.set_smac2_max_iterations()
        max_iterations = self.__settings["smac2"]["max_iterations"]
        return int(max_iterations) if max_iterations.isdigit() else None

    # Configuration: SMAC3 specific settings ###

    def set_smac3_number_of_trials(
            self: Settings, value: int = DEFAULT_smac3_number_of_runs,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the number of SMAC3 trials."""
        section = "smac3"
        name = "number_of_runs"

        if self.__check_setting_state(
                self.__smac3_number_of_trials_set, origin, name):
            self.__init_section(section)
            self.__smac3_number_of_trials_set = origin
            self.__settings[section][name] = str(value)

    def get_smac3_number_of_trials(self: Settings) -> int | None:
        """Return the number of SMAC3 trials (Solver calls).

        'The maximum number of trials (combination of configuration, seed, budget,
        and instance, depending on the task) to run.'
        """
        if self.__smac3_number_of_trials_set == SettingState.NOT_SET:
            self.set_smac3_number_of_trials()
        number_of_runs = self.__settings["smac3"]["number_of_runs"]
        return int(number_of_runs) if number_of_runs.isdigit() else None

    def set_smac3_smac_facade(
            self: Settings, value: str = DEFAULT_smac3_facade,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the SMAC3 facade."""
        section = "smac3"
        name = "facade"

        if self.__check_setting_state(self.__smac3_smac_facade_set, origin, name):
            self.__init_section(section)
            self.__smac3_smac_facade_set = origin
            self.__settings[section][name] = str(value)

    def get_smac3_smac_facade(self: Settings) -> str:
        """Return the SMAC3 facade."""
        if self.__smac3_smac_facade_set == SettingState.NOT_SET:
            self.set_smac3_smac_facade()
        return self.__settings["smac3"]["facade"]

    def set_smac3_facade_max_ratio(
            self: Settings, value: float = DEFAULT_smac3_facade_max_ratio,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the SMAC3 facade max ratio."""
        section = "smac3"
        name = "facade_max_ratio"

        if self.__check_setting_state(
                self.__smac3_facade_max_ratio_set, origin, name):
            self.__init_section(section)
            self.__smac3_facade_max_ratio_set = origin
            self.__settings[section][name] = str(value)

    def get_smac3_facade_max_ratio(self: Settings) -> float:
        """Return the SMAC3 facade max ratio."""
        if self.__smac3_facade_max_ratio_set == SettingState.NOT_SET:
            self.set_smac3_facade_max_ratio()
        return ast.literal_eval(self.__settings["smac3"]["facade_max_ratio"])

    def set_smac3_crash_cost(self: Settings, value: float = DEFAULT_smac3_crash_cost,
                             origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the SMAC3 objective crash cost."""
        section = "smac3"
        name = "crash_cost"

        if self.__check_setting_state(self.__smac3_crash_cost_set, origin, name):
            self.__init_section(section)
            self.__smac3_smac_facade_set = origin
            self.__settings[section][name] = str(value)

    def get_smac3_crash_cost(self: Settings) -> float | list[float]:
        """Get the SMAC3 objective crash cost.

        'crash_cost : float | list[float], defaults to np.inf
        Defines the cost for a failed trial. In case of multi-objective,
        each objective can be associated with a different cost.'
        """
        if self.__smac3_crash_cost_set == SettingState.NOT_SET:
            self.set_smac3_crash_cost()
        return ast.literal_eval(self.__settings["smac3"]["crash_cost"])

    def set_smac3_termination_cost_threshold(
            self: Settings,
            value: float = DEFAULT_smac3_termination_cost_threshold,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the SMAC3 termination cost threshold."""
        section = "smac3"
        name = "termination_cost_threshold"

        if self.__check_setting_state(
                self.__smac3_termination_cost_threshold_set, origin, name):
            self.__init_section(section)
            self.__smac3_termination_cost_threshold_set = origin
            self.__settings[section][name] = str(value)

    def get_smac3_termination_cost_threshold(self: Settings) -> float | list[float]:
        """Get the SMAC3 termination cost threshold.

        'Defines a cost threshold when the optimization should stop. In case of
        multi-objective, each objective *must* be associated with a cost.
        The optimization stops when all objectives crossed the threshold.'
        """
        if self.__smac3_termination_cost_threshold_set == SettingState.NOT_SET:
            self.set_smac3_termination_cost_threshold()
        return ast.literal_eval(self.__settings["smac3"]["termination_cost_threshold"])

    def set_smac3_walltime_limit(
            self: Settings, value: float = DEFAULT_smac3_walltime_limit,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the SMAC3 walltime limit."""
        section = "smac3"
        name = "walltime_limit"

        if self.__check_setting_state(self.__smac3_walltime_limit_set, origin, name):
            self.__init_section(section)
            self.__smac3_walltime_limit_set = origin
            self.__settings[section][name] = str(value)

    def get_smac3_walltime_limit(self: Settings) -> float:
        """Get the SMAC3 walltime limit.

        'The maximum time in seconds that SMAC is allowed to run.'
        """
        if self.__smac3_walltime_limit_set == SettingState.NOT_SET:
            self.set_smac3_walltime_limit()
        return ast.literal_eval(self.__settings["smac3"]["walltime_limit"])

    def set_smac3_cputime_limit(
            self: Settings, value: float = DEFAULT_smac3_cputime_limit,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the SMAC3 CPU time limit."""
        section = "smac3"
        name = "cputime_limit"

        if self.__check_setting_state(self.__smac3_cputime_limit_set, origin, name):
            self.__init_section(section)
            self.__smac3_cputime_limit_set = origin
            self.__settings[section][name] = str(value)

    def get_smac3_cputime_limit(self: Settings) -> float:
        """Get the SMAC3 CPU time limit.

        'The maximum CPU time in seconds that SMAC is allowed to run.'
        """
        if self.__smac3_cputime_limit_set == SettingState.NOT_SET:
            self.set_smac3_cputime_limit()
        return ast.literal_eval(self.__settings["smac3"]["cputime_limit"])

    def set_smac3_use_default_config(
            self: Settings, value: bool = DEFAULT_smac3_use_default_config,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the SMAC3 to use default config."""
        section = "smac3"
        name = "use_default_config"

        if self.__check_setting_state(self.__smac3_use_default_config_set, origin, name):
            self.__init_section(section)
            self.__smac3_use_default_config_set = origin
            self.__settings[section][name] = str(value)

    def get_smac3_use_default_config(self: Settings) -> bool:
        """Get the SMAC3 to use default config.

        'If True, the configspace's default configuration is evaluated in the
        initial design. For historic benchmark reasons, this is False by default.
        Notice, that this will result in n_configs + 1 for the initial design.
        Respecting n_trials, this will result in one fewer evaluated
        configuration in the optimization.'
        """
        if self.__smac3_use_default_config_set == SettingState.NOT_SET:
            self.set_smac3_use_default_config()
        return ast.literal_eval(self.__settings["smac3"]["use_default_config"])

    def set_smac3_min_budget(
            self: Settings, value: int | float = DEFAULT_smac3_min_budget,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the SMAC3 min budget."""
        section = "smac3"
        name = "min_budget"

        if self.__check_setting_state(self.__smac3_min_budget_set, origin, name):
            self.__init_section(section)
            self.__smac3_min_budget_set = origin
            self.__settings[section][name] = str(value)

    def get_smac3_min_budget(self: Settings) -> int | float:
        """Get the SMAC3 min budget.

        'The minimum budget (epochs, subset size, number of instances, ...) that
        is used for the optimization. Use this argument if you use multi-fidelity
        or instance optimization.'
        """
        if self.__smac3_min_budget_set == SettingState.NOT_SET:
            self.set_smac3_min_budget()
        return ast.literal_eval(self.__settings["smac3"]["min_budget"])

    def set_smac3_max_budget(
            self: Settings, value: int | float = DEFAULT_smac3_max_budget,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the SMAC3 max budget."""
        section = "smac3"
        name = "max_budget"

        if self.__check_setting_state(self.__smac3_max_budget_set, origin, name):
            self.__init_section(section)
            self.__smac3_max_budget_set = origin
            self.__settings[section][name] = str(value)

    def get_smac3_max_budget(self: Settings) -> int | float:
        """Get the SMAC3 max budget.

        'The maximum budget (epochs, subset size, number of instances, ...) that
        is used for the optimization. Use this argument if you use multi-fidelity
        or instance optimization.'
        """
        if self.__smac3_max_budget_set == SettingState.NOT_SET:
            self.set_smac3_max_budget()
        return ast.literal_eval(self.__settings["smac3"]["max_budget"])

    # Configuration: IRACE specific settings ###

    def get_irace_max_time(self: Settings) -> int:
        """Return the max time in seconds for IRACE."""
        if self.__irace_max_time_set == SettingState.NOT_SET:
            self.set_irace_max_time()
        return int(self.__settings["irace"]["max_time"])

    def set_irace_max_time(
            self: Settings, value: int = DEFAULT_irace_max_time,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the max time in seconds for IRACE."""
        section = "irace"
        name = "max_time"

        if value is not None and self.__check_setting_state(
                self.__irace_max_time_set, origin, name):
            self.__init_section(section)
            self.__irace_max_time_set = origin
            self.__settings[section][name] = str(value)

    def get_irace_max_experiments(self: Settings) -> int:
        """Return the max number of experiments for IRACE."""
        if self.__irace_max_experiments_set == SettingState.NOT_SET:
            self.set_irace_max_experiments()
        return int(self.__settings["irace"]["max_experiments"])

    def set_irace_max_experiments(
            self: Settings, value: int = DEFAULT_irace_max_experiments,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the max number of experiments for IRACE."""
        section = "irace"
        name = "max_experiments"

        if value is not None and self.__check_setting_state(
                self.__irace_max_experiments_set, origin, name):
            self.__init_section(section)
            self.__irace_max_experiments_set = origin
            self.__settings[section][name] = str(value)

    def get_irace_first_test(self: Settings) -> int | None:
        """Return the first test for IRACE.

        Specifies how many instances are evaluated before the first
        elimination test. IRACE Default: 5. [firstTest]
        """
        if self.__irace_first_test_set == SettingState.NOT_SET:
            self.set_irace_first_test()
        first_test = self.__settings["irace"]["first_test"]
        return int(first_test) if first_test.isdigit() else None

    def set_irace_first_test(
            self: Settings, value: int = DEFAULT_irace_first_test,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the first test for IRACE."""
        section = "irace"
        name = "first_test"

        if self.__check_setting_state(
                self.__irace_first_test_set, origin, name):
            self.__init_section(section)
            self.__irace_first_test_set = origin
            self.__settings[section][name] = str(value)

    def get_irace_mu(self: Settings) -> int | None:
        """Return the mu for IRACE.

        Parameter used to define the number of configurations sampled and
        evaluated at each iteration. IRACE Default: 5. [mu]
        """
        if self.__irace_mu_set == SettingState.NOT_SET:
            self.set_irace_mu()
        mu = self.__settings["irace"]["mu"]
        return int(mu) if mu.isdigit() else None

    def set_irace_mu(
            self: Settings, value: int = DEFAULT_irace_mu,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the mu for IRACE."""
        section = "irace"
        name = "mu"

        if self.__check_setting_state(
                self.__irace_mu_set, origin, name):
            self.__init_section(section)
            self.__irace_mu_set = origin
            self.__settings[section][name] = str(value)

    def get_irace_max_iterations(self: Settings) -> int:
        """Return the number of iterations for IRACE."""
        if self.__irace_max_iterations_set == SettingState.NOT_SET:
            self.set_irace_max_iterations()
        max_iterations = self.__settings["irace"]["max_iterations"]
        return int(max_iterations) if max_iterations.isdigit() else None

    def set_irace_max_iterations(
            self: Settings, value: int = DEFAULT_irace_max_iterations,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the number of iterations for IRACE.

        Maximum number of iterations to be executed. Each iteration involves the
        generation of new configurations and the use of racing to select the best
        configurations. By default (with 0), irace calculates a minimum number of
        iterations as N^iter = ⌊2 + log2 N param⌋, where N^param is the number of
        non-fixed parameters to be tuned.
        Setting this parameter may make irace stop sooner than it should without using
        all the available budget. IRACE recommends to use the default value (Empty).
        """
        section = "irace"
        name = "max_iterations"

        if self.__check_setting_state(
                self.__irace_max_iterations_set, origin, name):
            self.__init_section(section)
            self.__irace_max_iterations_set = origin
            self.__settings[section][name] = str(value)

    # Configuration: ParamILS specific settings ###

    def get_paramils_min_runs(self: Settings) -> int | None:
        """Return the minimum number of runs for ParamILS."""
        if self.__paramils_min_runs_set == SettingState.NOT_SET:
            self.set_paramils_min_runs()
        min_runs = self.__settings["paramils"]["min_runs"]
        return int(min_runs) if min_runs.isdigit() else None

    def set_paramils_min_runs(
            self: Settings, value: int = DEFAULT_paramils_min_runs,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the minimum number of runs for ParamILS."""
        section = "paramils"
        name = "min_runs"

        if self.__check_setting_state(
                self.__paramils_min_runs_set, origin, name):
            self.__init_section(section)
            self.__paramils_min_runs_set = origin
            self.__settings[section][name] = str(value)

    def get_paramils_max_runs(self: Settings) -> int | None:
        """Return the maximum number of runs for ParamILS."""
        if self.__paramils_max_runs_set == SettingState.NOT_SET:
            self.set_paramils_max_runs()
        max_runs = self.__settings["paramils"]["min_runs"]
        return int(max_runs) if max_runs.isdigit() else None

    def set_paramils_max_runs(
            self: Settings, value: int = DEFAULT_paramils_max_runs,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the maximum number of runs for ParamILS."""
        section = "paramils"
        name = "max_runs"

        if self.__check_setting_state(
                self.__paramils_max_runs_set, origin, name):
            self.__init_section(section)
            self.__paramils_max_runs_set = origin
            self.__settings[section][name] = str(value)

    def get_paramils_tuner_timeout(self: Settings) -> int | None:
        """Return the maximum CPU time for ParamILS."""
        if self.__paramils_tuner_timeout_set == SettingState.NOT_SET:
            self.set_paramils_tuner_timeout()
        tuner_timeout = self.__settings["paramils"]["tuner_timeout"]
        return int(tuner_timeout) if tuner_timeout.isdigit() else None

    def set_paramils_tuner_timeout(
            self: Settings, value: int = DEFAULT_paramils_tuner_timeout,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the maximum CPU time for ParamILS."""
        section = "paramils"
        name = "tuner_timeout"

        if self.__check_setting_state(
                self.__paramils_tuner_timeout_set, origin, name):
            self.__init_section(section)
            self.__paramils_tuner_timeout_set = origin
            self.__settings[section][name] = str(value)

    def get_paramils_focused_approach(self: Settings) -> bool:
        """Return the focused approach for ParamILS."""
        if self.__paramils_focused_approach_set == SettingState.NOT_SET:
            self.set_paramils_focused_approach()
        return bool(self.__settings["paramils"]["focused_approach"])

    def set_paramils_focused_approach(
            self: Settings, value: bool = DEFAULT_paramils_focused_approach,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the focused approach for ParamILS."""
        section = "paramils"
        name = "focused_approach"

        if self.__check_setting_state(
                self.__paramils_focused_approach_set, origin, name):
            self.__init_section(section)
            self.__paramils_focused_approach_set = origin
            self.__settings[section][name] = str(value)

    def get_paramils_initial_configurations(self: Settings) -> int | None:
        """Return the initial configurations for ParamILS."""
        if self.__paramils_initial_configurations_set == SettingState.NOT_SET:
            self.set_paramils_initial_configurations()
        intial_confs = self.__settings["paramils"]["initial_configurations"]
        return int(intial_confs) if intial_confs.isdigit() else None

    def set_paramils_initial_configurations(
            self: Settings, value: int = DEFAULT_paramils_initial_configurations,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the initial configurations for ParamILS."""
        section = "paramils"
        name = "initial_configurations"

        if self.__check_setting_state(
                self.__paramils_initial_configurations_set, origin, name):
            self.__init_section(section)
            self.__paramils_initial_configurations_set = origin
            self.__settings[section][name] = str(value)

    def get_paramils_random_restart(self: Settings) -> float | None:
        """Return the random restart chance for ParamILS."""
        if self.__paramils_random_restart_set == SettingState.NOT_SET:
            self.set_paramils_random_restart()
        return ast.literal_eval(self.__settings["paramils"]["random_restart"])

    def set_paramils_random_restart(
            self: Settings, value: float = DEFAULT_paramils_random_restart,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the random restart chance for ParamILS."""
        section = "paramils"
        name = "random_restart"

        if self.__check_setting_state(
                self.__paramils_random_restart_set, origin, name):
            self.__init_section(section)
            self.__paramils_random_restart_set = origin
            self.__settings[section][name] = str(value)

    def set_paramils_use_cpu_time_in_tunertime(
            self: Settings, value: bool = DEFAULT_paramils_use_cpu_time_in_tunertime,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set whether to use CPU time in tunertime."""
        section = "paramils"
        name = "use_cpu_time_in_tunertime"

        if self.__check_setting_state(
                self.__paramils_use_cpu_time_in_tunertime_set, origin, name):
            self.__init_section(section)
            self.__paramils_use_cpu_time_in_tunertime_set = origin
            self.__settings[section][name] = str(value)

    def get_paramils_use_cpu_time_in_tunertime(self: Settings) -> bool:
        """Return whether to use CPU time in tunertime."""
        if self.__paramils_use_cpu_time_in_tunertime_set == SettingState.NOT_SET:
            self.set_paramils_use_cpu_time_in_tunertime()
        return ast.literal_eval(self.__settings["paramils"]["use_cpu_time_in_tunertime"])

    def set_paramils_cli_cores(
            self: Settings, value: int = DEFAULT_paramils_cli_cores,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the number of cores to use for ParamILS CLI."""
        section = "paramils"
        name = "cli_cores"

        if self.__check_setting_state(
                self.__paramils_cli_cores_set, origin, name):
            self.__init_section(section)
            self.__paramils_cli_cores_set = origin
            self.__settings[section][name] = str(value)

    def get_paramils_cli_cores(self: Settings) -> int | None:
        """Number of cores to use to execute runs.

        In other words, the number of requests to run at a given time.
        """
        if self.__paramils_cli_cores_set == SettingState.NOT_SET:
            self.set_paramils_cli_cores()
        cli_cores = self.__settings["paramils"]["cli_cores"]
        return int(cli_cores) if cli_cores.isdigit() else None

    def set_paramils_max_iterations(
            self: Settings, value: int = DEFAULT_paramils_max_iterations,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the maximum number of ParamILS iterations."""
        section = "paramils"
        name = "max_iterations"

        if self.__check_setting_state(
                self.__paramils_max_iterations_set, origin, name):
            self.__init_section(section)
            self.__paramils_max_iterations_set = origin
            self.__settings[section][name] = str(value)

    def get_paramils_max_iterations(self: Settings) -> int | None:
        """Get the maximum number of paramils iterations."""
        if self.__smac2_max_iterations_set == SettingState.NOT_SET:
            self.set_paramils_max_iterations()
        max_iterations = self.__settings["paramils"]["max_iterations"]
        return int(max_iterations) if max_iterations.isdigit() else None

    # Selection settings ###

    def set_selection_class(
            self: Settings,
            value: str = DEFAULT_selector_class,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the Sparkle selector.

        Can contain any of the class names as defined in asf.selectors.
        """
        section = "selection"
        name = "selector_class"
        if value is not None and self.__check_setting_state(
                self.__selection_class_set, origin, name):
            self.__init_section(section)
            self.__selection_class_set = origin
            self.__settings[section][name] = str(value)

    def get_selection_class(self: Settings) -> type:
        """Return the selector class."""
        if self.__selection_class_set == SettingState.NOT_SET:
            self.set_selection_class()
        from asf import selectors
        return getattr(selectors, self.__settings["selection"]["selector_class"])

    def set_selection_model(
            self: Settings,
            value: str = DEFAULT_selector_model,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the selector model.

        Can be any of the sklearn.ensemble models.
        """
        section = "selection"
        name = "selector_model"
        if value is not None and self.__check_setting_state(
                self.__selection_model_set, origin, name):
            self.__init_section(section)
            self.__selection_model_set = origin
            self.__settings[section][name] = str(value)

    def get_selection_model(self: Settings) -> type:
        """Return the selector model class."""
        if self.__selection_model_set == SettingState.NOT_SET:
            self.set_selection_model()
        from sklearn import ensemble
        return getattr(ensemble, self.__settings["selection"]["selector_model"])

    # Slurm settings ###

    def set_slurm_max_parallel_runs_per_node(
            self: Settings,
            value: int = DEFAULT_slurm_max_parallel_runs_per_node,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the number of algorithms Slurm can run in parallel per node."""
        section = "slurm"
        name = "max_parallel_runs_per_node"

        if value is not None and self.__check_setting_state(
                self.__slurm_max_parallel_runs_per_node_set, origin, name):
            self.__init_section(section)
            self.__slurm_max_parallel_runs_per_node_set = origin
            self.__settings[section][name] = str(value)

    def get_slurm_max_parallel_runs_per_node(self: Settings) -> int:
        """Return the number of algorithms Slurm can run in parallel per node."""
        if self.__slurm_max_parallel_runs_per_node_set == SettingState.NOT_SET:
            self.set_slurm_max_parallel_runs_per_node()

        return int(self.__settings["slurm"]["max_parallel_runs_per_node"])

    def set_slurm_job_submission_limit(
            self: Settings,
            value: int = DEFAULT_slurm_job_submission_limit,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """[NOT ACTIVE YET] Set the number of jobs that can be submitted to Slurm."""
        section = "slurm"
        name = "job_submission_limit"

        if value is not None and self.__check_setting_state(
                self.__slurm_job_submission_limit_set, origin, name):
            self.__init_section(section)
            self.__slurm_job_submission_limit_set = origin
            self.__settings[section][name] = str(value)

    def get_slurm_job_submission_limit(self: Settings) -> int:
        """[NOT ACTIVE YET] Return the maximum number of jobs you can submit to Slurm."""
        if self.__slurm_job_submission_limit_set == SettingState.NOT_SET:
            self.set_slurm_job_submission_limit()

        return int(self.__settings["slurm"]["job_submission_limit"])

    def set_slurm_job_prepend(
            self: Settings,
            value: str = DEFAULT_slurm_job_prepend,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the Slurm job prepend."""
        section = "slurm"
        name = "job_prepend"

        if self.__check_setting_state(
                self.__slurm_job_prepend_set, origin, name):
            try:
                path = Path(value)
                if path.is_file():
                    with path.open() as f:
                        value = f.read()
                        f.close()
            except TypeError:
                pass
            self.__init_section(section)
            self.__slurm_job_prepend_set = origin
            self.__settings[section][name] = str(value)

    def get_slurm_job_prepend(self: Settings) -> str:
        """Return the Slurm job prepend."""
        if self.__slurm_job_prepend_set == SettingState.NOT_SET:
            self.set_slurm_job_prepend()

        return self.__settings["slurm"]["job_prepend"]

    # SLURM extra options

    def add_slurm_extra_option(self: Settings, name: str, value: str,
                               origin: SettingState = SettingState.DEFAULT) -> None:
        """Add additional Slurm options."""
        section = "slurm_extra"

        current_state = (self.__slurm_extra_options_set[name]
                         if name in self.__slurm_extra_options_set
                         else SettingState.NOT_SET)

        if value is not None and self.__check_setting_state(current_state, origin, name):
            self.__init_section(section)
            self.__slurm_extra_options_set[name] = origin
            self.__settings[section][name] = str(value)

    def get_slurm_extra_options(self: Settings,
                                as_args: bool = False) -> dict | list:
        """Return a dict with additional Slurm options."""
        section = "slurm_extra"
        options = dict()

        if "slurm_extra" in self.__settings.sections():
            for option in self.__settings["slurm_extra"]:
                options[option] = self.__settings.get(section, option)
        if as_args:
            return [f"--{key}={options[key]}" for key in options.keys()]
        return options

    # Ablation settings ###

    def set_ablation_racing_flag(self: Settings, value: bool = DEFAULT_ablation_racing,
                                 origin: SettingState = SettingState.DEFAULT) -> None:
        """Set a flag indicating whether racing should be used for ablation."""
        section = "ablation"
        name = "racing"

        if value is not None and self.__check_setting_state(
                self.__ablation_racing_flag_set, origin, name):
            self.__init_section(section)
            self.__ablation_racing_flag_set = origin
            self.__settings[section][name] = str(value)

    def get_ablation_racing_flag(self: Settings) -> bool:
        """Return a bool indicating whether the racing flag is set for ablation."""
        if self.__ablation_racing_flag_set == SettingState.NOT_SET:
            self.set_ablation_racing_flag()

        return bool(self.__settings["ablation"]["racing"])

    # Parallel Portfolio settings

    def set_parallel_portfolio_check_interval(
            self: Settings,
            value: int = DEFAULT_parallel_portfolio_check_interval,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the parallel portfolio check interval."""
        section = "parallel_portfolio"
        name = "check_interval"

        if value is not None and self.__check_setting_state(
                self.__parallel_portfolio_check_interval_set, origin, name):
            self.__init_section(section)
            self.__parallel_portfolio_check_interval_set = origin
            self.__settings[section][name] = str(value)

    def get_parallel_portfolio_check_interval(self: Settings) -> int:
        """Return the parallel portfolio check interval."""
        if self.__parallel_portfolio_check_interval_set == SettingState.NOT_SET:
            self.set_parallel_portfolio_check_interval()

        return int(
            self.__settings["parallel_portfolio"]["check_interval"])

    def set_parallel_portfolio_number_of_seeds_per_solver(
            self: Settings,
            value: int = DEFAULT_parallel_portfolio_num_seeds_per_solver,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the parallel portfolio seeds per solver to start."""
        section = "parallel_portfolio"
        name = "num_seeds_per_solver"

        if value is not None and self.__check_setting_state(
                self.__parallel_portfolio_num_seeds_per_solver_set, origin, name):
            self.__init_section(section)
            self.__parallel_portfolio_num_seeds_per_solver_set = origin
            self.__settings[section][name] = str(value)

    def get_parallel_portfolio_number_of_seeds_per_solver(self: Settings) -> int:
        """Return the parallel portfolio seeds per solver to start."""
        if self.__parallel_portfolio_num_seeds_per_solver_set == SettingState.NOT_SET:
            self.set_parallel_portfolio_number_of_seeds_per_solver()

        return int(
            self.__settings["parallel_portfolio"]["num_seeds_per_solver"])

    def set_run_on(self: Settings, value: Runner = DEFAULT_general_run_on,
                   origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the compute on which to run."""
        section = "general"
        name = "run_on"

        if value is not None and self.__check_setting_state(
                self.__run_on_set, origin, name):
            self.__init_section(section)
            self.__run_on_set = origin
            self.__settings[section][name] = value

    def get_run_on(self: Settings) -> Runner:
        """Return the compute on which to run."""
        if self.__run_on_set == SettingState.NOT_SET:
            self.set_run_on()

        return Runner(self.__settings["general"]["run_on"])

    @staticmethod
    def check_settings_changes(cur_settings: Settings, prev_settings: Settings) -> bool:
        """Check if there are changes between the previous and the current settings.

        Prints any section changes, printing None if no setting was found.

        Args:
          cur_settings: The current settings
          prev_settings: The previous settings

        Returns:
          True iff there are no changes.
        """
        cur_dict = cur_settings.__settings._sections
        prev_dict = prev_settings.__settings._sections

        cur_sections_set = set(cur_dict.keys())
        prev_sections_set = set(prev_dict.keys())
        sections_removed = prev_sections_set - cur_sections_set
        if sections_removed:
            print("Warning: the following sections have been removed:")
            for section in sections_removed:
                print(f"  - Section '{section}'")

        sections_added = cur_sections_set - prev_sections_set
        if sections_added:
            print("Warning: the following sections have been added:")
            for section in sections_added:
                print(f"  - Section '{section}'")

        sections_remained = cur_sections_set & prev_sections_set
        option_changed = False
        for section in sections_remained:
            printed_section = False
            names = set(cur_dict[section].keys()) | set(prev_dict[section].keys())
            for name in names:
                # if name is not present in one of the two dicts, get None as placeholder
                cur_val = cur_dict[section].get(name, None)
                prev_val = prev_dict[section].get(name, None)

                # If cur val is None, it is default
                if cur_val is not None and cur_val != prev_val:
                    # Have we printed the initial warning?
                    if not option_changed:
                        print("Warning: The following attributes/options have changed:")
                        option_changed = True

                    # do we have yet to print the section?
                    if not printed_section:
                        print(f"  - In the section '{section}':")
                        printed_section = True

                    # print actual change
                    print(f"    · '{name}' changed from '{prev_val}' to '{cur_val}'")

        return not (sections_removed or sections_added or option_changed)
