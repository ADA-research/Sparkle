"""Module to manage feature data files and common operations on them."""

from __future__ import annotations
import math
from pathlib import Path

import pandas as pd


class FeatureDataFrame(pd.DataFrame):
    """Class to manage feature data CSV files and common operations on them."""

    missing_value = math.nan
    extractor_dim = "Extractor"
    feature_group_dim = "FeatureGroup"
    feature_name_dim = "FeatureName"
    instance_set_index_dim = "InstanceSet"
    instance_index_dim = "Instance"
    multi_dim_index_names = [instance_set_index_dim, instance_index_dim]
    multi_dim_column_names = [extractor_dim, feature_group_dim, feature_name_dim]

    def __init__(
        self: FeatureDataFrame,
        csv_filepath: Path,
        instance_pairs: list[tuple[str, str]] = [],
        extractor_data: dict[str, list[tuple[str, str]]] = {},
    ) -> None:
        """Initialise a FeatureDataFrame object.

        Arguments:
            csv_filepath: The Path for the CSV storage. If it does not exist,
                a new DataFrame will be initialised and stored here.
            instance_pairs: The list of (set_name, instance_name) pairs to be added.
            extractor_data: A dictionary with extractor names as key, and a list of
                tuples ordered as [(feature_group, feature_name), ...] as value.
        """
        # Initialize a dataframe from an existing file
        if csv_filepath.exists():
            # Read the 2-level (InstanceSet, Instance) row index and 3-level
            # (Extractor, FeatureGroup, FeatureName) column header.
            temp_df = pd.read_csv(
                csv_filepath,
                header=[0, 1, 2],
                index_col=[0, 1],
                dtype={
                    FeatureDataFrame.extractor_dim: str,
                    FeatureDataFrame.feature_group_dim: str,
                    FeatureDataFrame.feature_name_dim: str,
                },
                on_bad_lines="skip",
                skip_blank_lines=True,
            )
            temp_df.index.names = FeatureDataFrame.multi_dim_index_names
            super().__init__(temp_df)
            self.csv_filepath = csv_filepath
        # Create a new dataframe
        else:
            # Unfold the extractor_data into lists
            if extractor_data:
                multi_column_lists = [
                    (extractor, group, feature_name)
                    for extractor in extractor_data
                    for group, feature_name in extractor_data[extractor]
                ]
            else:
                multi_column_lists = [
                    (
                        FeatureDataFrame.missing_value,
                        FeatureDataFrame.missing_value,
                        FeatureDataFrame.feature_name_dim,
                    )
                ]
            # Initialise new dataframe
            multi_columns = pd.MultiIndex.from_tuples(
                multi_column_lists, names=self.multi_dim_column_names
            )
            if instance_pairs:
                index = pd.MultiIndex.from_tuples(
                    instance_pairs, names=self.multi_dim_index_names
                )
            else:
                index = pd.MultiIndex.from_tuples([], names=self.multi_dim_index_names)
            super().__init__(
                data=self.missing_value,
                index=index,
                columns=multi_columns,
                dtype=float,
            )
            self.csv_filepath = csv_filepath
            self.save_csv()

        if self.index.duplicated().any():  # Drop all duplicates except for last
            self.reset_index(inplace=True)  # Reset index to columns
            idx_cols = self.columns[:2].tolist()  # Both InstanceSet and Instance cols
            self.drop_duplicates(
                subset=idx_cols, keep="last", inplace=True
            )  # filter duplicates from index columns
            self.set_index(idx_cols, inplace=True)  # Restore the MultiIndex (in-place)
            self.index.names = FeatureDataFrame.multi_dim_index_names

        # Sort the index to optimize lookup speed
        self.sort_index(axis=0, inplace=True)
        self.sort_index(axis=1, inplace=True)

    def add_extractor(
        self: FeatureDataFrame,
        extractor: str,
        extractor_features: list[tuple[str, str]],
        values: list[list[float]] = None,
    ) -> None:
        """Add an extractor and its feature names to the dataframe.

        Arguments:
            extractor: Name of the extractor
            extractor_features: Tuples of [FeatureGroup, FeatureName]
            values: Initial values of the Extractor per instance in the dataframe.
                Defaults to FeatureDataFrame.missing_value.
        """
        if extractor in self.extractors:
            print(
                f"WARNING: Tried adding already existing extractor {extractor} to "
                f"Feature DataFrame: {self.csv_filepath}"
            )
            return
        if values is None:
            values = [self.missing_value] * len(
                extractor_features
            )  # Single missing value for each feature
        extractor_dim = self.columns.get_level_values(FeatureDataFrame.extractor_dim)
        # Unfold to indices to lists
        for index, (feature_group, feature) in enumerate(extractor_features):
            self[(extractor, feature_group, feature)] = values[index]
        if self.num_extractors > 1:
            # Upon successfull adding of the extractor, remove the nan extractor
            if str(math.nan) in extractor_dim:
                self.drop(
                    str(math.nan),
                    axis=1,
                    level=FeatureDataFrame.extractor_dim,
                    inplace=True,
                )
            elif math.nan in extractor_dim:
                self.drop(
                    math.nan, axis=1, level=FeatureDataFrame.extractor_dim, inplace=True
                )

    def add_instances(
        self: FeatureDataFrame,
        instance_pairs: tuple[str, str] | list[tuple[str, str]],
        values: list[float] = None,
    ) -> None:
        """Add one or more instances to the dataframe.

        Args:
            instance_pairs: A (set_name, instance_name) pair or list of such pairs.
            values: Optional initial values for all features.
        """
        if isinstance(instance_pairs, tuple):
            instance_pairs = [instance_pairs]
        fill = values if values else FeatureDataFrame.missing_value
        row_values = fill if isinstance(fill, list) else [fill] * len(self.columns)
        for instance_pair in instance_pairs:
            self.loc[instance_pair, :] = row_values

    def remove_extractor(self: FeatureDataFrame, extractor: str) -> None:
        """Remove an extractor from the dataframe."""
        self.drop(extractor, axis=1, level=FeatureDataFrame.extractor_dim, inplace=True)
        # if self.num_extractors == 0:
        if self.num_extractors == 0:  # make sure we have atleast one 'extractor'
            self.add_extractor(
                str(FeatureDataFrame.missing_value),
                [(FeatureDataFrame.missing_value, FeatureDataFrame.feature_name_dim)],
            )

    def remove_instance_pairs(
        self: FeatureDataFrame,
        instance_pairs: tuple[str, str] | list[tuple[str, str]],
    ) -> None:
        """Remove one or more instances from the dataframe.

        Args:
            instance_pairs: A (set_name, instance_name) pair or list of such pairs.
        """
        self.drop(instance_pairs, axis=0, inplace=True)

    def get_feature_groups(
        self: FeatureDataFrame, extractor: str | list[str] = None
    ) -> list[str]:
        """Retrieve the feature groups in the dataframe.

        Args:
            extractor: Optional. If extractor(s) are given,
                yields only feature groups of that extractor.

        Returns:
            A list of feature groups.
        """
        columns = self.columns
        if extractor is not None:
            if isinstance(extractor, str):
                extractor = [extractor]
            columns = columns[columns.isin(extractor, level=0)]
        return columns.get_level_values(level=1).unique().to_list()

    def get_value(
        self: FeatureDataFrame,
        instance_pair: tuple[str, str],
        extractor: str,
        feature_group: str,
        feature_name: str,
    ) -> float:
        """Return a value in the dataframe.

        Args:
            instance_pair: A (set_name, instance_name) pair.
            extractor: Name of the extractor.
            feature_group: Name of the feature group.
            feature_name: Name of the feature.

        Returns:
            The value.
        """
        return self.loc[instance_pair, (extractor, feature_group, feature_name)]

    def set_value(
        self: FeatureDataFrame,
        instance_pair: tuple[str, str],
        extractor: str,
        feature_group: str,
        feature_name: str | list[str],
        value: float | list[float],
        append_write_csv: bool = False,
    ) -> None:
        """Set a value in the dataframe.

        Args:
            instance_pair: A (set_name, instance_name) pair.
            extractor: Name of the extractor.
            feature_group: Name of the feature group.
            feature_name: Name of the feature.
            value: The value to set.
            append_write_csv: CSV to be written to.
        """
        if isinstance(feature_name, list) and isinstance(value, list):
            if len(feature_name) != len(value):
                raise ValueError(
                    f"feature_name and values must be the same length ({len(feature_name)}, {len(value)})."
                )
        elif isinstance(feature_name, list) or isinstance(value, list):
            raise ValueError(
                f"feature_name parameter and value must be the same type ({type(feature_name)}, {type(value)})."
            )
        self.loc[instance_pair, (extractor, feature_group, feature_name)] = value
        if append_write_csv:
            writeable = self.loc[[instance_pair], :]  # Take line
            # Append the new rows to the dataframe csv file
            import os

            csv_string = writeable.to_csv(header=False)  # Convert to the csv lines
            for line in csv_string.splitlines():  # Should be only one line, but is safe now if we were to do multiple values
                fd = os.open(f"{self.csv_filepath}", os.O_WRONLY | os.O_APPEND)
                os.write(fd, f"{line}\n".encode("utf-8"))  # Encode to create buffer
                # Open and close for each line to minimise possibilities of conflict
                os.close(fd)

    def has_missing_vectors(self: FeatureDataFrame) -> bool:
        """Returns True if there are any Extractors still to be run on any instance."""
        for extractor in self.extractors:
            # True if any instance has ALL features null for this extractor
            if self[extractor].isnull().all(axis=1).any():
                return True
        return False

    def remaining_jobs(
        self: FeatureDataFrame,
        groupwise_computation: bool = True,
    ) -> list[tuple[tuple[str, str], str, str | None]]:
        """Return remaining feature-computation jobs.

        Args:
            groupwise_computation:
                If True, jobs are kept per feature group and returned as
                `((set_name, instance_name), extractor_name, feature_group)` tuples.
                If False, feature groups are collapsed and the return value uses
                `None` for the feature-group position:
                `((set_name, instance_name), extractor_name, None)`.

        Returns:
            A flat list of remaining jobs, always in the shape
            `((set_name, instance_name), extractor_name, feature_group | None)`.
        """
        extractor_values = self.extractors

        # DataFrame restricted to real extractor columns only.
        target_df = self.loc[:, extractor_values]

        if target_df.empty:
            return []

        # Build one boolean per (instance, extractor, feature_group):
        # 1) target_df.isnull(): mark missing cells as True.
        # 2) .T: move feature columns to the index for grouping by MultiIndex levels.
        # 3) .groupby(level=[Extractor, FeatureGroup]).all():
        #    collapse all feature names in the same group.
        #    Result is True only if the *entire* group is missing for an instance.
        # 4) final .T: restore instances on rows.
        # So missing_groups.loc[instance, (extractor, feature_group)] == True
        # means this job still has to be computed.
        missing_groups = (
            target_df.isnull()
            .T.groupby(
                level=[
                    FeatureDataFrame.extractor_dim,
                    FeatureDataFrame.feature_group_dim,
                ]
            )
            .all()
            .T
        )
        if groupwise_computation:
            # Convert the 2D table to a Series with MultiIndex:
            # (set_name, instance_name, extractor, feature_group) -> bool.
            stacked_missing = missing_groups.stack(
                [FeatureDataFrame.extractor_dim, FeatureDataFrame.feature_group_dim],
                future_stack=True,
            )
            # Keep only True entries and repack as ((set_name, instance_name), extractor, feature_group).
            return [
                ((set_name, instance_name), extractor, feature_group)
                for set_name, instance_name, extractor, feature_group in stacked_missing[
                    stacked_missing
                ].index.to_list()
            ]

        # Collapse feature groups into one boolean per (instance, extractor):
        missing_values_with_no_group = (
            missing_groups.T.groupby(level=[FeatureDataFrame.extractor_dim]).all().T
        )
        # Convert collapsed table to Series:
        # (set_name, instance_name, extractor) -> bool.
        stacked_missing = missing_values_with_no_group.stack(
            [FeatureDataFrame.extractor_dim],
            future_stack=True,
        )

        # Keep only True entries and expand to 3-tuple with feature-group slot = None.
        return [
            ((set_name, instance_name), extractor, None)
            for set_name, instance_name, extractor in stacked_missing[
                stacked_missing
            ].index.to_list()
        ]

    def get_instance(
        self: FeatureDataFrame,
        instance_pair: tuple[str, str],
        as_dataframe: bool = False,
    ) -> list[float]:
        """Return the feature vector of an instance pair.

        Args:
            instance_pair: A (set_name, instance_name) pair.
            as_dataframe: True if instances should be returned as df.

        Returns:
            The feature vector of an instance pair.
        """
        if as_dataframe:
            return self.loc[[instance_pair]]
        return self.loc[instance_pair].tolist()

    def impute_missing_values(self: FeatureDataFrame) -> None:
        """Imputes all NaN values by taking the average feature value."""
        # imputed_df = self.T.fillna(self.mean(axis=1)).T
        imputed_df = self.fillna(self.mean(axis=0))
        self[:] = imputed_df.values

    def has_missing_value(self: FeatureDataFrame) -> bool:
        """Return whether there are missing values in the feature data."""
        return self.isnull().any().any()

    def reset_dataframe(self: FeatureDataFrame) -> bool:
        """Resets all values to FeatureDataFrame.missing_value."""
        self.loc[:, (slice(None), slice(None), slice(None))] = (
            FeatureDataFrame.missing_value
        )

    def sort(self: FeatureDataFrame) -> None:
        """Sorts the DataFrame by Multi-Index for readability."""
        self.sort_index(inplace=True)

    @property
    def instance_pairs(self: FeatureDataFrame) -> list[tuple[str, str]]:
        """Return the (set_name, instance_name) pairs in the dataframe."""
        return self.index.tolist()

    @property
    def extractors(self: FeatureDataFrame) -> list[str]:
        """Returns all unique extractors in the DataFrame."""
        return [
            x
            for x in self.columns.get_level_values(
                FeatureDataFrame.extractor_dim
            ).unique()
            if str(x) != str(FeatureDataFrame.missing_value)
        ]

    @property
    def num_features(self: FeatureDataFrame) -> int:
        """Return the number of features in the dataframe."""
        # return self.shape[0]
        return self.shape[1]

    @property
    def num_instances(self: FeatureDataFrame) -> int:
        """Return the number of instances in the dataframe."""
        # return self.shape[1]
        return self.shape[0]

    @property
    def num_extractors(self: FeatureDataFrame) -> int:
        """Return the number of extractors in the dataframe."""
        return self.columns.get_level_values("Extractor").unique().size

    @property
    def features(self: FeatureDataFrame) -> list[str]:
        """Return the features in the dataframe."""
        # return self.index.get_level_values("FeatureName").unique().to_list()
        return self.columns.get_level_values("FeatureName").unique().to_list()

    def save_csv(self: FeatureDataFrame, csv_filepath: Path = None) -> None:
        """Write a CSV to the given path.

        Args:
            csv_filepath: String path to the csv file. Defaults to self.csv_filepath.
        """
        csv_filepath = self.csv_filepath if csv_filepath is None else csv_filepath
        if csv_filepath is None:
            raise ValueError("Cannot save DataFrame: no `csv_filepath` was provided.")
        self.sort_index(inplace=True)
        self.to_csv(csv_filepath)
