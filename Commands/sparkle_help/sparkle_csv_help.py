#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import pandas as pd
import numpy as np
import fcntl


class Sparkle_CSV:

    empty_column_name = r'""'

    @staticmethod
    def create_empty_csv(csv_filepath):
        if os.path.exists(csv_filepath):
            print('Path', csv_filepath, 'already exists!')
            print('Nothing changed!')
            return
        fo = open(csv_filepath, 'w+')
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        fo.write(Sparkle_CSV.empty_column_name)
        fo.close()
        return

    def __init__(self, csv_filepath):
        self.csv_filepath = csv_filepath
        self.dataframe = pd.read_csv(csv_filepath, index_col=0)
        return

    def clean_csv(self):
        for row in self.list_rows():
            for column in self.list_columns():
                self.set_value(row, column, None)
        self.update_csv()
        return

    def is_empty(self):
        ret = False
        if(self.dataframe.empty and self.get_column_size() == 0
           and self.get_row_size() == 0):
            ret = True
        return ret

    def update_csv(self):
        fo = open(self.csv_filepath, 'w+')
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        self.dataframe.to_csv(self.csv_filepath)
        fo.close()
        return

    def save_csv(self, csv_filepath: str):
        fo = open(csv_filepath, 'w+')
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        self.dataframe.to_csv(csv_filepath)
        fo.close()

        return

    def get_value_index(self, row_index, column_index):
        ret = self.dataframe.at[self.dataframe.index[row_index],
                                self.dataframe.columns[column_index]]
        return ret

    def set_value_index(self, row_index, column_index, value):
        self.dataframe.at[self.dataframe.index[row_index],
                          self.dataframe.columns[column_index]] = value
        return

    def get_value(self, row, column):
        ret = self.dataframe.at[row, column]
        return ret

    def set_value(self, row, column, value):
        self.dataframe.at[row, column] = value
        return

    def list_columns(self):
        ret = self.dataframe.columns.tolist()
        return ret

    def get_column_name(self, index):
        ret = self.dataframe.columns.tolist()[index]
        return ret

    def rename_column(self, ori_column_name, mod_column_name):
        if ori_column_name not in self.list_columns():
            print('Column ' + ori_column_name + ' does not exist!')
            print('Nothing changed!')
            return
        self.dataframe.rename(columns={ori_column_name: mod_column_name}, inplace=True)
        return

    def get_column_size(self) -> int:
        return len(self.dataframe.columns.tolist())

    def add_column(self, column_name, value_list=[]):
        if column_name in self.list_columns():
            print('Column ' + column_name + ' already exists!')
            print('Nothing changed!')
            return
        if value_list == []:
            value_list = [None]*self.get_row_size()
        self.dataframe[column_name] = value_list
        return

    def update_column(self, column_name, value_list):
        self.dataframe[column_name] = value_list
        return

    def delete_column(self, column_name):
        if column_name not in self.list_columns():
            print('Column ' + column_name + ' does not exist!')
            print('Nothing changed!')
            return
        self.dataframe = self.dataframe.drop(column_name, axis=1)
        return

    def dataframe_get_specific_column(self, column_name):
        return self.dataframe[[column_name]]

    def dataframe_get_specific_column_isnull(self, column_name):
        return self.dataframe[[column_name]].isnull()

    def list_get_specific_column(self, column_name):
        mydf = self.dataframe_get_specific_column(column_name)
        mydf = mydf.T
        mylist = np.array(mydf).tolist()[0]
        return mylist

    def list_get_specific_column_isnull(self, column_name):
        mydf = self.dataframe_get_specific_column_isnull(column_name)
        mydf = mydf.T
        mylist = np.array(mydf).tolist()[0]
        return mylist

    def list_rows(self):
        ret = self.dataframe.index.tolist()
        return ret

    def get_row_name(self, index):
        ret = self.dataframe.index.tolist()[index]
        return ret

    def rename_row(self, ori_row_name, mod_row_name):
        if ori_row_name not in self.list_rows():
            print('Row ' + ori_row_name + ' does not exist!')
            print('Nothing changed!')
            return
        self.dataframe.rename(index={ori_row_name: mod_row_name}, inplace=True)
        return

    def get_row_size(self) -> int:
        return len(self.dataframe.index.tolist())

    def add_row(self, row_name, value_list=[]):
        if row_name in self.list_rows():
            print('Row', row_name, 'already exists!')
            print('Nothing changed!')
            return

        if value_list == []:
            value_list = [None]*self.get_column_size()
        if value_list == []:
            df = pd.DataFrame([], index=[row_name])
            self.dataframe = self.dataframe.append(df)
        else:
            self.dataframe.loc[row_name] = value_list

        return

    def update_row(self, row_name, value_list):
        self.dataframe.loc[row_name] = value_list

        return

    def delete_row(self, row_name):
        if row_name not in self.list_rows():
            print('Row ' + row_name + ' does not exist!')
            print('Nothing changed!')
            return
        self.dataframe = self.dataframe.drop(row_name, axis=0)

        return

    def dataframe_get_specific_row(self, row_name):
        return self.dataframe.loc[[row_name]]

    def dataframe_get_specific_row_isnull(self, row_name):
        return self.dataframe.loc[[row_name]].isnull()

    def list_get_specific_row(self, row_name):
        mydf = self.dataframe_get_specific_row(row_name)
        mylist = np.array(mydf).tolist()[0]

        return mylist

    def list_get_specific_row_isnull(self, row_name):
        mydf = self.dataframe_get_specific_row_isnull(row_name)
        mylist = np.array(mydf).tolist()[0]

        return mylist
