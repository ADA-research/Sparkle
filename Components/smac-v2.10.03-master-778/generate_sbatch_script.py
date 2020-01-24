#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-

import os
import sys
sys.path.append('../../Commands')
from sparkle_help import sparkle_slurm_help


def get_last_level_directory_name(filepath):
	filepath = get_file_directory(filepath)
	if filepath[-1] == r'/': filepath = filepath[0:-1]
	right_index = filepath.rfind(r'/')
	if right_index<0: pass
	else: filepath = filepath[right_index+1:]
	return filepath
	

def get_file_directory(filepath):
	if os.path.isdir(filepath):
		if filepath[-1] != r'/':
			filedir = filepath + r'/'
		else:
			filedir = filepath
		return filedir
	right_index = filepath.rfind(r'/')
	if right_index<0: filedir = r'./'
	else: filedir = filepath[:right_index+1]
	return filedir

def get_file_name(filepath):
	if not os.path.isfile(filepath):
		return r''
	right_index = filepath.rfind(r'/')
	filename = filepath
	if right_index<0: pass
	else: filename = filepath[right_index+1:]
	return filename

def get_file_least_extension(filepath):
	filename = get_file_name(filepath)
	file_extension = r''
	right_index = filename.rfind(r'.')
	if right_index<0: pass
	else: file_extension = filename[right_index+1:]
	return file_extension


def generate_sbatch_script(sbatch_script_path, scenario_file, result_directory, num_of_smac_run, num_job_in_parallel, smac_execdir):
	job_name = sbatch_script_path
	num_job_total = num_of_smac_run

	path_modifier = '../../'
	sbatch_options_list = sparkle_slurm_help.get_slurm_sbatch_options_list(path_modifier)
	
	if num_job_in_parallel>num_job_total:
		num_job_in_parallel = num_job_total
	
	if result_directory[-1] != r'/':
		result_directory += r'/'
	
	if not os.path.exists(result_directory):
		os.system(r'mkdir -p ' + result_directory)
	
	if not os.path.exists(r'tmp/'):
		os.system(r'mkdir -p tmp/')
	
	fout = open(sbatch_script_path, 'w+')
	fout.write(r'#!/bin/bash' + '\n')
	fout.write(r'###' + '\n')
	fout.write(r'#SBATCH --job-name=' + job_name + '\n')
	fout.write(r'#SBATCH --output=' + r'tmp/' + job_name + r'.txt' + '\n')
	fout.write(r'#SBATCH --error=' + r'tmp/' + job_name + r'.err' + '\n')
	fout.write(r'###' + '\n')
	fout.write(r'###' + '\n')
	fout.write(r'#SBATCH --mem-per-cpu=3000' + '\n')
	fout.write(r'#SBATCH --array=0-' + str(num_job_total-1) + r'%' + str(num_job_in_parallel) + '\n')
	fout.write(r'###' + '\n')
	# Options from the slurm/sbatch settings file
	for i in sbatch_options_list:
		fout.write(r'#SBATCH ' + str(i) + '\n')
	fout.write(r'###' + '\n')

	fout.write('params=( \\' + '\n')
	
	for i in range(0, num_job_total):
		seed = i+1
		result_path = result_directory + sbatch_script_path + r'_seed_' + str(seed) + r'_smac.txt'
		smac_execdir_i = smac_execdir + r'/' + str(seed)
		fout.write('\'%s %d %s %s\' \\' % (scenario_file, seed, result_path, smac_execdir_i) + '\n')
		
	fout.write(r')' + '\n')

	#cmd_srun_prefix = r'srun -N1 -n1 --exclusive '
	cmd_srun_prefix = r'srun -N1 -n1 '
	cmd_srun_prefix += sparkle_slurm_help.get_slurm_srun_options_str(path_modifier)
	cmd_smac_prefix = r'./each_smac_run_core.sh '

	cmd = cmd_srun_prefix + r' ' + cmd_smac_prefix + r' ' + r'${params[$SLURM_ARRAY_TASK_ID]}'
	fout.write(cmd + '\n')
	fout.close()
	return


if __name__ == r'__main__':

	if len(sys.argv) != 6:
		print r'c Command error!'
		print r'c Usage: ' + sys.argv[0] + r' <scenario_file> <result_directory> <num_of_smac_run> <num_job_in_parallel> <smac_execdir>'
		sys.exit()
	
	scenario_file = sys.argv[1]
	res_directory_path = sys.argv[2]
	num_of_smac_run = int(sys.argv[3])
	num_job_in_parallel = int(sys.argv[4])
	smac_execdir = sys.argv[5]
	
	sbatch_script_path = get_file_name(scenario_file) + r'_' + str(num_of_smac_run) + r'_exp_sbatch.sh'
	generate_sbatch_script(sbatch_script_path, scenario_file, res_directory_path, num_of_smac_run, num_job_in_parallel, smac_execdir)
	os.system(r'chmod a+x ' + sbatch_script_path)
	
	

