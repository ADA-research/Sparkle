"""Custom helper class and functions to process CLI arguments with argparse."""

from __future__ import annotations
import argparse
import enum
from pathlib import Path
from typing import Any

from runrunner.base import Runner

from sparkle.platform.settings_help import SettingState
from sparkle.types.objective import PerformanceMeasure
from sparkle.platform.settings_help import SolutionVerifier
from CLI.help.command_help import CommandName
from sparkle.platform.settings_help import Settings


class SetByUser(argparse.Action):
    """Possible action to execute for CLI argument."""

    def __call__(self: SetByUser, parser: argparse.ArgumentParser,
                 namespace: argparse.Namespace, values: str, option_string: str = None)\
            -> None:
        """Set attributes when called."""
        setattr(namespace, self.dest, values)
        setattr(namespace, self.dest + "_nondefault", True)


# taken from https://stackoverflow.com/a/60750535
class EnumAction(argparse.Action):
    """Argparse action for handling Enums."""
    def __init__(self: EnumAction, **kwargs: str) -> None:
        """Initialise the EnumAction."""
        # Pop off the type value
        enum_type = kwargs.pop("type", None)

        # Ensure an Enum subclass is provided
        if enum_type is None:
            raise ValueError("type must be assigned an Enum when using EnumAction")
        if not issubclass(enum_type, enum.Enum):
            raise TypeError("type must be an Enum when using EnumAction")

        # Generate choices from the Enum
        kwargs.setdefault("choices", tuple(e.value for e in enum_type))

        super(EnumAction, self).__init__(**kwargs)

        self._enum = enum_type

    def __call__(self: EnumAction, parser: argparse.ArgumentParser,
                 namespace: argparse.Namespace, values: str, option_string: str = None) \
            -> None:
        """Converts value back to Enum."""
        value = self._enum(values)
        setattr(namespace, self.dest, value)


def user_set_state(args: argparse.Namespace, arg_name: str) -> SettingState:
    """Return the SettingState of an argument."""
    if hasattr(args, arg_name + "_nondefault"):
        return SettingState.CMD_LINE
    else:
        return SettingState.DEFAULT


def set_by_user(args: argparse.Namespace, arg_name: str) -> bool:
    """Return whether an argument was set through the CLI by the user or not."""
    return hasattr(args, arg_name + "_nondefault")


class ArgumentContainer():
    """Helper class for more convenient argument packaging and access."""
    def __init__(self: ArgumentContainer, names: list[str], kwargs: dict[str, Any])\
            -> None:
        """Create an ArgumentContainer.

        Args:
            names: List of names for the contained argument. For positional arguments,
                this will contain a single string. For positional arguments this will
                typically contain two, the first one starting with '-' and the second one
                starting with '--'.
            kwargs: Keyword arguments needed by the method parser.add_argument which adds
                the contained argument to a parser.
        """
        self.names = names
        self.kwargs = kwargs


AblationArgument = ArgumentContainer(names=["--ablation"],
                                     kwargs={"required": False,
                                             "action": "store_true",
                                             "help": "run ablation after configuration"})

AblationSettingsHelpArgument = \
    ArgumentContainer(names=["--ablation-settings-help"],
                      kwargs={"required": False,
                              "dest": "ablation_settings_help",
                              "action": "store_true",
                              "help": "Prints a list of setting that can be used for "
                                      "the ablation analysis"})

ActualArgument = ArgumentContainer(names=["--actual"],
                                   kwargs={"action": "store_true",
                                           "help": "compute the marginal contribution "
                                                   "for the actual selector"})

AlsoConstructSelectorAndReportArgument = \
    ArgumentContainer(names=["--also-construct-selector-and-report"],
                      kwargs={"action": "store_true",
                              "help": "after running the solvers also construct the "
                                      "selector and generate the report"})

CommandArgument = \
    ArgumentContainer(names=["--command"],
                      kwargs={"required": False,
                              "choices": CommandName.__members__,
                              "default": None,
                              "help": "command you want to run. Sparkle will wait for "
                                      "dependencies of this command to be completed"})

ConfiguratorArgument = ArgumentContainer(names=["--configurator"],
                                         kwargs={"type": Path,
                                                 "help": "path to configurator"})

CPUTimeArgument = \
    ArgumentContainer(names=["--cpu-time"],
                      kwargs={"type": int,
                              "help": "configuration budget per configurator run in "
                                      "seconds (cpu)"})

CutOffTimeArgument = \
    ArgumentContainer(names=["--cutoff-time"],
                      kwargs={"type": int,
                              "help": "The duration the portfolio will run before the "
                                      "solvers within the portfolio will be stopped "
                                      "(default: "
                                      f"{Settings.DEFAULT_general_target_cutoff_time})"})

