#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module to manage feature data CSV files and common operation son them."""
from __future__ import annotations
import sys
import numpy as np
import math

from sparkle.structures import csv_help as scsv


class SparkleFeatureDataCSV(scsv.SparkleCSV):
    """Class to manage feature data CSV files and common operations on them."""
    sparkle_special_string = "__@@SPARKLE@@__"  # No idea who came up with this baloney
    missing_value = math.nan

    def __init__(self: SparkleFeatureDataCSV, csv_filepath: str,
                 extractor_list: list[str] = None) -> None:
        """Initialise a SparkleFeatureDataCSV object."""
        scsv.SparkleCSV.__init__(self, csv_filepath)
        if extractor_list is None:
            extractor_list = []
        self.extractor_list = extractor_list

    def get_list_recompute_feature_computation_job(self: SparkleFeatureDataCSV)  \
            -> list[list[str | list[str]]]:
        """Return a list of feature computations to re-do per instance and solver."""
        list_recompute_feature_computation_job = []
        list_row_name = self.list_rows()
        for row_name in list_row_name:
            list_item = [row_name, self.extractor_list]
            list_recompute_feature_computation_job.append(list_item)

        return list_recompute_feature_computation_job

    def get_list_remaining_feature_computation_job(self: SparkleFeatureDataCSV)\
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
                    extractor_path = self.get_extractor_path_from_feature(column_name)

                    if extractor_path not in current_extractor_list:
                        current_extractor_list.append(extractor_path)

            list_item = [row_name, current_extractor_list]
            list_remaining_feature_computation_job.append(list_item)

        return list_remaining_feature_computation_job

    def get_extractor_path_from_feature(self: SparkleFeatureDataCSV,
                                        given_column_name: str) -> str:
        """Return the path to the feature extractor for a given feature."""
        extractor_name = given_column_name.replace(
            SparkleFeatureDataCSV.sparkle_special_string, "")
        return f"Extractors/{extractor_name}"

    def get_bool_in_rows(self: SparkleFeatureDataCSV, given_row_name: str) -> bool:
        """Return whether a row with a given name exists."""
        return given_row_name in self.list_rows()

    def get_bool_in_columns(self: SparkleFeatureDataCSV, given_column_name: str) -> bool:
        """Return whether a column with a given name exists."""
        return given_column_name in self.list_columns()

    def combine(self: SparkleFeatureDataCSV, second_sfdcsv: SparkleFeatureDataCSV)\
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

    def get_feature_vector_string(self: SparkleFeatureDataCSV, instance: int) -> str:
        """Return the feature vector of an instance as str."""
        feature_vector_string = ""
        row = instance

        for column in self.list_columns():
            feature_value = self.get_value(row, column)
            feature_vector_string = feature_vector_string + str(feature_value) + " "

        return feature_vector_string.strip()

    def calc_mean_over_all_non_missing_values_of_this_column(self: SparkleFeatureDataCSV,
                                                             column_name: str) -> float:
        """Return the mean over all non-missing values for this column."""
        sum_value = 0
        num = 0

        for row_name in self.list_rows():
            tmp_value = self.get_value(row_name, column_name)
            if tmp_value != SparkleFeatureDataCSV.sparkle_missing_value:
                num += 1
                sum_value += tmp_value

        if num == 0:
            # all values are missing value
            return SparkleFeatureDataCSV.sparkle_missing_value

        return sum_value / num

    def generate_mean_value_feature_vector(self: SparkleFeatureDataCSV) -> list[float]:
        """Return a list with the mean over all non-missing values for all columns."""
        list_mean_value_feature_vector = []
        for column_name in self.list_columns():
            list_item = self.calc_mean_over_all_non_missing_values_of_this_column(
                column_name)
            list_mean_value_feature_vector.append(list_item)

        return list_mean_value_feature_vector

    def impute_missing_value_of_this_column(self: SparkleFeatureDataCSV,
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

    def impute_missing_value_of_all_columns(self: SparkleFeatureDataCSV) -> None:
        """Impute missing data for all columns in this feature data CSV."""
        for column_name in self.list_columns():
            self.impute_missing_value_of_this_column(column_name)

        return

    def bool_exists_missing_value(self: SparkleFeatureDataCSV) -> bool:
        """Return whether there are missing values in the feature data."""
        return self.dataframe.isnull().any().any()
