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
    index_instance_set = "InstanceSet"
    index_instance = "Instance"
    index_run = "Run"
    multi_index_names = [index_objective, index_instance_set, index_instance, index_run]

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
        instance_pairs: list[tuple[str, str]] = None,
        n_runs: int = 1,
    ) -> None:
        """Initialise a PerformanceDataFrame.

        Consists of:
            - Columns representing the Solvers
            - Rows representing the result by multi-index in order of:
                * Objective (Static, given in constructor or read from file)
                * InstanceSet
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
            instance_pairs: List of (set_name, instance_name) pairs to add. By default None.
            n_runs: The number of runs to consider per Solver/Objective/Instance comb.
        """
        if csv_filepath and csv_filepath.exists():  # Read from file
            df = pd.read_csv(
                csv_filepath,
                header=[0, 1, 2],
                index_col=[0, 1, 2, 3],
                on_bad_lines="skip",
                dtype={
                    PerformanceDataFrame.column_value: str,
                    PerformanceDataFrame.column_seed: int,
                    # PerformanceDataFrame.index_run: int,  # NOTE: Preferrably, this would be set, but it is not included in the "on_bad_lines=skip" case for error lines.
                },
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
            configurations = {solver: {} for solver in self.solvers}
            for solver, config_key, config in configuration_lines[1:]:  # Skip header
                if (
                    solver in configurations
                ):  # Only add configurations to already known solvers, based on the columns
                    configurations[solver][config_key] = ast.literal_eval(
                        config.strip('"')
                    )
        else:  # New PerformanceDataFrame
            # Initialize empty DataFrame
            run_ids = list(range(1, n_runs + 1))  # We count runs from 1
            # We always need objectives to maintain the dimensions
            if objectives is None:
                objectives = [PerformanceDataFrame.missing_objective]
            else:
                objectives = [str(objective) for objective in objectives]
            # We always need an instance to maintain the dimensions
            if instance_pairs is None:
                instance_pairs = [
                    (
                        PerformanceDataFrame.missing_value,
                        PerformanceDataFrame.missing_value,
                    )
                ]
            # We always need a solver to maintain the dimensions
            if solvers is None:
                solvers = [PerformanceDataFrame.missing_value]
            # Build the 4-level index explicitly (from_product can't handle pair instances)
            midx = pd.MultiIndex.from_tuples(
                [
                    (objective, set_name, instance, run)
                    for objective in objectives
                    for (set_name, instance) in instance_pairs
                    for run in run_ids
                ],
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
                names=PerformanceDataFrame.multi_column_names,
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
                PerformanceDataFrame.multi_index_names, inplace=True
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
        return (
            self.index.get_level_values(PerformanceDataFrame.index_objective)
            .unique()
            .size
        )

    @property
    def num_instances(self: PerformanceDataFrame) -> int:
        """Return the number of unique (InstanceSet, Instance) pairs."""
        return len(self.instance_pairs)

    @property
    def num_runs(self: PerformanceDataFrame) -> int:
        """Return the maximum number of runs of each instance."""
        return self.index.get_level_values(PerformanceDataFrame.index_run).unique().size

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
        return (
            self.index.get_level_values(PerformanceDataFrame.index_objective)
            .unique()
            .to_list()
        )

    @property
    def objectives(self: PerformanceDataFrame) -> list[SparkleObjective]:
        """Return the objectives as a list of SparkleObjectives."""
        return [resolve_objective(objective) for objective in self.objective_names]

    @property
    def instance_pairs(self: PerformanceDataFrame) -> list[tuple[str, str]]:
        """Return the (set_name, instance_name) pairs as a list."""
        set_vals = self.index.get_level_values(PerformanceDataFrame.index_instance_set)
        inst_vals = self.index.get_level_values(PerformanceDataFrame.index_instance)
        pairs = list(zip(set_vals, inst_vals))
        # Unique, order-preserving
        return list(dict.fromkeys(pairs))

    @property
    def instance_sets(self: PerformanceDataFrame) -> list[str]:
        """Return the unique instance set names."""
        return (
            self.index.get_level_values(PerformanceDataFrame.index_instance_set)
            .unique()
            .tolist()
        )

    @property
    def run_ids(self: PerformanceDataFrame) -> list[int]:
        """Return the run ids as a list of integers."""
        return (
            self.index.get_level_values(PerformanceDataFrame.index_run)
            .unique()
            .to_list()
        )

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
        instance_pair: tuple[str, str],
    ) -> int:
        """Check whether a solver has any missing values for an instance.

        Args:
            solver: Solver to be checked.
            instance_pair: A (set_name, instance_name) pair.

        Returns:
            True(1) if any value (excluding the seed) is missing for the given
            solver/instance combination across all objectives, configurations
            and runs, False otherwise.
        """
        set_name, inst = instance_pair
        return (
            self.xs(solver, axis=1)
            .xs(set_name, axis=0, level=PerformanceDataFrame.index_instance_set)
            .xs(inst, axis=0, level=PerformanceDataFrame.index_instance)
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
        for instance_pair, run in itertools.product(self.instance_pairs, self.run_ids):
            self.loc[(objective_name,) + instance_pair + (run,)] = initial_value
        self.sort_index(axis=0, inplace=True)

    def add_instance(
        self: PerformanceDataFrame,
        instance_pair: tuple[str, str] | list[tuple[str, str]],
        initial_values: Any | list[Any] = None,
    ) -> None:
        """Add one or more instances to the DataFrame.

        Args:
            instance_pair: A (set_name, instance_name) pair, or a list of such pairs
                to add multiple instances at once.
            initial_values: The values assigned for each index of the new instance(s).
                The same values are used for every added instance. If a list, it must
                match the column dimension (Value, Seed, Configuration).
        """
        # Normalise to a list of pairs so the index is built and sorted only once.
        instance_pairs = (
            [instance_pair] if isinstance(instance_pair, tuple) else instance_pair
        )
        # Normalise initial_values into a full row once; it is shared by every instance.
        initial_values = initial_values or self.missing_value
        if not isinstance(initial_values, list):
            initial_values = (
                [initial_values]
                * 2  # Value and Seed per target column
                * self.num_solver_configurations
            )
        elif len(initial_values) == len(PerformanceDataFrame.multi_column_names):
            initial_values = initial_values * self.num_solvers

        existing_pairs = set(self.instance_pairs)
        for instance_pair in instance_pairs:
            if instance_pair in existing_pairs:
                print(
                    f"WARNING: Tried adding already existing instance {instance_pair} "
                    f"to Performance DataFrame: {self.csv_filepath}"
                )
                continue
            existing_pairs.add(instance_pair)  # Guard against duplicates in the input
            # Add rows for all combinations
            for objective, run in itertools.product(self.objective_names, self.run_ids):
                self.loc[(objective,) + instance_pair + (run,)] = initial_values

        # Remove the placeholder nan instance now that real instances exist.
        if self.num_instances > 1:
            for inst_pair in self.instance_pairs:
                instance_set, instance = inst_pair
                if not isinstance(instance, str) and math.isnan(float(instance)):
                    self.remove_instance(inst_pair)
                    break
        # Sort the index once to optimize lookup speed
        self.sort_index(axis=0, inplace=True)

    def add_runs(
        self: PerformanceDataFrame,
        num_extra_runs: int,
        instance_pairs: list[tuple[str, str]] = None,
        initial_values: Any | list[Any] = None,
    ) -> None:
        """Add runs to the DataFrame.

        Args:
            num_extra_runs: The number of runs to be added.
            instance_pairs: The instances for which runs are to be added.
              By default None, which means runs are added to all instances.
            initial_values: The initial value for each objective of each new run.
                If a list, needs to have a value for Value, Seed and Configuration.
        """
        initial_values = initial_values or self.missing_value
        if not isinstance(initial_values, list):
            initial_values = [initial_values] * self.num_solvers * 2  # Value and Seed
        elif len(initial_values) == 2:  # Value and seed provided
            initial_values = initial_values * self.num_solvers
        instance_pairs = (
            self.instance_pairs if instance_pairs is None else instance_pairs
        )
        for objective, instance_pair in itertools.product(
            self.objective_names, instance_pairs
        ):
            index_runs_start = len(self.loc[(objective,) + instance_pair]) + 1
            for run in range(index_runs_start, index_runs_start + num_extra_runs):
                self.loc[(objective,) + instance_pair + (run,)] = initial_values
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

    def remove_instance(
        self: PerformanceDataFrame,
        instance_pairs: tuple[str, str] | list[tuple[str, str]],
    ) -> None:
        """Drop instances from the Dataframe.

        Args:
            instance_pairs: A (set_name, instance_name) pair or list of such pairs.
        """
        if isinstance(instance_pairs, tuple):
            instance_pairs = [instance_pairs]
        num_instance_pairs = len(instance_pairs)
        # To make sure objectives / runs are saved when no instances are present
        if self.num_instances - num_instance_pairs == 0:
            for objective, run in itertools.product(self.objective_names, self.run_ids):
                self.loc[
                    (
                        objective,
                        PerformanceDataFrame.missing_value,
                        PerformanceDataFrame.missing_value,
                        run,
                    )
                ] = PerformanceDataFrame.missing_value
        # Build a mask over (InstanceSet, Instance) levels
        pair_idx = pd.MultiIndex.from_tuples(instance_pairs)

        # Get the index to be dropped with help of mask
        to_drop = self.index[
            self.index.droplevel(
                [PerformanceDataFrame.index_objective, PerformanceDataFrame.index_run]
            ).isin(pair_idx)
        ]
        self.drop(to_drop, inplace=True)
        # Sort the index to optimize lookup speed
        self.sort_index(axis=0, inplace=True)

    def remove_runs(
        self: PerformanceDataFrame,
        runs: int | list[int],
        instance_pairs: list[tuple[str, str]] = None,
    ) -> None:
        """Drop one or more runs from the Dataframe.

        Args:
            runs: The run indices to be removed. If its an int,
              the last n runs are removed. NOTE: If each instance has a different
              number of runs, the amount of removed runs is not uniform.
            instance_pairs: The instances for which runs are to be removed.
              By default None, which means runs are removed from all instances.
        """
        instance_pairs = (
            self.instance_pairs if instance_pairs is None else instance_pairs
        )
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
            if (
                row_index[3] == 1
            ):  # Run is at level 3 (Objective, InstanceSet, Instance, Run)
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
        instance_pair: tuple[str, str],
        objective: str = None,
        run: int = None,
    ) -> None:
        """Reset a value in the dataframe."""
        self.set_value(
            PerformanceDataFrame.missing_value, solver, instance_pair, objective, run
        )

    def set_value(
        self: PerformanceDataFrame,
        value: float | str | list[float | str] | list[list[float | str]],
        solver: str | list[str],
        instance_pair: tuple[str, str] | list[tuple[str, str]] | None,
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
            instance_pair: The (set_name, instance_name) pair for which the value should
                be set. If None, all instances are set.
            configuration: The configuration(s) for which the value should be set.
                When left None, set for all configurations
            objective: The objectives for which the value should be set.
                When left None, set for all objectives
            run: The run index for which the value should be set.
                If left None, set for all runs.
            solver_fields: The level to which each value should be assigned.
                Defaults to ["Value"].
            append_write_csv: For concurrent writing to the PerformanceDataFrame.
                If True, the value is directly appended to the CSV file.
                This will create duplicate entries in the file, but these are combined
                when loading the file.
        """
        # Convert indices to slices for None values
        solver = solver if solver else slice(solver)  # None case
        configuration = configuration if configuration else slice(configuration)
        objective = objective if objective else slice(objective)
        run = run if run else slice(run)
        if instance_pair is None:  # None selects all instances
            inst_set, inst_name = slice(None), slice(None)
        elif isinstance(instance_pair, list):  # Multiple (set, instance) pairs
            inst_set = [pair[0] for pair in instance_pair]
            inst_name = [pair[1] for pair in instance_pair]
        else:  # A single (set, instance) pair
            inst_set, inst_name = instance_pair
        row_idx = (objective, inst_set, inst_name, run)
        # Convert column indices to slices for setting multiple columns
        value = [value] if not isinstance(value, list) else value
        # NOTE: We currently forloop levels here, as it allows us to set the same
        # sequence of values to the indices
        for item, level in zip(value, solver_fields):
            self.loc[row_idx, (solver, configuration, level)] = item

        if append_write_csv:
            writeable = self.loc[row_idx, :]
            if isinstance(writeable, pd.Series):  # Single row, convert to pd.DataFrame
                writeable = self.loc[[row_idx], :]
            # Append the new rows to the dataframe csv file
            import os

            csv_string = writeable.to_csv(header=False)  # Convert to the csv lines
            for line in csv_string.splitlines():
                fd = os.open(f"{self.csv_filepath}", os.O_WRONLY | os.O_APPEND)
                os.write(fd, f"{line}\n".encode("utf-8"))  # Encode to create buffer
                # Open and close for each line to minimise possibilities of conflict
                os.close(fd)

    def get_value(
        self: PerformanceDataFrame,
        solver: str | list[str] = None,
        instance_pair: tuple[str, str] | list[tuple[str, str]] | None = None,
        configuration: str = None,
        objective: str = None,
        run: int = None,
        solver_fields: list[str] = ["Value"],
    ) -> float | str | list[Any]:
        """Index a value of the DataFrame and return it.

        Any dimension left as None is treated as a wildcard, selecting all
        entries along that dimension.

        Args:
            solver: Solver name or list of solver names. None selects all solvers.
            instance_pair: A (set_name, instance_name) pair, or None for all instances.
            configuration: Configuration key to select. None selects all configurations.
            objective: Objective name to select. None selects all objectives.
            run: Run id to select. None selects all runs.
            solver_fields: The solver value fields to return (e.g. "Value", "Seed").

        Returns:
            The selected value if a single cell is matched, otherwise a list of
            the matched values.
        """
        # Convert indices to slices for None values
        solver = solver if solver else slice(solver)
        configuration = configuration if configuration else slice(configuration)
        objective = objective if objective else slice(objective)
        solver_fields = solver_fields if solver_fields else slice(solver_fields)
        run = run if run else slice(run)
        if instance_pair is None:  # None selects all instances
            inst_set, inst_name = slice(None), slice(None)
        elif isinstance(instance_pair, list):  # Multiple (set, instance) pairs
            inst_set = [pair[0] for pair in instance_pair]
            inst_name = [pair[1] for pair in instance_pair]
        else:  # A single (set, instance) pair
            inst_set, inst_name = instance_pair
        row_idx = (objective, inst_set, inst_name, run)
        target = self.loc[row_idx, (solver, configuration, solver_fields)].values
        # Reduce dimensions when relevant
        if len(target) > 0 and isinstance(target[0], np.ndarray) and len(target[0]) == 1:
            target = target.flatten()
        target = target.tolist()
        if len(target) == 1:
            return target[0]
        return target

    def get_instance_num_runs(
        self: PerformanceDataFrame, instance_pair: tuple[str, str]
    ) -> int:
        """Return the number of runs for an instance.

        Args:
            instance_pair: A (set_name, instance_name) pair.
        """
        # We assume each objective has the same index for Instance/Runs
        return len(self.loc[(self.objective_names[0],) + instance_pair].index)

    # Calculables

    def mean(
        self: PerformanceDataFrame,
        objective: str = None,
        solver: str = None,
        instance_pair: tuple[str, str] = None,
    ) -> float:
        """Return the mean value of a slice of the dataframe.

        The slice is narrowed by each provided argument; arguments left as None
        are not filtered on.

        Args:
            objective: Objective to compute the mean over. If None, it is resolved
                via verify_objective (the sole objective for single objective data).
            solver: Solver name to restrict the slice to. None includes all solvers.
            instance_pair: A (set_name, instance_name) pair, or None for all instances.

        Returns:
            The mean of all values in the selected slice.
        """
        objective = self.verify_objective(objective)
        subset = self.xs(objective, level=PerformanceDataFrame.index_objective)
        if solver is not None:
            subset = subset.xs(solver, axis=1, drop_level=False)
        if instance_pair is not None:
            # instance_pair is a 2-level key spanning the InstanceSet and Instance row
            # levels, so narrow each level in turn: first on the set name, then on the
            # instance name. drop_level=False keeps the remaining MultiIndex levels
            # intact so the slice still aligns for the .mean() below.
            set_name, inst = instance_pair
            subset = subset.xs(
                set_name,
                axis=0,
                level=PerformanceDataFrame.index_instance_set,
                drop_level=False,
            )
            subset = subset.xs(
                inst,
                axis=0,
                level=PerformanceDataFrame.index_instance,
                drop_level=False,
            )
        value = subset.astype(float).mean()
        if isinstance(value, pd.Series):
            return value.mean()
        return value

    def remaining_jobs(
        self: PerformanceDataFrame, rerun: bool = False
    ) -> list[tuple[str, str, tuple[str, str], int]]:
        """Return a list of performance computation jobs there are to be done.

        Get a list of jobs to run from the performance data.
        If rerun is False (default), get only the tuples that don't have a
        value, else (True) get all the tuples.

        Args:
            rerun: Boolean indicating if we want to rerun all jobs

        Returns:
            A tuple of (solver, config, (set_name, instance_name), run) combinations
        """
        # Drop the seed as we are looking for missing objective values, not seeds.
        df = self.drop(
            PerformanceDataFrame.column_seed,
            axis=1,
            level=PerformanceDataFrame.column_meta,
        )
        df = df.droplevel(PerformanceDataFrame.column_meta, axis=1)

        # Each job is identified by (instance_set, instance_name, run, solver, config),
        # independent of objective. Collapse objective level to avoid duplicate generation.
        if rerun:
            job_index = df.index.droplevel(PerformanceDataFrame.index_objective).unique()
            return [
                (solver, config, (set_name, instance_name), run)
                for (solver, config), (
                    set_name,
                    instance_name,
                    run,
                ) in itertools.product(df.columns, job_index)
            ]

        # Compute a per-job missingness mask:
        # True means at least one objective value is still missing.
        missing_jobs = (
            df.isna()
            .groupby(
                level=[
                    PerformanceDataFrame.index_instance_set,
                    PerformanceDataFrame.index_instance,
                    PerformanceDataFrame.index_run,
                ],
                sort=False,
            )
            .any()
        )
        # Stack the solver and configuration levels to get a MultiIndex of
        # (instance_set, instance_name, run, solver, config) with boolean missingness.
        stacked_missing = missing_jobs.stack(
            [
                PerformanceDataFrame.column_solver,
                PerformanceDataFrame.column_configuration,
            ],
            future_stack=True,
        )

        # Add jobs only when value is True.
        result = []
        for (
            set_name,
            instance_name,
            run,
            solver,
            config,
        ), is_missing in stacked_missing.items():
            if not bool(is_missing):
                continue
            # NOTE: Keep historical behavior of skipping invalid run identifiers.
            if pd.isna(run):
                continue
            # NOTE: Force Run to be int, as it can be float on accident.
            if isinstance(run, (int, float, np.integer, np.floating)):
                run = int(run)
            result.append((solver, config, (set_name, instance_name), run))
        return result

    def configuration_performance(
        self: PerformanceDataFrame,
        solver: str,
        configuration: str | list[str] = None,
        objective: str | SparkleObjective = None,
        instance_pairs: list[tuple[str, str]] = None,
        per_instance: bool = False,
    ) -> tuple[str, float]:
        """Return the (best) configuration performance for objective over the instances.

        Args:
            solver: The solver for which we determine evaluate the configuration
            configuration: The configuration (id) to evaluate
            objective: The objective for which we calculate find the best value
            instance_pairs: The (set_name, instance_name) pairs to evaluate
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

        if instance_pairs:  # Filter instances
            pair_idx = pd.MultiIndex.from_tuples(instance_pairs)
            mask = subdf.index.droplevel(PerformanceDataFrame.index_run).isin(pair_idx)
            subdf = subdf[mask]
        if configuration:  # Filter configuration
            if not isinstance(configuration, list):
                configuration = [configuration]
            subdf = subdf.filter(configuration, axis=1)
        # Aggregate the runs (by Instance level name)
        subdf = subdf.groupby(
            [
                PerformanceDataFrame.index_instance_set,
                PerformanceDataFrame.index_instance,
            ]
        ).agg(func=objective.run_aggregator.__name__)
        # Aggregate the instances
        sub_series = subdf.agg(func=objective.instance_aggregator.__name__)
        sub_series = sub_series.dropna()
        if sub_series.empty:  # If all values are NaN, raise an error
            raise ValueError(
                f"No valid performance measurements for solver '{solver}' (Configuration: '{configuration}') "
                f"and objective '{objective.name}'."
            )
        # Select the best configuration
        best_conf = sub_series.idxmin() if objective.minimise else sub_series.idxmax()
        if per_instance:  # Return a list of instance results
            return best_conf, subdf[best_conf].to_list()
        return best_conf, sub_series[best_conf]

    def best_configuration(
        self: PerformanceDataFrame,
        solver: str,
        objective: SparkleObjective = None,
        instance_pairs: list[tuple[str, str]] = None,
    ) -> tuple[str, float]:
        """Return the best configuration for the given objective over the instances.

        Args:
            solver: The solver for which we determine the best configuration
            objective: The objective for which we calculate the best configuration
            instance_pairs: The (set_name, instance_name) pairs to evaluate

        Returns:
            The best configuration id and its aggregated performance.
        """
        return self.configuration_performance(solver, None, objective, instance_pairs)

    def best_instance_performance(
        self: PerformanceDataFrame,
        objective: str | SparkleObjective = None,
        instance_pairs: list[tuple[str, str]] = None,
        run_id: int = None,
        exclude_solvers: list[(str, str)] = None,
    ) -> pd.Series:
        """Return the best performance for each instance in the portfolio.

        Args:
            objective: The objective for which we calculate the best performance
            instance_pairs: The (set_name, instance_name) pairs to evaluate
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
        subdf = subdf.xs(
            objective.name, level=PerformanceDataFrame.index_objective
        )  # Drop objective -> (InstanceSet, Instance, Run)
        if exclude_solvers is not None:
            subdf = subdf.drop(exclude_solvers, axis=1)
        if instance_pairs is not None:
            # subdf is (InstanceSet, Instance, Run) here. A plain .loc with 2-tuples would
            # misalign against the 3-level index. Mask on the (InstanceSet, Instance) pair
            # with Run dropped, mirroring configuration_performance's filter. An empty pair
            # list selects nothing (from_tuples([]) cannot infer levels, so short-circuit).
            if len(instance_pairs) == 0:
                subdf = subdf.iloc[:0]
            else:
                pair_idx = pd.MultiIndex.from_tuples(instance_pairs)
                mask = subdf.index.droplevel(PerformanceDataFrame.index_run).isin(
                    pair_idx
                )
                subdf = subdf[mask]
        if run_id is not None:
            run_id = self.verify_run_id(run_id)
            subdf = subdf.xs(run_id, level=PerformanceDataFrame.index_run)
        else:
            # Drop the run level
            subdf = subdf.droplevel(PerformanceDataFrame.index_run)
        # Ensure the objective is numeric
        subdf = subdf.astype(float)
        series = subdf.min(axis=1) if objective.minimise else subdf.max(axis=1)
        # Ensure we always return the best for each run
        series = series.sort_values(ascending=objective.minimise)
        return series.groupby(series.index).first().astype(float)

    def best_performance(
        self: PerformanceDataFrame,
        exclude_solvers: list[(str, str)] = [],
        instance_pairs: list[tuple[str, str]] = None,
        objective: str | SparkleObjective = None,
    ) -> float:
        """Return the overall best performance of the portfolio.

        Args:
            exclude_solvers: List of (solver, config_id) to exclude in the calculation.
                Defaults to none.
            instance_pairs: The (set_name, instance_name) pairs to evaluate.
                If None, use all instances.
            objective: The objective for which we calculate the best performance

        Returns:
            The aggregated best performance of the portfolio over all instances.
        """
        objective = self.verify_objective(objective)
        if isinstance(objective, str):
            objective = resolve_objective(objective)
        instance_best = self.best_instance_performance(
            objective, instance_pairs=instance_pairs, exclude_solvers=exclude_solvers
        ).to_numpy(dtype=float)
        return objective.instance_aggregator(instance_best)

    def schedule_performance(
        self: PerformanceDataFrame,
        schedule: dict[tuple[str, str] : dict[str : (str, str, int)]],
        target_solver: str | tuple[str, str] = None,
        objective: str | SparkleObjective = None,
    ) -> float:
        """Return the performance of a selection schedule on the portfolio.

        Args:
            schedule: Compute the best performance according to a selection schedule.
                A schedule is a dictionary of (set_name, instance_name) pairs, with a
                schedule per instance, consisting of a triple of solver, config_id and
                maximum runtime.
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
        for ix, instance_pair in enumerate(schedule.keys()):
            for iy, (solver, config, max_runtime) in enumerate(schedule[instance_pair]):
                performance = float(
                    self.get_value(solver, instance_pair, config, objective.name)
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
                    instance_pair,
                    target_conf,
                    objective.name,
                )
        return performances

    def marginal_contribution(
        self: PerformanceDataFrame,
        objective: str | SparkleObjective = None,
        instance_pairs: list[tuple[str, str]] = None,
        sort: bool = False,
    ) -> list[float]:
        """Return the marginal contribution of the solver configuration on the instances.

        Args:
            objective: The objective for which we calculate the marginal contribution.
            instance_pairs: The (set_name, instance_name) pairs to evaluate
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
            objective=objective, instance_pairs=instance_pairs
        )
        for solver in self.solvers:
            for config_id in self.get_configurations(solver):
                # By calculating the best performance excluding this Solver,
                # we can determine its relative impact on the portfolio.
                missing_solver_config_best = self.best_performance(
                    exclude_solvers=[(solver, config_id)],
                    instance_pairs=instance_pairs,
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
        instance_pairs: list[tuple[str, str]] = None,
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
        # Reduce objective (4-level index -> 3-level: InstanceSet, Instance, Run)
        sub_df: pd.DataFrame = sub_df.loc(axis=0)[objective.name, :, :, :]
        # Drop Objective, Meta multi index
        sub_df = sub_df.droplevel(PerformanceDataFrame.index_objective).droplevel(
            PerformanceDataFrame.column_meta, axis=1
        )
        if instance_pairs is not None:  # Select instances
            # sub_df is (InstanceSet, Instance, Run) mask on the (InstanceSet, Instance)
            # pair with Run dropped rather than .loc with 2-tuples (which misaligns).
            if len(instance_pairs) == 0:
                sub_df = sub_df.iloc[:0]
            else:
                pair_idx = pd.MultiIndex.from_tuples(instance_pairs)
                mask = sub_df.index.droplevel(PerformanceDataFrame.index_run).isin(
                    pair_idx
                )
                sub_df = sub_df[mask]
        # Ensure data is numeric
        sub_df = sub_df.astype(float)
        # Aggregate runs (by Instance level name collapses InstanceSet and Instance into Instance)
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
            instance_pairs=self.instance_pairs,
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