DeterministicArgument = ArgumentContainer(names=["--deterministic"],
                                          kwargs={"required": True,
                                                  "type": int,
                                                  "choices": [0, 1],
                                                  "help": "indicate whether the solver "
                                                          "is deterministic or not"})

ExtractorPathArgument = ArgumentContainer(names=["extractor_path"],
                                          kwargs={"metavar": "extractor-path",
                                                  "type": str,
                                                  "help": "path or nickname of the "
                                                          "feature extractor"
                                                  })

InstancePathRunConfiguredSolverArgument = \
    ArgumentContainer(names=["instance_path"],
                      kwargs={"type": Path,
                              "nargs": "+",
                              "help": "Path(s) to instance file(s) (when multiple files "
                                      "are given, it is assumed this is a multi-file "
                                      "instance) or instance directory."})

InstancePathRunPortfolioSelectorArgument = \
    ArgumentContainer(names=["instance_path"],
                      kwargs={"type": str,
                              "nargs": "+",
                              "help": "Path to instance or instance directory"})

InstancePathsRunParallelPortfolioArgument = \
    ArgumentContainer(names=["--instance-paths"],
                      kwargs={"metavar": "PATH",
                              "nargs": "+",
                              "type": str,
                              "required": True,
                              "help": "Specify the instance_path(s) on which the "
                                      "portfolio will run. This can be a space-separated"
                                      " list of instances containing instance sets "
                                      "and/or singular instances. For example "
                                      "--instance-paths  Instances/PTN/Ptn-7824-b01.cnf "
                                      " Instances/PTN2/"})

InstanceSetTestArgument = \
    ArgumentContainer(names=["--instance-set-test"],
                      kwargs={"required": False,
                              "type": Path,
                              "help": "path to test instance set (only for validating)"})

InstanceSetTrainArgument = \
    ArgumentContainer(names=["--instance-set-train"],
                      kwargs={"required": True,
                              "type": Path,
                              "help": "path to training instance set"})

InstanceSetTestAblationArgument = \
    ArgumentContainer(names=["--instance-set-test"],
                      kwargs={"required": False,
                              "type": str,
                              "help": "path to test instance set"})

InstanceSetTrainAblationArgument = \
    ArgumentContainer(names=["--instance-set-train"],
                      kwargs={"required": False,
                              "type": str,
                              "help": "path to training instance set"})

InstanceSetTestReportArgument = \
    ArgumentContainer(names=["--instance-set-test"],
                      kwargs={"required": False,
                              "type": str,
                              "help": "path to testing instance set included in "
                              "Sparkle for an algorithm configuration report"})

InstanceSetTrainReportArgument = \
    ArgumentContainer(names=["--instance-set-train"],
                      kwargs={"required": False,
                              "type": str,
                              "help": "path to training instance set included in "
                              "Sparkle for an algorithm configuration report"})

InstancesPathArgument = ArgumentContainer(names=["instances_path"],
                                          kwargs={"metavar": "instances-path",
                                                  "type": str,
                                                  "help": "path to the instance set"})

InstancesPathRemoveArgument = \
    ArgumentContainer(names=["instances_path"],
                      kwargs={"metavar": "instances-path",
                              "type": str,
                              "help": "path to or nickname of the instance set"})

JobIdArgument = ArgumentContainer(names=["--job-id"],
                                  kwargs={"required": False,
                                          "type": str,
                                          "default": None,
                                          "help": "job ID to wait for"})

NicknameFeatureExtractorArgument = \
    ArgumentContainer(names=["--nickname"],
                      kwargs={"type": str,
                              "help": "set a nickname for the feature extractor"})

NicknameInstanceSetArgument = \
    ArgumentContainer(names=["--nickname"],
                      kwargs={"type": str,
                              "help": "set a nickname for the instance set"})

NicknamePortfolioArgument = \
    ArgumentContainer(names=["--portfolio-name"],
                      kwargs={"type": Path,
                              "help": "Specify a name of the portfolio. "
                                      "If none is given, one will be generated."})

NicknameRemoveExtractor = \
    ArgumentContainer(names=["--nickname"],
                      kwargs={"action": "store_true",
                              "help": "if set to True extractor_path is used as a "
                                      "nickname for the feature extractor"})

NicknameSolverArgument = \
    ArgumentContainer(names=["--nickname"],
                      kwargs={"type": str,
                              "help": "set a nickname for the solver"})

NoAblationReportArgument = ArgumentContainer(names=["--no-ablation"],
                                             kwargs={"required": False,
                                                     "dest": "flag_ablation",
                                                     "default": True,
                                                     "const": False,
                                                     "nargs": "?",
                                                     "help": "turn off reporting on "
                                                             "ablation for an algorithm "
                                                             "configuration report"})

