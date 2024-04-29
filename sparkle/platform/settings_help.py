"""Classes and Enums to control settings."""

from __future__ import annotations
import configparser
from enum import Enum
from pathlib import Path
from pathlib import PurePath
from typing import Callable
import builtins
import statistics

import sparkle_logging as slog
import global_variables as sgh
from sparkle.types.objective import SparkleObjective
from sparkle.configurator.configurator import Configurator


class SolutionVerifier(Enum):
    """Possible solution verifiers."""

    NONE = 0
    SAT = 1

    @staticmethod
    def from_str(verifier: str) -> SolutionVerifier:
        """Return a given str as SolutionVerifier."""
        if verifier == "NONE":
            verifier = SolutionVerifier.NONE
        elif verifier == "SAT":
            verifier = SolutionVerifier.SAT

        return verifier


class ProcessMonitoring(str, Enum):
    """Possible process monitoring approaches."""

    # Cancel all solvers within a portfolio once one solver finishes with an instance
    REALISTIC = "REALISTIC"
    # Cancel all solvers within a portfolio once one solver finishes with an instance,
    # after they have run equally long as the fastest solver on this instance so far.
    # This makes it possible to measure which solver would be fastest when they are
    # not able to start at the same time due to, e.g., insufficient CPU cores to start
    # all solvers at the same time.
    EXTENDED = "EXTENDED"

    @staticmethod
    def from_str(process_monitoring: str) -> ProcessMonitoring:
        """Return a given str as ProcessMonitoring."""
        return ProcessMonitoring(process_monitoring)


class SettingState(Enum):
    """Possible setting states."""

    NOT_SET = 0
    DEFAULT = 1
    FILE = 2
    CMD_LINE = 3


