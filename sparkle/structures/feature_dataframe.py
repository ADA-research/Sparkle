"""Module to manage feature data files and common operations on them."""
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
        """Initialise a FeatureDataFrame object.

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

    def add_instances(self: FeatureDataFrame,
                      instance: str | list[str],
                      values: list[float] = None) -> None:
        """Add one or more instances to the dataframe."""
        if values is None:
            values = FeatureDataFrame.missing_value
        self.dataframe[instance] = values

    def remove_extractor(self: FeatureDataFrame,
                         extractor: str) -> None:
        """Remove an extractor from the dataframe."""
        self.dataframe.drop(extractor, axis=0, level="Extractor", inplace=True)

    def remove_instances(self: FeatureDataFrame,
                         instances: str | list[str]) -> None:
        """Remove an instance from the dataframe."""
        self.dataframe.drop(instances, axis=1, inplace=True)

    def get_feature_groups(self: FeatureDataFrame,
                           extractor: str | list[str] = None) -> list[str]:
        """Retrieve the feature groups in the dataframe.

        Args:
            extractor: Optional. If extractor(s) are given,
                yields only feature groups of that extractor.

        Returns:
            A list of feature groups.
        """
        indices = self.dataframe.index
        if extractor is not None:
            if isinstance(extractor, str):
                extractor = [extractor]
            indices = indices[indices.isin(extractor, level=2)]
        return indices.get_level_values(level=0).unique().to_list()

    def get_value(self: FeatureDataFrame,
                  instance: str,
                  extractor: str,
                  feature_group: str,
                  feature_name: str) -> None:
        """Return a value in the dataframe."""
        return self.dataframe.loc[(feature_group, feature_name, extractor), instance]

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
            for extractor in self.extractors:
                extractor_features = self.dataframe.xs(extractor, level=2,
                                                       drop_level=False)
                if extractor_features.loc[:, instance].isnull().all():
                    return True
        return False

    def remaining_jobs(self: FeatureDataFrame) -> list[tuple[str, str, str]]:
        """Determines needed feature computations per instance/extractor/group.

        Returns:
            list: A list of tuples representing (Extractor, Instance, Feature Group).
                that needs to be computed.
        """
        remaining_jobs = []
        for extractor in self.extractors:
            for group in self.get_feature_groups(extractor):
                subset = self.dataframe.xs((group, extractor), level=(0, 2))
                for instance in self.dataframe.columns:
                    if subset.loc[:, instance].isnull().all():
                        remaining_jobs.append((instance, extractor, group))
        return remaining_jobs

    def get_instance(self: FeatureDataFrame, instance: str) -> list[float]:
        """Return the feature vector of an instance."""
        return self.dataframe[instance].tolist()

    def impute_missing_values(self: FeatureDataFrame) -> None:
        """Imputes all NaN values by taking the average feature value."""
        self.dataframe = self.dataframe.T.fillna(self.dataframe.mean(axis=1)).T

    def has_missing_value(self: FeatureDataFrame) -> bool:
        """Return whether there are missing values in the feature data."""
        return self.dataframe.isnull().any().any()

    def reset_dataframe(self: FeatureDataFrame) -> bool:
        """Resets all values to FeatureDataFrame.missing_value."""
        self.dataframe.loc[:, :] = FeatureDataFrame.missing_value

    def sort(self: FeatureDataFrame) -> None:
        """Sorts the DataFrame by Multi-Index for readability."""
        self.dataframe.sort_index(level=FeatureDataFrame.multi_dim_names)

    @property
    def instances(self: FeatureDataFrame) -> list[str]:
        """Return the instances in the dataframe."""
        return self.dataframe.columns

    @property
    def extractors(self: FeatureDataFrame) -> list[str]:
        """Returns all unique extractors in the DataFrame."""
        return self.dataframe.index.get_level_values("Extractor").unique().to_list()

    @property
    def num_features(self: FeatureDataFrame) -> int:
        """Return the number of features in the dataframe."""
        return self.dataframe.shape[0]

    @property
    def features(self: FeatureDataFrame) -> list[str]:
        """Return the features in the dataframe."""
        return self.dataframe.index.get_level_values("FeatureName").unique().to_list()

    def save_csv(self: FeatureDataFrame, csv_filepath: Path = None) -> None:
        """Write a CSV to the given path.

        Args:
            csv_filepath: String path to the csv file. Defaults to self.csv_filepath.
        """
        csv_filepath = self.csv_filepath if csv_filepath is None else csv_filepath
        self.dataframe.to_csv(csv_filepath)
