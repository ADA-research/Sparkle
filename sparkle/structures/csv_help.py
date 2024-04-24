#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper class for CSV manipulation."""
from __future__ import annotations
import pandas as pd
import fcntl
from pathlib import Path


class SparkleCSV:
    """Class to read, write, and update a CSV file."""

    def __init__(self: SparkleCSV, csv_filepath: str) -> None:
        """Initialise a CSV."""
        self.csv_filepath = csv_filepath
        self.dataframe = pd.read_csv(csv_filepath, index_col=0)

    @staticmethod
    def create_empty_csv(csv_filepath: str) -> None:
        """Create an empty CSV file."""
        if Path(csv_filepath).exists():
            print("Path", csv_filepath, "already exists!")
            print("Nothing changed!")
            return

        with Path(csv_filepath).open("w+") as fo:
            fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
            fo.write('""')

    def clean_csv(self: SparkleCSV) -> None:
        """Remove the value contents of the CSV, but not the row and column names."""
        for row in self.list_rows():
            for column in self.list_columns():
                self.set_value(row, column, None)
        self.save_csv()

    def save_csv(self: SparkleCSV, csv_filepath: str = None) -> None:
        """Write a CSV to the given path.

        Args:
            csv_filepath: String path to the csv file. Defaults to self.csv_filepath.
        """
        if csv_filepath is None:
            csv_filepath = self.csv_filepath
        with Path(csv_filepath).open("w+") as fo:
            fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
            self.dataframe.to_csv(csv_filepath)

    def get_value(self: SparkleCSV, row: str, column: str) -> str:
        """Get a value by name."""
        return self.dataframe.at[row, column]

    def set_value(self: SparkleCSV, row: str, column: str, value: str) -> None:
        """Set a value by name."""
        self.dataframe.at[row, column] = value

    def list_columns(self: SparkleCSV) -> None:
        """Return a list of columns."""
        return self.dataframe.columns.tolist()

    def add_column(self: SparkleCSV, column_name: str, value_list: list[str] = [])\
            -> None:
        """Add a column with the given values."""
        if column_name in self.list_columns():
            print("Column " + column_name + " already exists!")
            print("Nothing changed!")
            return
        if value_list == []:
            value_list = [None] * len(self.dataframe.index)
        self.dataframe[column_name] = value_list

    def delete_column(self: SparkleCSV, column_name: str) -> None:
        """Delete a specified column."""
        if column_name not in self.list_columns():
            print("Column " + column_name + " does not exist!")
            print("Nothing changed!")
            return
        self.dataframe = self.dataframe.drop(column_name, axis=1)

    def list_rows(self: SparkleCSV) -> list[str]:
        """Return a list of rows."""
        return self.dataframe.index.tolist()

    def add_row(self: SparkleCSV, row_name: str, value_list: list[str] = []) -> None:
        """Add a row with the given values."""
        if row_name in self.list_rows():
            print("Row", row_name, "already exists!")
            print("Nothing changed!")
            return

        if value_list == []:
            value_list = [None] * self.dataframe.columns.size
        if value_list == []:
            df = pd.DataFrame([], index=[row_name])
            self.dataframe = pd.concat([self.dataframe, df], axis=1)
        else:
            self.dataframe.loc[row_name] = value_list

    def delete_row(self: SparkleCSV, row_name: str) -> None:
        """Delete a specified row."""
        if row_name not in self.list_rows():
            print("Row " + row_name + " does not exist!")
            print("Nothing changed!")
            return
        self.dataframe = self.dataframe.drop(row_name, axis=0)
