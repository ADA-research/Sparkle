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
    instances_index_dim = "Instances"
    multi_dim_column_names = [extractor_dim, feature_group_dim, feature_name_dim]

    def __init__(
        self: FeatureDataFrame,
        csv_filepath: Path,
        instances: list[str] = [],
        extractor_data: dict[str, list[tuple[str, str]]] = {},
    ) -> None:
        """Initialise a FeatureDataFrame object.

        Arguments:
            csv_filepath: The Path for the CSV storage. If it does not exist,
                a new DataFrame will be initialised and stored here.
            instances: The list of instances (Columns) to be added to the DataFrame.
            extractor_data: A dictionary with extractor names as key, and a list of
                tuples ordered as [(feature_group, feature_name), ...] as value.
        """
        # Initialize a dataframe from an existing file
        if csv_filepath.exists():
            # Read from file
            temp_df = pd.read_csv(
                csv_filepath,
                # index_col=FeatureDataFrame.multi_dim_names,
                header=[0, 1, 2],
                index_col=[0],
                dtype={
                    FeatureDataFrame.extractor_dim: str,
                    FeatureDataFrame.feature_group_dim: str,
                    FeatureDataFrame.feature_name_dim: str,
                    FeatureDataFrame.instances_index_dim: str,
                },
                on_bad_lines="skip",
                skip_blank_lines=True,
            )
            super().__init__(temp_df)
            self.index.name = FeatureDataFrame.instances_index_dim
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
            super().__init__(
                data=self.missing_value,
                index=instances,
                columns=multi_columns,
                dtype=float,
            )
            self.index.name = FeatureDataFrame.instances_index_dim
            self.csv_filepath = csv_filepath
            self.save_csv()

        if self.index.duplicated().any():  # Drop all duplicates except for last
            self.reset_index(inplace=True)  # Reset index to column
            self.drop_duplicates(
                subset=self.columns[0], keep="last", inplace=True
            )  # filter duplicates from index column
            self.set_index(
                self.columns[0], inplace=True
            )  # Restore the Instance Index (in-place)
            self.index.name = FeatureDataFrame.instances_index_dim

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
        self: FeatureDataFrame, instance: str | list[str], values: list[float] = None
    ) -> None:
        """Add one or more instances to the dataframe."""
        if values is None:
            values = FeatureDataFrame.missing_value
        if isinstance(instance, str):
            instance = [instance]
        # with warnings.catch_warnings():  # Block Pandas Performance Warnings
        #     warnings.simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
        for i in instance:
            self.loc[i] = values

    def remove_extractor(self: FeatureDataFrame, extractor: str) -> None:
        """Remove an extractor from the dataframe."""
        self.drop(extractor, axis=1, level=FeatureDataFrame.extractor_dim, inplace=True)
        # if self.num_extractors == 0:
        if self.num_extractors == 0:  # make sure we have atleast one 'extractor'
            self.add_extractor(
                str(FeatureDataFrame.missing_value),
                [(FeatureDataFrame.missing_value, FeatureDataFrame.feature_name_dim)],
            )

    def remove_instances(self: FeatureDataFrame, instances: str | list[str]) -> None:
        """Remove an instance from the dataframe."""
        # self.drop(instances, axis=1, inplace=True)
        self.drop(instances, axis=0, inplace=True)

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
        instance: str,
        extractor: str,
        feature_group: str,
        feature_name: str,
    ) -> float:
        """Return a value in the dataframe."""
        # return self.loc[(feature_group, feature_name, extractor), instance]
        return self.loc[instance, (extractor, feature_group, feature_name)]

    def set_value(
        self: FeatureDataFrame,
        instance: str,
        extractor: str,
        feature_group: str,
        feature_name: str | list[str],
        value: float | list[float],
        append_write_csv: bool = False,
    ) -> None:
        """Set a value in the dataframe."""
        if isinstance(feature_name, list) and isinstance(value, list):
            if len(feature_name) != len(value):
                raise ValueError(
                    f"feature_name and values must be the same length ({len(feature_name)}, {len(value)})."
                )
        elif isinstance(feature_name, list) or isinstance(value, list):
            raise ValueError(
                f"feature_name parameter and value must be the same type ({type(feature_name)}, {type(value)})."
            )
        # self.loc[(feature_group, feature_name, extractor), instance] = value
        self.loc[instance, (extractor, feature_group, feature_name)] = value
        if append_write_csv:
            writeable = self.loc[[instance], :]  # Take line
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
            if (
                self[extractor].isnull().all().all()
            ):  # First all for the column, second all for the feature groups
                return True
        return False

    def remaining_jobs(self: FeatureDataFrame) -> list[tuple[str, str, str]]:
        """Determines needed feature computations per instance/extractor/group.

        Returns:
            list: A list of tuples representing (Instance, Extractor, Feature Group).
                that needs to be computed.
        """
        remaining_jobs = []
        for extractor, group, _ in self.columns:
            if (
                extractor == str(FeatureDataFrame.missing_value)
                or extractor == FeatureDataFrame.missing_value
            ):
                continue
            for instance in self.index:
                if self.loc[instance, (extractor, group, slice(None))].isnull().all():
                    remaining_jobs.append((instance, extractor, group))
        return list(set(remaining_jobs))  # Filter duplicates

    def get_instance(
        self: FeatureDataFrame, instance: str, as_dataframe: bool = False
    ) -> list[float]:
        """Return the feature vector of an instance."""
        if as_dataframe:
            return self.loc[[instance]]
        return self.loc[instance].tolist()

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
    def instances(self: FeatureDataFrame) -> list[str]:
        """Return the instances in the dataframe."""
        return self.index

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
