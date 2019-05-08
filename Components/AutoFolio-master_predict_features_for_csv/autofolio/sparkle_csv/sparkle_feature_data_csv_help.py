#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-

'''
Software:     Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors:     Chuan Luo, chuanluosaber@gmail.com
            Holger H. Hoos, hh@liacs.nl

Contact:     Chuan Luo, chuanluosaber@gmail.com
'''

import os
import sys
import pandas as pd
import numpy as np
import fcntl
from .sparkle_csv_help import Sparkle_CSV


class Sparkle_Feature_Data_CSV(Sparkle_CSV):
    
    def __init__(self, csv_filepath):
        Sparkle_CSV.__init__(self, csv_filepath)
        return
        
    def get_bool_in_rows(self, given_row_name):
        ret = given_row_name in self.list_rows()
        return ret
    
    def get_bool_in_columns(self, given_column_name):
        ret = given_column_name in self.list_columns()
        return ret
    
    def get_feature_vector_string(self, instance):
        feature_vector_string = r''
        row = instance
        for column in self.list_columns():
            feature_value = self.get_value(row, column)
            feature_vector_string = feature_vector_string + str(feature_value) + r' '
        return feature_vector_string.strip()
    
    def get_feature_vector_list(self, instance):
        feature_vector_list = []
        row = instance
        for column in self.list_columns():
            feature_value = float(self.get_value(row, column))
            feature_vector_list.append(feature_value)
        return feature_vector_list
            


    

