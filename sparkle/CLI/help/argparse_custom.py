"""Custom helper class and functions to process CLI arguments with argparse."""

from __future__ import annotations
import argparse
import enum
from pathlib import Path
from typing import Any

from runrunner.base import Runner

from sparkle.platform.settings_objects import SettingState, Settings


class SetByUser(argparse.Action):
    """Possible action to execute for CLI argument."""

    def __call__(self: SetByUser, parser: argparse.ArgumentParser,
                 namespace: argparse.Namespace, values: str, option_string: str = None)\
            -> None:
        """Set attributes when called."""
        setattr(namespace, self.dest, values)
        setattr(namespace, self.dest + "_nondefault", True)


# Taken from https://stackoverflow.com/a/60750535
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
SelectorAblationArgument =\
    ArgumentContainer(names=["--solver-ablation"],
                      kwargs={"required": False,
                              "action": "store_true",
                              "help": "construct a selector for "
                                      "each solver ablation combination"})

ActualMarginalContributionArgument = \
    ArgumentContainer(names=["--actual"],
                      kwargs={"action": "store_true",
                              "help": "compute the marginal contribution "
                                      "for the actual selector"})

AlsoConstructSelectorAndReportArgument = \
    ArgumentContainer(names=["--also-construct-selector-and-report"],
                      kwargs={"action": "store_true",
                              "help": "after running the solvers also construct the "
                                      "selector and generate the report"})

CleanupArgumentAll = \
    ArgumentContainer(names=["--all"],
                      kwargs={"action": "store_true",
                              "help": "clean all output files"})

CleanupArgumentRemove = \
    ArgumentContainer(names=["--remove"],
                      kwargs={"action": "store_true",
                              "help": "remove all files in the platform, including "
                                      "user data such as InstanceSets and Solvers"})

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

DeterministicArgument =\
    ArgumentContainer(names=["--deterministic"],
                      kwargs={"action": "store_true",
                              "help": "Flag indicating the solver is deterministic"})

DownloadExamplesArgument =\
    ArgumentContainer(names=["--download-examples"],
                      kwargs={"action": argparse.BooleanOptionalAction,
                              "default": False,
                              "help": "Download the Examples into the directory."})

ExtractorPathArgument = ArgumentContainer(names=["extractor_path"],
                                          kwargs={"metavar": "extractor-path",
                                                  "type": str,
                                                  "help": "path or nickname of the "
                                                          "feature extractor"
                                                  })

GenerateJSONArgument = ArgumentContainer(names=["--only-json"],
                                         kwargs={"required": False,
                                                 "default": False,
                                                 "type": bool,
                                                 "help": "if set to True, only generate "
                                                         "machine readable output"
                                                 })

InstancePathPositional = ArgumentContainer(names=["instance_path"],
                                           kwargs={"type": Path,
                                                   "help": "Path to an instance (set)"})

InstancePath = ArgumentContainer(names=["--instance-path"],
                                 kwargs={"type": Path,
                                         "help": "Path to an instance (set)"})

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

JobIDsArgument = ArgumentContainer(names=["--job-ids"],
                                   kwargs={"required": False,
                                           "nargs": "+",
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

PerfectSelectorMarginalContributionArgument =\
    ArgumentContainer(names=["--perfect"],
                      kwargs={"action": "store_true",
                              "help": "compute the marginal contribution "
                                      "for the perfect selector"})

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

RunOnArgument = ArgumentContainer(names=["--run-on"],
                                  kwargs={"type": Runner,
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

SkipChecksArgument = ArgumentContainer(
    names=["--skip-checks"],
    kwargs={"dest": "run_checks",
            "default": True,
            "action": "store_false",
            "help": "Checks the solver's functionality by testing it on an instance "
                    "and the pcs file, when applicable."})

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

SolverSeedsArgument = \
    ArgumentContainer(names=["--solver-seeds"],
                      kwargs={"type": int,
                              "help": "number of random seeds per solver to execute"})

SolverRemoveArgument = \
    ArgumentContainer(names=["solver"],
                      kwargs={"metavar": "solver",
                              "type": str,
                              "help": "name, path to or nickname of the solver"})

SolverPathArgument = ArgumentContainer(names=["solver_path"],
                                       kwargs={"metavar": "solver-path",
                                               "type": str,
                                               "help": "path to the solver"})

SolverReportArgument = ArgumentContainer(names=["--solver"],
                                         kwargs={"required": False,
                                                 "type": str,
                                                 "default": None,
                                                 "help": "path to solver for an "
                                                 "algorithm configuration report"})

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

SparkleObjectiveArgument = \
    ArgumentContainer(names=["--objectives"],
                      kwargs={"type": str,
                              "help": "the comma seperated objective(s) to use."})
