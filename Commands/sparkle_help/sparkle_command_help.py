#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Command names and dependency associations."""

from __future__ import annotations
from enum import Enum

from Commands.sparkle_help import sparkle_snapshot_help as srh
from Commands.sparkle_help import sparkle_file_help as sfh


class CommandName(str, Enum):
    """Enum of all command names."""

    ABOUT = "about"
    ADD_FEATURE_EXTRACTOR = "add_feature_extractor"
    ADD_INSTANCES = "add_instances"
    ADD_SOLVER = "add_solver"
    CLEANUP_CURRENT_SPARKLE_PLATFORM = "cleanup_current_sparkle_platform"
    CLEANUP_TEMPORARY_FILES = "cleanup_temporary_files"
    COMPUTE_FEATURES = "compute_features"
    COMPUTE_MARGINAL_CONTRIBUTION = "compute_marginal_contribution"
    CONFIGURE_SOLVER = "configure_solver"
    CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR = "construct_sparkle_portfolio_selector"
    GENERATE_REPORT = "generate_report"
    INITIALISE = "initialise"
    LOAD_SNAPSHOT = "load_snapshot"
    REMOVE_FEATURE_EXTRACTOR = "remove_feature_extractor"
    REMOVE_INSTANCES = "remove_instances"
    REMOVE_SOLVER = "remove_solver"
    RUN_ABLATION = "run_ablation"
    RUN_SOLVERS = "run_solvers"
    RUN_SPARKLE_PORTFOLIO_SELECTOR = "run_sparkle_portfolio_selector"
    RUN_STATUS = "run_status"
    SAVE_SNAPSHOT = "save_snapshot"
    SPARKLE_WAIT = "sparkle_wait"
    SYSTEM_STATUS = "system_status"
    VALIDATE_CONFIGURED_VS_DEFAULT = "validate_configured_vs_default"
    RUN_CONFIGURED_SOLVER = "run_configured_solver"
    CONSTRUCT_SPARKLE_PARALLEL_PORTFOLIO = "construct_sparkle_parallel_portfolio"
    RUN_SPARKLE_PARALLEL_PORTFOLIO = "run_sparkle_parallel_portfolio"

    @staticmethod
    def from_str(command_name: str) -> CommandName:
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
    CommandName.ADD_FEATURE_EXTRACTOR: [CommandName.INITIALISE],
    CommandName.ADD_INSTANCES: [CommandName.INITIALISE],
    CommandName.ADD_SOLVER: [CommandName.INITIALISE],
    CommandName.CLEANUP_CURRENT_SPARKLE_PLATFORM: [],
    CommandName.CLEANUP_TEMPORARY_FILES: [],
    CommandName.COMPUTE_FEATURES: [CommandName.INITIALISE,
                                   CommandName.ADD_FEATURE_EXTRACTOR,
                                   CommandName.ADD_INSTANCES],
    CommandName.COMPUTE_MARGINAL_CONTRIBUTION: [
        CommandName.INITIALISE,
        CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR],
    CommandName.CONFIGURE_SOLVER: [CommandName.INITIALISE,
                                   CommandName.ADD_INSTANCES,
                                   CommandName.ADD_SOLVER],
    CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR: [CommandName.INITIALISE,
                                                       CommandName.COMPUTE_FEATURES,
                                                       CommandName.RUN_SOLVERS],
    CommandName.CONSTRUCT_SPARKLE_PARALLEL_PORTFOLIO: [CommandName.INITIALISE,
                                                       CommandName.ADD_INSTANCES,
                                                       CommandName.ADD_SOLVER],
    CommandName.GENERATE_REPORT: [CommandName.INITIALISE,
                                  CommandName.CONFIGURE_SOLVER,
                                  CommandName.VALIDATE_CONFIGURED_VS_DEFAULT,
                                  CommandName.RUN_ABLATION,
                                  CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR,
                                  CommandName.RUN_SPARKLE_PORTFOLIO_SELECTOR],
    CommandName.INITIALISE: [],
    CommandName.LOAD_SNAPSHOT: [],
    CommandName.REMOVE_FEATURE_EXTRACTOR: [CommandName.INITIALISE],
    CommandName.REMOVE_INSTANCES: [CommandName.INITIALISE],
    CommandName.REMOVE_SOLVER: [CommandName.INITIALISE],
    CommandName.RUN_ABLATION: [CommandName.INITIALISE,
                               CommandName.CONFIGURE_SOLVER],
    CommandName.RUN_SOLVERS: [CommandName.INITIALISE,
                              CommandName.ADD_INSTANCES,
                              CommandName.ADD_SOLVER],
    CommandName.RUN_SPARKLE_PORTFOLIO_SELECTOR: [
        CommandName.INITIALISE,
        CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR],
    CommandName.RUN_STATUS: [],
    CommandName.SAVE_SNAPSHOT: [],
    CommandName.SPARKLE_WAIT: [],
    CommandName.SYSTEM_STATUS: [],
    CommandName.VALIDATE_CONFIGURED_VS_DEFAULT: [CommandName.INITIALISE,
                                                 CommandName.CONFIGURE_SOLVER],
    CommandName.RUN_CONFIGURED_SOLVER: [CommandName.INITIALISE,
                                        CommandName.CONFIGURE_SOLVER],
    CommandName.RUN_SPARKLE_PARALLEL_PORTFOLIO: [
        CommandName.INITIALISE,
        CommandName.CONSTRUCT_SPARKLE_PARALLEL_PORTFOLIO]
}


def check_for_initialise(argv: list[str], requirements: list[CommandName] = None)\
        -> None:
    """Function to check if initialize command was executed and execute it otherwise.

    Args:
        argv: List of the arguments from the caller.
        requirements: The requirements that have to be executed before the calling
            function.
    """
    if not srh.detect_current_sparkle_platform_exists(check_all_dirs=True):
        print("-----------------------------------------------")
        print("No Sparkle platform found; "
              + "The platform will now be initialized automatically")
        if requirements is not None:
            if len(requirements) == 1:
                print(f"The command {requirements[0]} has \
                      to be executed before executing this command.")
            else:
                print(f"""The commands {", ".join(requirements)} \
                      have to be executed before executing this command.""")
        print("-----------------------------------------------")
        sfh.initialise_sparkle(argv)
