"""Class for Sparkle Objective and Performance."""
from __future__ import annotations
from enum import Enum


class PerformanceMeasure(str, Enum):
    """Possible performance measures."""
    ERR = "ERR"
    DEFAULT = "DEFAULT"
    RUNTIME = "RUNTIME"
    QUALITY_ABSOLUTE = "QUALITY_ABSOLUTE_MINIMISATION"
    QUALITY_ABSOLUTE_MINIMISATION = "QUALITY_ABSOLUTE_MINIMISATION"
    QUALITY_ABSOLUTE_MAXIMISATION = "QUALITY_ABSOLUTE_MAXIMISATION"

    @classmethod
    def _missing_(cls: PerformanceMeasure, value: object) -> PerformanceMeasure:
        """Return error performance measure."""
        return PerformanceMeasure.ERR


class Metric:
    """Metric for Sparkle objective."""

    def __init__(self: Metric, metric: str) -> None:
        """Initialize Metric."""
        self.name = metric

    def __str__(self: Metric) -> str:
        """Return the name of the metric."""
        return self.name


class SparkleObjective():
    """Objective for Sparkle specified by user.

    Specified in settings.ini's [general] performance_measure.
    Contains the type of Performance Measure, and the type of metric.
    """

    def __init__(self: SparkleObjective, performance_setting: str) -> None:
        """Create sparkle objective from string of format TYPE:METRIC."""
        self.name = performance_setting
        if ":" not in performance_setting:
            print(f"WARNING: Objective {performance_setting} not fully specified. "
                  "Continuing with default values.")
            performance_measure, metric = performance_setting, ""
        else:
            performance_measure, metric = performance_setting.split(":")
        self.PerformanceMeasure = PerformanceMeasure(performance_measure)
        self.metric = metric

        if self.PerformanceMeasure == PerformanceMeasure.ERR:
            print(f"WARNING: Performance measure {performance_measure} not found!")

    def __str__(self: SparkleObjective) -> str:
        """Return a string of the format TYPE:METRIC."""
        return f"{self.PerformanceMeasure}:{self.metric}"

    @staticmethod
    def from_multi_str(performance_setting: str) -> list[SparkleObjective]:
        """Create one or more Objectives from the settings string."""
        objectives_str = performance_setting.split(",")
        return [SparkleObjective(objective.strip()) for objective in objectives_str]
