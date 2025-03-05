"""Helper module to manage Sparkle scenarios."""
# Keep in CLI help

from __future__ import annotations
import configparser
from enum import Enum
from pathlib import Path
from pathlib import PurePath

from sparkle.configurator.configurator import ConfigurationScenario
from sparkle.solver import Solver
from sparkle.instance import Instance_Set, InstanceSet


class Scenario(str, Enum):
    """Enum of possible execution scenarios for Sparkle."""

    NONE = "NONE"
    SELECTION = "SELECTION"
    CONFIGURATION = "CONFIGURATION"
    PARALLEL_PORTFOLIO = "PARALLEL_PORTFOLIO"


class ReportingScenario:
    """Class to manage scenarios executed with Sparkle."""

    # ReportingScenario path names and defaults
    __reporting_scenario_file = Path("latest_scenario.ini")
    __reporting_scenario_dir = Path("Output")
    DEFAULT_reporting_scenario_path = Path(
        PurePath(__reporting_scenario_dir / __reporting_scenario_file))

    # Constant default values
    DEFAULT_latest_scenario = Scenario.NONE

    DEFAULT_selection_portfolio_path = Path("")
    DEFAULT_selection_test_case_directory = Path("")

    DEFAULT_parallel_portfolio_path = Path("")
    DEFAULT_parallel_portfolio_instance_list = []

    DEFAULT_config_solver = Path("")
    DEFAULT_config_instance_set_train = Path("")
    DEFAULT_config_instance_set_test = Path("")

    def __init__(self: ReportingScenario) -> None:
        """Initialise a ReportingScenario object."""
        # ReportingScenario 'dictionary' in configparser format
        self.__scenario = configparser.ConfigParser()

        # Initialise scenario in default file path
        self.read_scenario_ini()

    def read_scenario_ini(
            self: ReportingScenario, file_path: Path = DEFAULT_reporting_scenario_path)\
            -> None:
        """Read the scenario from an INI file.

        Args:
            file_path: Path of the INI file for the scenario. Defaults to
                DEFAULT_reporting_scenario_path.
        """
        # If the file does not exist or is empty set default values
        if not Path(file_path).is_file() or Path(file_path).stat().st_size == 0:
            self.set_latest_scenario()
            self.set_selection_scenario_path()
            self.set_selection_test_case_directory()
            self.set_parallel_portfolio_path()
            self.set_parallel_portfolio_instance_path()
            self.set_config_solver()
            self.set_config_instance_set_train()
            self.set_config_instance_set_test()

        # Read file
        file_scenario = configparser.ConfigParser()
        file_scenario.read(file_path)

        # Set internal scenario based on data read from FILE if they were read
        # successfully
        if file_scenario.sections() != []:
            section = "latest"
            option_names = ("scenario",)  # Comma to make it a tuple
            for option in option_names:
                if file_scenario.has_option(section, option):
                    value = Scenario(file_scenario.get(section, option))
                    self.set_latest_scenario(value)
                    file_scenario.remove_option(section, option)

            section = "selection"
            option_names = ("scenario_path",)  # Comma to make it a tuple
            for option in option_names:
                if file_scenario.has_option(section, option):
                    value = Path(file_scenario.get(section, option))
                    self.set_selection_scenario_path(value)
                    file_scenario.remove_option(section, option)

            option_names = ("test_case_directory",)  # Comma to make it a tuple
            for option in option_names:
                if file_scenario.has_option(section, option):
                    value = Path(file_scenario.get(section, option))
                    self.set_selection_test_case_directory(value)
                    file_scenario.remove_option(section, option)

            section = "configuration"
            option_names = ("solver",)  # Comma to make it a tuple
            for option in option_names:
                if file_scenario.has_option(section, option):
                    value = Path(file_scenario.get(section, option))
                    self.set_config_solver(value)
                    file_scenario.remove_option(section, option)

            option_names = ("instance_set_train",)  # Comma to make it a tuple
            for option in option_names:
                if file_scenario.has_option(section, option):
                    value = Path(file_scenario.get(section, option))
                    self.set_config_instance_set_train(value)
                    file_scenario.remove_option(section, option)

            option_names = ("instance_set_test",)  # Comma to make it a tuple
            for option in option_names:
                if file_scenario.has_option(section, option):
                    value = Path(file_scenario.get(section, option))
                    self.set_config_instance_set_test(value)
                    file_scenario.remove_option(section, option)

            option_names = ("scenario_file_path", )
            for option in option_names:
                if file_scenario.has_option(section, option):
                    value = Path(file_scenario.get(section, option))
                    self.set_configuration_scenario(value)
                    file_scenario.remove_option(section, option)

            section = "parallel_portfolio"
            option_names = ("portfolio_path",)  # Comma to make it a tuple
            for option in option_names:
                if file_scenario.has_option(section, option):
                    value = Path(file_scenario.get(section, option))
                    self.set_parallel_portfolio_path(value)
                    file_scenario.remove_option(section, option)

            option_names = ("instance_path",)  # Comma to make it a tuple
            for option in option_names:
                if file_scenario.has_option(section, option):
                    value = file_scenario.get(section, option)
                    self.set_parallel_portfolio_instance_path(value)
                    file_scenario.remove_option(section, option)

            # Report on any unknown settings that were read
            sections = file_scenario.sections()

            for section in sections:
                for option in file_scenario[section]:
                    print(f'Unrecognised section - option combination:"{section} '
                          f'{option}" in file {file_path} ignored')

        # Print error if unable to read the scenario file
        elif not file_path.exists():
            print(f"WARNING: Failed to read latest scenario from {file_path}. "
                  "Default values will be used.")

    def write_scenario_ini(
            self: ReportingScenario, file_path: Path = DEFAULT_reporting_scenario_path)\
            -> None:
        """Write the scenario file in INI format.

        Args:
            file_path: Path of the INI file for the scenario. Defaults to
                DEFAULT_reporting_scenario_path.
        """
        # Create needed directories if they don't exist
        file_dir = file_path.parents[0]
        file_dir.mkdir(parents=True, exist_ok=True)

        # Write the scenario to file
        with Path(str(file_path)).open("w") as scenario_file:
            self.__scenario.write(scenario_file)

    def __init_section(self: ReportingScenario, section: str) -> None:
        """Initialise a section in the scenario file.

        Args:
            section: Name of the section.
        """
        if section not in self.__scenario:
            self.__scenario[section] = {}

    # Generic setters ###

    def path_setter(self: ReportingScenario, section: str, name: str, value: Path)\
            -> None:
        """Set a generic Path for the scenario.

        Args:
            section: Name of the section.
            name: Name of the path element.
            value: Value of the path given.
        """
        if value is not None:
            self.__init_section(section)
            self.__scenario[section][name] = str(value)

    # Generic getters ###

    def none_if_empty_path(self: ReportingScenario, path: Path) -> Path:
        """Return None if a path is empty or the Path otherwise.

        Args:
            path: Path value given.

        Returns:
            None if the given path is empty, the given Path value otherwise.
        """
        if str(path) == "" or str(path) == ".":
            return None
        return path

    # Latest settings ###

    def set_latest_scenario(self: ReportingScenario,
                            value: Scenario = DEFAULT_latest_scenario) -> None:
        """Set the latest Scenario that was executed."""
        section = "latest"
        name = "scenario"

        if value is not None:
            self.__init_section(section)
            self.__scenario[section][name] = value.name

    def get_latest_scenario(self: ReportingScenario) -> Scenario:
        """Return the latest Scenario that was executed."""
        return Scenario(self.__scenario["latest"]["scenario"])

    # Selection settings ###

    def set_selection_scenario_path(
            self: ReportingScenario, value: Path = DEFAULT_selection_portfolio_path)\
            -> None:
        """Set the path to portfolio selector used for algorithm selection."""
        section = "selection"
        name = "scenario_path"
        self.path_setter(section, name, value)

    def get_selection_scenario_path(self: ReportingScenario) -> Path:
        """Return the path to portfolio selector used for algorithm selection."""
        return Path(self.__scenario["selection"]["scenario_path"])

    def set_selection_test_case_directory(
            self: ReportingScenario,
            value: Path = DEFAULT_selection_test_case_directory) -> None:
        """Set the path to the testing set that was used for algorithm selection."""
        section = "selection"
        name = "test_case_directory"
        self.path_setter(section, name, value)

    def get_selection_test_case_directory(self: ReportingScenario) -> str:
        """Return the path to the testing set that was used for algorithm selection."""
        try:
            path = self.__scenario["selection"]["test_case_directory"]
            if Path(path) == Path("."):
                path = None
        except KeyError:
            path = None
        return path

    # Parallel portfolio settings ###

    def set_parallel_portfolio_path(
            self: ReportingScenario,
            value: Path = DEFAULT_parallel_portfolio_path) -> None:
        """Set the path to the parallel portfolio."""
        section = "parallel_portfolio"
        name = "portfolio_path"
        self.path_setter(section, name, value)

    def get_parallel_portfolio_path(self: ReportingScenario) -> Path:
        """Return the path to the parallel portfolio."""
        return Path(self.__scenario["parallel_portfolio"]["portfolio_path"])

    def set_parallel_portfolio_instance_path(
            self: ReportingScenario,
            value: Path = None) -> None:
        """Set the instance path used with the parallel portfolio."""
        section = "parallel_portfolio"
        name = "instance_path"
        self.path_setter(section, name, value)

    def get_parallel_portfolio_instance_set(self: ReportingScenario) -> InstanceSet:
        """Return the instance list used with the parallel portfolio.

        If instance list is empty return None.
        """
        if self.__scenario["parallel_portfolio"]["instance_path"] is None:
            return None
        return Instance_Set(Path(self.__scenario["parallel_portfolio"]["instance_path"]))

    # Configuration settings ###

    def set_config_solver(self: ReportingScenario,
                          value: Solver | Path = DEFAULT_config_solver) -> None:
        """Set the path to the solver that was configured."""
        section = "configuration"
        name = "solver"
        if isinstance(value, Solver):
            value = value.directory
        self.path_setter(section, name, value)

    def get_config_solver(self: ReportingScenario) -> Solver:
        """Return the path to the solver that was configured."""
        path = self.none_if_empty_path(Path(self.__scenario["configuration"]["solver"]))
        if path is not None:
            return Solver(path)
        return None

    def set_config_instance_set_train(
            self: ReportingScenario, value: Path = DEFAULT_config_instance_set_train)\
            -> None:
        """Set the path to the training instance set used for configuration."""
        section = "configuration"
        name = "instance_set_train"
        self.path_setter(section, name, value)

    def get_config_instance_set_train(self: ReportingScenario) -> InstanceSet:
        """Return the path to the training instance set used for configuration."""
        path = self.none_if_empty_path(
            Path(self.__scenario["configuration"]["instance_set_train"]))
        if path is None:
            return None
        return Instance_Set(path)

    def set_configuration_scenario(self: ReportingScenario,
                                   value: Scenario | Path) -> None:
        """Set the path to the scenario that was used for configuration."""
        section = "configuration"
        name = "scenario_file_path"
        if isinstance(value, ConfigurationScenario):
            value = value.scenario_file_path
        self.path_setter(section, name, value)

    def get_configuration_scenario(self: ReportingScenario,
                                   scenario_class: ConfigurationScenario) -> Scenario:
        """Return the path to the scenario that was used for configuration."""
        path = self.none_if_empty_path(
            Path(self.__scenario["configuration"]["scenario_file_path"]))
        if path is None:
            return None
        return scenario_class.from_file(path)

    def set_config_instance_set_test(
            self: ReportingScenario, value: Path = DEFAULT_config_instance_set_test)\
            -> None:
        """Set the path to the testing instance set used for configuration."""
        section = "configuration"
        name = "instance_set_test"
        self.path_setter(section, name, value)

    def get_config_instance_set_test(self: ReportingScenario) -> InstanceSet:
        """Return the path to the testing instance set used for configuration."""
        path = self.none_if_empty_path(
            Path(self.__scenario["configuration"]["instance_set_test"]))
        if path is None:
            return None
        return Instance_Set(path)