NumberOfRunsConfigurationArgument = \
    ArgumentContainer(names=["--number-of-runs"],
                      kwargs={"type": int,
                              "help": "number of configuration runs to execute"})

NumberOfRunsAblationArgument = \
    ArgumentContainer(names=["--number-of-runs"],
                      kwargs={"type": int,
                              "default": Settings.DEFAULT_config_number_of_runs,
                              "action": SetByUser,
                              "help": "Number of configuration runs to execute"})

ParallelArgument = ArgumentContainer(names=["--parallel"],
                                     kwargs={"action": "store_true",
                                             "help": "Run the command in parallel"})

PerfectArgument = ArgumentContainer(names=["--perfect"],
                                    kwargs={"action": "store_true",
                                            "help": "compute the marginal contribution "
                                                    "for the perfect selector"})

PerformanceMeasureArgument = \
    ArgumentContainer(names=["--performance-measure"],
                      kwargs={"choices": PerformanceMeasure.__members__,
                              "default": Settings.
                              DEFAULT_general_sparkle_objective.PerformanceMeasure,
                              "action": SetByUser,
                              "help": "the performance measure, e.g. runtime"})

PerformanceMeasureSimpleArgument = \
    ArgumentContainer(names=["--performance-measure"],
                      kwargs={"choices": PerformanceMeasure.__members__,
                              "help": "the performance measure, e.g. runtime"})

RacingArgument = ArgumentContainer(names=["--racing"],
                                   kwargs={"type": bool,
                                           "default": Settings.
                                           DEFAULT_ablation_racing,
                                           "action": SetByUser,
                                           "help": "Performs abaltion analysis with "
                                                   "racing"})

RecomputeFeaturesArgument = \
    ArgumentContainer(names=["--recompute"],
                      kwargs={"action": "store_true",
                              "help": "Re-run feature extractor for instances with "
                                      "previously computed features"})

RecomputeMarginalContributionArgument = \
    ArgumentContainer(names=["--recompute"],
                      kwargs={"action": "store_true",
                              "help": "force marginal contribution to be recomputed even"
                                      " when it already exists in file for the current "
                                      "selector"})

RecomputeMarginalContributionForSelectorArgument = \
    ArgumentContainer(names=["--recompute-marginal-contribution"],
                      kwargs={"action": "store_true",
                              "help": "force marginal contribution to be recomputed even"
                                      " when it already exists in file for the current "
                                      "selector"})

RecomputePortfolioSelectorArgument = \
    ArgumentContainer(names=["--recompute-portfolio-selector"],
                      kwargs={"action": "store_true",
                              "help": "force the construction of a new portfolio "
                              "selector even when it already exists for the current "
                              "feature and performance data. NOTE: This will also "
                              "result in the computation of the marginal contributions "
                              "of solvers to the new portfolio selector."})

RecomputeRunSolversArgument = \
    ArgumentContainer(names=["--recompute"],
                      kwargs={"action": "store_true",
                              "help": "recompute the performance of all solvers on all "
                                      "instances"})

RunExtractorNowArgument = \
    ArgumentContainer(names=["--run-extractor-now"],
                      kwargs={"default": False,
                              "action": "store_true",
                              "help": "immediately run the feature extractor(s) on all "
                                      "the instances"})

RunExtractorLaterArgument = \
    ArgumentContainer(names=["--run-extractor-later"],
                      kwargs={"dest": "run_extractor_now",
                              "action": "store_false",
                              "help": "do not immediately run the feature extractor(s) "
                                      "on all the instances (default)"})

RunOnArgument = ArgumentContainer(names=["--run-on"],
                                  kwargs={"type": Runner,
                                          "default": Runner.SLURM,
                                          "choices": [Runner.LOCAL,
                                                      Runner.SLURM],
                                          "action": EnumAction,
                                          "help": "On which computer or cluster "
                                                  "environment to execute the "
                                                  "calculation."})

RunSolverNowArgument = ArgumentContainer(names=["--run-solver-now"],
                                         kwargs={"default": False,
                                                 "action": "store_true",
                                                 "help": "immediately run the solver(s) "
                                                         "on all instances"})

RunSolverLaterArgument = ArgumentContainer(names=["--run-solver-later"],
                                           kwargs={"dest": "run_solver_now",
                                                   "action": "store_false",
                                                   "help": "do not immediately run the "
                                                           "solver(s) on all instances "
                                                           "(default)"})

SelectionReportArgument = \
    ArgumentContainer(names=["--selection"],
                      kwargs={"action": "store_true",
                              "help": "set to generate a normal selection report"})

SettingsFileArgument = \
    ArgumentContainer(names=["--settings-file"],
                      kwargs={"type": Path,
                              "default": Settings.DEFAULT_settings_path,
                              "action": SetByUser,
                              "help": "Specify the settings file to use in case you want"
                                      " to use one other than the default"})

