#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-

import os
import sys

#real_solver_name = 'PbO-CCSAT'
#solver_name = r'each_pbo-ccsat_run_core.sh'
#solver_path = r'./' + solver_name
#runsolver_path = r'./runsolver'
#runsolver_cpu_cutoff_time = 5000
#cmd_runsolver_prefix = runsolver_path + r' --timestamp --use-pty -C ' + str(runsolver_cpu_cutoff_time)

#cmd_srun_prefix = r'srun -N1 -n1 --exclusive '


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


def visit_all_cnf_files_recursive(path, list_all_cnf_files):
	if os.path.isfile(path):
		file_extension = get_file_least_extension(path)
		if file_extension == r'cnf':
			list_all_cnf_files.append(path)
		return
	elif os.path.isdir(path):
		if path[-1] != r'/':
			this_path = path + r'/'
		else:
			this_path = path
		list_all_items = os.listdir(this_path)
		for item in list_all_items:
			visit_all_cnf_files_recursive(this_path+item, list_all_cnf_files)
	return


def generate_sbatch_script(sbatch_script_path, executable_wrapper_name, cnf_directory_path, res_directory_path, list_all_cnf_files, cutoff_time_each_run, num_job_in_parallel):
	job_name = sbatch_script_path
	num_job_total = len(list_all_cnf_files)
	
	if num_job_in_parallel>num_job_total:
		num_job_in_parallel = num_job_total
	
	executable_wrapper_path = r'./' + executable_wrapper_name
	runsolver_path = r'./runsolver'
	cmd_runsolver_prefix = runsolver_path + r' --timestamp --use-pty -C ' + str(cutoff_time_each_run) + r' -o '
	cmd_srun_prefix = r'srun -N1 -n1 --exclusive '
	
	seed = 1
	
	if cnf_directory_path[-1] != r'/':
		cnf_directory_path += r'/'
	
	if res_directory_path[-1] != r'/':
		res_directory_path += r'/'
	
	if not os.path.exists(res_directory_path):
		os.system(r'mkdir -p ' + res_directory_path)
	
	fout = open(sbatch_script_path, 'w+')
	fout.write(r'#!/bin/bash' + '\n')
	fout.write(r'###' + '\n')
	fout.write(r'#SBATCH --job-name=' + job_name + '\n')
	fout.write(r'#SBATCH --output=' + r'tmp/' + job_name + r'.txt' + '\n')
	fout.write(r'#SBATCH --error=' + r'tmp/' + job_name + r'.err' + '\n')
	fout.write(r'###' + '\n')
	fout.write(r'###' + '\n')
	fout.write(r'#SBATCH --partition=graceALL' + '\n')
	fout.write(r'#SBATCH --mem-per-cpu=3000' + '\n')
	fout.write(r'#SBATCH --array=0-' + str(num_job_total-1) + r'%' + str(num_job_in_parallel) + '\n')
	fout.write(r'###' + '\n')
	
	fout.write('params=( \\' + '\n')
	
	for instance_path in list_all_cnf_files:
		instance_name = get_file_name(instance_path)
		instance_directory = get_file_directory(instance_path)
		result_name = executable_wrapper_name + r'_' + instance_name + r'_' + str(seed) + r'.res'
		result_directory = instance_directory.replace(cnf_directory_path, res_directory_path, 1)
		if not os.path.exists(result_directory):
			os.system(r'mkdir -p ' + result_directory)
		result_path = result_directory + result_name
		fout.write('\'%s %s %s %s\' \\' % (result_path, executable_wrapper_path, './', instance_path) + '\n')
		
	fout.write(r')' + '\n')
	
	#cmd = cmd_srun_prefix + r' ' + cmd_runsolver_prefix + r' ' + r'${params[$SLURM_ARRAY_TASK_ID]}'
	cmd = cmd_srun_prefix + r' ' + cmd_runsolver_prefix + r' ' + r'${params[$SLURM_ARRAY_TASK_ID]}'
	
	fout.write(cmd + '\n')
	fout.close()
	return


if __name__ == r'__main__':

	if len(sys.argv) != 7:
		print r'c Command error!'
		print r'c Usage: ' + sys.argv[0] + r' <executable_wrapper_name> <cnf_directory> <result_directory> <cutoff_time_each_run> <num_job_in_parallel> <train_or_test>'
		sys.exit()
	
	executable_wrapper_name = sys.argv[1]
	cnf_directory_path = sys.argv[2]
	res_directory_path = sys.argv[3]
	cutoff_time_each_run = int(sys.argv[4])
	num_job_in_parallel = int(sys.argv[5])
	train_or_test = sys.argv[6]
	
	list_all_cnf_files = []
	visit_all_cnf_files_recursive(cnf_directory_path, list_all_cnf_files)
	
	if train_or_test == 'train':
		sbatch_script_path = executable_wrapper_name + r'_' + get_last_level_directory_name(cnf_directory_path) + r'_train_exp_sbatch.sh'
	else:
		sbatch_script_path = executable_wrapper_name + r'_' + get_last_level_directory_name(cnf_directory_path) + r'_test_exp_sbatch.sh'
	generate_sbatch_script(sbatch_script_path, executable_wrapper_name, cnf_directory_path, res_directory_path, list_all_cnf_files, cutoff_time_each_run, num_job_in_parallel)
	os.system(r'chmod a+x ' + sbatch_script_path)
	
	

