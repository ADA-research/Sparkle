"""Class for Sparkle Objective and Performance."""
from __future__ import annotations
from enum import Enum


class PerformanceMeasure(Enum):
    """Possible performance measures."""
    ERR = -1
    DEFAULT = 0
    RUNTIME = 1
    QUALITY_ABSOLUTE = 2
    QUALITY_ABSOLUTE_MINIMISATION = 2
    QUALITY_ABSOLUTE_MAXIMISATION = 3

    @staticmethod
    def from_str(performance_measure: str) -> PerformanceMeasure:
        """Return a given str as PerformanceMeasure."""
        if performance_measure == "DEFAULT":
            return PerformanceMeasure.DEFAULT
        if performance_measure == "RUNTIME":
            return PerformanceMeasure.RUNTIME
        elif performance_measure == "QUALITY_ABSOLUTE":
            return PerformanceMeasure.QUALITY_ABSOLUTE
        elif performance_measure == "QUALITY_ABSOLUTE_MAXIMISATION":
            return PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION
        elif performance_measure == "QUALITY_ABSOLUTE_MINIMISATION":
            return PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION
        return PerformanceMeasure.ERR

    @staticmethod
    def to_str(performance_measure: PerformanceMeasure) -> str:
        """Return a given PerformanceMeasure as str."""
        if performance_measure == PerformanceMeasure.DEFAULT:
            return "DEFAULT"
        if performance_measure == PerformanceMeasure.RUNTIME:
            return "RUNTIME"
        elif performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE:
            return "QUALITY_ABSOLUTE"
        elif performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION:
            return "QUALITY_ABSOLUTE_MAXIMISATION"
        elif performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION:
            return "QUALITY_ABSOLUTE_MINIMISATION"
        return "ERR"


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
        self.PerformanceMeasure = PerformanceMeasure.from_str(performance_measure)
        self.metric = metric

        if self.PerformanceMeasure == PerformanceMeasure.ERR:
            print(f"WARNING: Performance measure {performance_measure} not found!")
        return

    def __str__(self: SparkleObjective) -> str:
        """Return a string of the format TYPE:METRIC."""
        return f"{PerformanceMeasure.to_str(self.PerformanceMeasure)}:{self.metric}"

    @staticmethod
    def from_multi_str(performance_setting: str) -> list[SparkleObjective]:
        """Create one or more Objectives from the settings string."""
        objectives_str = performance_setting.split(",")
        return [SparkleObjective(objective.strip()) for objective in objectives_str]
