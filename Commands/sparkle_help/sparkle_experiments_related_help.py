#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''


def init():
	global sleep_time_after_each_solver_run
	global sleep_time_after_each_extractor_run

	#default settings
	sleep_time_after_each_solver_run = 0 #1 #add at version 1.0.2
	sleep_time_after_each_extractor_run = 0 #1 #add at version 1.0.2

	return

init()

