#!/usr/bin/env python3
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

try:
	from sparkle_help import sparkle_global_help
	from sparkle_help import sparkle_csv_help as scsv
	from sparkle_help import sparkle_experiments_related_help
except ImportError:
	import sparkle_global_help
	import sparkle_csv_help as scsv
	import sparkle_experiments_related_help


class Sparkle_Performance_Data_CSV(scsv.Sparkle_CSV):
	
	def test(self):
		print('c just a test')
		return
	
	def __init__(self, csv_filepath):
		scsv.Sparkle_CSV.__init__(self, csv_filepath)
		self.solver_list = sparkle_global_help.solver_list
		return
	
	def get_list_recompute_performance_computation_job(self):
		list_recompute_performance_computation_job = []
		list_row_name = self.list_rows()
		list_column_name = self.list_columns()
		
		for row_name in list_row_name:
			list_item = [row_name, list_column_name]
			list_recompute_performance_computation_job.append(list_item)	
		return list_recompute_performance_computation_job

	def get_list_remaining_performance_computation_job(self):
		list_remaining_performance_computation_job = []
		bool_array_isnull = self.dataframe.isnull()
		for row_name in self.list_rows():
			current_solver_list = []
			for column_name in self.list_columns():
				flag_value_is_null = bool_array_isnull.at[row_name, column_name]
				if flag_value_is_null:
					current_solver_list.append(column_name)
			list_item = [row_name, current_solver_list]
			list_remaining_performance_computation_job.append(list_item)
		return list_remaining_performance_computation_job

	def get_list_processed_performance_computation_job(self):
		list_processed_performance_computation_job = []
		bool_array_isnull = self.dataframe.isnull()
		for row_name in self.list_rows():
			current_solver_list = []
			for column_name in self.list_columns():
				flag_value_is_null = bool_array_isnull.at[row_name, column_name]
				if not flag_value_is_null:
					current_solver_list.append(column_name)
			list_item = [row_name, current_solver_list]
			list_processed_performance_computation_job.append(list_item)
		return list_processed_performance_computation_job

	def calc_score_of_solver_on_instance(self, solver, instance, captime, num_instances, num_solvers):
		score = -1
		runtime = self.get_value(instance, solver)
		if runtime<captime:
			inc_score = (captime - runtime)/(num_instances*num_solvers*captime +1)
			score = 1 + inc_score
		else:
			score = 0
		return score
	
	def calc_virtual_best_score_of_portfolio_on_instance(self, instance, captime, num_instances, num_solvers):
		virtual_best_score = -1
		for solver in self.list_columns():
			score_solver = self.calc_score_of_solver_on_instance(solver, instance, captime, num_instances, num_solvers)
			if virtual_best_score == -1 or virtual_best_score < score_solver: virtual_best_score = score_solver
		if virtual_best_score == -1 and len(self.list_columns()) == 0:
			virtual_best_score = 0
		return virtual_best_score

	def calc_virtual_best_performance_of_portfolio(self, captime, num_instances, num_solvers):
		virtual_best_performance = 0
		for instance in self.list_rows():
			virtual_best_score = self.calc_virtual_best_score_of_portfolio_on_instance(instance, captime, num_instances, num_solvers)
			#print 'c ' + instance + ' ' + str(virtual_best_score)
			virtual_best_performance = virtual_best_performance + virtual_best_score
		return virtual_best_performance
	
	def get_dict_vbs_penalty_time_on_each_instance(self):
		mydict = {}
		for instance in self.list_rows():
			vbs_penalty_time = sparkle_experiments_related_help.penalty_time
			for solver in self.list_columns():
				runtime = self.get_value(instance, solver)
				if runtime < vbs_penalty_time:
					vbs_penalty_time = runtime
			mydict[instance] = vbs_penalty_time
		return mydict
	
	def calc_vbs_penaltry_time(self, cutoff_time_each_run, par_num=10):
		penalty_time_each_run = cutoff_time_each_run * par_num
		vbs_penalty_time = 0.0
		vbs_count = 0
		
		for instance in self.list_rows():
			vbs_penalty_time_on_this_instance = -1
			vbs_count += 1
			for solver in self.list_columns():
				this_run_time = self.get_value(instance, solver)
				if vbs_penalty_time_on_this_instance < 0 or vbs_penalty_time_on_this_instance > this_run_time:
					vbs_penalty_time_on_this_instance = this_run_time
			if vbs_penalty_time_on_this_instance > cutoff_time_each_run:
				vbs_penalty_time_on_this_instance = penalty_time_each_run
			vbs_penalty_time += vbs_penalty_time_on_this_instance
		
		vbs_penalty_time = vbs_penalty_time / vbs_count
		return vbs_penalty_time

	def get_solver_penalty_time_ranking_list(self, cutoff_time_each_run, par_num=10):
		solver_penalty_time_ranking_list = []
		penalty_time_each_run = cutoff_time_each_run * par_num
		
		for solver in self.list_columns():
			this_penalty_time = 0.0
			this_count = 0
			for instance in self.list_rows():
				this_run_time = self.get_value(instance, solver)
				this_count += 1
				if this_run_time <= cutoff_time_each_run:
					this_penalty_time += this_run_time
				else:
					this_penalty_time += penalty_time_each_run
			this_penalty_time = this_penalty_time/this_count
			solver_penalty_time_ranking_list.append([solver, this_penalty_time])
	
		solver_penalty_time_ranking_list.sort(key=lambda this_penalty_time: this_penalty_time[1])
		return solver_penalty_time_ranking_list


