#!/usr/bin/env python3
"""Sparkle class to organise configuration output."""

from __future__ import annotations

from sparkle.CLI.help import global_variables as gv
from sparkle.platform.settings_objects import Settings
from sparkle.platform import generate_report_for_parallel_portfolio as sgrfpp
from sparkle.instance import InstanceSet

import json
from pathlib import Path, PurePath


class ParallelPortfolioResults:
    """Class that stores parallel portfolio results."""
    def __init__(self: ParallelPortfolioOutput,
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
                        "TIMEOUT": 0,
                        "KILLED": 0,
                        "SUCCESS": 0
                    }
                # Increment the appropriate outcome count
                self.solver_performance[solver_name][outcome] += 1


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
        if output.is_dir():
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
        print("Analysis of selection can be found here: ", self.output)


if __name__ == "__main__":
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings(), prev_settings)

    path = Path("Output/Parallel_Portfolio/Raw_Data/runtime_experiment")
    perf_path = gv.settings().DEFAULT_performance_data_path
    feature_path = gv.settings().DEFAULT_feature_data_path
    cutoff_time = gv.settings().get_general_target_cutoff_time()
    penalised_time = gv.settings().get_penalised_time()

    instance_set = gv.latest_scenario().get_parallel_portfolio_instance_set()

    output = path / "Analysis" / "parallel_portfolio.json"

    output = ParallelPortfolioOutput(path, instance_set, cutoff_time,
                                     penalised_time, output)
    output.write_output()