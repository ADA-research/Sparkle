"""Custom helper class and functions to process CLI arguments with argparse."""

from __future__ import annotations
import argparse
from pathlib import Path
from typing import Any

from sparkle.platform.settings_help import SettingState


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


ExtractorPathArgument = ArgumentContainer(names=["extractor_path"],
                                          kwargs={"metavar": "extractor-path",
                                                  "type": str,
                                                  "help": "path to the feature extractor"
                                                  })

InstancesPathArgument = ArgumentContainer(names=["instances_path"],
                                          kwargs={"metavar": "instances-path",
                                                  "type": str,
                                                  "help": "path to the instance set"})

NicknameFeatureExtractorArgument = ArgumentContainer(names=["--nickname"],
                                     kwargs={"type": str,
                                             "help": "set a nickname for the feature "
                                             + "extractor"})

ParallelFeatureExtractorArgument = \
    ArgumentContainer(names=["--parallel"],
                      kwargs={"action": "store_true",
                              "help": "run the feature extractor on "
                              + "multiple instances in parallel"})

ParallelInstancesArgument = \
    ArgumentContainer(names=["--parallel"],
                      kwargs={"action": "store_true",
                              "help": "run the solvers and feature extractor on "
                              + "multiple instances in parallel"})

RunExtractorNowArgument = \
    ArgumentContainer(names=["--run-extractor-now"],
                      kwargs={"default": False,
                              "action": "store_true",
                              "help": "immediately run the newly added feature extractor"
                              + " on the existing instances"})

RunExtractorLaterArgument = \
    ArgumentContainer(names=["--run-extractor-later"],
                      kwargs={"dest": "run_extractor_now",
                              "action": "store_false",
                              "help": "do not immediately run the newly added feature "
                              + "extractor on the existing instances (default)"})

RunSolverNowArgument = ArgumentContainer(names=["--run-solver-now"],
                                         kwargs={"default": False,
                                                 "action": "store_true",
                                                 "help": "immediately run the solver(s) "
                                                 + "on the newly added instances"})

RunSolverLaterArgument = ArgumentContainer(names=["--run-solver-later"],
                                           kwargs={"dest": "run_solver_now",
                                                   "action": "store_false",
                                                   "help": "do not immediately run the "
                                                   + "solver(s) on the newly added "
                                                   + "instances (default)"})

SolverArgument = ArgumentContainer(names=["--solver"],
                                   kwargs={"required": True,
                                           "type": Path,
                                           "help": "path to solver"})


class SetByUser(argparse.Action):
    """Possible action to execute for CLI argument."""

    def __call__(self: SetByUser, parser: argparse.ArgumentParser,
                 namespace: argparse.Namespace, values: str, option_string: str = None)\
            -> None:
        """Set attributes when called."""
        setattr(namespace, self.dest, values)
        setattr(namespace, self.dest + "_nondefault", True)


def user_set_state(args: argparse.Namespace, arg_name: str) -> SettingState:
    """Return the SettingState of an argument."""
    if hasattr(args, arg_name + "_nondefault"):
        return SettingState.CMD_LINE
    else:
        return SettingState.DEFAULT


def set_by_user(args: argparse.Namespace, arg_name: str) -> bool:
    """Return whether an argument was set through the CLI by the user or not."""
    return hasattr(args, arg_name + "_nondefault")
