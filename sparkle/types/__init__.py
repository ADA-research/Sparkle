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


objective_string_regex = re.compile(
    r"(?P<name>[\w\-_]+)(:(?P<direction>min|max))?(:(?P<type>metric|objective))?$")
objective_variable_regex = re.compile(r"(-?\d+)$")


def _check_class(candidate: Callable) -> bool:
    """Verify whether a loaded class is a valid objective class."""
    return inspect.isclass(candidate) and issubclass(candidate, SparkleObjective)


def resolve_objective(objective_name: str) -> SparkleObjective:
    """Try to resolve the objective class by (case-sensitive) name.

    convention: objective_name(variable-k)?(:[min|max])?(:[metric|objective])?
    Here, min|max refers to the minimisation or maximisation of the objective
    and metric|objective refers to whether the objective should be optimized
    or just recorded.

    Order of resolving:
        class_name of user defined SparkleObjectives
        class_name of sparkle defined SparkleObjectives
        default SparkleObjective with minimization unless specified as max

    Args:
        name: The name of the objective class. Can include parameter value k.

    Returns:
        Instance of the Objective class or None if not found.
    """
    match = objective_string_regex.fullmatch(objective_name)
    if match is None or objective_name == "" or not objective_name[0].isalpha():
        return None

    name = match.group("name")
    minimise = not match.group("direction") == "max"  # .group returns "" if no match
    metric = match.group("type") == "metric"

    # Search for optional variable and record split point between name and variable
    name_options = [(name, None), ]  # Options of names to check for
    if m := objective_variable_regex.search(name):
        argument = int(m.group())
        name_options = [(name[:m.start()], argument), ] + name_options  # Prepend

    # First try to resolve the user input classes
    for rname, rarg in name_options:
        try:
            user_module = importlib.import_module("Settings.objective")
            for o_name, o_class in inspect.getmembers(user_module,
                                                      predicate=_check_class):
                if o_name == rname:
                    if rarg is not None:
                        return o_class(rarg, minimise=minimise, metric=metric)
                    return o_class(minimise=minimise, metric=metric)
        except Exception:
            pass

    for rname, rarg in name_options:
        # Try to match with specially defined classes
        for o_name, o_class in inspect.getmembers(objective,
                                                  predicate=_check_class):
            if o_name == rname:
                if rarg is not None:
                    return o_class(rarg, minimise=minimise, metric=metric)
                return o_class(minimise=minimise, metric=metric)

    # No special objects found. Return objective with full name
    return SparkleObjective(name=objective_name, minimise=minimise, metric=metric)
