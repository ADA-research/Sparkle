"""Classes and Enums to control settings."""
from __future__ import annotations
import configparser
from enum import Enum
from pathlib import Path
from pathlib import PurePath

from sparkle.types import SparkleObjective, resolve_objective
from sparkle.types.objective import PAR
from sparkle.solver import Selector
from sparkle.configurator.configurator import Configurator
from sparkle.solver.verifier import SATVerifier
from sparkle.configurator import implementations as cim

from runrunner import Runner
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
    __settings_dir = Path("Settings")
    __settings_file = Path("sparkle_settings.ini")

    # Default settings path
    DEFAULT_settings_path = PurePath(cwd_prefix / __settings_dir / __settings_file)

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

    # Autofolio component
    DEFAULT_general_sparkle_selector = DEFAULT_components / "AutoFolio/scripts/autofolio"

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
    DEFAULT_validation_output = DEFAULT_output / "Validation"
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
        DEFAULT_output, DEFAULT_configuration_output,
        DEFAULT_selection_output, DEFAULT_validation_output,
        DEFAULT_tmp_output,
        DEFAULT_log_output,
        DEFAULT_solver_dir, DEFAULT_instance_dir,
        DEFAULT_feature_data, DEFAULT_performance_data,
        DEFAULT_extractor_dir,
    ]

    # Old default file paths from GV which should be turned into variables
    DEFAULT_feature_data_path =\
        DEFAULT_feature_data / "feature_data.csv"
    DEFAULT_performance_data_path =\
        DEFAULT_performance_data / "performance_data.csv"

    # Constant default values
    DEFAULT_general_sparkle_objective = PAR(10)
    DEFAULT_general_sparkle_configurator = cim.SMAC2.__name__
    DEFAULT_general_solution_verifier = str(None)
    DEFAULT_general_target_cutoff_time = 60
    DEFAULT_general_extractor_cutoff_time = 60
    DEFAULT_number_of_jobs_in_parallel = 25
    DEFAULT_general_verbosity = VerbosityLevel.STANDARD
    DEFAULT_general_check_interval = 10

    DEFAULT_config_wallclock_time = 600
    DEFAULT_config_cpu_time = None
    DEFAULT_config_solver_calls = None
    DEFAULT_config_number_of_runs = 25
    DEFAULT_configurator_target_cutoff_length = "max"

    DEFAULT_portfolio_construction_timeout = None

    DEFAULT_slurm_max_parallel_runs_per_node = 8

    DEFAULT_ablation_racing = False

    DEFAULT_parallel_portfolio_check_interval = 4
    DEFAULT_parallel_portfolio_num_seeds_per_solver = 1

    def __init__(self: Settings, file_path: PurePath = None) -> None:
        """Initialise a settings object."""
        # Settings 'dictionary' in configparser format
        self.__settings = configparser.ConfigParser()

        # Setting flags
        self.__general_sparkle_objective_set = SettingState.NOT_SET
        self.__general_sparkle_configurator_set = SettingState.NOT_SET
        self.__general_sparkle_selector_set = SettingState.NOT_SET
        self.__general_solution_verifier_set = SettingState.NOT_SET
        self.__general_target_cutoff_time_set = SettingState.NOT_SET
        self.__general_extractor_cutoff_time_set = SettingState.NOT_SET
        self.__general_verbosity_set = SettingState.NOT_SET
        self.__general_check_interval_set = SettingState.NOT_SET

        self.__config_wallclock_time_set = SettingState.NOT_SET
        self.__config_cpu_time_set = SettingState.NOT_SET
        self.__config_solver_calls_set = SettingState.NOT_SET
        self.__config_number_of_runs_set = SettingState.NOT_SET

        self.__run_on_set = SettingState.NOT_SET
        self.__number_of_jobs_in_parallel_set = SettingState.NOT_SET
        self.__slurm_max_parallel_runs_per_node_set = SettingState.NOT_SET
        self.__configurator_target_cutoff_length_set = SettingState.NOT_SET
        self.__slurm_extra_options_set = dict()
        self.__ablation_racing_flag_set = SettingState.NOT_SET

        self.__parallel_portfolio_check_interval_set = SettingState.NOT_SET
        self.__parallel_portfolio_num_seeds_per_solver_set = SettingState.NOT_SET

        self.__general_sparkle_configurator = None

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
            option_names = ("objective", )
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

            option_names = ("selector", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.get(section, option)
                    self.set_general_sparkle_selector(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("solution_verifier", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.get(section, option).lower()
                    self.set_general_solution_verifier(value, state)
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
            option_names = ("wallclock_time", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_config_wallclock_time(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("cpu_time", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_config_cpu_time(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("solver_calls", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_config_solver_calls(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("number_of_runs", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_config_number_of_runs(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("target_cutoff_length", "smac_each_run_cutoff_length")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.get(section, option)
                    self.set_configurator_target_cutoff_length(value, state)
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
        else:
            print(f"ERROR: Failed to read settings from {file_path} The file may have "
                  "been empty, located in a different path, or be in another format than"
                  " INI. Default Settings values be used.")

    def write_used_settings(self: Settings) -> None:
        """Write the used settings to the default locations."""
        # Write to latest settings file
        self.write_settings_ini(self.__settings_dir / "latest.ini")

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
        # Write the settings to file
        with file_path.open("w") as settings_file:
            self.__settings.write(settings_file)
        # Rebuild slurm extra if needed
        if slurm_extra_section_options is not None:
            self.__settings.add_section("slurm_extra")
            for key in slurm_extra_section_options:
                self.__settings["slurm_extra"][key] = slurm_extra_section_options[key]

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
        name = "objective"
        if value is not None and self.__check_setting_state(
                self.__general_sparkle_objective_set, origin, name):
            if isinstance(value, list):
                value = ",".join([str(obj) for obj in value])
            else:
                value = str(value)
            # Append standard Sparkle Objectives
            if "status" not in value:
                value += ",status"
            if "cpu_time" not in value:
                value += ",cpu_time"
            if "wall_time" not in value:
                value += ",wall_time"
            if "memory" not in value:
                value += ",memory"
            self.__init_section(section)
            self.__general_sparkle_objective_set = origin
            self.__settings[section][name] = value

    def get_general_sparkle_objectives(self: Settings) -> list[SparkleObjective]:
        """Return the performance measure."""
        if self.__general_sparkle_objective_set == SettingState.NOT_SET:
            self.set_general_sparkle_objectives()

        return [resolve_objective(obj)
                for obj in self.__settings["general"]["objective"].split(",")]

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
        if self.__general_sparkle_configurator is None:
            configurator_subclass =\
                cim.resolve_configurator(self.__settings["general"]["configurator"])
            if configurator_subclass is not None:
                self.__general_sparkle_configurator = configurator_subclass(
                    objectives=self.get_general_sparkle_objectives(),
                    base_dir=Settings.DEFAULT_tmp_output,
                    output_path=Settings.DEFAULT_configuration_output_raw)
            else:
                print("WARNING: Configurator class name not recognised:"
                      f'{self.__settings["general"]["configurator"]}. '
                      "Configurator not set.")
        return self.__general_sparkle_configurator

    def set_general_sparkle_selector(
            self: Settings,
            value: Path = DEFAULT_general_sparkle_selector,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the Sparkle selector."""
        section = "general"
        name = "selector"
        if value is not None and self.__check_setting_state(
                self.__general_sparkle_selector_set, origin, name):
            self.__init_section(section)
            self.__general_sparkle_selector_set = origin
            self.__settings[section][name] = str(value)

    def get_general_sparkle_selector(self: Settings) -> Selector:
        """Return the selector init method."""
        if self.__general_sparkle_selector_set == SettingState.NOT_SET:
            self.set_general_sparkle_selector()
        return Selector(Path(self.__settings["general"]["selector"]),
                        self.DEFAULT_selection_output_raw)

    def set_general_solution_verifier(
            self: Settings, value: str = DEFAULT_general_solution_verifier,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the solution verifier to use."""
        section = "general"
        name = "solution_verifier"

        if value is not None and self.__check_setting_state(
                self.__general_solution_verifier_set, origin, name):
            self.__init_section(section)
            self.__general_solution_verifier_set = origin
            self.__settings[section][name] = value

    def get_general_solution_verifier(self: Settings) -> object:
        """Return the solution verifier to use."""
        if self.__general_solution_verifier_set == SettingState.NOT_SET:
            self.set_general_solution_verifier()
        name = self.__settings["general"]["solution_verifier"].lower()
        if name == str(SATVerifier()).lower():
            return SATVerifier()
        return None

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

        return int(
            self.__settings["general"]["check_interval"])

    # Configuration settings ###

    def set_config_wallclock_time(
            self: Settings, value: int = DEFAULT_config_wallclock_time,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the budget per configuration run in seconds (wallclock)."""
        section = "configuration"
        name = "wallclock_time"

        if value is not None and self.__check_setting_state(
                self.__config_wallclock_time_set, origin, name):
            self.__init_section(section)
            self.__config_wallclock_time_set = origin
            self.__settings[section][name] = str(value)

    def get_config_wallclock_time(self: Settings) -> int:
        """Return the budget per configuration run in seconds (wallclock)."""
        if self.__config_wallclock_time_set == SettingState.NOT_SET:
            self.set_config_wallclock_time()
        return int(self.__settings["configuration"]["wallclock_time"])

    def set_config_cpu_time(
            self: Settings, value: int = DEFAULT_config_cpu_time,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the budget per configuration run in seconds (cpu)."""
        section = "configuration"
        name = "cpu_time"

        if value is not None and self.__check_setting_state(
                self.__config_cpu_time_set, origin, name):
            self.__init_section(section)
            self.__config_cpu_time_set = origin
            self.__settings[section][name] = str(value)

    def get_config_cpu_time(self: Settings) -> int | None:
        """Return the budget per configuration run in seconds (cpu)."""
        if self.__config_cpu_time_set == SettingState.NOT_SET:
            self.set_config_cpu_time()
            return None

        return int(self.__settings["configuration"]["cpu_time"])

    def set_config_solver_calls(
            self: Settings, value: int = DEFAULT_config_solver_calls,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the number of solver calls."""
        section = "configuration"
        name = "solver_calls"

        if value is not None and self.__check_setting_state(
                self.__config_solver_calls_set, origin, name):
            self.__init_section(section)
            self.__config_solver_calls_set = origin
            self.__settings[section][name] = str(value)

    def get_config_solver_calls(self: Settings) -> int | None:
        """Return the number of solver calls."""
        if self.__config_solver_calls_set == SettingState.NOT_SET:
            self.set_config_solver_calls()
            return None

        return int(self.__settings["configuration"]["solver_calls"])

    def set_config_number_of_runs(
            self: Settings, value: int = DEFAULT_config_number_of_runs,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the number of configuration runs."""
        section = "configuration"
        name = "number_of_runs"

        if value is not None and self.__check_setting_state(
                self.__config_number_of_runs_set, origin, name):
            self.__init_section(section)
            self.__config_number_of_runs_set = origin
            self.__settings[section][name] = str(value)

    def get_config_number_of_runs(self: Settings) -> int:
        """Return the number of configuration runs."""
        if self.__config_number_of_runs_set == SettingState.NOT_SET:
            self.set_config_number_of_runs()

        return int(self.__settings["configuration"]["number_of_runs"])

    # Configuration: SMAC specific settings ###

    def set_configurator_target_cutoff_length(
            self: Settings, value: str = DEFAULT_configurator_target_cutoff_length,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the target algorithm cutoff length."""
        section = "configuration"
        name = "target_cutoff_length"

        if value is not None and self.__check_setting_state(
                self.__configurator_target_cutoff_length_set, origin, name):
            self.__init_section(section)
            self.__configurator_target_cutoff_length_set = origin
            self.__settings[section][name] = str(value)

    def get_configurator_target_cutoff_length(self: Settings) -> str:
        """Return the target algorithm cutoff length."""
        if self.__configurator_target_cutoff_length_set == SettingState.NOT_SET:
            self.set_configurator_target_cutoff_length()
        return self.__settings["configuration"]["target_cutoff_length"]

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

    def set_run_on(self: Settings, value: Runner = str,
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
                if cur_val != prev_val:
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
