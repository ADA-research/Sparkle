#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module to manage performance data CSV files and common operations on them."""


from __future__ import annotations
from typing import Callable
import fcntl
from pathlib import Path
import sys

from statistics import mean
import pandas as pd
import global_variables as gv
from sparkle.platform import settings_help

global settings
gv.settings = settings_help.Settings()


class PerformanceDataFrame():
    """Class to manage performance data and common operations on them."""

    def __init__(self: PerformanceDataFrame,
                 csv_filepath: Path,
                 solvers: list[str] = [],
                 objectives: list[str | settings_help.SparkleObjective] = None,
                 instances: list[str] = [],
                 n_runs: int = 1,
                 init_df: bool = True) -> None:
        """Initialise a SparklePerformanceDataCSV object.

        Consists of:
            - Columns representing the Solvers
            - Rows representing the result by multi-index in order of:
                * Objective (Static, from settings)
                * Instance
                * Runs (Static, given in constructor)

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
        # Sanity check, remove later
        if not isinstance(self.csv_filepath, Path):
            self.csv_filepath = Path(self.csv_filepath)
        self.multi_dim_names = ["Objective", "Instance", "Run"]
        # Objectives is a ``static'' dimension
        if objectives is None:
            objectives = gv.settings.get_general_sparkle_objectives()
        self.objective_names =\
            [o.name if isinstance(o, settings_help.SparkleObjective) else o
             for o in objectives]
        self.multi_objective = len(self.objective_names) > 1
        # Runs is a ``static'' dimension
        self.n_runs = n_runs
        self.run_ids = list(range(1, self.n_runs + 1))
        if init_df:
            if self.csv_filepath.exists():
                self.dataframe = pd.read_csv(csv_filepath, index_col=0)
                # Enforce dimensions
                if self.multi_dim_names[0] not in self.dataframe.columns:
                    # No Objective, cast column
                    self.objective_names = [self.multi_dim_names[0]]
                    self.dataframe[self.multi_dim_names[0]] = self.objective_names[0]
                    self.multi_objective = False
                if self.multi_dim_names[2] not in self.dataframe.columns:
                    # No runs column
                    self.n_runs = 1
                    self.dataframe[self.multi_dim_names[2]] = self.n_runs
                    self.run_ids = [self.n_runs]
                if self.multi_dim_names[1] not in self.dataframe.columns:
                    # Instances are listed as rows, force into column
                    self.dataframe = self.dataframe.reset_index().rename(
                        columns={"index": self.multi_dim_names[1]})

                # Cast Columns to multi dim
                self.dataframe = self.dataframe.set_index(self.multi_dim_names)
            else:
                # Initialize empty DataFrame
                midx = pd.MultiIndex.from_product(
                    [self.objective_names, instances, self.run_ids],
                    names=self.multi_dim_names)
                self.dataframe = pd.DataFrame(gv.sparkle_missing_value,
                                              index=midx,
                                              columns=solvers)
                self.save_csv()

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
            return self.objective_names[0]
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
                names=self.multi_dim_names)
            self.dataframe = pd.DataFrame(initial_value, index=midx, columns=solvers)
        else:
            if instance_name in self.dataframe.index.levels[1]:
                print(f"WARNING: Tried adding already existing solver {instance_name} "
                      f"to Performance DataFrame: {self.csv_filepath}")
                return
            # Create the missing indices
            levels = [self.dataframe.index.levels[0].tolist(),
                      [instance_name],
                      self.dataframe.index.levels[2].tolist()]
            emidx = pd.MultiIndex(levels, names=self.multi_dim_names)
            # Create the missing column values
            edf = pd.DataFrame(gv.sparkle_missing_value,
                               index=emidx,
                               columns=self.dataframe.columns)
            # Concatenate the original and new dataframe together
            self.dataframe = pd.concat([self.dataframe, edf])
        return

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
        self.dataframe.loc[(objective, instance, run), solver] = value

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
        self.set_value(gv.sparkle_missing_value, solver, instance, objective, run)

    def get_value(self: PerformanceDataFrame,
                  solver: str,
                  instance: str,
                  objective: str = None,
                  run: int = None) -> None:
        """Index a value of the DataFrame and return it."""
        objective, run = self.verify_indexing(objective, run)
        return self.dataframe.loc[(objective, instance, run), solver]

    def get_num_objectives(self: PerformanceDataFrame) -> int:
        """Retrieve the number of objectives in the DataFrame."""
        return self.dataframe.index.levels[0].size

    def get_num_instances(self: PerformanceDataFrame) -> int:
        """Return the number of instances."""
        return self.dataframe.index.levels[1].size

    def get_num_runs(self: PerformanceDataFrame) -> int:
        """Return the number of runs."""
        return self.dataframe.index.levels[2].size

    def get_num_solvers(self: PerformanceDataFrame) -> int:
        """Return the number of solvers."""
        return self.dataframe.columns.size

    def get_instances(self: PerformanceDataFrame) -> list[str]:
        """Return the instances as a Pandas Index object."""
        return self.dataframe.index.levels[1].tolist()

    def save_csv(self: PerformanceDataFrame, csv_filepath: Path = None) -> None:
        """Write a CSV to the given path.

        Args:
            csv_filepath: String path to the csv file. Defaults to self.csv_filepath.
        """
        csv_filepath = self.csv_filepath if csv_filepath is None else csv_filepath
        with csv_filepath.open("w+") as fo:
            fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
            self.dataframe.to_csv(csv_filepath)

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

    def get_list_recompute_performance_computation_job(self: PerformanceDataFrame)\
            -> list[list[list]]:
        """Return column-row combinations in the dataframe as [[row, all_columns]]."""
        list_recompute_performance_computation_job = []
        list_column_name = self.dataframe.columns.to_list()

        for row_name in self.dataframe.index:
            if not self.multi_objective and self.n_runs == 1:
                # Simplification for unused dimensions
                list_item = [row_name[1], list_column_name]
            else:
                list_item = [row_name, list_column_name]
            list_recompute_performance_computation_job.append(list_item)

        return list_recompute_performance_computation_job

    def get_list_remaining_performance_computation_job(self: PerformanceDataFrame) \
            -> list[list[list]]:
        """Return a list of needed performance computations per instance and solver.

        This will return any objective/instance/run combination.
        """
        list_remaining_performance_computation_job = []
        bool_array_isnull = self.dataframe.isnull()
        for row_name in self.dataframe.index:
            current_solver_list = []
            for column_name in self.dataframe.columns:
                flag_value_is_null = bool_array_isnull.at[row_name, column_name]
                if flag_value_is_null:
                    current_solver_list.append(column_name)
            if not self.multi_objective and self.n_runs == 1:
                # Simplification for unused dimensions
                list_item = [row_name[1], current_solver_list]
            else:
                list_item = [row_name, current_solver_list]
            list_remaining_performance_computation_job.append(list_item)
        return list_remaining_performance_computation_job

    def get_best_performance_per_instance(
            self: PerformanceDataFrame,
            objective: str = None,
            run_agg: Callable = None,
            best: Callable = pd.DataFrame.max) -> list[float]:
        """Return a list with the best performance per instance.

        Allows user to specify how to aggregate runs together.
        Must be pandas accepted callable.

        Args:
            objective: The objective over which we want the maximum
            run_agg: The method defining how runs are combined per Instance/solver
            best: Callable, replace with pd.DataFrame.min to minimise
        """
        objective = self.verify_objective(objective)
        if run_agg is None:
            return best(self.dataframe.loc[(objective), :], axis=1).to_list()
        else:
            # Select the objective, group by runs, apply the aggregator and select max
            agg_runs = self.dataframe.loc[(objective), :].groupby(level=0).run_agg()
            return best(agg_runs, axis=1).to_list()

    def calc_portfolio_vbs_instance(
            self: PerformanceDataFrame,
            instance: str,
            minimise: bool,
            objective: str = None,
            capvalue: float = None,
            run_aggregator: Callable = mean) -> float:
        """Return the VBS performance for a specific instance.

        Args:
            instance: For which instance we shall calculate the VBS
            minimise: Whether we should minimise or maximise the score
            objective: The objective for which we calculate the VBS
            capvalue: The minimum/maximum scoring value the VBS is allowed to have
            run_aggregator: How we aggregate multiple runs for an instance-solver
                combination. Only relevant for multi-runs.

        Returns:
            The virtual best solver performance for this instance.
        """
        objective = self.verify_objective(objective)
        penalty_factor = gv.settings.get_general_penalty_multiplier()
        if capvalue is None:
            capvalue = sys.float_info.max
            if not minimise:
                capvalue = capvalue * -1
        penalty = penalty_factor * capvalue
        virtual_best_score = None
        for solver in self.dataframe.columns:
            if isinstance(instance, str):
                runs = self.dataframe.loc[(objective, instance), solver]
                if minimise:
                    runs[runs > capvalue] = penalty
                else:
                    runs[runs < capvalue] = penalty
                score_solver = run_aggregator(runs)
            else:
                score_solver = float(self.dataframe.loc[instance, solver])
            if virtual_best_score is None or\
                    minimise and virtual_best_score > score_solver or\
                    not minimise and virtual_best_score < score_solver:
                virtual_best_score = score_solver

        # Shouldn't this throw an error?
        if virtual_best_score is None and len(self.dataframe.columns) == 0:
            print("WARNING: PerformanceDataFrame could not calculate VBS "
                  f"instance {instance}")
            virtual_best_score = 0

        return virtual_best_score

    def calc_virtual_best_performance_of_portfolio(
            self: PerformanceDataFrame,
            aggregation_function: Callable[[list[float]], float],
            minimise: bool,
            capvalue_list: list[float],
            objective: str = None) -> float:
        """Return the overall VBS performance of the portfolio.

        Args:
            aggregation_function: The method of combining all VBS scores together
            minimise: Whether the scores are minimised or not
            capvalue_list: List of capvalue per instance

        Returns:
            The combined virtual best performance of the portfolio over all instances.
        """
        objective = self.verify_objective(objective)
        virtual_best = []
        capvalue = None
        for idx, instance in enumerate(self.dataframe.index):
            if capvalue_list is not None:
                capvalue = capvalue_list[idx]

            virtual_best_score = (
                self.calc_portfolio_vbs_instance(
                    instance, minimise, objective, capvalue))
            virtual_best.append(virtual_best_score)

        return aggregation_function(virtual_best)

    def get_dict_vbs_penalty_time_on_each_instance(
            self: PerformanceDataFrame,
            objective: str = None,
            run_id: int = None) -> dict:
        """Return a dictionary of penalised runtimes and instances for the VBS."""
        objective = self.verify_objective(objective)
        instance_penalized_runtimes = {}
        vbs_penalty_time = gv.settings.get_penalised_time()
        for instance in self.dataframe.index.levels[1]:
            if run_id is None:
                runtime = self.dataframe.loc[(objective, instance), :].min(axis=None)
            else:
                runtime =\
                    self.dataframe.loc[(objective, instance, run_id), :].min(axis=None)
            instance_penalized_runtimes[instance] = min(vbs_penalty_time, runtime)

        return instance_penalized_runtimes

    def calc_vbs_penalty_time(self: PerformanceDataFrame,
                              objective: str = None,
                              run_id: int = None) -> float:
        """Return the penalised performance of the VBS."""
        objective = self.verify_objective(objective)
        cutoff_time = gv.settings.get_general_target_cutoff_time()
        penalty_multiplier = gv.settings.get_general_penalty_multiplier()
        penalty_time_each_run = cutoff_time * penalty_multiplier

        # Calculate the minimum for the selected objective per instance
        if run_id is not None:
            min_instance_df =\
                self.dataframe.loc(axis=0)[objective, :, run_id].min(axis=1)
        else:
            min_instance_df =\
                self.dataframe.loc(axis=0)[objective, :, :].min(axis=1)
        # Penalize those exceeding cutoff
        min_instance_df[min_instance_df > cutoff_time] = penalty_time_each_run
        # Return average
        return min_instance_df.sum() / self.dataframe.index.size

    def get_solver_penalty_time_ranking_list(self: PerformanceDataFrame,
                                             objective: str = None) -> list[list[float]]:
        """Return a list with solvers ranked by penalised runtime."""
        objective = self.verify_objective(objective)
        cutoff_time = gv.settings.get_general_target_cutoff_time()

        solver_penalty_time_ranking_list = []
        penalty_time_each_run =\
            cutoff_time * gv.settings.get_general_penalty_multiplier()
        num_instances = self.dataframe.index.size
        sub_df = self.dataframe.loc(axis=0)[objective, :, :]
        for solver in self.dataframe.columns:
            masked_col = sub_df[solver]
            masked_col[masked_col > cutoff_time] = penalty_time_each_run
            this_penalty_time = masked_col.sum() / num_instances
            solver_penalty_time_ranking_list.append([solver, this_penalty_time])

        # Sort the list by second value (the penalised run time)
        solver_penalty_time_ranking_list.sort(
            key=lambda this_penalty_time: this_penalty_time[1])

        return solver_penalty_time_ranking_list

    def clean_csv(self: PerformanceDataFrame) -> None:
        """Set all values in Performance Data to None."""
        self.dataframe[:] = gv.sparkle_missing_value
        self.save_csv()

    def copy(self: PerformanceDataFrame,
             csv_filepath: Path = None) -> PerformanceDataFrame:
        """Create a copy of this object.

        Args:
            csv_filepath: The new filepath to use for saving the object to.
                Warning: If None, the original path is used and could lead to dataloss!
        """
        csv_filepath = self.csv_filepath if csv_filepath is None else csv_filepath
        pd_copy = PerformanceDataFrame(csv_filepath, init_df=False)
        pd_copy.dataframe = self.dataframe.copy()
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