SnapshotArgument = ArgumentContainer(names=["snapshot_file_path"],
                                     kwargs={"metavar": "snapshot-file-path",
                                             "type": str,
                                             "help": "path to the snapshot file"})

SolverArgument = ArgumentContainer(names=["--solver"],
                                   kwargs={"required": True,
                                           "type": Path,
                                           "help": "path to solver"})

SolversArgument = ArgumentContainer(names=["--solvers"],
                                    kwargs={"required": False,
                                            "nargs": "+",
                                            "type": list[str],
                                            "help": "Specify the list of solvers to be "
                                                    "used. If not specifed, all solvers "
                                                    "known in Sparkle will be used."})

SolverCallsArgument = \
    ArgumentContainer(names=["--solver-calls"],
                      kwargs={"type": int,
                              "help": "number of solver calls to execute"})

SolverRemoveArgument = \
    ArgumentContainer(names=["solver"],
                      kwargs={"metavar": "solver",
                              "type": str,
                              "help": "name, path to or nickname of the solver"})

SolverPathArgument = ArgumentContainer(names=["solver_path"],
                                       kwargs={"metavar": "solver-path",
                                               "type": str,
                                               "help": "path to the solver"})

SolverPortfolioArgument = \
    ArgumentContainer(names=["--solver"],
                      kwargs={"required": False,
                              "nargs": "+",
                              "type": str,
                              "help": "Specify the list of solvers, add "
                              '\",<#solver_variations>\" to the end of a path to add '
                              "multiple instances of a single solver. For example "
                              "--solver Solver/PbO-CCSAT-Generic,25 to construct a "
                              "portfolio containing 25 variations of "
                              "PbO-CCSAT-Generic."})

SolverReportArgument = ArgumentContainer(names=["--solver"],
                                         kwargs={"required": False,
                                                 "type": str,
                                                 "default": None,
                                                 "help": "path to solver for an "
                                                 "algorithm configuration report"})

SolverVariationsArgument = \
    ArgumentContainer(names=["--solver-variations"],
                      kwargs={"default": 1,
                              "type": int,
                              "help": "Use this option to add multiple variations of the"
                                      " solver by using a different random seed for each"
                                      " varation."})

TargetCutOffTimeAblationArgument = \
    ArgumentContainer(names=["--target-cutoff-time"],
                      kwargs={"type": int,
                              "default": Settings.DEFAULT_general_target_cutoff_time,
                              "action": SetByUser,
                              "help": "cutoff time per target algorithm run in seconds"})

TargetCutOffTimeConfigurationArgument = \
    ArgumentContainer(names=["--target-cutoff-time"],
                      kwargs={"type": int,
                              "help": "cutoff time per target algorithm run in seconds"})

TargetCutOffTimeRunSolversArgument = \
    ArgumentContainer(names=["--target-cutoff-time"],
                      kwargs={"type": int,
                              "help": "cutoff time per target algorithm run in seconds"})

TargetCutOffTimeValidationArgument = \
    ArgumentContainer(names=["--target-cutoff-time"],
                      kwargs={"type": int,
                              "default": Settings.DEFAULT_general_target_cutoff_time,
                              "action": SetByUser,
                              "help": "cutoff time per target algorithm run in seconds"})

TestCaseDirectoryArgument = \
    ArgumentContainer(names=["--test-case-directory"],
                      kwargs={"type": str,
                              "default": None,
                              "help": "Path to test case directory of an instance set "
                              + "for a selection report"})

UseFeaturesArgument = ArgumentContainer(names=["--use-features"],
                                        kwargs={"required": False,
                                                "action": "store_true",
                                                "help": "use the training set's features"
                                                        " for configuration"})

ValidateArgument = ArgumentContainer(names=["--validate"],
                                     kwargs={"required": False,
                                             "action": "store_true",
                                             "help": "validate after configuration"})

VerboseArgument = ArgumentContainer(names=["--verbose", "-v"],
                                    kwargs={"action": "store_true",
                                            "help": "output status in verbose mode"})

VerifierArgument = \
    ArgumentContainer(names=["--verifier"],
                      kwargs={"choices": SolutionVerifier.__members__,
                              "help": "problem specific verifier that should be used to "
                                      "verify solutions found by a target algorithm"})

WallClockTimeArgument = \
    ArgumentContainer(names=["--wallclock-time"],
                      kwargs={"type": int,
                              "help": "configuration budget per configurator run in "
                                      "seconds (wallclock)"})

SelectorTimeoutArgument = \
    ArgumentContainer(names=["--selector-timeout"],
                      kwargs={"type": int,
                              "default": Settings.DEFAULT_portfolio_construction_timeout,
                              "help": "Cuttoff time (in seconds) for the algorithm"
                                      "selector construction"})
