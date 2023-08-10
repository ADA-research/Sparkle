#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper class for CSV manipulation."""

import pandas as pd
import numpy as np
import fcntl
from pathlib import Path
from __future__ import annotations


class SparkleCSV:
    """Class to read, write, and update a CSV file."""

    empty_column_name = '""'

    @staticmethod
    def create_empty_csv(csv_filepath: str)  -> None:
        """Create an empty CSV file."""
        if Path(csv_filepath).exists():
            print("Path", csv_filepath, "already exists!")
            print("Nothing changed!")
            return
        fo = Path(csv_filepath).open("w+")
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        fo.write(SparkleCSV.empty_column_name)
        fo.close()
        return

    def __init__(self: SparkleCSV, csv_filepath: str)  -> None:
        """Initialise a CSV."""
        self.csv_filepath = csv_filepath
        self.dataframe = pd.read_csv(csv_filepath, index_col=0)
        return

    def clean_csv(self: SparkleCSV)  -> None:
        """Remove the value contents of the CSV, but not the row and column names."""
        for row in self.list_rows():
            for column in self.list_columns():
                self.set_value(row, column, None)
        self.update_csv()
        return

    def is_empty(self: SparkleCSV) -> bool:
        """Return whether the CSV is empty or not."""
        ret = False
        if (self.dataframe.empty and self.get_column_size() == 0
           and self.get_row_size() == 0):
            ret = True
        return ret

    def update_csv(self: SparkleCSV) -> None:
        """Update a CSV file."""
        fo = Path(self.csv_filepath).open("w+")
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        self.dataframe.to_csv(self.csv_filepath)
        fo.close()
        return

    def save_csv(self: SparkleCSV, csv_filepath: str)  -> None:
        """Write a CSV to the given path."""
        fo = Path(csv_filepath).open("w+")
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        self.dataframe.to_csv(csv_filepath)
        fo.close()

        return

    def get_value_index(self: SparkleCSV, row_index: int, column_index: int)  -> str:
        """Return a value by index."""
        ret = self.dataframe.at[self.dataframe.index[row_index],
                                self.dataframe.columns[column_index]]
        return ret

    def set_value_index(self: SparkleCSV, row_index: int, column_index: int, value: str)  -> None:
        """Set a value by index."""
        self.dataframe.at[self.dataframe.index[row_index],
                          self.dataframe.columns[column_index]] = value
        return

    def get_value(self: SparkleCSV, row: str, column: str)  -> str:
        """Get a value by name."""
        ret = self.dataframe.at[row, column]
        return ret

    def set_value(self: SparkleCSV, row: str, column: str, value: str)  -> None:
        """Set a value by name."""
        self.dataframe.at[row, column] = value
        return

    def list_columns(self: SparkleCSV) -> None:
        """Return a list of columns."""
        ret = self.dataframe.columns.tolist()
        return ret

    def get_column_name(self: SparkleCSV, index: int)  -> str:
        """Return the name of a column for a given index."""
        ret = self.dataframe.columns.tolist()[index]
        return ret

    def rename_column(self: SparkleCSV, ori_column_name: str, mod_column_name: str)  -> None:
        """Change the name of a column."""
        if ori_column_name not in self.list_columns():
            print("Column " + ori_column_name + " does not exist!")
            print("Nothing changed!")
            return
        self.dataframe.rename(columns={ori_column_name: mod_column_name}, inplace=True)
        return

    def get_column_size(self: SparkleCSV) -> int:
        """Return the size of a column."""
        return len(self.dataframe.columns.tolist())

    def add_column(self: SparkleCSV, column_name: str, value_list: list[str] = []) -> None:
        """Add a column with the given values."""
        if column_name in self.list_columns():
            print("Column " + column_name + " already exists!")
            print("Nothing changed!")
            return
        if value_list == []:
            value_list = [None] * self.get_row_size()
        self.dataframe[column_name] = value_list
        return

    def update_column(self: SparkleCSV, column_name: str, value_list: str) -> None:
        """Update a column with the given values."""
        self.dataframe[column_name] = value_list
        return

    def delete_column(self: SparkleCSV, column_name: str)  -> None:
        """Delete a specified column."""
        if column_name not in self.list_columns():
            print("Column " + column_name + " does not exist!")
            print("Nothing changed!")
            return
        self.dataframe = self.dataframe.drop(column_name, axis=1)
        return

    def dataframe_get_specific_column(self: SparkleCSV, column_name: str) -> pd.DataFrame:
        """Return a specified column as dataframe."""
        return self.dataframe[[column_name]]

    def dataframe_get_specific_column_isnull(self: SparkleCSV, column_name: str)  -> pd.DataFrame:
        """Return a dataframe indicating whether elements of a column are null."""
        return self.dataframe[[column_name]].isnull()

    def list_get_specific_column(self: SparkleCSV, column_name: str)  -> list[str]:
        """Return a specfied column as list."""
        mydf = self.dataframe_get_specific_column(column_name)
        mydf = mydf.T
        mylist = np.array(mydf).tolist()[0]
        return mylist

    def list_get_specific_column_isnull(self: SparkleCSV, column_name: str)  -> list[bool]:
        """Return a list[bool] indicating whether elements of a column are null."""
        mydf = self.dataframe_get_specific_column_isnull(column_name)
        mydf = mydf.T
        mylist = np.array(mydf).tolist()[0]
        return mylist

    def list_rows(self: SparkleCSV)  -> list[str]:
        """Return a list of rows."""
        ret = self.dataframe.index.tolist()
        return ret

    def get_row_name(self: SparkleCSV, index: int) -> str:
        """Return the name of a row."""
        ret = self.dataframe.index.tolist()[index]
        return ret

    def rename_row(self: SparkleCSV, ori_row_name: str, mod_row_name: str)  -> None:
        """Change the name of a row."""
        if ori_row_name not in self.list_rows():
            print("Row " + ori_row_name + " does not exist!")
            print("Nothing changed!")
            return
        self.dataframe.rename(index={ori_row_name: mod_row_name}, inplace=True)
        return

    def get_row_size(self: SparkleCSV) -> int:
        """Return the size of a row."""
        return len(self.dataframe.index.tolist())

    def add_row(self: SparkleCSV, row_name: str, value_list: list[str] = [])  -> None:
        """Add a row with the given values."""
        if row_name in self.list_rows():
            print("Row", row_name, "already exists!")
            print("Nothing changed!")
            return

        if value_list == []:
            value_list = [None] * self.get_column_size()
        if value_list == []:
            df = pd.DataFrame([], index=[row_name])
            self.dataframe = pd.concat([self.dataframe, df], axis=1)
        else:
            self.dataframe.loc[row_name] = value_list

        return

    def update_row(self: SparkleCSV, row_name: str, value_list: str)  -> None:
        """Update the value of a given row."""
        self.dataframe.loc[row_name] = value_list

        return

    def delete_row(self: SparkleCSV, row_name: str)   -> None:
        """Delete a specified row."""
        if row_name not in self.list_rows():
            print("Row " + row_name + " does not exist!")
            print("Nothing changed!")
            return
        self.dataframe = self.dataframe.drop(row_name, axis=0)

        return

    def dataframe_get_specific_row(self: SparkleCSV, row_name: str)   -> pd.Series:
        """Return a row with a given name."""
        return self.dataframe.loc[[row_name]]

    def dataframe_get_specific_row_isnull(self: SparkleCSV, row_name: str)  -> bool:
        """Return whether a given row is null or not."""
        return self.dataframe.loc[[row_name]].isnull()

    def list_get_specific_row(self: SparkleCSV, row_name: str)  -> list[str]:
        """Return a row with a given name as list."""
        mydf = self.dataframe_get_specific_row(row_name)
        mylist = np.array(mydf).tolist()[0]

        return mylist

    def list_get_specific_row_isnull(self: SparkleCSV, row_name: str)  -> list[str]:
        """Return whether a given row is null or not as a list."""
        mydf = self.dataframe_get_specific_row_isnull(row_name)
        mylist = np.array(mydf).tolist()[0]

        return mylist
