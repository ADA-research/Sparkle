"""This package provides types for Sparkle applications."""
import importlib
import inspect
import re
from typing import Callable

from sparkle.types.sparkle_callable import SparkleCallable
from sparkle.types.features import FeatureGroup, FeatureSubgroup, FeatureType
from sparkle.types.status import SolverStatus
from sparkle.types import objective
from sparkle.types.objective import SparkleObjective, UseTime


class_name_regex = re.compile(r"[a-zA-Z]+(\d*)$")


def _check_class(candidate: Callable) -> bool:
    """Verify whether a loaded class is a valid objective class."""
    return inspect.isclass(candidate) and issubclass(candidate, SparkleObjective)


def resolve_objective(name: str) -> SparkleObjective:
    """Try to resolve the objective class by (case sensitive) name.

    Args:
        name: The name of the objective class. Can included parameter value k.

    Returns:
        Instance of the Objective class or None if not found.
    """
    # First try to resolve the user input classes
    match = class_name_regex.fullmatch(name)
    argument = None
    if match is None:
        return None
    if match.groups()[0] != "":
        # If the name contains an argument, substitute it with 'k' for matching
        name = name.replace(match.groups()[0], "") + "k"
        argument = int(match.groups()[0])
    try:
        user_module = importlib.import_module("Settings.objective")
        for o_name, o_class in inspect.getmembers(user_module,
                                                  predicate=_check_class):
            if o_name == name:
                if argument is not None:
                    return o_class(argument)
                return o_class()
    except Exception:
        pass
    # Try to match with specially defined classes
    for o_name, o_class in inspect.getmembers(objective,
                                              predicate=_check_class):
        if o_name == name:
            if argument is not None:
                return o_class(argument)
            return o_class()
    if argument is None:
        return SparkleObjective(name=name)
    # Argument was given but cannot be passed
    return None
