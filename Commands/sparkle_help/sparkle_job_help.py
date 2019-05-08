#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import os
import time
import random
import sys
import fcntl


def get_num_of_total_job_from_list(list_jobs):
	num = 0
	for i in range(0, len(list_jobs)):
		num += len(list_jobs[i][1])
	return num

def expand_total_job_from_list(list_jobs):
	total_job_list = []
	for i in range(0, len(list_jobs)):
		first_item = list_jobs[i][0]
		second_item_list = list_jobs[i][1]
		len_second_item_list = len(second_item_list)
		for j in range(0, len_second_item_list):
			second_item = second_item_list[j]
			total_job_list.append([first_item, second_item])
	return total_job_list






	
