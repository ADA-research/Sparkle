#!/usr/bin/env python3
"""Sparkle class to organise configuration output."""

from __future__ import annotations

from sparkle.platform import generate_report_for_parallel_portfolio as sgrfpp
from sparkle.instance import InstanceSet
from sparkle.platform.output.structures import ParallelPortfolioResults
from sparkle.types import SparkleObjective

import json
from pathlib import Path
import csv


class ParallelPortfolioOutput:
    """Class that collects parallel portfolio data and outputs it a JSON format."""

    def __init__(self: ParallelPortfolioOutput, parallel_portfolio_path: Path,
                 instance_set: InstanceSet,
                 objective: SparkleObjective,
                 output: Path) -> None:
        """Initialize ParallelPortfolioOutput class.

        Args:
            parallel_portfolio_path: Path to parallel portfolio output directory
            instance_set: List of instances
            objective: The objective of the portfolio
            output: Path to the output directory
        """
        if not output.is_file():
            self.output = output / "parallel_portfolio.json"
        else:
            self.output = output

        self.instance_set = instance_set
        csv_data = [line for line in
                    csv.reader((parallel_portfolio_path / "results.csv").open("r"))]
        header = csv_data[0]
        csv_data = csv_data[1:]
        solver_column = header.index("Solver")
        instance_column = header.index("Instance")
        status_column = [i for i, v in enumerate(header)
                         if v.startswith("status")][0]
        objective_column = header.index(objective.name)
        self.solver_list = list(set([line[solver_column] for line in csv_data]))

        # Collect solver performance for each instance
        instance_results = {name: [] for name in instance_set._instance_names}
        for row in csv_data:
            if row[instance_column] in instance_results.keys():
                instance_results[row[instance_column]].append(
                    [row[solver_column], row[status_column], row[objective_column]])

        solvers_solutions = self.get_solver_solutions(self.solver_list, csv_data)
        unsolved_instances = self.instance_set.size - sum([solvers_solutions[key]
                                                           for key in solvers_solutions])
        # sbs_runtime is redundant, the same information is available in instance_results
        _, sbs, runtime_all_solvers, _ =\
            sgrfpp.get_portfolio_metrics(self.solver_list,
                                         instance_set,
                                         instance_results,
                                         objective)

        self.results = ParallelPortfolioResults(unsolved_instances,
                                                sbs, runtime_all_solvers,
                                                instance_results)

    def get_solver_solutions(self: ParallelPortfolioOutput,
                             solver_list: list[str],
                             csv_data: list[list[str]]) -> dict:
        """Return dictionary with solution count for each solver."""
        # Default initalisation, increase solution counter for each successful evaluation
        solvers_solutions = {solver: 0 for solver in solver_list}
        instance_names_copy = self.instance_set._instance_names.copy()

        for line in csv_data:
            if line[0] in instance_names_copy and line[2].lower() == "success":
                solvers_solutions[line[1]] += 1
                instance_names_copy.remove(line[0])

        return solvers_solutions

    def serialize_instances(self: ParallelPortfolioOutput,
                            instances: list[InstanceSet]) -> dict:
        """Transform Instances to dictionary format."""
        # Even though parallel portfolio currently doesn't support multi sets,
        # this function is already ready to support mutliple sets
        return {
            "number_of_instance_sets": len(instances),
            "instance_sets": [
                {
                    "name": instance.name,
                    "number_of_instances": instance.size
                }
                for instance in instances
            ]
        }

    def serialize_results(self: ParallelPortfolioOutput,
                          pr: ParallelPortfolioResults) -> dict:
        """Transform results to dictionary format."""
        return {
            "sbs": pr.sbs,
            "unsolved_instances": pr.unsolved_instances,
            "runtime_solvers": pr.runtime_solvers,
            "solvers_performance": pr.solver_performance,
            "instance_results": pr.instance_results,
        }

    def write_output(self: ParallelPortfolioOutput) -> None:
        """Write data into a JSON file."""
        output_data = {
            "number_of_solvers": len(self.solver_list),
            "solvers": self.solver_list,
            "instances": self.serialize_instances([self.instance_set]),
            "results": self.serialize_results(self.results),
        }

        self.output.parent.mkdir(parents=True, exist_ok=True)
        with self.output.open("w") as f:
            json.dump(output_data, f, indent=4)
