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
import global_variables as gv
from sparkle.types.objective import SparkleObjective
from sparkle.configurator.configurator import Configurator
from sparkle.configurator import implementations as cim


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
    DEFAULT_general_sparkle_configurator = cim.SMAC2.__name__
    DEFAULT_general_solution_verifier = SolutionVerifier.NONE
    DEFAULT_general_target_cutoff_time = 60
    DEFAULT_general_penalty_multiplier = 10
    DEFAULT_general_extractor_cutoff_time = 60

    DEFAULT_config_wallclock_time = 600
    DEFAULT_config_cpu_time = None
    DEFAULT_config_solver_calls = None
    DEFAULT_config_number_of_runs = 25

    DEFAULT_portfolio_construction_timeout = None

    DEFAULT_slurm_number_of_runs_in_parallel = 25
    DEFAULT_slurm_max_parallel_runs_per_node = 8

    DEFAULT_smac_target_cutoff_length = "max"

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
        self.__general_solution_verifier_set = SettingState.NOT_SET
        self.__general_target_cutoff_time_set = SettingState.NOT_SET
        self.__general_cap_value_set = SettingState.NOT_SET
        self.__general_penalty_multiplier_set = SettingState.NOT_SET
        self.__general_metric_aggregation_function_set = SettingState.NOT_SET
        self.__general_extractor_cutoff_time_set = SettingState.NOT_SET

        self.__config_wallclock_time_set = SettingState.NOT_SET
        self.__config_cpu_time_set = SettingState.NOT_SET
        self.__config_solver_calls_set = SettingState.NOT_SET
        self.__config_number_of_runs_set = SettingState.NOT_SET

        self.__slurm_number_of_runs_in_parallel_set = SettingState.NOT_SET
        self.__slurm_max_parallel_runs_per_node_set = SettingState.NOT_SET
        self.__slurm_extra_options_set = dict()
        self.__smac_target_cutoff_length_set = SettingState.NOT_SET
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
                    value = file_settings.get(section, option)
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
            option_names = ("wallclock_time", "smac_whole_time_budget")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_config_wallclock_time(value, state)
                    file_settings.remove_option(section, option)

            section = "configuration"
            option_names = ("cpu_time", "smac_cpu_time_budget")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_config_cpu_time(value, state)
                    file_settings.remove_option(section, option)

            section = "configuration"
            option_names = ("solver_calls", "smac_solver_calls_budget")
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_config_solver_calls(value, state)
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
            option_names = ("max_parallel_runs_per_node", "clis_per_node", )
            for option in option_names:
                if file_settings.has_option(section, option):
                    value = file_settings.getint(section, option)
                    self.set_slurm_max_parallel_runs_per_node(value, state)
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
        file_path_output = PurePath(gv.sparkle_global_output_dir / slog.caller_out_dir
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

        return

    def get_general_sparkle_configurator(self: Settings) -> Configurator:
        """Return the configurator init method."""
        if self.__general_sparkle_configurator_set == SettingState.NOT_SET:
            self.set_general_sparkle_configurator()
        if self.__general_sparkle_configurator is None:
            configurator_subclass =\
                cim.resolve_configurator(self.__settings["general"]["configurator"])
            if configurator_subclass is not None:
                self.__general_sparkle_configurator = configurator_subclass()
            else:
                print("WARNING: Configurator class name not recognised:"
                      f'{self.__settings["general"]["configurator"]}. '
                      "Configurator not set.")
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

        return

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

        return

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

        return

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

        return

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

        return

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
            self.__parallel_portfolio_check_interval_set = origin
            self.__settings[section][name] = str(value)

        return

    def get_parallel_portfolio_number_of_seeds_per_solver(self: Settings) -> int:
        """Return the parallel portfolio seeds per solver to start."""
        if self.__parallel_portfolio_num_seeds_per_solver_set == SettingState.NOT_SET:
            self.set_parallel_portfolio_number_of_seeds_per_solver()

        return int(
            self.__settings["parallel_portfolio"]["num_seeds_per_solver"])

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
        printed_warning = False

        cur_dict = cur_settings.__settings._sections
        prev_dict = prev_settings.__settings._sections

        for section in cur_dict.keys():
            printed_section = False
            names = set(cur_dict[section].keys()) | set(prev_dict[section].keys())
            for name in names:
                # if name is not present in one of the two dicts, get None as placeholder
                cur_val = cur_dict[section].get(name, None)
                prev_val = prev_dict[section].get(name, None)
                if cur_val != prev_val:
                    # do we have yet to print the initial warning?
                    if not printed_warning:
                        print("Warning: The following attributes/options have changed:")
                        printed_warning = True

                    # do we have yet to print the section?
                    if not printed_section:
                        print(f"In the section '{section}':")
                        printed_section = True

                    # print actual change
                    print(f"  - '{name}' changed from '{prev_val}' "
                          f"to '{cur_val}'")

        return not printed_warning
