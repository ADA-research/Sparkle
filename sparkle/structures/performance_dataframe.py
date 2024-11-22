#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module to manage performance data files and common operations on them."""
from __future__ import annotations
import itertools
from pathlib import Path
import math
import pandas as pd

from sparkle.types import SparkleObjective, resolve_objective


class PerformanceDataFrame(pd.DataFrame):
    """Class to manage performance data and common operations on them."""
    missing_value = math.nan

    missing_objective = "UNKNOWN"

    index_objective = "Objective"
    index_instance = "Instance"
    index_run = "Run"
    multi_index_names = [index_objective, index_instance, index_run]

    column_value = "Value"
    column_seed = "Seed"
    column_configuration = "Configuration"
    multi_column_names = [column_value, column_seed, column_configuration]

    def __init__(self: PerformanceDataFrame,
                 csv_filepath: Path,
                 solvers: list[str] = None,
                 objectives: list[str | SparkleObjective] = None,
                 instances: list[str] = None,
                 n_runs: int = 1,
                 ) -> None:
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
        """
        if csv_filepath.exists():
            df = pd.read_csv(csv_filepath, header=[0, 1], index_col=[0, 1, 2])
            super().__init__(df)
            self.csv_filepath = csv_filepath
        else:
            # Initialize empty DataFrame
            run_ids = list(range(1, n_runs + 1))  # We count runs from 1
            # We always need objectives to maintain the dimensions
            if objectives is None:
                objectives = [PerformanceDataFrame.missing_objective]
            else:
                objectives = [str(o) for o in objectives]
            # We always need an instance to maintain the dimensions
            if instances is None:
                instances = [PerformanceDataFrame.missing_value]
            # We always need a solver to maintain the dimensions
            if solvers is None:
                solvers = [PerformanceDataFrame.missing_value]
            midx = pd.MultiIndex.from_product(
                [objectives, instances, run_ids],
                names=PerformanceDataFrame.multi_index_names)
            mcolumns = pd.MultiIndex.from_product(
                [solvers, PerformanceDataFrame.multi_column_names],
                names=["Solver", "Meta"])
            super().__init__(PerformanceDataFrame.missing_value,
                             index=midx, columns=mcolumns)
            self.csv_filepath = csv_filepath
            self.save_csv()

        # Sort the index to optimize lookup speed
        self.sort_index(inplace=True)

    # Properties

    @property
    def num_objectives(self: PerformanceDataFrame) -> int:
        """Retrieve the number of objectives in the DataFrame."""
        return self.index.get_level_values(0).unique().size

    @property
    def num_instances(self: PerformanceDataFrame) -> int:
        """Return the number of instances."""
        return self.index.get_level_values(1).unique().size

    @property
    def num_runs(self: PerformanceDataFrame) -> int:
        """Return the number of runs."""
        return self.index.get_level_values(2).unique().size

    @property
    def num_solvers(self: PerformanceDataFrame) -> int:
        """Return the number of solvers."""
        return self.columns.get_level_values(0).unique().size

    @property
    def multi_objective(self: PerformanceDataFrame) -> bool:
        """Return whether the dataframe represent MO or not."""
        return self.num_objectives > 1

    @property
    def solvers(self: PerformanceDataFrame) -> list[str]:
        """Return the solver present as a list of strings."""
        return self.columns.get_level_values(0).unique().to_list()

    @property
    def objective_names(self: PerformanceDataFrame) -> list[str]:
        """Return the objective names as a list of strings."""
        return self.index.get_level_values(0).unique().to_list()

    @property
    def objectives(self: PerformanceDataFrame) -> list[SparkleObjective]:
        """Return the objectives as a list of SparkleObjectives."""
        return [resolve_objective(o) for o in self.objective_names]

    @property
    def instances(self: PerformanceDataFrame) -> list[str]:
        """Return the instances as a Pandas Index object."""
        return self.index.get_level_values(1).unique().to_list()

    @property
    def run_ids(self: PerformanceDataFrame) -> list[int]:
        """Return the run ids as a list of integers."""
        return self.index.get_level_values(2).unique().to_list()

    @property
    def has_missing_values(self: PerformanceDataFrame) -> bool:
        """Returns True if there are any missing values in the dataframe."""
        return self.isnull().any().drop([PerformanceDataFrame.column_seed,
                                         PerformanceDataFrame.column_configuration],
                                        level=1).any()

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
                raise ValueError("Error: MO Data, but objective not specified.")
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
            if self.num_runs > 1:
                raise ValueError("Error: Multiple run performance data, "
                                 "but run not specified")
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

    # Getters and Setters

    def add_solver(self: PerformanceDataFrame,
                   solver_name: str,
                   initial_value: float | list[str | float] = None) -> None:
        """Add a new solver to the dataframe. Initializes value to None by default.

        Args:
            solver_name: The name of the solver to be added.
            initial_value: The value assigned for each index of the new solver.
                If not None, must match the index dimension (n_obj * n_inst * n_runs).
        """
        if solver_name in self.solvers:
            print(f"WARNING: Tried adding already existing solver {solver_name} to "
                  f"Performance DataFrame: {self.csv_filepath}")
            return
        initial_value =\
            [initial_value] if not isinstance(initial_value, list) else initial_value
        column_dim_size = len(PerformanceDataFrame.multi_column_names)
        if len(initial_value) < column_dim_size:
            initial_value.extend([None] * (column_dim_size - len(initial_value)))
        for field, value in zip(PerformanceDataFrame.multi_column_names, initial_value):
            self[solver_name, field] = value
        if self.num_solvers == 2:  # Remove nan solver
            for solver in self.solvers:
                if not isinstance(solver, str) and math.isnan(solver):
                    self.remove_solver(solver)
                    break
        # Sort the index to optimize lookup speed
        self.sort_index(axis=1, inplace=True)

    def add_instance(self: PerformanceDataFrame,
                     instance_name: str,
                     initial_value: float = None) -> None:
        """Add and instance to the DataFrame."""
        initial_value = initial_value or self.missing_value

        if instance_name in self.instances:
            print(f"WARNING: Tried adding already existing instance {instance_name} "
                  f"to Performance DataFrame: {self.csv_filepath}")
            return
        # Add rows for all combinations
        for objective, run in itertools.product(self.objective_names, self.run_ids):
            self.loc[(objective, instance_name, run)] = initial_value
        if self.num_instances == 2:  # Remove nan instance
            for instance in self.instances:
                if not isinstance(instance, str) and math.isnan(instance):
                    self.remove_instance(instance)
                    break
        # Sort the index to optimize lookup speed
        self.sort_index(axis=0, inplace=True)

    def remove_solver(self: PerformanceDataFrame, solver_name: str | list[str]) -> None:
        """Drop one or more solvers from the Dataframe."""
        # To make sure objectives / runs are saved when no solvers are present
        if self.num_solvers == 1:
            self.add_solver(PerformanceDataFrame.missing_value)
        self.drop(columns=solver_name, axis=1, inplace=True)
        # Sort the index to optimize lookup speed
        self.sort_index(axis=1, inplace=True)

    def remove_instance(self: PerformanceDataFrame, instance_name: str) -> None:
        """Drop an instance from the Dataframe."""
        # To make sure objectives / runs are saved when no instances are present
        if self.num_instances == 1:
            self.add_instance(PerformanceDataFrame.missing_value)
        self.drop(instance_name,
                  axis=0,
                  level=PerformanceDataFrame.index_instance, inplace=True)
        # Sort the index to optimize lookup speed
        self.sort_index(axis=0, inplace=True)
        # self.reset_index(inplace=True)
        # self.set_index(PerformanceDataFrame.multi_index_names, inplace=True)

    def correct_dimensions(self: PerformanceDataFrame) -> None:
        """Add/remove nan instance/solver if necessary."""
        return

    def reset_value(self: PerformanceDataFrame,
                    solver: str,
                    instance: str,
                    objective: str = None,
                    run: int = None) -> None:
        """Reset a value in the dataframe."""
        self.set_value(PerformanceDataFrame.missing_value,
                       solver, instance, objective, run)

    # Can we make this handle a sequence of inputs instead of just 1?
    def set_value(self: PerformanceDataFrame,
                  value: float | str | list[float | str],
                  solver: str,
                  instance: str,
                  objective: str = None,
                  run: int = None,
                  solver_fields: list[str] = ["Value"]) -> None:
        """Setter method to assign a value to the Dataframe.

        Args:
            value: Value(s) to be assigned.
            solver: The solver that produced the value.
            instance: The instance that the value was produced on.
            objective: The objective for which the result was produced.
                Optional in case of using single objective.
            run: The run index for which the result was produced.
                Optional in case of doing single run results.
            solver_fields: The level to which each value should be assinged.
                Defaults to ["Value"].
        """
        objective, run = self.verify_indexing(objective, run)
        value = [value] if not isinstance(value, list) else value
        for item, level in zip(value, solver_fields):
            self.at[(objective, instance, run), (solver, level)] = item

    # Can we unify get_value and get_values?
    def get_value(self: PerformanceDataFrame,
                  solver: str,
                  instance: str,
                  objective: str = None,
                  run: int = None,
                  solver_fields: list[str] = ["Value"]
                  ) -> float | str | list[float | str]:
        """Index a value of the DataFrame and return it."""
        objective, run = self.verify_indexing(objective, run)
        target = list(self.loc[(objective, instance, run), solver][solver_fields])
        if len(target) == 1:
            return target[0]
        return target

    def get_values(self: PerformanceDataFrame,
                   solver: str,
                   instance: str = None,
                   objective: str = None,
                   run: int = None,
                   solver_fields: list[str] = ["Value"]
                   ) -> list[float | str] | list[list[float | str]]:
        """Return a list of solver values."""
        subdf = self[solver][solver_fields]
        if objective is not None:
            objective = self.verify_objective(objective)
            subdf = subdf.xs(objective, level=0, drop_level=False)
        if instance is not None:
            subdf = subdf.xs(instance, level=1, drop_level=False)
        if run is not None:
            run = self.verify_run_id(run)
            subdf = subdf.xs(run, level=2, drop_level=False)
        # Convert dict to list
        result = [subdf[field].to_list() for field in solver_fields]
        if len(result) == 1:
            return result[0]
        return result

    # Calculables

    def mean(self: PerformanceDataFrame,
             objective: str = None,
             solver: str = None,
             instance: str = None) -> float:
        """Return the mean value of a slice of the dataframe."""
        objective = self.verify_objective(objective)
        subset = self.xs(objective, level=0)
        if solver is not None:
            subset = subset.xs(solver, axis=1, drop_level=False)
        if instance is not None:
            subset = subset.xs(instance, axis=0, drop_level=False)
        value = subset.astype(float).mean()
        if isinstance(value, pd.Series):
            return value.mean()
        return value

    # TODO: This method should be refactored or not exist
    def get_job_list(self: PerformanceDataFrame, rerun: bool = False) \
            -> list[tuple[str, str]]:
        """Return a list of performance computation jobs there are to be done.

        Get a list of tuple[instance, solver] to run from the performance data.
        If rerun is False (default), get only the tuples that don't have a
        value, else (True) get all the tuples.

        Args:
            rerun: Boolean indicating if we want to rerun all jobs

        Returns:
            A list of [instance, solver] combinations
        """
        # Format the dataframe such that only the values remain
        df = self.stack(future_stack=True)
        df.drop([PerformanceDataFrame.column_seed,
                 PerformanceDataFrame.column_configuration], level=-1, inplace=True)
        df.index.droplevel()
        if not rerun:  # Filter the nan values
            df = df.isnull()

        # Count the number of missing objective values for each Instance/Run/Algorithm
        df.index = df.index.droplevel(PerformanceDataFrame.index_objective)
        df.index = df.index.droplevel(-1)
        index_names = df.index.names
        df = df.groupby(df.index).agg({cname: "sum" for cname in df.columns})
        df.index = pd.MultiIndex.from_tuples(df.index, names=index_names)

        # Return the Instance, Run, Algorithm combinations
        return [index + (column, )
                for index, column in itertools.product(df.index, df.columns)
                if rerun or df[column][index] > 0]

    # TODO: This method should be refactored or not exist
    def remaining_jobs(self: PerformanceDataFrame) -> dict[str, list[str]]:
        """Return a dictionary for empty values as instance key and solver values."""
        remaining_jobs = {}
        jobs = self.get_job_list(rerun=False)
        for instance, _, solver in jobs:
            if instance not in remaining_jobs:
                remaining_jobs[instance] = [solver]
            else:
                remaining_jobs[instance].append(solver)
        return remaining_jobs

    def best_instance_performance(
            self: PerformanceDataFrame,
            objective: str | SparkleObjective = None,
            run_id: int = None,
            exclude_solvers: list[str] = None) -> pd.Series:
        """Return the best performance for each instance in the portfolio.

        Args:
            objective: The objective for which we calculate the best performance
            run_id: The run for which we calculate the best performance. If None,
                we consider all runs.
            exclude_solvers: List of solvers to exclude in the calculation.

        Returns:
            The best performance for each instance in the portfolio.
        """
        objective = self.verify_objective(objective)
        if isinstance(objective, str):
            objective = resolve_objective(objective)
        # Drop Seed/Configuration
        subdf = self.drop(
            [PerformanceDataFrame.column_seed,
             PerformanceDataFrame.column_configuration],
            axis=1, level=1)
        subdf = subdf.xs(objective.name, level=0)
        if exclude_solvers is not None:
            subdf = subdf.drop(exclude_solvers, axis=1, level=0)
        if run_id is not None:
            run_id = self.verify_run_id(run_id)
            subdf = subdf.xs(run_id, level=1)
        else:
            # Drop the run level
            subdf = subdf.droplevel(level=1)
        if objective.minimise:
            series = subdf.min(axis=1)
        else:
            series = subdf.max(axis=1)
        # Ensure we always return the best for each run
        series = series.sort_values(ascending=objective.minimise)
        return series.groupby(series.index).first().astype(float)

    def best_performance(
            self: PerformanceDataFrame,
            exclude_solvers: list[str] = [],
            objective: str | SparkleObjective = None) -> float:
        """Return the overall best performance of the portfolio.

        Args:
            exclude_solvers: List of solvers to exclude in the calculation.
                Defaults to none.
            objective: The objective for which we calculate the best performance

        Returns:
            The aggregated best performance of the portfolio over all instances.
        """
        objective = self.verify_objective(objective)
        if isinstance(objective, str):
            objective = resolve_objective(objective)
        instance_best = self.best_instance_performance(
            objective, exclude_solvers=exclude_solvers).to_numpy(dtype=float)
        return objective.instance_aggregator(instance_best)

    def schedule_performance(
            self: PerformanceDataFrame,
            schedule: dict[str: list[tuple[str, float | None]]],
            target_solver: str = None,
            objective: str | SparkleObjective = None) -> float:
        """Return the performance of a selection schedule on the portfolio.

        Args:
            schedule: Compute the best performance according to a selection schedule.
                A dictionary with instances as keys and a list of tuple consisting of
                (solver, max_runtime) or solvers if no runtime prediction should be used.
            target_solver: If not None, store the values in this solver of the DF.
            objective: The objective for which we calculate the best performance

        Returns:
            The performance of the schedule over the instances in the dictionary.
        """
        objective = self.verify_objective(objective)
        if isinstance(objective, str):
            objective = resolve_objective(objective)
        select = min if objective.minimise else max
        performances = [0.0 for _ in range(len(schedule.keys()))]
        for ix, instance in enumerate(schedule.keys()):
            for iy, (solver, max_runtime) in enumerate(schedule[instance]):
                performance = self.get_value(solver, instance, objective.name)
                if max_runtime is not None:  # We are dealing with runtime
                    performances[ix] += performance
                    if performance < max_runtime:
                        break  # Solver finished in time
                else:  # Quality, we take the best found performance
                    if iy == 0:  # First solver, set initial value
                        performances[ix] = performance
                        continue
                    performances[ix] = select(performances[ix], performance)
            if target_solver is not None:
                self.set_value(performances[ix], target_solver, instance, objective.name)
        return performances

    def marginal_contribution(
            self: PerformanceDataFrame,
            objective: str | SparkleObjective = None,
            sort: bool = False) -> list[float]:
        """Return the marginal contribution of the solvers on the instances.

        Args:
            objective: The objective for which we calculate the marginal contribution.
            sort: Whether to sort the results afterwards
        Returns:
            The marginal contribution of each solver.
        """
        output = []
        objective = self.verify_objective(objective)
        if isinstance(objective, str):
            objective = resolve_objective(objective)
        best_performance = self.best_performance(objective=objective)
        for solver in self.solvers:
            # By calculating the best performance excluding this Solver,
            # we can determine its relative impact on the portfolio.
            missing_solver_best = self.best_performance(
                exclude_solvers=[solver],
                objective=objective)
            # Now we need to see how much the portfolio's best performance
            # decreases without this solver.
            marginal_contribution = missing_solver_best / best_performance
            if missing_solver_best == best_performance:
                # No change, no contribution
                marginal_contribution = 0.0
            output.append((solver, marginal_contribution, missing_solver_best))
        if sort:
            output.sort(key=lambda x: x[1], reverse=objective.minimise)
        return output

    def get_solver_ranking(self: PerformanceDataFrame,
                           objective: str | SparkleObjective = None
                           ) -> list[tuple[str, float]]:
        """Return a list with solvers ranked by average performance."""
        objective = self.verify_objective(objective)
        if isinstance(objective, str):
            objective = resolve_objective(objective)
        # Drop Seed/Configuration
        subdf = self.drop(
            [PerformanceDataFrame.column_seed,
             PerformanceDataFrame.column_configuration],
            axis=1, level=1)
        sub_df = subdf.loc(axis=0)[objective.name, :, :]
        # Reduce Runs Dimension
        sub_df = sub_df.droplevel("Run").astype(float)
        # By using .__name__, pandas converts it to a Pandas Aggregator function
        sub_df = sub_df.groupby(sub_df.index).agg(func=objective.run_aggregator.__name__)
        solver_ranking = [(solver, objective.instance_aggregator(
            sub_df[solver].astype(float))) for solver in self.solvers]
        # Sort the list by second value (the performance)
        solver_ranking.sort(key=lambda performance: performance[1],
                            reverse=(not objective.minimise))
        return solver_ranking

    def save_csv(self: PerformanceDataFrame, csv_filepath: Path = None) -> None:
        """Write a CSV to the given path.

        Args:
            csv_filepath: String path to the csv file. Defaults to self.csv_filepath.
        """
        csv_filepath = self.csv_filepath if csv_filepath is None else csv_filepath
        self.to_csv(csv_filepath)

    def clone(self: PerformanceDataFrame,
              csv_filepath: Path = None) -> PerformanceDataFrame:
        """Create a copy of this object.

        Args:
            csv_filepath: The new filepath to use for saving the object to.
                Warning: If the original path is used, it could lead to dataloss!
        """
        csv_filepath = csv_filepath or self.csv_filepath
        if self.csv_filepath.exists():
            pd_copy = PerformanceDataFrame(csv_filepath)
        else:
            pd_copy = PerformanceDataFrame(
                csv_filepath=csv_filepath,
                solvers=self.solvers,
                objectives=self.objectives,
                instances=self.instances,
                n_runs=self.num_runs)
            for solver in self.solvers:
                for index in self.index:
                    pd_copy.loc[index, solver] = self.loc[index, solver]
        return pd_copy

    def clean_csv(self: PerformanceDataFrame) -> None:
        """Set all values in Performance Data to None."""
        self[:] = PerformanceDataFrame.missing_value
        self.save_csv()

    def to_autofolio(self: PerformanceDataFrame,
                     objective: SparkleObjective = None,
                     target: Path = None) -> Path:
        """Port the data to a format acceptable for AutoFolio."""
        if (objective is None and self.multi_objective or self.num_runs > 1):
            print(f"ERROR: Currently no porting available for {self.csv_filepath} "
                  "to Autofolio due to multi objective or number of runs.")
            return
        autofolio_df = super().copy()
        if objective is not None:
            autofolio_df = autofolio_df.loc[objective.name]
            autofolio_df.index = autofolio_df.index.droplevel("Run")
        else:
            autofolio_df.index = autofolio_df.index.droplevel(["Objective", "Run"])
        if target is None:
            path = self.csv_filepath.parent / f"autofolio_{self.csv_filepath.name}"
        else:
            path = target / f"autofolio_{self.csv_filepath.name}"
        autofolio_df.to_csv(path)
        return path
