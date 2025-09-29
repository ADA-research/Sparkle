"""Module to manage performance data files and common operations on them."""

from __future__ import annotations
import ast
import copy
from typing import Any
import itertools
from pathlib import Path
import math
import numpy as np
import pandas as pd

from sparkle.types import SparkleObjective, resolve_objective


class PerformanceDataFrame(pd.DataFrame):
    """Class to manage performance data and common operations on them."""

    missing_value = math.nan

    missing_objective = "UNKNOWN"
    default_configuration = "Default"

    index_objective = "Objective"
    index_instance = "Instance"
    index_run = "Run"
    multi_index_names = [index_objective, index_instance, index_run]

    column_solver = "Solver"
    column_configuration = "Configuration"
    column_meta = "Meta"
    column_value = "Value"
    column_seed = "Seed"
    multi_column_names = [column_solver, column_configuration, column_meta]
    multi_column_value = [column_value, column_seed]
    multi_column_dtypes = [str, int]

    def __init__(
        self: PerformanceDataFrame,
        csv_filepath: Path,
        solvers: list[str] = None,
        configurations: dict[str, dict[str, dict]] = None,
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
            configurations: The configuration keys per solver to add, structured as
                configurations[solver][config_key] = {"parameter": "value", ..}
            objectives: List of SparkleObjectives or objective names. By default None,
                then the objectives will be derived from Sparkle Settings if possible.
            instances: List of instance names to be added into the Dataframe
            n_runs: The number of runs to consider per Solver/Objective/Instance comb.
        """
        if csv_filepath and csv_filepath.exists():  # Read from file
            df = pd.read_csv(
                csv_filepath,
                header=[0, 1, 2],
                index_col=[0, 1, 2],
                on_bad_lines="skip",
                dtype={"Value": str, "Seed": int},
                comment="$",
            )  # $ For extra data lines
            super().__init__(df)
            self.csv_filepath = csv_filepath
            # Load configuration mapping
            with self.csv_filepath.open() as f:
                configuration_lines = [
                    line.strip().strip("$").split(",", maxsplit=2)
                    for line in f.readlines()
                    if line.startswith("$")
                ]
            configurations = {s: {} for s in self.solvers}
            for solver, config_key, config in configuration_lines[1:]:  # Skip header
                configurations[solver][config_key] = ast.literal_eval(config.strip('"'))
        else:  # New PerformanceDataFrame
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
                names=PerformanceDataFrame.multi_index_names,
            )
            # Create the multi index tuples
            if configurations is None:
                configurations = {
                    solver: {PerformanceDataFrame.default_configuration: {}}
                    for solver in solvers
                }
            column_tuples = []
            # We cannot do .from_product here as config ids are per solver
            for solver in configurations.keys():
                for config_id in configurations[solver].keys():
                    column_tuples.extend(
                        [
                            (solver, config_id, PerformanceDataFrame.column_seed),
                            (solver, config_id, PerformanceDataFrame.column_value),
                        ]
                    )
            mcolumns = pd.MultiIndex.from_tuples(
                column_tuples,
                names=[
                    PerformanceDataFrame.column_solver,
                    PerformanceDataFrame.column_configuration,
                    PerformanceDataFrame.column_meta,
                ],
            )
            # Set dtype object to avoid inferring float for categorical objectives
            super().__init__(
                PerformanceDataFrame.missing_value,
                index=midx,
                columns=mcolumns,
                dtype="object",
            )
            self.csv_filepath = csv_filepath

        # Store configuration in global attributes dictionary, see Pandas Docs
        self.attrs = configurations

        if self.index.duplicated().any():  # Drop all duplicates except for last
            # NOTE: This is rather convoluted (but fast!) due to the fact we need to do it inplace to maintain our type (PerformanceDataFrame)
            # Make the index levels into columns (in-place)
            self.reset_index(inplace=True)
            # The first nlevels columns are the index columns created by reset_index, drop duplicates in those columns
            idx_cols = self.columns[
                : len(PerformanceDataFrame.multi_index_names)
            ].tolist()
            self.drop_duplicates(
                subset=idx_cols, keep="last", inplace=True
            )  # Drop duplicates
            self.set_index(idx_cols, inplace=True)  # Restore the MultiIndex (in-place)
            self.index.rename(
                self.multi_index_names, inplace=True
            )  # Restore level names

        # Sort the index to optimize lookup speed
        self.sort_index(axis=0, inplace=True)
        self.sort_index(axis=1, inplace=True)

        if csv_filepath and not self.csv_filepath.exists():  # New Performance DataFrame
            self.save_csv()

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
        """Return the maximum number of runs of each instance."""
        return self.index.get_level_values(2).unique().size

    @property
    def num_solvers(self: PerformanceDataFrame) -> int:
        """Return the number of solvers."""
        return self.columns.get_level_values(0).unique().size

    @property
    def num_solver_configurations(self: PerformanceDataFrame) -> int:
        """Return the number of solver configurations."""
        return int(
            self.columns.get_level_values(  # Config has a seed & value
                PerformanceDataFrame.column_configuration
            ).size
            / 2
        )

    @property
    def multi_objective(self: PerformanceDataFrame) -> bool:
        """Return whether the dataframe represent MO or not."""
        return self.num_objectives > 1

    @property
    def solvers(self: PerformanceDataFrame) -> list[str]:
        """Return the solver present as a list of strings."""
        # Do not return the nan solver as its not an actual solver
        return (
            self.columns.get_level_values(PerformanceDataFrame.column_solver)
            .dropna()
            .unique()
            .to_list()
        )

    @property
    def configuration_ids(self: PerformanceDataFrame) -> list[str]:
        """Return the list of configuration keys."""
        return (
            self.columns.get_level_values(PerformanceDataFrame.column_configuration)
            .unique()
            .to_list()
        )

    @property
    def configurations(self: PerformanceDataFrame) -> dict[str, dict[str, dict]]:
        """Return a dictionary (copy) containing the configurations for each solver."""
        return copy.deepcopy(self.attrs)  # Deepcopy to avoid mutation of attribute

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
        return (
            self.drop(
                PerformanceDataFrame.column_seed,
                level=PerformanceDataFrame.column_meta,
                axis=1,
            )
            .isnull()
            .any()
            .any()
        )

    def is_missing(
        self: PerformanceDataFrame,
        solver: str,
        instance: str,
    ) -> int:
        """Checks if a solver/instance is missing values."""
        return (
            self.xs(solver, axis=1)
            .xs(instance, axis=0, level=PerformanceDataFrame.index_instance)
            .drop(
                PerformanceDataFrame.column_seed,
                level=PerformanceDataFrame.column_meta,
                axis=1,
            )
            .isnull()
            .any()
            .any()
        )

    def verify_objective(self: PerformanceDataFrame, objective: str) -> str:
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

    def verify_run_id(self: PerformanceDataFrame, run_id: int) -> int:
        """Method to check whether run id is valid.

        Similar to verify_objective but here we check the dimensionality of runs.

        Args:
            run_id: the run as specified by the user.
        """
        if run_id is None:
            if self.num_runs > 1:
                raise ValueError(
                    "Error: Multiple run performance data, but run not specified"
                )
            else:
                run_id = self.run_ids[0]
        return run_id

    def verify_indexing(
        self: PerformanceDataFrame, objective: str, run_id: int
    ) -> tuple[str, int]:
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

    def add_solver(
        self: PerformanceDataFrame,
        solver_name: str,
        configurations: list[(str, dict)] = None,
        initial_value: float | list[str | float] = None,
    ) -> None:
        """Add a new solver to the dataframe. Initializes value to None by default.

        Args:
            solver_name: The name of the solver to be added.
            configurations: A list of configuration keys for the solver.
            initial_value: The value assigned for each index of the new solver.
                If not None, must match the index dimension (n_obj * n_inst * n_runs).
        """
        if solver_name in self.solvers:
            print(
                f"WARNING: Tried adding already existing solver {solver_name} to "
                f"Performance DataFrame: {self.csv_filepath}"
            )
            return
        if not isinstance(initial_value, list):  # Single value
            initial_value = [[initial_value, initial_value]]
        if configurations is None:
            configurations = [(PerformanceDataFrame.default_configuration, {})]
        self.attrs[solver_name] = {}
        for (config_key, config), (value, seed) in itertools.product(
            configurations, initial_value
        ):
            self[(solver_name, config_key, PerformanceDataFrame.column_seed)] = seed
            self[(solver_name, config_key, PerformanceDataFrame.column_value)] = value
            self.attrs[solver_name][config_key] = config
        if self.num_solvers == 2:  # Remove nan solver
            for solver in self.solvers:
                if str(solver) == str(PerformanceDataFrame.missing_value):
                    self.remove_solver(solver)
                    break

    def add_configuration(
        self: PerformanceDataFrame,
        solver: str,
        configuration_id: str | list[str],
        configuration: dict[str, Any] | list[dict[str, Any]] = None,
    ) -> None:
        """Add new configurations for a solver to the dataframe.

        If the key already exists, update the value.

        Args:
            solver: The name of the solver to be added.
            configuration_id: The name of the configuration to be added.
            configuration: The configuration to be added.
        """
        if not isinstance(configuration_id, list):
            configuration_id = [configuration_id]
        if not isinstance(configuration, list):
            configuration = [configuration]
        for config_id, config in zip(configuration_id, configuration):
            if config_id not in self.get_configurations(solver):
                self[(solver, config_id, PerformanceDataFrame.column_value)] = None
                self[(solver, config_id, PerformanceDataFrame.column_seed)] = None
            self.attrs[solver][config_id] = config
        # Sort the index to optimize lookup speed
        self.sort_index(axis=1, inplace=True)

    def add_objective(
        self: PerformanceDataFrame, objective_name: str, initial_value: float = None
    ) -> None:
        """Add an objective to the DataFrame."""
        initial_value = initial_value or self.missing_value
        if objective_name in self.objective_names:
            print(
                f"WARNING: Tried adding already existing objective {objective_name} "
                f"to Performance DataFrame: {self.csv_filepath}"
            )
            return
        for instance, run in itertools.product(self.instances, self.run_ids):
            self.loc[(objective_name, instance, run)] = initial_value
        self.sort_index(axis=0, inplace=True)

    def add_instance(
        self: PerformanceDataFrame,
        instance_name: str,
        initial_values: Any | list[Any] = None,
    ) -> None:
        """Add and instance to the DataFrame.

        Args:
            instance_name: The name of the instance to be added.
            initial_values: The values assigned for each index of the new instance.
                If list, must match the column dimension (Value, Seed, Configuration).
        """
        initial_values = initial_values or self.missing_value
        if not isinstance(initial_values, list):
            initial_values = (
                [initial_values]
                * 2  # Value and Seed per target column
                * self.num_solver_configurations
            )
        elif len(initial_values) == len(PerformanceDataFrame.multi_column_names):
            initial_values = initial_values * self.num_solvers

        if instance_name in self.instances:
            print(
                f"WARNING: Tried adding already existing instance {instance_name} "
                f"to Performance DataFrame: {self.csv_filepath}"
            )
            return
        # Add rows for all combinations
        for objective, run in itertools.product(self.objective_names, self.run_ids):
            self.loc[(objective, instance_name, run)] = initial_values
        if self.num_instances == 2:  # Remove nan instance
            for instance in self.instances:
                if not isinstance(instance, str) and math.isnan(instance):
                    self.remove_instances(instance)
                    break
        # Sort the index to optimize lookup speed
        self.sort_index(axis=0, inplace=True)

    def add_runs(
        self: PerformanceDataFrame,
        num_extra_runs: int,
        instance_names: list[str] = None,
        initial_values: Any | list[Any] = None,
    ) -> None:
        """Add runs to the DataFrame.

        Args:
            num_extra_runs: The number of runs to be added.
            instance_names: The instances for which runs are to be added.
              By default None, which means runs are added to all instances.
            initial_values: The initial value for each objective of each new run.
                If a list, needs to have a value for Value, Seed and Configuration.
        """
        initial_values = initial_values or self.missing_value
        if not isinstance(initial_values, list):
            initial_values = [initial_values] * self.num_solvers * 2  # Value and Seed
        elif len(initial_values) == 2:  # Value and seed provided
            initial_values = initial_values * self.num_solvers
        instance_names = self.instances if instance_names is None else instance_names
        for objective, instance in itertools.product(
            self.objective_names, instance_names
        ):
            index_runs_start = len(self.loc[(objective, instance)]) + 1
            for run in range(index_runs_start, index_runs_start + num_extra_runs):
                self.loc[(objective, instance, run)] = initial_values
            # Sort the index to optimize lookup speed
            # NOTE: It would be better to do this at the end, but that results in
            # PerformanceWarning: indexing past lexsort depth may impact performance.
            self.sort_index(axis=0, inplace=True)

    def get_configurations(self: PerformanceDataFrame, solver_name: str) -> list[str]:
        """Return the list of configuration keys for a solver."""
        return list(
            self[solver_name]
            .columns.get_level_values(PerformanceDataFrame.column_configuration)
            .unique()
        )

    def get_full_configuration(
        self: PerformanceDataFrame, solver: str, configuration_id: str | list[str]
    ) -> dict | list[dict]:
        """Return the actual configuration associated with the configuration key."""
        if isinstance(configuration_id, str):
            return self.attrs[solver][configuration_id]
        return [self.attrs[solver][cid] for cid in configuration_id]

    def remove_solver(self: PerformanceDataFrame, solvers: str | list[str]) -> None:
        """Drop one or more solvers from the Dataframe."""
        if not solvers:  # Bugfix for when an empty list is passed to avoid nan adding
            return
        # To make sure objectives / runs are saved when no solvers are present
        solvers = [solvers] if isinstance(solvers, str) else solvers
        if self.num_solvers == 1:  # This would preferrably be done after removing
            for field in PerformanceDataFrame.multi_column_value:
                self[
                    PerformanceDataFrame.missing_value,
                    PerformanceDataFrame.missing_value,
                    field,
                ] = PerformanceDataFrame.missing_value
        self.drop(columns=solvers, level=0, axis=1, inplace=True)
        for solver in solvers:
            del self.attrs[solver]

    def remove_configuration(
        self: PerformanceDataFrame, solver: str, configuration: str | list[str]
    ) -> None:
        """Drop one or more configurations from the Dataframe."""
        if isinstance(configuration, str):
            configuration = [configuration]
        for config in configuration:
            self.drop((solver, config), axis=1, inplace=True)
            del self.attrs[solver][config]
        # Sort the index to optimize lookup speed
        self.sort_index(axis=1, inplace=True)

    def remove_objective(
        self: PerformanceDataFrame, objectives: str | list[str]
    ) -> None:
        """Remove objective from the Dataframe."""
        if len(self.objectives) < 2:
            raise Exception("Cannot remove last objective from PerformanceDataFrame")
        self.drop(
            objectives,
            axis=0,
            level=PerformanceDataFrame.index_objective,
            inplace=True,
        )

    def remove_instances(self: PerformanceDataFrame, instances: str | list[str]) -> None:
        """Drop instances from the Dataframe."""
        # To make sure objectives / runs are saved when no instances are present
        num_instances = len(instances) if isinstance(instances, list) else 1
        if self.num_instances - num_instances == 0:
            for objective, run in itertools.product(self.objective_names, self.run_ids):
                self.loc[(objective, PerformanceDataFrame.missing_value, run)] = (
                    PerformanceDataFrame.missing_value
                )
        self.drop(
            instances, axis=0, level=PerformanceDataFrame.index_instance, inplace=True
        )
        # Sort the index to optimize lookup speed
        self.sort_index(axis=0, inplace=True)

    def remove_runs(
        self: PerformanceDataFrame,
        runs: int | list[int],
        instance_names: list[str] = None,
    ) -> None:
        """Drop one or more runs from the Dataframe.

        Args:
            runs: The run indices to be removed. If its an int,
              the last n runs are removed. NOTE: If each instance has a different
              number of runs, the amount of removed runs is not uniform.
            instance_names: The instances for which runs are to be removed.
              By default None, which means runs are removed from all instances.
        """
        instance_names = self.instances if instance_names is None else instance_names
        runs = (
            list(range((self.num_runs + 1) - runs, (self.num_runs + 1)))
            if isinstance(runs, int)
            else runs
        )
        self.drop(runs, axis=0, level=PerformanceDataFrame.index_run, inplace=True)
        # Sort the index to optimize lookup speed
        self.sort_index(axis=0, inplace=True)

    def remove_empty_runs(self: PerformanceDataFrame) -> None:
        """Remove runs that contain no data, except for the first."""
        for row_index in self.index:
            if row_index[2] == 1:  # First run, never delete
                continue
            if self.loc[row_index].isna().all():
                self.drop(row_index, inplace=True)

    def filter_objective(self: PerformanceDataFrame, objective: str | list[str]) -> None:
        """Filter the Dataframe to a subset of objectives."""
        if isinstance(objective, str):
            objective = [objective]
        self.drop(
            list(set(self.objective_names) - set(objective)),
            axis=0,
            level=PerformanceDataFrame.index_objective,
            inplace=True,
        )

    def reset_value(
        self: PerformanceDataFrame,
        solver: str,
        instance: str,
        objective: str = None,
        run: int = None,
    ) -> None:
        """Reset a value in the dataframe."""
        self.set_value(
            PerformanceDataFrame.missing_value, solver, instance, objective, run
        )

    def set_value(
        self: PerformanceDataFrame,
        value: float | str | list[float | str] | list[list[float | str]],
        solver: str | list[str],
        instance: str | list[str],
        configuration: str = None,
        objective: str | list[str] = None,
        run: int | list[int] = None,
        solver_fields: list[str] = ["Value"],
        append_write_csv: bool = False,
    ) -> None:
        """Setter method to assign a value to the Dataframe.

        Allows for setting the same value to multiple indices.

        Args:
            value: Value(s) to be assigned. If value is a list, first dimension is
                the solver field, second dimension is if multiple different values are
                to be assigned. Must be the same shape as target.
            solver: The solver(s) for which the value should be set.
                If solver is a list, multiple solvers are set. If None, all
                solvers are set.
            instance: The instance(s) for which the value should be set.
                If instance is a list, multiple instances are set. If None, all
                instances are set.
            configuration: The configuration(s) for which the value should be set.
                When left None, set for all configurations
            objective: The objectives for which the value should be set.
                When left None, set for all objectives
            run: The run index for which the value should be set.
                If left None, set for all runs.
            solver_fields: The level to which each value should be assinged.
                Defaults to ["Value"].
            append_write_csv: For concurrent writing to the PerformanceDataFrame.
                If True, the value is directly appended to the CSV file.
                This will create duplicate entries in the file, but these are combined
                when loading the file.
        """
        # Convert indices to slices for None values
        solver = slice(solver) if solver is None else solver
        configuration = slice(configuration) if configuration is None else configuration
        instance = slice(instance) if instance is None else instance
        objective = slice(objective) if objective is None else objective
        run = slice(run) if run is None else run
        # Convert column indices to slices for setting multiple columns
        value = [value] if not isinstance(value, list) else value
        # NOTE: We currently forloop levels here, as it allows us to set the same
        # sequence of values to the indices
        for item, level in zip(value, solver_fields):
            self.loc[(objective, instance, run), (solver, configuration, level)] = item

        if append_write_csv:
            writeable = self.loc[(objective, instance, run), :]
            if isinstance(writeable, pd.Series):  # Single row, convert to pd.DataFrame
                writeable = self.loc[[(objective, instance, run)], :]
            # Append the new rows to the dataframe csv file
            writeable.to_csv(self.csv_filepath, mode="a", header=False)

    def get_value(
        self: PerformanceDataFrame,
        solver: str | list[str] = None,
        instance: str | list[str] = None,
        configuration: str = None,
        objective: str = None,
        run: int = None,
        solver_fields: list[str] = ["Value"],
    ) -> float | str | list[Any]:
        """Index a value of the DataFrame and return it."""
        # Convert indices to slices for None values
        solver = slice(solver) if solver is None else solver
        configuration = slice(configuration) if configuration is None else configuration
        instance = slice(instance) if instance is None else instance
        objective = slice(objective) if objective is None else objective
        solver_fields = slice(solver_fields) if solver_fields is None else solver_fields
        run = slice(run) if run is None else run
        target = self.loc[
            (objective, instance, run), (solver, configuration, solver_fields)
        ].values
        # Reduce dimensions when relevant
        if len(target) > 0 and isinstance(target[0], np.ndarray) and len(target[0]) == 1:
            target = target.flatten()
        target = target.tolist()
        if len(target) == 1:
            return target[0]
        return target

    def get_instance_num_runs(self: PerformanceDataFrame, instance: str) -> int:
        """Return the number of runs for an instance."""
        # We assume each objective has the same index for Instance/Runs
        return len(self.loc[(self.objective_names[0], instance)].index)

    # Calculables

    def mean(
        self: PerformanceDataFrame,
        objective: str = None,
        solver: str = None,
        instance: str = None,
    ) -> float:
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

    def get_job_list(
        self: PerformanceDataFrame, rerun: bool = False
    ) -> list[tuple[str, str]]:
        """Return a list of performance computation jobs there are to be done.

        Get a list of tuple[instance, solver] to run from the performance data.
        If rerun is False (default), get only the tuples that don't have a
        value, else (True) get all the tuples.

        Args:
            rerun: Boolean indicating if we want to rerun all jobs

        Returns:
            A tuple of (solver, config, instance, run) combinations
        """
        # Drop the seed as we are looking for nan values, not seeds
        df = self.drop(
            PerformanceDataFrame.column_seed,
            axis=1,
            level=PerformanceDataFrame.column_meta,
        )
        df = df.droplevel(PerformanceDataFrame.column_meta, axis=1)
        if rerun:  # Return all combinations
            # Drop objective, not needed
            df = df.droplevel(PerformanceDataFrame.index_objective, axis=0)
            result = [
                tuple(column) + tuple(index)
                for column, index in itertools.product(df.columns, df.index)
            ]
        else:
            result = []
            for (solver, config), (objective, instance, run) in itertools.product(
                df.columns, df.index
            ):
                value = df.loc[(objective, instance, run), (solver, config)]
                if value is None or (
                    isinstance(value, (int, float)) and math.isnan(value)
                ):
                    result.append(tuple([solver, config, instance, run]))
        # Filter duplicates while keeping the order conistent
        result = list(dict.fromkeys(result))
        return result

    def configuration_performance(
        self: PerformanceDataFrame,
        solver: str,
        configuration: str | list[str] = None,
        objective: str | SparkleObjective = None,
        instances: list[str] = None,
        per_instance: bool = False,
    ) -> tuple[str, float]:
        """Return the (best) configuration performance for objective over the instances.

        Args:
            solver: The solver for which we determine evaluate the configuration
            configuration: The configuration (id) to evaluate
            objective: The objective for which we calculate find the best value
            instances: The instances which should be selected for the evaluation
            per_instance: Whether to return the performance per instance,
                or aggregated.

        Returns:
            The (best) configuration id and its aggregated performance.
        """
        objective = self.verify_objective(objective)
        if isinstance(objective, str):
            objective = resolve_objective(objective)
        # Filter objective
        subdf = self.xs(objective.name, level=0, drop_level=True)
        # Filter solver
        subdf = subdf.xs(solver, axis=1, drop_level=True)
        # Drop the seed, then drop meta level as it is no longer needed
        subdf = subdf.drop(
            PerformanceDataFrame.column_seed,
            axis=1,
            level=PerformanceDataFrame.column_meta,
        )
        subdf = subdf.droplevel(PerformanceDataFrame.column_meta, axis=1)
        # Ensure the objective is numeric
        subdf = subdf.astype(float)

        if instances:  # Filter instances
            subdf = subdf.loc[instances, :]
        if configuration:  # Filter configuration
            if not isinstance(configuration, list):
                configuration = [configuration]
            subdf = subdf.filter(configuration, axis=1)
        # Aggregate the runs
        subdf = subdf.groupby(PerformanceDataFrame.index_instance).agg(
            func=objective.run_aggregator.__name__
        )
        # Aggregate the instances
        sub_series = subdf.agg(func=objective.instance_aggregator.__name__)
        # Select the best configuration
        best_conf = sub_series.idxmin() if objective.minimise else sub_series.idxmax()
        if per_instance:  # Return a list of instance results
            return best_conf, subdf[best_conf].to_list()
        return best_conf, sub_series[best_conf]

    def best_configuration(
        self: PerformanceDataFrame,
        solver: str,
        objective: SparkleObjective = None,
        instances: list[str] = None,
    ) -> tuple[str, float]:
        """Return the best configuration for the given objective over the instances.

        Args:
            solver: The solver for which we determine the best configuration
            objective: The objective for which we calculate the best configuration
            instances: The instances which should be selected for the evaluation

        Returns:
            The best configuration id and its aggregated performance.
        """
        return self.configuration_performance(solver, None, objective, instances)

    def best_instance_performance(
        self: PerformanceDataFrame,
        objective: str | SparkleObjective = None,
        instances: list[str] = None,
        run_id: int = None,
        exclude_solvers: list[(str, str)] = None,
    ) -> pd.Series:
        """Return the best performance for each instance in the portfolio.

        Args:
            objective: The objective for which we calculate the best performance
            instances: The instances which should be selected for the evaluation
            run_id: The run for which we calculate the best performance. If None,
                we consider all runs.
            exclude_solvers: List of (solver, config_id) to exclude in the calculation.

        Returns:
            The best performance for each instance in the portfolio.
        """
        objective = self.verify_objective(objective)
        if isinstance(objective, str):
            objective = resolve_objective(objective)
        subdf = self.drop(  # Drop Seed, not needed
            [PerformanceDataFrame.column_seed],
            axis=1,
            level=PerformanceDataFrame.column_meta,
        )
        subdf = subdf.xs(objective.name, level=0)  # Drop objective
        if exclude_solvers is not None:
            subdf = subdf.drop(exclude_solvers, axis=1)
        if instances is not None:
            subdf = subdf.loc[instances, :]
        if run_id is not None:
            run_id = self.verify_run_id(run_id)
            subdf = subdf.xs(run_id, level=1)
        else:
            # Drop the run level
            subdf = subdf.droplevel(level=1)
        # Ensure the objective is numeric
        subdf = subdf.astype(float)
        series = subdf.min(axis=1) if objective.minimise else subdf.max(axis=1)
        # Ensure we always return the best for each run
        series = series.sort_values(ascending=objective.minimise)
        return series.groupby(series.index).first().astype(float)

    def best_performance(
        self: PerformanceDataFrame,
        exclude_solvers: list[(str, str)] = [],
        instances: list[str] = None,
        objective: str | SparkleObjective = None,
    ) -> float:
        """Return the overall best performance of the portfolio.

        Args:
            exclude_solvers: List of (solver, config_id) to exclude in the calculation.
                Defaults to none.
            instances: The instances which should be selected for the evaluation
                If None, use all instances.
            objective: The objective for which we calculate the best performance

        Returns:
            The aggregated best performance of the portfolio over all instances.
        """
        objective = self.verify_objective(objective)
        if isinstance(objective, str):
            objective = resolve_objective(objective)
        instance_best = self.best_instance_performance(
            objective, instances=instances, exclude_solvers=exclude_solvers
        ).to_numpy(dtype=float)
        return objective.instance_aggregator(instance_best)

    def schedule_performance(
        self: PerformanceDataFrame,
        schedule: dict[str : dict[str : (str, str, int)]],
        target_solver: str | tuple[str, str] = None,
        objective: str | SparkleObjective = None,
    ) -> float:
        """Return the performance of a selection schedule on the portfolio.

        Args:
            schedule: Compute the best performance according to a selection schedule.
                A schedule is a dictionary of instances, with a schedule per instance,
                consisting of a triple of solver, config_id and maximum runtime.
            target_solver: If not None, store the found values in this solver of the DF.
            objective: The objective for which we calculate the best performance

        Returns:
            The performance of the schedule over the instances in the dictionary.
        """
        objective = self.verify_objective(objective)
        if isinstance(objective, str):
            objective = resolve_objective(objective)
        select = min if objective.minimise else max
        performances = [0.0] * len(schedule.keys())
        if not isinstance(target_solver, tuple):
            target_conf = PerformanceDataFrame.default_configuration
        else:
            target_solver, target_conf = target_solver
        if target_solver and target_solver not in self.solvers:
            self.add_solver(target_solver)
        for ix, instance in enumerate(schedule.keys()):
            for iy, (solver, config, max_runtime) in enumerate(schedule[instance]):
                performance = float(
                    self.get_value(solver, instance, config, objective.name)
                )
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
                self.set_value(
                    performances[ix],
                    target_solver,
                    instance,
                    target_conf,
                    objective.name,
                )
        return performances

    def marginal_contribution(
        self: PerformanceDataFrame,
        objective: str | SparkleObjective = None,
        instances: list[str] = None,
        sort: bool = False,
    ) -> list[float]:
        """Return the marginal contribution of the solver configuration on the instances.

        Args:
            objective: The objective for which we calculate the marginal contribution.
            instances: The instances which should be selected for the evaluation
            sort: Whether to sort the results afterwards
        Returns:
            The marginal contribution of each solver (configuration) as:
            [(solver, config_id, marginal_contribution, portfolio_best_performance_without_solver)]
        """
        output = []
        objective = self.verify_objective(objective)
        if isinstance(objective, str):
            objective = resolve_objective(objective)
        best_performance = self.best_performance(
            objective=objective, instances=instances
        )
        for solver in self.solvers:
            for config_id in self.get_configurations(solver):
                # By calculating the best performance excluding this Solver,
                # we can determine its relative impact on the portfolio.
                missing_solver_config_best = self.best_performance(
                    exclude_solvers=[(solver, config_id)],
                    instances=instances,
                    objective=objective,
                )
                # Now we need to see how much the portfolio's best performance
                # decreases without this solver.
                marginal_contribution = missing_solver_config_best / best_performance
                if missing_solver_config_best == best_performance:
                    # No change, no contribution
                    marginal_contribution = 0.0
                output.append(
                    (
                        solver,
                        config_id,
                        marginal_contribution,
                        missing_solver_config_best,
                    )
                )
        if sort:
            output.sort(key=lambda x: x[2], reverse=objective.minimise)
        return output

    def get_solver_ranking(
        self: PerformanceDataFrame,
        objective: str | SparkleObjective = None,
        instances: list[str] = None,
    ) -> list[tuple[str, dict, float]]:
        """Return a list with solvers ranked by average performance."""
        objective = self.verify_objective(objective)
        if isinstance(objective, str):
            objective = resolve_objective(objective)
        # Drop Seed
        sub_df = self.drop(
            [PerformanceDataFrame.column_seed],
            axis=1,
            level=PerformanceDataFrame.column_meta,
        )
        # Reduce objective
        sub_df: pd.DataFrame = sub_df.loc(axis=0)[objective.name, :, :]
        # Drop Objective, Meta multi index
        sub_df = sub_df.droplevel(PerformanceDataFrame.index_objective).droplevel(
            PerformanceDataFrame.column_meta, axis=1
        )
        if instances is not None:  # Select instances
            sub_df = sub_df.loc(axis=0)[instances,]
        # Ensure data is numeric
        sub_df = sub_df.astype(float)
        # Aggregate runs
        sub_df = sub_df.groupby(PerformanceDataFrame.index_instance).agg(
            func=objective.run_aggregator.__name__
        )
        # Aggregate instances
        sub_series = sub_df.aggregate(func=objective.instance_aggregator.__name__)
        # Sort by objective
        sub_series.sort_values(ascending=objective.minimise, inplace=True)
        return [(index[0], index[1], sub_series[index]) for index in sub_series.index]

    def save_csv(self: PerformanceDataFrame, csv_filepath: Path = None) -> None:
        """Write a CSV to the given path.

        Args:
            csv_filepath: String path to the csv file. Defaults to self.csv_filepath.
        """
        csv_filepath = self.csv_filepath if csv_filepath is None else csv_filepath
        self.to_csv(csv_filepath)
        # Append the configurations
        with csv_filepath.open("a") as fout:
            fout.write("\n$Solver,configuration_id,Configuration\n")
            for solver in self.solvers:
                for config_id in self.attrs[solver]:
                    configuration = self.attrs[solver][config_id]
                    fout.write(f"${solver},{config_id},{str(configuration)}\n")

    def clone(
        self: PerformanceDataFrame, csv_filepath: Path = None
    ) -> PerformanceDataFrame:
        """Create a copy of this object.

        Args:
            csv_filepath: The new filepath to use for saving the object to.
                If None, will not be saved.
                Warning: If the original path is used, it could lead to dataloss!
        """
        pd_copy = PerformanceDataFrame(
            csv_filepath=csv_filepath,
            solvers=self.solvers,
            configurations=self.configurations,
            objectives=self.objectives,
            instances=self.instances,
            n_runs=self.num_runs,
        )
        # Copy values
        for column_index in self.columns:
            for index in self.index:
                pd_copy.at[index, column_index] = self.loc[index, column_index]
        # Ensure everything is sorted?
        return pd_copy

    def clean_csv(self: PerformanceDataFrame) -> None:
        """Set all values in Performance Data to None."""
        self[:] = PerformanceDataFrame.missing_value
        self.save_csv()
