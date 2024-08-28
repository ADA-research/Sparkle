#!/usr/bin/env python3
"""Sparkle output structures."""

from __future__ import annotations

from sparkle.solver import Solver
from sparkle.instance import InstanceSet

from runrunner.base import Status


class ValidationResults:
    """Class that stores validation information and results."""
    def __init__(self: ValidationResults, solver: Solver,
                 configuration: dict, instance_set: InstanceSet,
                 results: list[list[str, Status, float, float]]) -> None:
        """Initalize ValidationResults.

        Args:
            solver: The name of the solver
            configuration: The configuration being used
            instance_set: The set of instances
            results: Validation results in the format:
                [["instance", "status", "quality", "runtime"]]
        """
        self.solver = solver
        self.configuration = configuration
        self.instance_set = instance_set
        self.result_header = ["instance", "status", "quality", "runtime"]
        self.result_vals = results


class ConfigurationResults:
    """Class that aggregates configuration results."""
    def __init__(self: ConfigurationResults, metrics: float,
                 results: ValidationResults) -> None:
        """Initalize ConfigurationResults.

        Args:
            metrics: The performance of a configured solver
            results: The results for one configuration
        """
        self.performance = metrics
        self.results = results
