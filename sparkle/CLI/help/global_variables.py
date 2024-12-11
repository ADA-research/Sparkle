#!/usr/bin/env python3
"""Definitions of constants broadly used in Sparkle."""
import ast

from sparkle.CLI.help.reporting_scenario import ReportingScenario
from sparkle.platform.settings_objects import Settings


# TODO: Handle different seed requirements; for the moment this is a dummy function
def get_seed() -> int:
    """Return a seed."""
    return 1


__latest_scenario: ReportingScenario = None


def latest_scenario() -> ReportingScenario:
    """Function to get the global latest scenario object."""
    global __latest_scenario
    if __latest_scenario is None:
        __latest_scenario = ReportingScenario()
    return __latest_scenario


__settings: Settings = None


def settings() -> Settings:
    """Function to get the global settings object."""
    global __settings
    if __settings is None:
        __settings = Settings()
    return __settings


reference_list_dir = settings().DEFAULT_reference_dir
extractor_nickname_list_path = reference_list_dir / "sparkle_extractor_nickname_list.txt"
solver_nickname_list_path = reference_list_dir / "sparkle_solver_nickname_list.txt"
instances_nickname_path = reference_list_dir / "sparkle_instance_nickname_list.txt"

file_storage_data_mapping = {solver_nickname_list_path: {},
                             instances_nickname_path: {},
                             extractor_nickname_list_path: {}}

for data_path in file_storage_data_mapping.keys():
    if data_path.exists():
        with data_path.open("r+") as fo:
            file_storage_data_mapping[data_path] = ast.literal_eval(fo.read())

solver_nickname_mapping = file_storage_data_mapping[solver_nickname_list_path]
