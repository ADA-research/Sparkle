"""Class for Sparkle Objective and Performance."""
from __future__ import annotations
from enum import Enum
import typing
import numpy as np


class UseTime(str, Enum):
    """Use time or not."""
    WALL_TIME = "WALL_TIME"
    CPU_TIME = "CPU_TIME"
    NO = "NO"

    @classmethod
    def _missing_(cls: UseTime, value: object) -> UseTime:
        """Return error use time."""
        return UseTime.NO


class SparkleObjective:
    """Objective for Sparkle specified by user."""

    name: str
    run_aggregator: typing.Callable
    instance_aggregator: typing.Callable
    solver_aggregator: typing.Callable
    minimise: bool
    post_process: typing.Callable
    use_time: UseTime

    def __init__(self: SparkleObjective,
                 name: str,
                 run_aggregator: typing.Callable = np.mean,
                 instance_aggregator: typing.Callable = np.mean,
                 solver_aggregator: typing.Callable = None,
                 minimise: bool = True,
                 post_process: typing.Callable = None,
                 use_time: UseTime = UseTime.NO) -> None:
        """Create sparkle objective from string."""
        self.name = name
        self.run_aggregator: typing.Callable = run_aggregator
        self.instance_aggregator: typing.Callable = instance_aggregator
        if solver_aggregator is None:
            solver_aggregator = np.min if minimise else np.max
        self.solver_aggregator: typing.Callable = solver_aggregator
        self.minimise: bool = minimise
        self.post_process: typing.Callable = post_process
        self.use_time: UseTime = use_time

    def __str__(self: SparkleObjective) -> str:
        """Return a stringified version."""
        return f"{self.name}"

    @property
    def time(self: SparkleObjective) -> bool:
        """Return whether the objective is time based."""
        return self.use_time != UseTime.NO


class PAR(SparkleObjective):
    """Penalised Averaged Runtime Objective for Sparkle."""

    def __init__(self: PAR, k: int = 10) -> None:
        """Initialize PAR."""
        self.k = k
        if k <= 0:
            raise ValueError("k must be greater than 0.")

        def penalise(value: float, cutoff: float) -> float:
            """Return penalised value."""
            if value > cutoff:
                return cutoff * self.k
            return value

        super().__init__(f"PAR{k}", use_time=UseTime.CPU_TIME, post_process=penalise)
