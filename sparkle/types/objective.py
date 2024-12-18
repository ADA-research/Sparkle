"""Class for Sparkle Objective and Performance."""
from __future__ import annotations
from enum import Enum
import typing
import numpy as np
from sparkle.types.status import SolverStatus


class UseTime(str, Enum):
    """Enum describing what type of time to use."""
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
    metric: bool

    def __init__(self: SparkleObjective,
                 name: str,
                 run_aggregator: typing.Callable = np.mean,
                 instance_aggregator: typing.Callable = np.mean,
                 solver_aggregator: typing.Callable = None,
                 minimise: bool = True,
                 post_process: typing.Callable = None,
                 use_time: UseTime = UseTime.NO,
                 metric: bool = False) -> None:
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
        self.metric = metric

    def __str__(self: SparkleObjective) -> str:
        """Return a stringified version."""
        return self.name

    @property
    def stem(self: SparkleObjective) -> str:
        """Return the stem of the objective name."""
        return self.name.split(":")[0]

    @property
    def time(self: SparkleObjective) -> bool:
        """Return whether the objective is time based."""
        return self.use_time != UseTime.NO


class PAR(SparkleObjective):
    """Penalised Averaged Runtime Objective for Sparkle."""
    negative_status = {SolverStatus.CRASHED,
                       SolverStatus.KILLED,
                       SolverStatus.ERROR,
                       SolverStatus.TIMEOUT,
                       SolverStatus.WRONG}

    def __init__(self: PAR, k: int = 10,
                 minimise: bool = True,
                 metric: bool = False) -> None:
        """Initialize PAR."""
        self.k = k
        if k <= 0:
            raise ValueError("k must be greater than 0.")

        def penalise(value: float, cutoff: float, status: SolverStatus) -> float:
            """Return penalised value."""
            if status in PAR.negative_status or value > cutoff:
                return cutoff * self.k
            return value

        super().__init__(f"PAR{k}",
                         minimise=minimise,
                         use_time=UseTime.CPU_TIME,
                         post_process=penalise,
                         metric=metric)
