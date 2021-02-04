#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import sys

try:
	from sparkle_help import sparkle_global_help as sgh
	from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
	from sparkle_help import sparkle_job_help
	from sparkle_help import sparkle_compute_features_help as scf
	from sparkle_help import sparkle_slurm_help as ssh
	from sparkle_help import sparkle_logging as sl
except ImportError:
	import sparkle_global_help as sgh
	import sparkle_feature_data_csv_help as sfdcsv
	import sparkle_job_help
	import sparkle_compute_features_help as scf
	import sparkle_slurm_help as ssh
	import sparkle_logging as sl


def computing_features_parallel(feature_data_csv_path, mode):
	####
	# This function is used for computing features in parallel.
	# The 1st argument (feature_data_csv_path) specifies the path of the csv file where the resulting feature data would be placed.
	# The 2nd argument (mode) specifies the mode of computation. It has 2 possible values (1 or 2). If this value is 1, it means that this function will compute the remaining jobs for feature computation. Otherwise (if this value is 2), it means that this function will re-compute all jobs for feature computation.
	####
	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path) # open the csv file in terms of feature data
	if mode == 1: list_feature_computation_job = feature_data_csv.get_list_remaining_feature_computation_job() # the value of mode is 1, so the list of computation jobs is the list of the remaining jobs
	elif mode == 2: list_feature_computation_job = feature_data_csv.get_list_recompute_feature_computation_job() # the value of mode is 2, so the list of computation jobs is the list of all jobs (recomputing)
	else: # the abnormal case, exit
		print('c Computing features mode error!')
		print('c Do not compute features')
		sys.exit()
	
	####
	# set the options to the runsolver software
	runsolver_path = sgh.runsolver_path
	if len(sgh.extractor_list) == 0:
		cutoff_time_each_extractor_run = sgh.settings.get_general_extractor_cutoff_time()
	else:
		cutoff_time_each_extractor_run = sgh.settings.get_general_extractor_cutoff_time() / len(sgh.extractor_list)
	cutoff_time_each_run_option = r'-C ' + str(cutoff_time_each_extractor_run)
	print('c Cutoff time for each run on computing features is set to ' + str(cutoff_time_each_extractor_run) + ' seconds') # print the information about the cutoff time
	####
	
	####
	# expand the job list
	total_job_num = sparkle_job_help.get_num_of_total_job_from_list(list_feature_computation_job)

	# If there are no jobs, stop
	if total_job_num < 1:
		print('c No feature computation jobs to run; stopping execution! To recompute feature values use the --recompute flag.')
		sys.exit()
	# If there are jobs update feature data ID
	else:
		scf.update_feature_data_id()

	print('c The number of total running jobs: ' + str(total_job_num))
	total_job_list = sparkle_job_help.expand_total_job_from_list(list_feature_computation_job)
	####
	
	####
	# generate the sbatch script
	n_jobs = len(total_job_list)
	sbatch_script_name, sbatch_script_dir = ssh.generate_sbatch_script_for_feature_computation(n_jobs, feature_data_csv_path, total_job_list)
	####

	execution_dir = './'
	sbatch_script_path = sbatch_script_dir + sbatch_script_name
	jobid = ssh.submit_sbatch_script(sbatch_script_path, execution_dir) # execute the sbatch script via slurm

	# Log output paths
	sl.add_output(sbatch_script_path, 'Slurm batch script to compute features in parallel')

	return jobid

