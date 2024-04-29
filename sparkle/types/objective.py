"""Class for Sparkle Objective and Performance."""
from __future__ import annotations
from enum import Enum


class PerformanceMeasure(Enum):
    """Possible performance measures."""
    ERR = -1
    RUNTIME = 0
    QUALITY_ABSOLUTE = 1
    QUALITY_ABSOLUTE_MINIMISATION = 1
    QUALITY_ABSOLUTE_MAXIMISATION = 2

    @staticmethod
    def from_str(performance_measure: str) -> PerformanceMeasure:
        """Return a given str as PerformanceMeasure."""
        if performance_measure == "RUNTIME":
            performance_measure = PerformanceMeasure.RUNTIME
        elif performance_measure == "QUALITY_ABSOLUTE":
            performance_measure = PerformanceMeasure.QUALITY_ABSOLUTE
        elif performance_measure == "QUALITY_ABSOLUTE_MAXIMISATION":
            performance_measure = PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION
        elif performance_measure == "QUALITY_ABSOLUTE_MINIMISATION":
            performance_measure = PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION
        else:
            performance_measure = PerformanceMeasure.ERR

        return performance_measure


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

    @staticmethod
    def from_multi_str(performance_setting: str) -> list[SparkleObjective]:
        """Create one or more Objectives from the settings string."""
        objectives_str = performance_setting.split(",")
        return [SparkleObjective(objective.strip()) for objective in objectives_str]
