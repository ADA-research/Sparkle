#!/usr/bin/env python3
"""Sparkle class to organise configuration output."""

from __future__ import annotations

from sparkle.platform import generate_report_for_parallel_portfolio as sgrfpp
from sparkle.instance import InstanceSet
from sparkle.platform.output.structures import ParallelPortfolioResults

import json
from pathlib import Path


class ParallelPortfolioOutput:
    """Class that collects parallel portfolio data and outputs it a JSON format."""

    def __init__(self: ParallelPortfolioOutput, parallel_portfolio_path: Path,
                 instance_set: InstanceSet,
                 cutoff_time: int, penalised_time: int,
                 output: Path) -> None:
        """Initialize ParallelPortfolioOutput class.

        Args:
            parallel_portfolio_path: Path to parallel portfolio output directory
            instance_set: List of instances
            cutoff_time: The cutoff time
            penalised_time: The penalised time
            output: Path to the output directory
        """
        if not output.is_file():
            self.output = output / "parallel_portfolio.json"
        else:
            self.output = output

        self.instance_set = instance_set
        self.cutoff_time = cutoff_time
        self.penalised_time = penalised_time

        csv_data = [line.split(",") for line in
                    (parallel_portfolio_path / "results.csv").open("r").readlines()]
        self.solver_list = list(set([line[1] for line in csv_data]))

        # Collect solver performance for each instance
        instance_results = {name: [] for name in instance_set._instance_names}
        for row in csv_data:
            if row[0] in instance_results.keys():
                instance_results[row[0]].append([row[1], row[2], row[3]])

        solvers_solutions = self.get_solver_solutions(self.solver_list, csv_data)
        unsolved_instances = self.instance_set.size - sum([solvers_solutions[key]
                                                           for key in solvers_solutions])
        # sbs_runtime is redundant, the same information is available in instance_results
        _, sbs, runtime_all_solvers =\
            sgrfpp.get_dict_sbs_penalty_time_on_each_instance(self.solver_list,
                                                              instance_set,
                                                              instance_results,
                                                              cutoff_time,
                                                              penalised_time)

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

    def serialize_settings(self: ParallelPortfolioOutput) -> dict:
        """Transform settings to dictionary format."""
        return {
            "cutoff_time": self.cutoff_time,
            "penalised_time": self.penalised_time
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
            "settings": self.serialize_settings(),
        }

        self.output.parent.mkdir(parents=True, exist_ok=True)
        with self.output.open("w") as f:
            json.dump(output_data, f, indent=4)
