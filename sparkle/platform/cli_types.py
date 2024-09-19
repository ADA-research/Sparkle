"""Helper types for command line interface."""
from enum import Enum
from typing import Type


class VerbosityLevel(Enum):
    """Enum of possible verbosity states."""

    QUIET = 0
    STANDARD = 1

    @staticmethod
    def from_string(name: str) -> "VerbosityLevel":
        """Converts string to VerbosityLevel."""
        return VerbosityLevel[name]


class TEXT(Enum):
    """Class for ANSI text formatting."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # BG = Background
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    @classmethod
    def format_text(cls: Type["TEXT"], formats: list[str], text: str) -> str:
        """Styles the string based on the provided formats."""
        start_format = "".join(format_.value for format_ in formats)
        end_format = cls.RESET.value
        return f"{start_format}{text}{end_format}"


class CommandName(str, Enum):
    """Enum of all command names."""

    ABOUT = "about"
    ADD_FEATURE_EXTRACTOR = "add_feature_extractor"
    ADD_INSTANCES = "add_instances"
    ADD_SOLVER = "add_solver"
    COMPUTE_FEATURES = "compute_features"
    COMPUTE_MARGINAL_CONTRIBUTION = "compute_marginal_contribution"
    CONFIGURE_SOLVER = "configure_solver"
    CONSTRUCT_PORTFOLIO_SELECTOR = "construct_portfolio_selector"
    GENERATE_REPORT = "generate_report"
    INITIALISE = "initialise"
    REMOVE_FEATURE_EXTRACTOR = "remove_feature_extractor"
    REMOVE_INSTANCES = "remove_instances"
    REMOVE_SOLVER = "remove_solver"
    RUN_ABLATION = "run_ablation"
    RUN_ABLATION_VALIDATION = "run_ablation_validation"
    ABLATION_CALLBACK = "ablation_callback"
    ABLATION_VALIDATION_CALLBACK = "ablation_validation_callback"
    RUN_SOLVER = "run_solver"
    RUN_SOLVERS = "run_solvers"
    RUN_PORTFOLIO_SELECTOR = "run_portfolio_selector"
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
# also after CONSTRUCT_PORTFOLIO_SELECTOR, but does not need both
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
        CommandName.CONSTRUCT_PORTFOLIO_SELECTOR],
    CommandName.CONFIGURE_SOLVER: [CommandName.INITIALISE,
                                   CommandName.ADD_INSTANCES,
                                   CommandName.ADD_SOLVER],
    CommandName.CONSTRUCT_PORTFOLIO_SELECTOR: [CommandName.INITIALISE,
                                               CommandName.COMPUTE_FEATURES,
                                               CommandName.RUN_SOLVERS],
    CommandName.GENERATE_REPORT: [CommandName.INITIALISE,
                                  CommandName.CONFIGURE_SOLVER,
                                  CommandName.VALIDATE_CONFIGURED_VS_DEFAULT,
                                  CommandName.RUN_ABLATION,
                                  CommandName.CONSTRUCT_PORTFOLIO_SELECTOR,
                                  CommandName.RUN_PORTFOLIO_SELECTOR],
    CommandName.INITIALISE: [],
    CommandName.REMOVE_FEATURE_EXTRACTOR: [CommandName.INITIALISE],
    CommandName.REMOVE_INSTANCES: [CommandName.INITIALISE],
    CommandName.REMOVE_SOLVER: [CommandName.INITIALISE],
    CommandName.RUN_ABLATION: [CommandName.INITIALISE,
                               CommandName.CONFIGURE_SOLVER],
    CommandName.RUN_SOLVERS: [CommandName.INITIALISE,
                              CommandName.ADD_INSTANCES,
                              CommandName.ADD_SOLVER],
    CommandName.RUN_PORTFOLIO_SELECTOR: [
        CommandName.INITIALISE,
        CommandName.CONSTRUCT_PORTFOLIO_SELECTOR],
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
