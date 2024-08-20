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
    def __init__(self: ConfigurationResults, default_metrics: float,
                 configured_metrics: float,
                 results_default: ValidationResults,
                 results_configured: ValidationResults) -> None:
        """Initalize ConfigurationResults.

        Args:
            default_metrics: The performance result of the default solver
            configured_metrics: The performance of the configured solver
            results_default: The default results
            results_configured: The configured results
        """
        self.performance = {
            "default_metrics": default_metrics,
            "configured_metrics": configured_metrics
        }
        self.configured_results = results_configured
        self.default_results = results_default
