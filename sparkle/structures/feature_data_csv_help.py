#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module to manage feature data CSV files and common operation son them."""
from __future__ import annotations
import sys
import numpy as np
import pandas as pd
import math
from pathlib import Path


class FeatureDataFrame:
    """Class to manage feature data CSV files and common operations on them."""
    missing_value = math.nan

    def __init__(self: FeatureDataFrame,
                 csv_filepath: Path,
                 extractors: list[str],
                 instances: list[str],
                 extractor_features: dict[str, list[str]]
                 ) -> None:
        """Initialise a SparkleFeatureDataCSV object."""
        self.csv_filepath = csv_filepath
        #Create a multi-index dataframe
        #Columns are the Instances
        #Indices are (FeatureName, Extractor)
        #Because every instance wants every combination of Extractor/featurename to have a result, but it doesn't have to have one
        #But Extractors may share features, therefore, first group by FeatureName so that it could then have multiple results for the same feature/instance combination by Extractor key.
        #Maybe we also need a FeatureGroup?
        self.multi_dim_names = ["FeatureName", "Extractor"]
        
        if self.csv_filepath.exists():
            # Read from file
            self.dataframe = pd.read_csv(self.csv_filepath)
            return
        # The feature names are possibly shared over multiple extractors
        self.feature_names = set([feature for extractor in extractor_features
                                  for feature in extractor_features[extractor]])
        
        # Initialise new dataframe
        midx = pd.MultiIndex.from_product(
            [self.feature_names, extractors],
            names=self.multi_dim_names)
        self.dataframe = pd.DataFrame(FeatureDataFrame.missing_value,
                                      index=midx,
                                      columns=instances)
        self.save_csv()

    def add_extractor(self: FeatureDataFrame,
                      extractor: str,
                      extractor_features: list[str]) -> None:
        """Add an extractor and its feature names to the dataframe."""
        return

    def add_instance(self: FeatureDataFrame,
                     instance: str,
                     features: list[float] = None) -> None:
        """Add an instance to the dataframe."""
        if features is None:
            features = FeatureDataFrame.missing_value
        self.dataframe[instance] = features

    def remove_extractor(self: FeatureDataFrame,
                         extractor: str) -> None:
        """Remove an extractor from the dataframe."""
        return

    def remove_instance(self: FeatureDataFrame,
                        instance: str) -> None:
        """Remove an instance from the dataframe."""
        self.dataframe.drop(instance, axis=1, inplace=True)

    def save_csv(self: FeatureDataFrame, csv_filepath: Path = None) -> None:
        """Write a CSV to the given path.

        Args:
            csv_filepath: String path to the csv file. Defaults to self.csv_filepath.
        """
        csv_filepath = self.csv_filepath if csv_filepath is None else csv_filepath
        self.dataframe.to_csv(csv_filepath)

    def remaining_feature_computation_job(self: FeatureDataFrame)\
            -> list[list[str, str]]:
        """Return a list of needed feature computations per instance and solver.

        Returns:
            A list of feature computation jobs. Each job is a list containing a str row
            name and a str column name.
        """
        list_remaining_feature_computation_job = []
        bool_array_isnull = self.dataframe.isnull()
        for row_name in self.list_rows():
            current_extractor_list = []

            for column_name in self.list_columns():
                flag_value_is_null = bool_array_isnull.at[row_name, column_name]

                if (type(flag_value_is_null) is not np.bool_
                        and len(flag_value_is_null) > 1):
                    print("ERROR: Duplicate feature computation job.")
                    sys.exit(-1)

                if flag_value_is_null:
                    #This no longer works due to special string removal
                    extractor_path = self.get_extractor_path_from_feature(column_name)

                    if extractor_path not in current_extractor_list:
                        current_extractor_list.append(extractor_path)

            list_item = [row_name, current_extractor_list]
            list_remaining_feature_computation_job.append(list_item)

        return list_remaining_feature_computation_job

    def get_extractor_path_from_feature(self: FeatureDataFrame,
                                        given_column_name: str) -> str:
        """Return the path to the feature extractor for a given feature."""
        #This one actually uses the special str, lets rework
        sparkle_special_string = FeatureDataFrame.sparkle_special_string
        index = given_column_name.find(sparkle_special_string)
        length = len(sparkle_special_string)
        extractor_name = given_column_name[index + length:]
        extractor_path = "Extractors/" + extractor_name

        return extractor_path

    def get_bool_in_rows(self: FeatureDataFrame, given_row_name: str) -> bool:
        """Return whether a row with a given name exists."""
        return given_row_name in self.list_rows()

    def get_bool_in_columns(self: FeatureDataFrame, given_column_name: str) -> bool:
        """Return whether a column with a given name exists."""
        return given_column_name in self.list_columns()

    #Only called in compute_feature.py (core)
    def combine(self: FeatureDataFrame, second_sfdcsv: FeatureDataFrame)\
            -> None:
        """Combine this CSV with a given CSV."""
        list_columns_second_sfdcsv = second_sfdcsv.list_columns()
        list_rows_second_sfdcsv = second_sfdcsv.list_rows()

        len_list_columns_second_sfdcsv = len(list_columns_second_sfdcsv)
        len_list_rows_second_sfdcsv = len(list_rows_second_sfdcsv)

        for i in range(len_list_rows_second_sfdcsv):
            row_name_second_sfdcsv = str(second_sfdcsv.dataframe.index[i])
            bool_in_rows = self.get_bool_in_rows(row_name_second_sfdcsv)

            for j in range(len_list_columns_second_sfdcsv):
                column_name_second_sfdcsv = second_sfdcsv.dataframe.columns[j]
                bool_in_columns = self.get_bool_in_columns(column_name_second_sfdcsv)
                value = second_sfdcsv.dataframe.iloc[i, j]

                if bool_in_rows:
                    if bool_in_columns:
                        self.set_value(str(row_name_second_sfdcsv),
                                       column_name_second_sfdcsv,
                                       value)
                    else:
                        self.add_column(column_name_second_sfdcsv)
                        self.set_value(str(row_name_second_sfdcsv),
                                       column_name_second_sfdcsv,
                                       value)
                else:
                    if bool_in_columns:
                        self.add_row(row_name_second_sfdcsv)
                        self.set_value(str(row_name_second_sfdcsv),
                                       column_name_second_sfdcsv,
                                       value)
                    else:
                        self.add_row(row_name_second_sfdcsv)
                        self.add_column(column_name_second_sfdcsv)
                        self.set_value(str(row_name_second_sfdcsv),
                                       column_name_second_sfdcsv,
                                       value)

        return

    #Only called in compute_marginal_contribution_help.get_list_predict_schedule
    def get_feature_vector_string(self: FeatureDataFrame, instance: int) -> str:
        """Return the feature vector of an instance as str."""
        feature_vector_string = ""
        row = instance

        for column in self.list_columns():
            feature_value = self.get_value(row, column)
            feature_vector_string = feature_vector_string + str(feature_value) + " "

        return feature_vector_string.strip()

    #Only called in impute_missing_value_of_all_columns
    def impute_missing_value_of_this_column(self: FeatureDataFrame,
                                            column_name: str) -> None:
        """Impute missing data for a given column in this feature data CSV.

        Calculates the mean (if possible) of the existing values and assigns it to
        the indices that have a missing value.

        Args:
            column_name: column to be imputed
        """
        sum_value = 0
        num = 0

        list_missing_value_row_name = []
        for row_name in self.list_rows():
            tmp_value = self.get_value(row_name, column_name)
            if tmp_value == np.nan:
                # this is missing value
                missing_item = row_name
                list_missing_value_row_name.append(missing_item)
            else:
                # this is non-missing value
                num += 1
                sum_value += tmp_value

        if len(list_missing_value_row_name) == 0 or num == 0:
            return  # no missing value, or all missing values

        mean_value = sum_value / num
        for row_name in list_missing_value_row_name:
            self.set_value(row_name, column_name, mean_value)

    #Only called in construct_portfolio_selector_help.construct_sparkle_portfolio_selector
    def impute_missing_value_of_all_columns(self: FeatureDataFrame) -> None:
        """Impute missing data for all columns in this feature data CSV."""
        for column_name in self.list_columns():
            self.impute_missing_value_of_this_column(column_name)

        return

    #Only called in construct_portfolio_selector_help.construct_sparkle_portfolio_selector
    def bool_exists_missing_value(self: FeatureDataFrame) -> bool:
        """Return whether there are missing values in the feature data."""
        return self.dataframe.isnull().any().any()
