#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''Helper class for CSV manipulation.'''

import os
import pandas as pd
import numpy as np
import fcntl


class SparkleCSV:
    '''Class to read, write, and update a CSV file.'''

    empty_column_name = '""'

    @staticmethod
    def create_empty_csv(csv_filepath):
        '''Create an empty CSV file.'''
        if os.path.exists(csv_filepath):
            print('Path', csv_filepath, 'already exists!')
            print('Nothing changed!')
            return
        fo = open(csv_filepath, 'w+')
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        fo.write(SparkleCSV.empty_column_name)
        fo.close()
        return

    def __init__(self, csv_filepath):
        '''Initialise a CSV.'''
        self.csv_filepath = csv_filepath
        self.dataframe = pd.read_csv(csv_filepath, index_col=0)
        return

    def clean_csv(self):
        '''Remove the value contents of the CSV, but not the row and column names.'''
        for row in self.list_rows():
            for column in self.list_columns():
                self.set_value(row, column, None)
        self.update_csv()
        return

    def is_empty(self) -> bool:
        '''Return whether the CSV is empty or not.'''
        ret = False
        if (self.dataframe.empty and self.get_column_size() == 0
           and self.get_row_size() == 0):
            ret = True
        return ret

    def update_csv(self):
        '''Update a CSV file.'''
        fo = open(self.csv_filepath, 'w+')
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        self.dataframe.to_csv(self.csv_filepath)
        fo.close()
        return

    def save_csv(self, csv_filepath: str):
        '''Write a CSV to the given path.'''
        fo = open(csv_filepath, 'w+')
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        self.dataframe.to_csv(csv_filepath)
        fo.close()

        return

    def get_value_index(self, row_index, column_index):
        '''Return a value by index.'''
        ret = self.dataframe.at[self.dataframe.index[row_index],
                                self.dataframe.columns[column_index]]
        return ret

    def set_value_index(self, row_index, column_index, value):
        '''Set a value by index.'''
        self.dataframe.at[self.dataframe.index[row_index],
                          self.dataframe.columns[column_index]] = value
        return

    def get_value(self, row, column):
        '''Get a value by name.'''
        ret = self.dataframe.at[row, column]
        return ret

    def set_value(self, row, column, value):
        '''Set a value by name.'''
        self.dataframe.at[row, column] = value
        return

    def list_columns(self):
        '''Return a list of columns.'''
        ret = self.dataframe.columns.tolist()
        return ret

    def get_column_name(self, index):
        '''Return the name of a column for a given index.'''
        ret = self.dataframe.columns.tolist()[index]
        return ret

    def rename_column(self, ori_column_name, mod_column_name):
        '''Change the name of a column.'''
        if ori_column_name not in self.list_columns():
            print('Column ' + ori_column_name + ' does not exist!')
            print('Nothing changed!')
            return
        self.dataframe.rename(columns={ori_column_name: mod_column_name}, inplace=True)
        return

    def get_column_size(self) -> int:
        '''Return the size of a column.'''
        return len(self.dataframe.columns.tolist())

    def add_column(self, column_name, value_list=[]):
        '''Add a column with the given values.'''
        if column_name in self.list_columns():
            print('Column ' + column_name + ' already exists!')
            print('Nothing changed!')
            return
        if value_list == []:
            value_list = [None] * self.get_row_size()
        self.dataframe[column_name] = value_list
        return

    def update_column(self, column_name, value_list):
        '''Update a column with the given values.'''
        self.dataframe[column_name] = value_list
        return

    def delete_column(self, column_name):
        '''Delete a specified column.'''
        if column_name not in self.list_columns():
            print('Column ' + column_name + ' does not exist!')
            print('Nothing changed!')
            return
        self.dataframe = self.dataframe.drop(column_name, axis=1)
        return

    def dataframe_get_specific_column(self, column_name):
        '''Return a specified column as dataframe.'''
        return self.dataframe[[column_name]]

    def dataframe_get_specific_column_isnull(self, column_name):
        '''Return a dataframe indicating whether elements of a column are null.'''
        return self.dataframe[[column_name]].isnull()

    def list_get_specific_column(self, column_name):
        '''Return a specfied column as list.'''
        mydf = self.dataframe_get_specific_column(column_name)
        mydf = mydf.T
        mylist = np.array(mydf).tolist()[0]
        return mylist

    def list_get_specific_column_isnull(self, column_name):
        '''Return a list[bool] indicating whether elements of a column are null.'''
        mydf = self.dataframe_get_specific_column_isnull(column_name)
        mydf = mydf.T
        mylist = np.array(mydf).tolist()[0]
        return mylist

    def list_rows(self):
        '''Return a list of rows.'''
        ret = self.dataframe.index.tolist()
        return ret

    def get_row_name(self, index):
        '''Return the name of a row.'''
        ret = self.dataframe.index.tolist()[index]
        return ret

    def rename_row(self, ori_row_name, mod_row_name):
        '''Change the name of a row.'''
        if ori_row_name not in self.list_rows():
            print('Row ' + ori_row_name + ' does not exist!')
            print('Nothing changed!')
            return
        self.dataframe.rename(index={ori_row_name: mod_row_name}, inplace=True)
        return

    def get_row_size(self) -> int:
        '''Return the size of a row.'''
        return len(self.dataframe.index.tolist())

    def add_row(self, row_name, value_list=[]):
        '''Add a row with the given values.'''
        if row_name in self.list_rows():
            print('Row', row_name, 'already exists!')
            print('Nothing changed!')
            return

        if value_list == []:
            value_list = [None] * self.get_column_size()
        if value_list == []:
            df = pd.DataFrame([], index=[row_name])
            self.dataframe = pd.concat([self.dataframe, df], axis=1)
        else:
            self.dataframe.loc[row_name] = value_list

        return

    def update_row(self, row_name, value_list):
        '''Update the value of a given row.'''
        self.dataframe.loc[row_name] = value_list

        return

    def delete_row(self, row_name):
        '''Delete a specified row.'''
        if row_name not in self.list_rows():
            print('Row ' + row_name + ' does not exist!')
            print('Nothing changed!')
            return
        self.dataframe = self.dataframe.drop(row_name, axis=0)

        return

    def dataframe_get_specific_row(self, row_name):
        '''Return a row with a given name.'''
        return self.dataframe.loc[[row_name]]

    def dataframe_get_specific_row_isnull(self, row_name):
        '''Return whether a given row is null or not.'''
        return self.dataframe.loc[[row_name]].isnull()

    def list_get_specific_row(self, row_name):
        '''Return a row with a given name as list.'''
        mydf = self.dataframe_get_specific_row(row_name)
        mylist = np.array(mydf).tolist()[0]

        return mylist

    def list_get_specific_row_isnull(self, row_name):
        '''Return whether a given row is null or not as a list.'''
        mydf = self.dataframe_get_specific_row_isnull(row_name)
        mylist = np.array(mydf).tolist()[0]

        return mylist
