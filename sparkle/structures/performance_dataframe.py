#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module to manage performance data CSV files and common operations on them."""


from __future__ import annotations
from typing import Callable
import operator
from pathlib import Path
import sys
import math
from statistics import mean
import pandas as pd

from sparkle.types.objective import SparkleObjective


class PerformanceDataFrame():
    """Class to manage performance data and common operations on them."""
    missing_value = math.nan
    missing_objective = "DEFAULT:UNKNOWN"
    multi_dim_names = ["Objective", "Instance", "Run"]

    def __init__(self: PerformanceDataFrame,
                 csv_filepath: Path,
                 solvers: list[str] = [],
                 objectives: list[str | SparkleObjective] = None,
                 instances: list[str] = [],
                 n_runs: int = 1,
                 init_df: bool = True) -> None:
        """Initialise a PerformanceDataFrame.

        Consists of:
            - Columns representing the Solvers
            - Rows representing the result by multi-index in order of:
                * Objective (Static, given in constructor or read from file)
                * Instance
                * Runs (Static, given in constructor or read from file)

        Args:
            csv_filepath: If path exists, load from Path.
                Otherwise create new and save to this path.
            solvers: List of solver names to be added into the Dataframe
            objectives: List of SparkleObjectives or objective names. By default None,
                then the objectives will be derived from Sparkle Settings if possible.
            instances: List of instance names to be added into the Dataframe
            n_runs: The number of runs to consider per Solver/Objective/Instance comb.
            init_df: Whether the dataframe should be initialised. Set to false to reduce
                heavy IO loads.
        """
        self.csv_filepath = csv_filepath
        # Runs is a ``static'' dimension
        self.n_runs = n_runs
        self.run_ids = list(range(1, self.n_runs + 1))  # We count runs from 1
        if init_df:
            if self.csv_filepath.exists():
                self.dataframe = pd.read_csv(csv_filepath)
                has_rows = len(self.dataframe.index) > 0
                if (PerformanceDataFrame.multi_dim_names[0] not in self.dataframe.columns
                        or not has_rows):
                    # No objective present, force into column
                    if objectives is None:
                        self.dataframe[PerformanceDataFrame.multi_dim_names[0]] =\
                            PerformanceDataFrame.missing_objective
                    else:  # Constructor is provided with the objectives
                        objectives = [o.name if isinstance(o, SparkleObjective) else o
                                      for o in objectives]
                        self.dataframe[PerformanceDataFrame.multi_dim_names[0]] =\
                            objectives
                if (PerformanceDataFrame.multi_dim_names[2] not in self.dataframe.columns
                        or not has_rows):
                    # No runs column present, force into column
                    self.n_runs = 1
                    self.dataframe[PerformanceDataFrame.multi_dim_names[2]] = self.n_runs
                    self.run_ids = [self.n_runs]
                else:
                    # Runs are present, determine run ids
                    run_label = PerformanceDataFrame.multi_dim_names[2]
                    self.run_ids = self.dataframe[run_label].unique().tolist()
                if PerformanceDataFrame.multi_dim_names[1] not in self.dataframe.columns:
                    # Instances are listed as rows, force into column
                    self.dataframe = self.dataframe.reset_index().rename(
                        columns={"index": PerformanceDataFrame.multi_dim_names[1]})
                # Now we can cast the columns into multi dim
                self.dataframe = self.dataframe.set_index(
                    PerformanceDataFrame.multi_dim_names)
            else:
                # Initialize empty DataFrame
                if objectives is None:
                    objective_names = [PerformanceDataFrame.missing_objective]
                else:
                    objective_names =\
                        [o.name if isinstance(o, SparkleObjective) else o
                         for o in objectives]
                midx = pd.MultiIndex.from_product(
                    [objective_names, instances, self.run_ids],
                    names=PerformanceDataFrame.multi_dim_names)
                self.dataframe = pd.DataFrame(PerformanceDataFrame.missing_value,
                                              index=midx,
                                              columns=solvers)
                self.save_csv()
            # Sort the index to optimize lookup speed
            self.dataframe = self.dataframe.sort_index()

    def verify_objective(self: PerformanceDataFrame,
                         objective: str) -> str:
        """Method to check whether the specified objective is valid.

        Users are allowed to index the dataframe without specifying all dimensions.
        However, when dealing with multiple objectives this is not allowed and this
        is verified here. If we have only one objective this is returned. Otherwise,
        if an objective is specified by the user this is returned.

        Args:
            objective: The objective given by the user
        """
        if objective is None:
            if self.multi_objective:
                print("Error: MO Performance Data, but objective not specified.")
                sys.exit(-1)
            elif self.num_objectives == 1:
                return self.objective_names[0]
            else:
                return PerformanceDataFrame.missing_objective
        return objective

    def verify_run_id(self: PerformanceDataFrame,
                      run_id: int) -> int:
        """Method to check whether run id is valid.

        Similar to verify_objective but here we check the dimensionality of runs.

        Args:
            run_id: the run as specified by the user.
        """
        if run_id is None:
            if self.n_runs > 1:
                print("Error: Multiple run performance data, but run not specified")
                sys.exit(-1)
            else:
                run_id = self.run_ids[0]
        return run_id

    def verify_indexing(self: PerformanceDataFrame,
                        objective: str,
                        run_id: int) -> tuple[str, int]:
        """Method to check whether data indexing is correct.

        Users are allowed to use the Performance Dataframe without the second and
        fourth dimension (Objective and Run respectively) in the case they only
        have one objective or only do one run. This method adjusts the indexing for
        those cases accordingly.

        Args:
            objective: The given objective name
            run_id: The given run index

        Returns:
            A tuple representing the (possibly adjusted) Objective and Run index.
        """
        objective = self.verify_objective(objective)
        run_id = self.verify_run_id(run_id)
        return objective, run_id

    def add_solver(self: PerformanceDataFrame,
                   solver_name: str,
                   initial_value: float | list[float] = None) -> None:
        """Add a new solver to the dataframe. Initializes value to None by default.

        Args:
            solver_name: The name of the solver to be added.
            initial_value: The value assigned for each index of the new solver.
                If not None, must match the index dimension (n_obj * n_inst * n_runs).
        """
        if solver_name in self.dataframe.columns:
            print(f"WARNING: Tried adding already existing solver {solver_name} to "
                  f"Performance DataFrame: {self.csv_filepath}")
            return
        self.dataframe[solver_name] = initial_value

    def add_instance(self: PerformanceDataFrame,
                     instance_name: str,
                     initial_value: float | list[float] = None) -> None:
        """Add and instance to the DataFrame."""
        if self.dataframe.index.size == 0 or self.dataframe.columns.size == 0:
            # First instance or no Solvers yet
            solvers = self.dataframe.columns.to_list()
            instances = self.dataframe.index.levels[1].to_list() + [instance_name]
            midx = pd.MultiIndex.from_product(
                [self.objective_names, instances, self.run_ids],
                names=PerformanceDataFrame.multi_dim_names)
            self.dataframe = pd.DataFrame(initial_value, index=midx, columns=solvers)
        else:
            if instance_name in self.dataframe.index.levels[1]:
                print(f"WARNING: Tried adding already existing instance {instance_name} "
                      f"to Performance DataFrame: {self.csv_filepath}")
                return
            # Create the missing indices
            levels = [self.dataframe.index.levels[0].tolist(),
                      [instance_name],
                      self.dataframe.index.levels[2].tolist()]
            emidx = pd.MultiIndex(levels, names=PerformanceDataFrame.multi_dim_names)
            # Create the missing column values
            edf = pd.DataFrame(PerformanceDataFrame.missing_value,
                               index=emidx,
                               columns=self.dataframe.columns)
            # Concatenate the original and new dataframe together
            self.dataframe = pd.concat([self.dataframe, edf])

    # Can we make this handle a sequence of inputs instead of just 1?
    def set_value(self: PerformanceDataFrame,
                  value: float,
                  solver: str,
                  instance: str,
                  objective: str = None,
                  run: int = None) -> None:
        """Setter method to assign a value to the Dataframe.

        Args:
            value: Float value to be assigned.
            solver: The solver that produced the value.
            instance: The instance that the value was produced on.
            objective: The objective for which the result was produced.
                Optional in case of using single objective.
            run: The run index for which the result was produced.
                Optional in case of doing single run results.
        """
        objective, run = self.verify_indexing(objective, run)
        self.dataframe.at[(objective, instance, run), solver] = value

    def remove_solver(self: PerformanceDataFrame, solver_name: str) -> None:
        """Drop a solver from the Dataframe."""
        self.dataframe.drop(solver_name, axis=1, inplace=True)

    def remove_instance(self: PerformanceDataFrame, instance_name: str) -> None:
        """Drop an instance from the Dataframe."""
        self.dataframe.drop(instance_name, axis=0, level="Instance", inplace=True)

    def reset_value(self: PerformanceDataFrame,
                    solver: str,
                    instance: str,
                    objective: str = None,
                    run: int = None) -> None:
        """Reset a value in the dataframe."""
        self.set_value(PerformanceDataFrame.missing_value,
                       solver, instance, objective, run)

    def get_value(self: PerformanceDataFrame,
                  solver: str,
                  instance: str,
                  objective: str = None,
                  run: int = None) -> float:
        """Index a value of the DataFrame and return it."""
        objective, run = self.verify_indexing(objective, run)
        return self.dataframe.loc[(objective, instance, run), solver]

    @property
    def num_objectives(self: PerformanceDataFrame) -> int:
        """Retrieve the number of objectives in the DataFrame."""
        return self.dataframe.index.levels[0].size

    @property
    def num_instances(self: PerformanceDataFrame) -> int:
        """Return the number of instances."""
        return self.dataframe.index.levels[1].size

    @property
    def num_runs(self: PerformanceDataFrame) -> int:
        """Return the number of runs."""
        return self.dataframe.index.levels[2].size

    @property
    def num_solvers(self: PerformanceDataFrame) -> int:
        """Return the number of solvers."""
        return self.dataframe.columns.size

    @property
    def multi_objective(self: PerformanceDataFrame) -> bool:
        """Return whether the dataframe represent MO or not."""
        return self.num_objectives > 1

    @property
    def solvers(self: PerformanceDataFrame) -> list[str]:
        """Return the solver present as a list of strings."""
        return self.dataframe.columns.tolist()

    @property
    def objective_names(self: PerformanceDataFrame) -> list[str]:
        """Return the objective names as a list of strings."""
        if self.num_objectives == 0:
            return [PerformanceDataFrame.missing_objective]
        return self.dataframe.index.levels[0].tolist()

    @property
    def instances(self: PerformanceDataFrame) -> list[str]:
        """Return the instances as a Pandas Index object."""
        return self.dataframe.index.levels[1].tolist()

    def penalise(self: PerformanceDataFrame,
                 threshold: float,
                 penalty: float,
                 objective: str = None,
                 lower_bound: bool = False) -> None:
        """Penalises the DataFrame values if crossing threshold by specified penalty.

        Directly updates the DataFrame object held by this class.

        Args:
            threshold: The threshold of performances to be met
            penalty: The values assigned for out of bounds performances
            objective: The objective that should be penalised.
            lower_bound: Whether the threshold is a lower_bound. By default,
                the threshold is treated as an upperbound for performance values.
        """
        objective = self.verify_objective(objective)
        comparison_op = operator.lt if lower_bound else operator.gt
        self.dataframe[comparison_op(self.dataframe.loc[(objective), :],
                                     threshold)] = penalty

    def get_job_list(self: PerformanceDataFrame, rerun: bool = False) \
            -> list[tuple[str, str]]:
        """Return a list of performance computation jobs there are to be done.

        Get a list of tuple[instance, solver] to run from the performance data
        csv file. If rerun is False (default), get only the tuples that don't have a
        value in the table, else (True) get all the tuples.

        Args:
            rerun: Boolean indicating if we want to rerun all jobs
        """
        df = self.dataframe.stack(future_stack=True)
        if not rerun:
            df = df[df.isnull()]
        if not self.multi_objective:
            df.index = df.index.droplevel(["Objective"])
        if self.n_runs == 1:
            df.index = df.index.droplevel(["Run"])
        return df.index.tolist()

    def has_missing_performance(self: PerformanceDataFrame) -> bool:
        """Returns True if there are any missing values in the dataframe."""
        return self.dataframe.isnull().any().any()

    def remaining_jobs(self: PerformanceDataFrame) -> dict[str, list[str]]:
        """Return a dictionary for empty values per instance and solver combination."""
        remaining_jobs = {}
        null_df = self.dataframe.isnull()
        for row in self.dataframe.index:
            instance = row[1]
            for solver in self.dataframe.columns:
                if null_df.at[row, solver]:
                    if instance not in remaining_jobs:
                        remaining_jobs[instance] = set([solver])
                    else:
                        remaining_jobs[instance].add(solver)
        return remaining_jobs

    def get_best_performance_per_instance(
            self: PerformanceDataFrame,
            objective: str = None,
            run_agg: Callable = None,
            best: Callable = pd.DataFrame.min) -> list[float]:
        """Return a list with the best performance per instance.

        Allows user to specify how to aggregate runs together.
        Must be pandas accepted callable.

        Args:
            objective: The objective over which we want the ``best''
            run_agg: The method defining how runs are combined per Instance/solver
            best: Callable, replace with pd.DataFrame.max to maximise

        Returns:
            A list of floats representing the best performance per instance
        """
        objective = self.verify_objective(objective)
        if run_agg is None:
            return best(self.dataframe.loc[(objective), :], axis=1).to_list()
        else:
            # Select the objective, group by runs, apply the aggregator and select max
            agg_runs = self.dataframe.loc[(objective), :].groupby(level=0).run_agg()
            return best(agg_runs, axis=1).to_list()

    def best_performance_instance(
            self: PerformanceDataFrame,
            instance: str,
            minimise: bool,
            objective: str = None,
            exclude_solvers: list[str] = [],
            run_aggregator: Callable = mean) -> float:
        """Return the best performance for a specific instance.

        Args:
            instance: The instance in question
            minimise: Whether we should minimise or maximise the score
            objective: The objective for which we calculate the best performance
            capvalue: The minimum/maximum scoring value the VBS is allowed to have
            run_aggregator: How we aggregate multiple runs for an instance-solver
                combination. Only relevant for multi-runs.
            exclude_solvers: List of solvers to exclude in the calculation.

        Returns:
            The virtual best solver performance for this instance.
        """
        objective = self.verify_objective(objective)
        best_score = None
        compare = operator.lt if minimise else operator.gt
        for solver in self.solvers:
            if solver in exclude_solvers:
                continue
            if isinstance(instance, str):
                runs = self.dataframe.loc[(objective, instance), solver]
                score_solver = run_aggregator(runs)
            else:
                score_solver = float(self.dataframe.loc[instance, solver])
            if best_score is None or compare(score_solver, best_score):
                best_score = score_solver

        if best_score is None:
            print("WARNING: PerformanceDataFrame could not calculate best performance "
                  f"for instance {instance}.")
            return PerformanceDataFrame.missing_value

        return best_score

    def best_performance(
            self: PerformanceDataFrame,
            aggregation_function: Callable[[list[float]], float],
            minimise: bool,
            exclude_solvers: list[str] = [],
            objective: str = None) -> float:
        """Return the overall best performance of the portfolio.

        Args:
            aggregation_function: The method of combining all VBS scores together
            minimise: Whether the scores are minimised or not
            capvalue_list: List of capvalue per instance
            penalty_list: List of penalty per instance
            exclude_solvers: List of solvers to exclude in the calculation.
                Defaults to none.

        Returns:
            The aggregated best performance of the portfolio over all instances.
        """
        objective = self.verify_objective(objective)
        instance_best = []
        for instance in self.instances:
            best_score = self.best_performance_instance(
                instance, minimise, objective, exclude_solvers)
            instance_best.append(best_score)

        return aggregation_function(instance_best)

    def marginal_contribution(self: PerformanceDataFrame,
                              aggregation_function: Callable[[list[float]], float],
                              minimise: bool,
                              pre_selection: list[str] = None,
                              objective: str = None,
                              ) -> list[float]:
        """Return the marginal contribution of the solvers on the instances.

        Args:
            aggregation_function: Function for combining scores over instances together.
            minimise: Whether we should minimise or maximise the score of the objective.
            capvalue_list: List of capvalue per instance
            penalty_list: List of penalty per instance
            objective: The objective for which we calculate the marginal contribution.

        Returns:
            The marginal contribution of each solver.
        """
        output = []
        objective = self.verify_objective(objective)
        best_performance = self.best_performance(
            aggregation_function, minimise, objective=objective)
        for solver in self.solvers:
            # By calculating the best performance excluding this Solver,
            # we can determine its relative impact on the portfolio.
            missing_solver_best = self.best_performance(
                aggregation_function,
                minimise,
                exclude_solvers=[solver],
                objective=objective)
            # Now we need to see how much the portfolio's best performance
            # decreases without this solver.
            marginal_contribution = missing_solver_best / best_performance
            if missing_solver_best == best_performance:
                # No change, no contribution
                marginal_contribution = 0.0
            output.append((solver, marginal_contribution, missing_solver_best))
        return output

    def get_dict_vbs_penalty_time_on_each_instance(
            self: PerformanceDataFrame,
            penalised_time: int,
            objective: str = None,
            run_id: int = None) -> dict:
        """Return a dictionary of penalised runtimes and instances for the VBS."""
        objective = self.verify_objective(objective)
        instance_penalized_runtimes = {}
        for instance in self.dataframe.index.levels[1]:
            if run_id is None:
                runtime = self.dataframe.loc[(objective, instance), :].min(axis=None)
            else:
                runtime =\
                    self.dataframe.loc[(objective, instance, run_id), :].min(axis=None)
            instance_penalized_runtimes[instance] = min(penalised_time, runtime)

        return instance_penalized_runtimes

    def calc_vbs_penalty_time(self: PerformanceDataFrame,
                              cutoff_time: int = None,
                              penalty: int = None,
                              objective: str = None) -> float:
        """Return the penalised performance of the VBS."""
        objective = self.verify_objective(objective)
        if cutoff_time is not None and penalty is not None:
            self.penalise(cutoff_time, penalty)
        # Calculate the minimum for the selected objective per instance
        min_instance_df = self.dataframe.loc(axis=0)[objective, :, :].min(axis=1)
        # Return average
        return min_instance_df.sum() / self.dataframe.index.size

    def get_solver_penalty_time_ranking(self: PerformanceDataFrame,
                                        cutoff_time: int = None,
                                        penalty: int = None,
                                        objective: str = None,
                                        ) -> list[list[float]]:
        """Return a list with solvers ranked by penalised runtime."""
        objective = self.verify_objective(objective)
        if cutoff_time is not None and penalty is not None:
            self.penalise(cutoff_time, penalty, objective)
        solver_penalty_time_ranking = []
        num_instances = self.dataframe.index.size
        sub_df = self.dataframe.loc(axis=0)[objective, :, :]
        for solver in self.dataframe.columns:
            average_time = sub_df[solver].sum() / num_instances
            solver_penalty_time_ranking.append([solver, average_time])

        # Sort the list by second value (the penalised run time)
        solver_penalty_time_ranking.sort(
            key=lambda this_penalty_time: this_penalty_time[1])

        return solver_penalty_time_ranking

    def save_csv(self: PerformanceDataFrame, csv_filepath: Path = None) -> None:
        """Write a CSV to the given path.

        Args:
            csv_filepath: String path to the csv file. Defaults to self.csv_filepath.
        """
        csv_filepath = self.csv_filepath if csv_filepath is None else csv_filepath
        self.dataframe.to_csv(csv_filepath)

    def clean_csv(self: PerformanceDataFrame) -> None:
        """Set all values in Performance Data to None."""
        self.dataframe[:] = PerformanceDataFrame.missing_value
        self.save_csv()

    def copy(self: PerformanceDataFrame,
             csv_filepath: Path = None) -> PerformanceDataFrame:
        """Create a copy of this object.

        Args:
            csv_filepath: The new filepath to use for saving the object to.
                Warning: If the original path is used, it could lead to dataloss!
        """
        csv_filepath = self.csv_filepath if csv_filepath is None else csv_filepath
        pd_copy = PerformanceDataFrame(self.csv_filepath, init_df=False)
        pd_copy.dataframe = self.dataframe.copy()
        pd_copy.csv_filepath = csv_filepath
        return pd_copy

    def to_autofolio(self: PerformanceDataFrame) -> Path:
        """Port the data to a format acceptable for AutoFolio."""
        if self.multi_objective or self.n_runs > 1:
            print(f"ERROR: Currently no porting available for {self.csv_filepath} "
                  "to Autofolio due to multi objective or number of runs.")
            return
        autofolio_df = self.dataframe.copy()
        autofolio_df.index = autofolio_df.index.droplevel(["Objective", "Run"])
        path = self.csv_filepath.parent / f"autofolio_{self.csv_filepath.name}"
        autofolio_df.to_csv(path)
        return path