class Settings:
    """Read, write, set, and get settings."""

    # Settings path names and default
    __settings_file = Path("sparkle_settings.ini")
    __settings_dir = Path("Settings")
    DEFAULT_settings_path = PurePath(__settings_dir / __settings_file)

    # Constant default values
    DEFAULT_general_sparkle_objective = SparkleObjective("RUNTIME:PAR10")
    DEFAULT_general_sparkle_configurator = Configurator.smac_v2
    DEFAULT_general_solution_verifier = SolutionVerifier.NONE
    DEFAULT_general_target_cutoff_time = 60
    DEFAULT_general_penalty_multiplier = 10
    DEFAULT_general_extractor_cutoff_time = 60

    DEFAULT_config_budget_per_run = 600
    DEFAULT_config_number_of_runs = 25

    DEFAULT_slurm_number_of_runs_in_parallel = 25
    DEFAULT_slurm_clis_per_node = 8

    DEFAULT_smac_target_cutoff_length = "max"

    DEFAULT_ablation_racing = False

    DEFAULT_paraport_overwriting = False
    DEFAULT_paraport_process_monitoring = ProcessMonitoring.REALISTIC

    def __init__(self: Settings, file_path: PurePath = None) -> None:
        """Initialise a settings object."""
        # Settings 'dictionary' in configparser format
        self.__settings = configparser.ConfigParser()

        # Setting flags
        self.__general_sparkle_objective_set = SettingState.NOT_SET
        self.__general_sparkle_configurator_set = SettingState.NOT_SET
        self.__general_solution_verifier_set = SettingState.NOT_SET
        self.__general_target_cutoff_time_set = SettingState.NOT_SET
        self.__general_cap_value_set = SettingState.NOT_SET
        self.__general_penalty_multiplier_set = SettingState.NOT_SET
        self.__general_metric_aggregation_function_set = SettingState.NOT_SET
        self.__general_extractor_cutoff_time_set = SettingState.NOT_SET

        self.__config_budget_per_run_set = SettingState.NOT_SET
        self.__config_number_of_runs_set = SettingState.NOT_SET

        self.__slurm_number_of_runs_in_parallel_set = SettingState.NOT_SET
        self.__slurm_clis_per_node_set = SettingState.NOT_SET
        self.__slurm_extra_options_set = dict()
        self.__smac_target_cutoff_length_set = SettingState.NOT_SET
        self.__ablation_racing_flag_set = SettingState.NOT_SET
        self.__paraport_overwriting_flag_set = SettingState.NOT_SET
        self.__paraport_process_monitoring_set = SettingState.NOT_SET

        self.__general_sparkle_configurator = None

        if file_path is None:
            # Initialise settings from default file path
            self.read_settings_ini()
        else:
            # Initialise settings from a given file path
            self.read_settings_ini(file_path)

        return

    def read_settings_ini(self: Settings, file_path: PurePath = DEFAULT_settings_path,
                          state: SettingState = SettingState.FILE) -> None:
        """Read the settings from an INI file."""
        # Read file
        file_settings = configparser.ConfigParser()
        file_settings.read(str(file_path))

        # Set internal settings based on data read from FILE if they were read
        # successfully
        if file_settings.sections() != []:
            section = "general"
            option_names = ("objective", "smac_run_obj")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = SparkleObjective.from_multi_str(
                        file_settings.get(section, option))
                    self.set_general_sparkle_objectives(value, state)
                    file_settings.remove_option(section, option)

            # Comma so python understands it's a tuple...
            option_names = ("configurator",)
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = getattr(Configurator, file_settings.get(section, option))
                    self.set_general_sparkle_configurator(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("solution_verifier",)
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = SolutionVerifier.from_str(file_settings.get(section, option))
                    self.set_general_solution_verifier(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("target_cutoff_time", "smac_each_run_cutoff_time",
                            "cutoff_time_each_performance_computation")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_general_target_cutoff_time(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("cap_value",)
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getfloat(section, option)
                    self.set_general_cap_value(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("penalty_multiplier", "penalty_number")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_general_penalty_multiplier(value, state)
                    file_settings.remove_option(section, option)

            option_names = ("extractor_cutoff_time",
                            "cutoff_time_each_feature_computation")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_general_extractor_cutoff_time(value, state)
                    file_settings.remove_option(section, option)

            section = "configuration"
            option_names = ("budget_per_run", "smac_whole_time_budget")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_config_budget_per_run(value, state)
                    file_settings.remove_option(section, option)

            section = "configuration"
            option_names = ("number_of_runs", "num_of_smac_runs")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_config_number_of_runs(value, state)
                    file_settings.remove_option(section, option)

            section = "slurm"
            option_names = ("number_of_runs_in_parallel", "num_of_smac_runs_in_parallel",
                            "num_job_in_parallel")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_slurm_number_of_runs_in_parallel(value, state)
                    file_settings.remove_option(section, option)

            section = "slurm"
            option_names = ("clis_per_node", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_slurm_clis_per_node(value, state)
                    file_settings.remove_option(section, option)

            section = "smac"
            option_names = ("target_cutoff_length", "smac_each_run_cutoff_length")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.get(section, option)
                    self.set_smac_target_cutoff_length(value, state)
                    file_settings.remove_option(section, option)

            section = "ablation"
            option_names = ("racing", "ablation_racing")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getboolean(section, option)
                    self.set_ablation_racing_flag(value, state)
                    file_settings.remove_option(section, option)

            section = "parallel_portfolio"
            option_names = ("overwriting", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getboolean(section, option)
                    self.set_paraport_overwriting_flag(value, state)
                    file_settings.remove_option(section, option)

            section = "parallel_portfolio"
            option_names = ("process_monitoring", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = ProcessMonitoring.from_str(
                        file_settings.get(section, option))
                    self.set_paraport_process_monitoring(value, state)
                    file_settings.remove_option(section, option)

            # TODO: Report on any unknown settings that were read
            sections = file_settings.sections()

            for section in sections:
                for option in file_settings[section]:
                    # TODO: Quick fix to support partitions and excludes, but should not
                    # allow any option
                    if section == "slurm":
                        print(f'Unrecognised SLURM option "{option}" found in '
                              f"{str(file_path)}. Option is added to any SLURM batches")
                        value = file_settings.get(section, option)
                        self.add_slurm_extra_option(option, value, state)
                    else:
                        print(f'Unrecognised section - option combination: "{section} '
                              f'{option}" in file {str(file_path)} ignored')

        # Print error if unable to read the settings
        else:
            print(f"ERROR: Failed to read settings from {str(file_path)} The file may "
                  "have been empty, located in a different path, or be in another format"
                  " than INI. Settings from different sources will be used (e.g. default"
                  " values).")

        return

    def write_used_settings(self: Settings) -> None:
        """Write the used settings to the default locations."""
        # Write to general output directory
        file_path_output = PurePath(sgh.sparkle_global_output_dir / slog.caller_out_dir
                                    / self.__settings_dir / self.__settings_file)
        self.write_settings_ini(Path(file_path_output))

        # Write to latest settings file
        file_path_latest = PurePath(self.__settings_dir / "latest.ini")
        self.write_settings_ini(Path(file_path_latest))

        return

    def write_settings_ini(self: Settings, file_path: Path) -> None:
        """Write the settings to an INI file."""
        # Create needed directories if they don't exist
        file_dir = file_path.parents[0]
        file_dir.mkdir(parents=True, exist_ok=True)

        # Write the settings to file
        with Path(str(file_path)).open("w") as settings_file:
            self.__settings.write(settings_file)

            # Log the settings file location
            slog.add_output(str(file_path), "Settings used by Sparkle for this command")

        return

    def __init_section(self: Settings, section: str) -> None:
        if section not in self.__settings:
            self.__settings[section] = {}

        return

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
                value = ",".join([obj.name for obj in value])
            self.__init_section(section)
            self.__general_sparkle_objective_set = origin
            self.__settings[section][name] = value

        return

    def get_general_sparkle_objectives(self: Settings) -> list[SparkleObjective]:
        """Return the performance measure."""
        if self.__general_sparkle_objective_set == SettingState.NOT_SET:
            self.set_general_sparkle_objectives()

        return SparkleObjective.from_multi_str(
            self.__settings["general"]["objective"])

    def set_general_sparkle_configurator(
            self: Settings,
            value: Callable = DEFAULT_general_sparkle_configurator,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the Sparkle configurator."""
        section = "general"
        name = "configurator"
        if value is not None and self.__check_setting_state(
                self.__general_sparkle_configurator_set, origin, name):
            self.__init_section(section)
            self.__general_sparkle_configurator_set = origin
            self.__settings[section][name] = value.__name__

        return

    def get_general_sparkle_configurator(self: Settings) -> Configurator:
        """Return the configurator init method."""
        if self.__general_sparkle_configurator_set == SettingState.NOT_SET:
            self.set_general_sparkle_configurator()
        if self.__general_sparkle_configurator is None:
            self.__general_sparkle_configurator =\
                getattr(Configurator, self.__settings["general"]["configurator"])()
        return self.__general_sparkle_configurator

    def get_performance_metric_for_report(self: Settings) -> str:
        """Return a string describing the full performance metric, e.g. PAR10."""
        objectives = self.get_general_sparkle_objectives()
        if len(objectives) == 1:
            return objectives[0].metric
        return ""

    def set_general_cap_value(
            self: Settings, value: float = None,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the general cap value."""
        section = "general"
        name = "cap_value"

        if value is not None and self.__check_setting_state(
                self.__general_cap_value_set, origin, name):
            self.__init_section(section)
            self.__general_cap_value_set = origin
            self.__settings[section][name] = float(value)

        return

    def get_general_cap_value(self: Settings) -> float:
        """Get the general cap value."""
        if self.__general_cap_value_set == SettingState.NOT_SET:
            self.set_general_cap_value()

        if "cap_value" in self.__settings["general"]:
            return self.__settings["general"]["cap_value"]
        else:
            return None

    def set_general_penalty_multiplier(
            self: Settings, value: int = DEFAULT_general_penalty_multiplier,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the penalty multiplier."""
        section = "general"
        name = "penalty_multiplier"

        if value is not None and self.__check_setting_state(
                self.__general_penalty_multiplier_set, origin, name):
            self.__init_section(section)
            self.__general_penalty_multiplier_set = origin
            self.__settings[section][name] = str(value)

        return

    def get_general_penalty_multiplier(self: Settings) -> int:
        """Return the penalty multiplier."""
        if self.__general_penalty_multiplier_set == SettingState.NOT_SET:
            self.set_general_penalty_multiplier()

        return int(self.__settings["general"]["penalty_multiplier"])

    def set_general_metric_aggregation_function(
            self: Settings, value: str = "mean",
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the general aggregation function of performance measure."""
        section = "general"
        name = "metric_aggregation_function"

        if value is not None and self.__check_setting_state(
                self.__general_metric_aggregation_function_set, origin, name):
            self.__init_section(section)
            self.__general_metric_aggregation_function_set = origin
            self.__settings[section][name] = value

        return

    def get_general_metric_aggregation_function(self: Settings) -> Callable:
        """Set the general aggregation function of performance measure."""
        if self.__general_metric_aggregation_function_set == SettingState.NOT_SET:
            self.set_general_metric_aggregation_function()
        method = self.__settings["general"]["metric_aggregation_function"]
        libraries = (builtins, statistics)
        for lib in libraries:
            if not isinstance(method, str):
                break
            try:
                method = getattr(lib, method)
            except AttributeError:
                continue
        return method

    def get_penalised_time(self: Settings, custom_cutoff: int = None) -> int:
        """Return the penalised time associated with the cutoff time."""
        if custom_cutoff is None:
            cutoff_time = self.get_general_target_cutoff_time()
        else:
            cutoff_time = custom_cutoff

        penalty_multiplier = self.get_general_penalty_multiplier()
        penalised_time = cutoff_time * penalty_multiplier

        return penalised_time

    def set_general_solution_verifier(
            self: Settings, value: SolutionVerifier = DEFAULT_general_solution_verifier,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the solution verifier to use."""
        section = "general"
        name = "solution_verifier"

        if value is not None and self.__check_setting_state(
                self.__general_solution_verifier_set, origin, name):
            self.__init_section(section)
            self.__general_solution_verifier_set = origin
            self.__settings[section][name] = value.name

        return

    def get_general_solution_verifier(self: Settings) -> SolutionVerifier:
        """Return the solution verifier to use."""
        if self.__general_solution_verifier_set == SettingState.NOT_SET:
            self.set_general_solution_verifier()

        return SolutionVerifier.from_str(self.__settings["general"]["solution_verifier"])

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

        return

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

        return

    def get_general_extractor_cutoff_time(self: Settings) -> int:
        """Return the cutoff time in seconds for feature extraction."""
        if self.__general_extractor_cutoff_time_set == SettingState.NOT_SET:
            self.set_general_extractor_cutoff_time()

        return int(self.__settings["general"]["extractor_cutoff_time"])

    # Configuration settings ###

    def set_config_budget_per_run(
            self: Settings, value: int = DEFAULT_config_budget_per_run,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the budget per configuration run in seconds."""
        section = "configuration"
        name = "budget_per_run"

        if value is not None and self.__check_setting_state(
                self.__config_budget_per_run_set, origin, name):
            self.__init_section(section)
            self.__config_budget_per_run_set = origin
            self.__settings[section][name] = str(value)

        return

    def get_config_budget_per_run(self: Settings) -> int:
        """Return the budget per configuration run in seconds."""
        if self.__config_budget_per_run_set == SettingState.NOT_SET:
            self.set_config_budget_per_run()

        return int(self.__settings["configuration"]["budget_per_run"])

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

        return

    def get_config_number_of_runs(self: Settings) -> int:
        """Return the number of configuration runs."""
        if self.__config_number_of_runs_set == SettingState.NOT_SET:
            self.set_config_number_of_runs()

        return int(self.__settings["configuration"]["number_of_runs"])

    # Configuration: SMAC specific settings ###

    def set_smac_target_cutoff_length(
            self: Settings, value: str = DEFAULT_smac_target_cutoff_length,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the target algorithm cutoff length."""
        section = "smac"
        name = "target_cutoff_length"

        if value is not None and self.__check_setting_state(
                self.__smac_target_cutoff_length_set, origin, name):
            self.__init_section(section)
            self.__smac_target_cutoff_length_set = origin
            self.__settings[section][name] = str(value)

        return

    def get_smac_target_cutoff_length(self: Settings) -> str:
        """Return the target algorithm cutoff length."""
        if self.__smac_target_cutoff_length_set == SettingState.NOT_SET:
            self.set_smac_target_cutoff_length()

        return self.__settings["smac"]["target_cutoff_length"]

    # Slurm settings ###

    def set_slurm_number_of_runs_in_parallel(
            self: Settings, value: int = DEFAULT_slurm_number_of_runs_in_parallel,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the number of runs Slurm can do in parallel."""
        section = "slurm"
        name = "number_of_runs_in_parallel"

        if value is not None and self.__check_setting_state(
                self.__slurm_number_of_runs_in_parallel_set, origin, name):
            self.__init_section(section)
            self.__slurm_number_of_runs_in_parallel_set = origin
            self.__settings[section][name] = str(value)

        return

    def get_slurm_number_of_runs_in_parallel(self: Settings) -> int:
        """Return the number of runs Slurm can do in parallel."""
        if self.__slurm_number_of_runs_in_parallel_set == SettingState.NOT_SET:
            self.set_slurm_number_of_runs_in_parallel()

        return int(self.__settings["slurm"]["number_of_runs_in_parallel"])

    def set_slurm_clis_per_node(self: Settings, value: int = DEFAULT_slurm_clis_per_node,
                                origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the number of algorithms Slurm can run in parallel per node."""
        section = "slurm"
        name = "clis_per_node"

        if value is not None and self.__check_setting_state(
                self.__slurm_clis_per_node_set, origin, name):
            self.__init_section(section)
            self.__slurm_clis_per_node_set = origin
            self.__settings[section][name] = str(value)

        return

    def get_slurm_clis_per_node(self: Settings) -> int:
        """Return the number of algorithms Slurm can run in parallel per node."""
        if self.__slurm_clis_per_node_set == SettingState.NOT_SET:
            self.set_slurm_clis_per_node()

        return int(self.__settings["slurm"]["clis_per_node"])

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

    def get_slurm_extra_options(self: Settings) -> dict:
        """Return a dict with additional Slurm options."""
        section = "slurm_extra"
        options = dict()

        if "slurm_extra" in self.__settings.sections():
            for option in self.__settings["slurm_extra"]:
                options[option] = self.__settings.get(section, option)

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

        return

    def get_ablation_racing_flag(self: Settings) -> bool:
        """Return a bool indicating whether the racing flag is set for ablation."""
        if self.__ablation_racing_flag_set == SettingState.NOT_SET:
            self.set_ablation_racing_flag()

        return bool(self.__settings["ablation"]["racing"])

    # Parallel Portfolio settings ###

    def set_paraport_overwriting_flag(
            self: Settings, value: bool = DEFAULT_paraport_overwriting,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the parallel portfolio overwriting flag to a given value."""
        section = "parallel_portfolio"
        name = "overwriting"

        if value is not None and self.__check_setting_state(
                self.__paraport_overwriting_flag_set, origin, name):
            self.__init_section(section)
            self.__paraport_overwriting_flag_set = origin
            self.__settings[section][name] = str(value)

        return

    def get_paraport_overwriting_flag(self: Settings) -> bool:
        """Return the parallel portfolio overwriting flag state."""
        if self.__paraport_overwriting_flag_set == SettingState.NOT_SET:
            self.set_paraport_overwriting_flag()

        return bool(self.__settings["parallel_portfolio"]["overwriting"])

    def set_paraport_process_monitoring(
            self: Settings,
            value: ProcessMonitoring = DEFAULT_paraport_process_monitoring,
            origin: SettingState = SettingState.DEFAULT) -> None:
        """Set the parallel portfolio process monitoring state."""
        section = "parallel_portfolio"
        name = "process_monitoring"

        if value is not None and self.__check_setting_state(
                self.__paraport_overwriting_flag_set, origin, name):
            self.__init_section(section)
            self.__paraport_process_monitoring_set = origin
            self.__settings[section][name] = value.name

        return

    def get_paraport_process_monitoring(self: Settings) -> ProcessMonitoring:
        """Return the parallel portfolio process monitoring state."""
        if self.__paraport_process_monitoring_set == SettingState.NOT_SET:
            self.set_paraport_process_monitoring()

        return ProcessMonitoring.from_str(
            self.__settings["parallel_portfolio"]["process_monitoring"])
