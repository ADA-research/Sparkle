#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module to manage feature data CSV files and common operation son them."""
from __future__ import annotations
import pandas as pd
import math
from pathlib import Path


class FeatureDataFrame:
    """Class to manage feature data CSV files and common operations on them."""
    missing_value = math.nan
    multi_dim_names = ["FeatureGroup", "FeatureName", "Extractor"]

    def __init__(self: FeatureDataFrame,
                 csv_filepath: Path,
                 instances: list[str] = [],
                 extractor_data: dict[str, list[tuple[str, str]]] = {}
                 ) -> None:
        """Initialise a SparkleFeatureDataCSV object.

        Arguments:
            csv_filepath: The Path for the CSV storage. If it does not exist,
                a new DataFrame will be initialised and stored here.
            instances: The list of instances (Columns) to be added to the DataFrame.
            extractor_data: A dictionary with extractor names as key, and a list of
                tuples ordered as [(feature_group, feature_name), ...] as value.
        """
        self.csv_filepath = csv_filepath
        if self.csv_filepath.exists():
            # Read from file
            self.dataframe = pd.read_csv(self.csv_filepath,
                                         index_col=FeatureDataFrame.multi_dim_names)
            return
        # Unfold the extractor_data into lists
        multi_index_lists = [[], [], []]
        for extractor in extractor_data:
            for group, feature_name in extractor_data[extractor]:
                multi_index_lists[0].append(group)
                multi_index_lists[1].append(feature_name)
                multi_index_lists[2].append(extractor)
        # Initialise new dataframe
        self.dataframe = pd.DataFrame(FeatureDataFrame.missing_value,
                                      index=multi_index_lists,
                                      columns=instances)
        self.dataframe.index.names = FeatureDataFrame.multi_dim_names
        self.save_csv()

    def add_extractor(self: FeatureDataFrame,
                      extractor: str,
                      extractor_features: list[tuple[str, str]],
                      values: list[list[float]] = None) -> None:
        """Add an extractor and its feature names to the dataframe.

        Arguments:
            extractor: Name of the extractor
            extractor_features: Tuples of [FeatureGroup, FeatureName]
            values: Initial values of the Extractor per instance in the dataframe.
                Defaults to FeatureDataFrame.missing_value.
        """
        if values is None:
            values = [FeatureDataFrame.missing_value
                      for _ in range(len(extractor_features))]
        # Unfold to indices to lists
        for index, pair in enumerate(extractor_features):
            feature_group, feature = pair
            self.dataframe.loc[(feature_group, feature, extractor), :] = values[index]

    def add_instance(self: FeatureDataFrame,
                     instance: str,
                     values: list[float] = None) -> None:
        """Add an instance to the dataframe."""
        if values is None:
            values = FeatureDataFrame.missing_value
        self.dataframe[instance] = values

    def remove_extractor(self: FeatureDataFrame,
                         extractor: str) -> None:
        """Remove an extractor from the dataframe."""
        self.dataframe.drop(extractor, axis=0, level="Extractor", inplace=True)

    def remove_instance(self: FeatureDataFrame,
                        instance: str) -> None:
        """Remove an instance from the dataframe."""
        self.dataframe.drop(instance, axis=1, inplace=True)

    def get_extractors(self: FeatureDataFrame) -> list[str]:
        """Returns all unique extractors in the DataFrame."""
        return self.dataframe.index.get_level_values("Extractor").unique().to_list()

    def set_value(self: FeatureDataFrame,
                  instance: str,
                  extractor: str,
                  feature_group: str,
                  feature_name: str,
                  value: float) -> None:
        """Set a value in the dataframe."""
        self.dataframe.loc[(feature_group, feature_name, extractor), instance] = value

    def has_missing_vectors(self: FeatureDataFrame) -> bool:
        """Returns True if there are any Extractors still to be run on any instance."""
        for instance in self.dataframe.columns:
            for extractor in self.get_extractors():
                extractor_features = self.dataframe.xs(extractor, level=2,
                                                       drop_level=False)
                if extractor_features.loc[:, instance].isnull().all():
                    return True
        return False

    def remaining_jobs(self: FeatureDataFrame) -> dict[str, list[str]]:
        """Determines needed feature computations per instance/extractor combination.

        Returns:
            dict: With instances as key, and a list of extractors as value that
                still need to compute their vectors for the instance.
        """
        remaining_jobs = {}
        for instance in self.dataframe.columns:
            # A job is remaining iff for one extractor each value on the instance is null
            for extractor in self.get_extractors():
                extractor_features = self.dataframe.xs(extractor, level=2,
                                                       drop_level=False)
                if extractor_features.loc[:, instance].isnull().all():
                    if instance not in remaining_jobs:
                        remaining_jobs[instance] = [extractor]
                    else:
                        remaining_jobs[instance].append(extractor)
        return remaining_jobs

    def get_instance(self: FeatureDataFrame, instance: str) -> list[float]:
        """Return the feature vector of an instance."""
        return self.dataframe[instance].tolist()

    def impute_missing_values(self: FeatureDataFrame) -> None:
        """Imputes all NaN values by taking the average feature value per feature."""
        for index in self.dataframe.index:
            if self.dataframe[index, :].isnull().any():
                # Compute the null indices as the average
                self.dataframe[self.dataframe[index, :].isnull()] =\
                    self.dataframe[index, :].mean()

    def has_missing_value(self: FeatureDataFrame) -> bool:
        """Return whether there are missing values in the feature data."""
        return self.dataframe.isnull().any().any()

    def reset_dataframe(self: FeatureDataFrame) -> bool:
        """Resets all values to FeatureDataFrame.missing_value."""
        self.dataframe.loc[:, :] = FeatureDataFrame.missing_value

    def sort(self: FeatureDataFrame) -> None:
        """Sorts the DataFrame by Multi-Index for readability."""
        self.dataframe.sort_index(level=FeatureDataFrame.multi_dim_names)

    def save_csv(self: FeatureDataFrame, csv_filepath: Path = None) -> None:
        """Write a CSV to the given path.

        Args:
            csv_filepath: String path to the csv file. Defaults to self.csv_filepath.
        """
        csv_filepath = self.csv_filepath if csv_filepath is None else csv_filepath
        self.dataframe.to_csv(csv_filepath)

    def to_autofolio(self: FeatureDataFrame) -> Path:
        """Port the data to a format acceptable for AutoFolio."""
        autofolio_df = self.dataframe.copy()
        # Reduce Multi-Index by unifying into one
        autofolio_df.index = autofolio_df.index.map("_".join)
        # Autofolio expects features as columns, rows as instances
        autofolio_df = autofolio_df.T
        path = self.csv_filepath.parent / f"autofolio_{self.csv_filepath.name}"
        autofolio_df.to_csv(path)
        return path
