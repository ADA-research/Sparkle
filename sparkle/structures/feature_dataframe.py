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
            extractors: A dictionary with extractor names as key, and a list of tuples
                ordered as [(feature_group, feature_name), ...] as value.
        """
        self.csv_filepath = csv_filepath
        #Create a multi-index dataframe
        #Columns are the Instances
        #Indices are (FeatureName, Extractor)
        #Because every instance wants every combination of Extractor/featurename to have a result, but it doesn't have to have one
        #But Extractors may share features, therefore, first group by FeatureName so that it could then have multiple results for the same feature/instance combination by Extractor key.
        # Each feature belongs to a feature group which is for example recognised by autofolio
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
        #Format sanity checks? value size
        if values is None:
            values = [FeatureDataFrame.missing_value
                      for _ in range(len(extractor_features))]
        # Unfold to indices to lists
        for index, pair in enumerate(extractor_features):
            feature_group, feature_name = pair
            self.dataframe.loc[(feature_group, feature_name, extractor), :] = values[index]

    def add_instance(self: FeatureDataFrame,
                     instance: str,
                     values: list[float] = None) -> None:
        """Add an instance to the dataframe."""
        #Sanity check? features need to be the correct size
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

    def get_nan_locs(self: FeatureDataFrame) -> tuple[list[tuple[str]], list[str]]:
        """Retrieves the index and column combinations that have NaN values."""
        subdataframe = self.dataframe[self.dataframe.isnull()]
        return subdataframe.index.to_list(), subdataframe.columns.to_list()

    def get_num_features(self: FeatureDataFrame, extractor: str) -> int:
        """Returns the number of features for an extractor."""
        #TODO
        return

    def set_value(self: FeatureDataFrame,
                  instance: str,
                  extractor: str,
                  feature_group: str,
                  feature_name: str,
                  value: float) -> None:
        """Set a value in the dataframe."""
        self.dataframe.loc[(feature_group, feature_name, extractor), instance] = value

    def remaining_feature_computation_job(self: FeatureDataFrame)\
            -> list[list[str, str]]:
        """Return a needed feature computations per instance/extractor combination.

        Returns:
            A list of feature computation jobs. Each job is a list containing a str row
            name and a str column name.
        """
        remaining_jobs = {}
        for instance in self.dataframe.columns:
            for extractor in self.get_extractors():
                subset = self.dataframe.xs(extractor, level=2, drop_level=False)
                if subset.loc[:, instance].isnull().all():
                    if instance not in remaining_jobs:
                        remaining_jobs[instance] = [extractor]
                    else:
                        remaining_jobs[instance].append(extractor)
        # For now we just return the feature extractors and instance combinations
        # With [[instance_name, extractor1, extractor2, ...]]
        return [[key, remaining_jobs[key]] for key in remaining_jobs.keys()]

    def get_instance(self: FeatureDataFrame, instance: str) -> list:
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
        self.dataframe[:,:] = FeatureDataFrame.missing_value

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
