#!/usr/bin/env python3
"""Definitions of constants broadly used in Sparkle."""

import ast
from argparse import Namespace
import random
import numpy as np

from sparkle.platform.settings_objects import Settings
from sparkle.structures import PerformanceDataFrame
from sparkle.configurator.configurator import ConfigurationScenario
from sparkle.configurator.implementations import (
    SMAC2Scenario,
    SMAC3Scenario,
    ParamILSScenario,
    IRACEScenario,
)
from sparkle.selector import SelectionScenario


__settings: Settings = None


def settings(argsv: Namespace = None) -> Settings:
    """Function to get the global settings object."""
    global __settings
    if __settings is None:
        __settings = Settings(Settings.DEFAULT_settings_path, argsv=argsv)
        # Set global random state
        max_seed = 2**32 - 1
        latest_ini = Settings(Settings.DEFAULT_previous_settings_path)
        # Determine seed priority: latest.ini > __settings > random
        seed = latest_ini.seed or __settings.seed or random.randint(0, max_seed)
        # Set global RNG states
        np.random.seed(seed)
        random.seed(seed)
        __settings.random_state = seed
        # Next seed will be saved in latest.ini when the cli script calls 'write_used_settings()'
        next_seed = random.randint(0, max_seed)
        __settings.seed = next_seed

    elif argsv is not None:
        __settings.apply_arguments(argsv)

    return __settings


__configuration_scenarios: list[ConfigurationScenario] = None
__selection_scenarios: list[SelectionScenario] = None


def configuration_scenarios(refresh: bool = False) -> list[ConfigurationScenario]:
    """Fetch all known configuration scenarios."""
    global __configuration_scenarios
    config_path = Settings.DEFAULT_configuration_output
    if __configuration_scenarios is None or refresh:
        __configuration_scenarios = []
        for f in config_path.glob("*/*/*.*"):  # We look for files at depth three
            if "scenario" not in f.name:
                continue
            if "SMAC2" in str(f):
                __configuration_scenarios.append(SMAC2Scenario.from_file(f))
            elif "SMAC3" in str(f):
                __configuration_scenarios.append(SMAC3Scenario.from_file(f))
            elif "ParamILS" in str(f):
                __configuration_scenarios.append(ParamILSScenario.from_file(f))
            elif "IRACE" in str(f):
                __configuration_scenarios.append(IRACEScenario.from_file(f))
    return __configuration_scenarios


def selection_scenarios(refresh: bool = False) -> list[SelectionScenario]:
    """Fetch all known selection scenarios."""
    global __selection_scenarios
    selection_path = Settings.DEFAULT_selection_output
    if __selection_scenarios is None or refresh:
        __selection_scenarios = []
        for f in selection_path.glob("*/*/*.txt"):  # We look for files at depth three
            if "scenario" not in f.name:
                continue
            __selection_scenarios.append(SelectionScenario.from_file(f))
    return __selection_scenarios


def parallel_portfolio_scenarios() -> list[PerformanceDataFrame]:
    """Fetch all known parallel portfolio scenarios."""
    parallel_portfolio_path = Settings.DEFAULT_parallel_portfolio_output
    return [PerformanceDataFrame(f) for f in parallel_portfolio_path.glob("*/*.csv")]


reference_list_dir = Settings.DEFAULT_reference_dir
extractor_nickname_list_path = reference_list_dir / "sparkle_extractor_nickname_list.txt"
solver_nickname_list_path = reference_list_dir / "sparkle_solver_nickname_list.txt"
instances_nickname_path = reference_list_dir / "sparkle_instance_nickname_list.txt"

file_storage_data_mapping = {
    solver_nickname_list_path: {},
    instances_nickname_path: {},
    extractor_nickname_list_path: {},
}

for data_path in file_storage_data_mapping.keys():
    if data_path.exists():
        with data_path.open("r+") as fo:
            file_storage_data_mapping[data_path] = ast.literal_eval(fo.read())

solver_nickname_mapping = file_storage_data_mapping[solver_nickname_list_path]
instance_set_nickname_mapping = file_storage_data_mapping[instances_nickname_path]
