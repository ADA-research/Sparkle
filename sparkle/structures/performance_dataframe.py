#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module to manage performance data files and common operations on them."""
from __future__ import annotations
from pathlib import Path
import sys
import math
import pandas as pd

from sparkle.types import SparkleObjective, resolve_objective


class PerformanceDataFrame():
    """Class to manage performance data and common operations on them."""
    missing_value = math.nan
    missing_objective = "UNKNOWN"
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
        if objectives is not None:
            self.objectives = [resolve_objective(o) if isinstance(o, str) else o
                               for o in objectives]
        else:
            self.objectives = [SparkleObjective(PerformanceDataFrame.missing_objective)]
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
                        self.dataframe[PerformanceDataFrame.multi_dim_names[0]] =\
                            [o.name for o in self.objectives]
                else:
                    # Objectives are present, determine which ones
                    names = self.dataframe[PerformanceDataFrame.multi_dim_names[0]]
                    self.objectives = [resolve_objective(name) for name in
                                       names.unique()]
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
                midx = pd.MultiIndex.from_product(
                    [[o.name for o in self.objectives], instances, self.run_ids],
                    names=PerformanceDataFrame.multi_dim_names)
                self.dataframe = pd.DataFrame(PerformanceDataFrame.missing_value,
                                              index=midx,
                                              columns=solvers)
                self.save_csv()
            # Sort the index to optimize lookup speed
            self.dataframe = self.dataframe.sort_index()

    def __repr__(self: PerformanceDataFrame) -> str:
        """Return string representation of the DataFrame."""
        return self.dataframe.__repr__()

    # Properties

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

    @property
    def has_missing_values(self: PerformanceDataFrame) -> bool:
        """Returns True if there are any missing values in the dataframe."""
        return self.dataframe.isnull().any().any()

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

    # Getters and Setters

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
            # NOTE: Did this fix Jeroen's bug? .from_arrays instead of direct constructor
            emidx = pd.MultiIndex.from_arrays(levels,
                                              names=PerformanceDataFrame.multi_dim_names)
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

    def remove_solver(self: PerformanceDataFrame, solver_name: str | list[str]) -> None:
        """Drop one or more solvers from the Dataframe."""
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

    # Can we unify get_value and get_values?
    def get_value(self: PerformanceDataFrame,
                  solver: str,
                  instance: str,
                  objective: str = None,
                  run: int = None) -> float:
        """Index a value of the DataFrame and return it."""
        objective, run = self.verify_indexing(objective, run)
        return float(self.dataframe.loc[(objective, instance, run), solver])

    def get_values(self: PerformanceDataFrame,
                   solver: str,
                   instance: str = None,
                   objective: str = None,
                   run: int = None) -> list[float]:
        """Return a list of solver values."""
        subdf = self.dataframe[solver]
        if objective is not None:
            objective = self.verify_objective(objective)
            subdf = subdf.xs(objective, level=0, drop_level=False)
        if instance is not None:
            subdf = subdf.xs(instance, level=1, drop_level=False)
        if run is not None:
            run = self.verify_run_id(run)
            subdf = subdf.xs(run, level=2, drop_level=False)
        return subdf.to_list()

    # Modifiers

    '''def penalise(self: PerformanceDataFrame,
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
                                     threshold)] = penalty'''

    # Calculables

    def mean(self: PerformanceDataFrame,
             objective: str = None,
             solver: str = None,
             instance: str = None) -> float:
        """Return the mean value of a slice of the dataframe."""
        objective = self.verify_objective(objective)
        subset = self.dataframe.xs(objective, level=0)
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

        Get a list of tuple[instance, solver] to run from the performance data
        csv file. If rerun is False (default), get only the tuples that don't have a
        value in the table, else (True) get all the tuples.

        Args:
            rerun: Boolean indicating if we want to rerun all jobs
        """
        df = self.dataframe.stack(future_stack=True)
        if not rerun:
            df = df[df.isnull()]
        df.index = df.index.droplevel(["Objective"])
        return df.index.unique().tolist()

    # TODO: This method should be refactored or not exist
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
        subdf = self.dataframe.xs(objective.name, level=0)
        if exclude_solvers is not None:
            subdf = subdf.drop(exclude_solvers, axis=1)
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
        sub_df = self.dataframe.loc(axis=0)[objective.name, :, :]
        # Reduce Runs Dimension
        sub_df = sub_df.droplevel("Run")
        sub_df = sub_df.groupby(sub_df.index).agg(func=objective.run_aggregator)
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

    def to_autofolio(self: PerformanceDataFrame,
                     objective: SparkleObjective = None,
                     target: Path = None) -> Path:
        """Port the data to a format acceptable for AutoFolio."""
        if (objective is None and self.multi_objective or self.n_runs > 1):
            print(f"ERROR: Currently no porting available for {self.csv_filepath} "
                  "to Autofolio due to multi objective or number of runs.")
            return
        autofolio_df = self.dataframe.copy()
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
