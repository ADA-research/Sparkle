#!/usr/bin/env python3
"""Sparkle output structures."""
from __future__ import annotations
import sys
from pathlib import Path

from runrunner.base import Status

from sparkle.solver import Solver
from sparkle.types import SolverStatus, SparkleObjective
from sparkle.instance import InstanceSet
from sparkle.structures import PerformanceDataFrame


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


class SelectionSolverData:
    """Class that stores solver information."""
    def __init__(self: SelectionSolverData,
                 solver_performance_ranking: list[tuple[str, float]],
                 num_solvers: int) -> None:
        """Initalize SelectionSolverData.

        Args:
            solver_performance_ranking: list with solvers ranked by avg. performance
            num_solvers: The number of solvers
        """
        self.solver_performance_ranking = solver_performance_ranking
        self.single_best_solver = solver_performance_ranking[0][0]
        self.num_solvers = num_solvers


class SelectionPerformance:
    """Class that stores selection performance results."""
    def __init__(self: SelectionSolverData,
                 performance_path: Path,
                 vbs_performance: float,
                 objective: SparkleObjective) -> None:
        """Initalize SelectionPerformance.

        Args:
            performance_path: Path to portfolio selector performance
            vbs_performance: The performance of the virtual best selector
            objective: The objective (Performance type)
        """
        if not performance_path.exists():
            print(f"ERROR: {performance_path} does not exist.")
            sys.exit(-1)
        actual_performance_data = PerformanceDataFrame(performance_path)
        self.vbs_performance = vbs_performance
        self.actual_performance = actual_performance_data.mean(
            objective=objective.name)
        self.metric = objective.name


class ParallelPortfolioResults:
    """Class that stores parallel portfolio results."""
    def __init__(self: ParallelPortfolioResults,
                 unsolved_instances: int,
                 sbs: str,
                 runtime_solvers: dict[str, float],
                 instance_results: dict[str, list]) -> None:
        """Initalize SelectionSolverData.

        Args:
            unsolved_instances: Number of unsolved instances
            sbs: Name of the single best solver
            runtime_solvers: Dictionary containing penalised average runtime per solver
            instance_results: Dictionary containing
        """
        self.unsolved_instances = unsolved_instances
        self.sbs = sbs
        self.runtime_solvers = runtime_solvers
        self.instance_results = instance_results

        self.solver_performance = {}
        # Iterate over each instance and aggregate the results
        for _, results in self.instance_results.items():
            for solver_result in results:
                solver_name = solver_result[0]
                outcome = solver_result[1]
                # Initialize the solver's record in solver_performance if not present
                if solver_name not in self.solver_performance:
                    self.solver_performance[solver_name] = {
                        status: 0 for status in SolverStatus
                    }
                # Increment the appropriate outcome count
                self.solver_performance[solver_name][outcome] += 1
