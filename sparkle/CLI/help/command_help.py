#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Command names and dependency associations."""
from __future__ import annotations
from enum import Enum


class CommandName(str, Enum):
    """Enum of all command names."""

    ABOUT = "about"
    ADD_FEATURE_EXTRACTOR = "add_feature_extractor"
    ADD_INSTANCES = "add_instances"
    ADD_SOLVER = "add_solver"
    COMPUTE_FEATURES = "compute_features"
    COMPUTE_MARGINAL_CONTRIBUTION = "compute_marginal_contribution"
    CONFIGURE_SOLVER = "configure_solver"
    CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR = "construct_sparkle_portfolio_selector"
    GENERATE_REPORT = "generate_report"
    INITIALISE = "initialise"
    REMOVE_FEATURE_EXTRACTOR = "remove_feature_extractor"
    REMOVE_INSTANCES = "remove_instances"
    REMOVE_SOLVER = "remove_solver"
    RUN_ABLATION = "run_ablation"
    RUN_ABLATION_VALIDATION = "run_ablation_validation"
    ABLATION_CALLBACK = "ablation_callback"
    ABLATION_VALIDATION_CALLBACK = "ablation_validation_callback"
    RUN_SOLVERS = "run_solvers"
    RUN_SPARKLE_PORTFOLIO_SELECTOR = "run_sparkle_portfolio_selector"
    RUN_STATUS = "run_status"
    SPARKLE_WAIT = "sparkle_wait"
    SYSTEM_STATUS = "system_status"
    VALIDATE_CONFIGURED_VS_DEFAULT = "validate_configured_vs_default"
    RUN_CONFIGURED_SOLVER = "run_configured_solver"
    RUN_PARALLEL_PORTFOLIO = "run_parallel_portfolio"
    VALIDATION = "validation"


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
    CommandName.GENERATE_REPORT: [CommandName.INITIALISE,
                                  CommandName.CONFIGURE_SOLVER,
                                  CommandName.VALIDATE_CONFIGURED_VS_DEFAULT,
                                  CommandName.RUN_ABLATION,
                                  CommandName.CONSTRUCT_SPARKLE_PORTFOLIO_SELECTOR,
                                  CommandName.RUN_SPARKLE_PORTFOLIO_SELECTOR],
    CommandName.INITIALISE: [],
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
    CommandName.SPARKLE_WAIT: [],
    CommandName.SYSTEM_STATUS: [],
    CommandName.VALIDATE_CONFIGURED_VS_DEFAULT: [CommandName.INITIALISE,
                                                 CommandName.CONFIGURE_SOLVER],
    CommandName.RUN_CONFIGURED_SOLVER: [CommandName.INITIALISE,
                                        CommandName.CONFIGURE_SOLVER],
    CommandName.RUN_PARALLEL_PORTFOLIO: [
        CommandName.INITIALISE]
}
