#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import os
import sys
import pandas as pd
import numpy as np
import fcntl
import sparkle_global_help
import sparkle_csv_help as scsv


class Sparkle_Feature_Data_CSV(scsv.Sparkle_CSV):
	
	def test(self):
		print 'c just a test'
		return
	
	def __init__(self, csv_filepath):
		scsv.Sparkle_CSV.__init__(self, csv_filepath)
		self.extractor_list = sparkle_global_help.extractor_list
		return
	
	def get_list_recompute_feature_computation_job(self):
		list_recompute_feature_computation_job = []
		list_row_name = self.list_rows()
		
		for row_name in list_row_name:
			list_item = [row_name, self.extractor_list]
			list_recompute_feature_computation_job.append(list_item)
		return list_recompute_feature_computation_job
	
	def get_list_remaining_feature_computation_job(self):
		list_remaining_feature_computation_job = []
		bool_array_isnull = self.dataframe.isnull()
		for row_name in self.list_rows():
			current_extractor_list = []
			for column_name in self.list_columns():
				flag_value_is_null = bool_array_isnull.get_value(row_name, column_name)
				if flag_value_is_null:
					extractor_path = self.get_extractor_path_from_feature(column_name)
					if not extractor_path in current_extractor_list:
						current_extractor_list.append(extractor_path)
			list_item = [row_name, current_extractor_list]
			list_remaining_feature_computation_job.append(list_item)
		return list_remaining_feature_computation_job
	
	def get_list_processed_feature_computation_job(self):
		list_processed_feature_computation_job = []
		bool_array_isnull = self.dataframe.isnull()
		for row_name in self.list_rows():
			current_extractor_list = []
			for column_name in self.list_columns():
				flag_value_is_null = bool_array_isnull.get_value(row_name, column_name)
				if not flag_value_is_null:
					extractor_path = self.get_extractor_path_from_feature(column_name)
					if not extractor_path in current_extractor_list:
						current_extractor_list.append(extractor_path)
			list_item = [row_name, current_extractor_list]
			list_processed_feature_computation_job.append(list_item)
		return list_processed_feature_computation_job
	
	def get_extractor_path_from_feature(self, given_column_name):
		sparkle_special_string = sparkle_global_help.sparkle_special_string
		index = given_column_name.find(sparkle_special_string)
		length = len(sparkle_special_string)
		extractor_name = given_column_name[index+length:]
		extractor_path = r'Extractors/' + extractor_name
		return extractor_path
	
	def get_bool_in_rows(self, given_row_name):
		ret = given_row_name in self.list_rows()
		return ret
	
	def get_bool_in_columns(self, given_column_name):
		ret = given_column_name in self.list_columns()
		return ret
	
	def combine(self, second_sfdcsv):
		#print 'c to combine'
		
		list_columns_second_sfdcsv = second_sfdcsv.list_columns()
		list_rows_second_sfdcsv = second_sfdcsv.list_rows()
		
		len_list_columns_second_sfdcsv = len(list_columns_second_sfdcsv)
		len_list_rows_second_sfdcsv = len(list_rows_second_sfdcsv)
		
		for i in range(0, len_list_rows_second_sfdcsv):
			row_name_second_sfdcsv = second_sfdcsv.get_row_name(i)
			bool_in_rows = self.get_bool_in_rows(row_name_second_sfdcsv)
			for j in range(0, len_list_columns_second_sfdcsv):
				column_name_second_sfdcsv = second_sfdcsv.get_column_name(j)
				bool_in_columns = self.get_bool_in_columns(column_name_second_sfdcsv)
				value = second_sfdcsv.get_value_index(i, j)
				if bool_in_rows:
					if bool_in_columns:
						self.set_value(row_name_second_sfdcsv, column_name_second_sfdcsv, value)
						#pass
					else:
						self.add_column(column_name_second_sfdcsv)
						self.set_value(row_name_second_sfdcsv, column_name_second_sfdcsv, value)
						#pass
				else:
					if bool_in_columns:
						self.add_row(row_name_second_sfdcsv)
						self.set_value(row_name_second_sfdcsv, column_name_second_sfdcsv, value)
						#pass
					else:
						self.add_row(row_name_second_sfdcsv)
						self.add_column(column_name_second_sfdcsv)
						self.set_value(row_name_second_sfdcsv, column_name_second_sfdcsv, value)
						#pass
		
		return
	
	
	def reload_and_combine_and_update(self, second_sfdcsv):
		fo = open(self.csv_filepath, 'r+')
		fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
		self.dataframe = pd.read_csv(self.csv_filepath,index_col=0)
		self.combine(second_sfdcsv)
		self.dataframe.to_csv(self.csv_filepath)
		fo.close()
		return
	
	
	def get_feature_vector_string(self, instance):
		feature_vector_string = r''
		row = instance
		for column in self.list_columns():
			feature_value = self.get_value(row, column)
			feature_vector_string = feature_vector_string + str(feature_value) + r' '
		return feature_vector_string.strip()
	
	
	def calc_mean_over_all_non_missing_values_of_this_column(self, column_name):
		sum_value = 0
		num = 0
		
		for row_name in self.list_rows():
			tmp_value = self.get_value(row_name, column_name)
			if tmp_value < sparkle_global_help.sparkle_missing_value+1:
				continue
			else:
				num += 1
				sum_value += tmp_value
		
		if num == 0:
			 #all values are missing value
			return sparkle_global_help.sparkle_missing_value
		
		mean_value = sum_value/num
		return mean_value
	
	
	def generate_mean_value_feature_vector(self):
		list_mean_value_feature_vector = []
		for column_name in self.list_columns():
			list_item = self.calc_mean_over_all_non_missing_values_of_this_column(column_name)
			list_mean_value_feature_vector.append(list_item)
		return list_mean_value_feature_vector
	
	
	
	def	impute_missing_value_of_this_column(self, column_name):
		sum_value = 0
		num = 0
		
		list_missing_value_row_name = []
		
		for row_name in self.list_rows():
			tmp_value = self.get_value(row_name, column_name)
			if tmp_value < sparkle_global_help.sparkle_missing_value+1:
				#this is missing value
				missing_item = row_name
				list_missing_value_row_name.append(missing_item)
			else:
				#this is non-missing value
				num += 1
				sum_value += tmp_value
		
		if len(list_missing_value_row_name) == 0: return #no missing value
		if num == 0: return #all values are missing value
		
		mean_value = sum_value/num
		for row_name in list_missing_value_row_name:
			self.set_value(row_name, column_name, mean_value)
		return
	
	def impute_missing_value_of_all_columns(self):
		for column_name in self.list_columns():
			self.impute_missing_value_of_this_column(column_name)
		return
	

	def bool_exists_missing_value(self):
		for column_name in self.list_columns():
			for row_name in self.list_rows():
				tmp_value = self.get_value(row_name, column_name)
				if tmp_value < sparkle_global_help.sparkle_missing_value+1:
					return True
		return False


	

