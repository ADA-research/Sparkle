#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Command names and dependency associations."""

from enum import Enum


class CommandName(str, Enum):
    """Enum of all command names."""

    ABOUT = 'ABOUT'
    ADD_FEATURE_EXTRACTOR = 'ADD_FEATURE_EXTRACTOR'
    ADD_INSTANCES = 'ADD_INSTANCES'
    ADD_SOLVER = 'ADD_SOLVER'
    CLEANUP_CURRENT_SPARKLE_PLATFORM = 'CLEANUP_CURRENT_SPARKLE_PLATFORM'
    CLEANUP_TEMPORARY_FILES = 'CLEANUP_TEMPORARY_FILES'
    COMPUTE_FEATURES = 'COMPUTE_FEATURES'
    COMPUTE_MARGINAL_CONTRIBUTION = 'COMPUTE_MARGINAL_CONTRIBUTION'
    CONFIGURE_SOLVER = 'CONFIGURE_SOLVER'
    CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR = 'CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR'
    GENERATE_REPORT = 'GENERATE_REPORT'
    INITIALISE = 'INITIALISE'
    LOAD_RECORD = 'LOAD_RECORD'
    REMOVE_FEATURE_EXTRACTOR = 'REMOVE_FEATURE_EXTRACTOR'
    REMOVE_INSTANCES = 'REMOVE_INSTANCES'
    REMOVE_RECORD = 'REMOVE_RECORD'
    REMOVE_SOLVER = 'REMOVE_SOLVER'
    RUN_ABLATION = 'RUN_ABLATION'
    RUN_SOLVERS = 'RUN_SOLVERS'
    RUN_SPARKLE_PORTFOLIO_SELECTOR = 'RUN_SPARKLE_PORTFOLIO_SELECTOR'
    RUN_STATUS = 'RUN_STATUS'
    SAVE_RECORD = 'SAVE_RECORD'
    SPARKLE_WAIT = 'SPARKLE_WAIT'
    SYSTEM_STATUS = 'SYSTEM_STATUS'
    VALIDATE_CONFIGURED_VS_DEFAULT = 'VALIDATE_CONFIGURED_VS_DEFAULT'
    RUN_CONFIGURED_SOLVER = 'RUN_CONFIGURED_SOLVER'
    CONSTRUCT_SPARKLE_PARALLEL_PORTFOLIO = 'CONSTRUCT_SPARKLE_PARALLEL_PORTFOLIO'
    RUN_SPARKLE_PARALLEL_PORTFOLIO = 'RUN_SPARKLE_PARALLEL_PORTFOLIO'

    @staticmethod
    def from_str(command_name: str):
        """Convert a given str to a CommandName."""
        return CommandName(command_name)


# NOTE: This dependency list contains all possible direct dependencies, including
# optional dependencies, and 'either or' dependencies
#
# Optional dpendency: GENERATE_REPORT is possible based on just CONFIGURE_SOLVER,
# but can optionally wait for VALIDATE_CONFIGURED_VS_DEFAULT as well
#
# 'Either or' dependency: GENERATE_REPORT can run after CONFIGURE_SOLVER, but
# also after CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR, but does not need both
#
# TODO: Check if empty dependency lists are correct. These were not important
# when this was implemented, but might have 'trivial' dependencies, such as the
# INITIALISE command.
COMMAND_DEPENDENCIES = {
    CommandName.ABOUT: [],
    CommandName.ADD_FEATURE_EXTRACTOR: [],
    CommandName.ADD_INSTANCES: [],
    CommandName.ADD_SOLVER: [],
    CommandName.CLEANUP_CURRENT_SPARKLE_PLATFORM: [],
    CommandName.CLEANUP_TEMPORARY_FILES: [],
    CommandName.COMPUTE_FEATURES: [CommandName.ADD_FEATURE_EXTRACTOR,
                                   CommandName.ADD_INSTANCES],
    CommandName.COMPUTE_MARGINAL_CONTRIBUTION: [
        CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR],
    CommandName.CONFIGURE_SOLVER: [CommandName.ADD_INSTANCES, CommandName.ADD_SOLVER],
    CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR: [CommandName.COMPUTE_FEATURES,
                                                       CommandName.RUN_SOLVERS],
    CommandName.GENERATE_REPORT: [CommandName.CONFIGURE_SOLVER,
                                  CommandName.VALIDATE_CONFIGURED_VS_DEFAULT,
                                  CommandName.RUN_ABLATION,
                                  CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR,
                                  CommandName.RUN_SPARKLE_PORTFOLIO_SELECTOR],
    CommandName.INITIALISE: [],
    CommandName.LOAD_RECORD: [],
    CommandName.REMOVE_FEATURE_EXTRACTOR: [],
    CommandName.REMOVE_INSTANCES: [],
    CommandName.REMOVE_RECORD: [],
    CommandName.REMOVE_SOLVER: [],
    CommandName.RUN_ABLATION: [CommandName.CONFIGURE_SOLVER],
    CommandName.RUN_SOLVERS: [CommandName.ADD_INSTANCES, CommandName.ADD_SOLVER],
    CommandName.RUN_SPARKLE_PORTFOLIO_SELECTOR: [
        CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR],
    CommandName.RUN_STATUS: [],
    CommandName.SAVE_RECORD: [],
    CommandName.SPARKLE_WAIT: [],
    CommandName.SYSTEM_STATUS: [],
    CommandName.VALIDATE_CONFIGURED_VS_DEFAULT: [CommandName.CONFIGURE_SOLVER],
    CommandName.RUN_CONFIGURED_SOLVER: [CommandName.CONFIGURE_SOLVER],
    CommandName.RUN_SPARKLE_PARALLEL_PORTFOLIO: [
        CommandName.CONSTRUCT_SPARKLE_PARALLEL_PORTFOLIO]
}
