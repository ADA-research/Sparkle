#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import sparkle_global_help

def get_slurm_options(path_modifier=None):
	if path_modifier is None:
		path_modifier = ''

	slurm_options_list = []
	sparkle_slurm_settings_path = str(path_modifier) + sparkle_global_help.sparkle_slurm_settings_path
	
	settings_file = open(sparkle_slurm_settings_path, 'r')
	while True:
		current_line = settings_file.readline()
		if not current_line:
			break
		if current_line[0] == '-':
			current_line = current_line.strip()
			slurm_options_list.append(current_line)
	settings_file.close()

	return slurm_options_list

# Get a list of options to be used with sbatch calls
def get_slurm_sbatch_options(path_modifier=None):
	return get_slurm_options(path_modifier)

def get_slurm_srun_options():
	return get_slurm_options()
