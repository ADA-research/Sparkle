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
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_basic_help as sbh
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_job_help as sjh
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_slurm_help as ssh
from sparkle_help import sparkle_logging as sl
from sparkle_help.sparkle_command_help import CommandName
from sparkle_help import sparkle_job_help as sjh

from sparkle.slurm_parsing import SlurmBatch
import runrunner as rrr

def generate_running_solvers_sbatch_shell_script(total_job_num: int, num_job_in_parallel: int, total_job_list) -> (str, str, str):
	sbatch_script_name = r'running_solvers_sbatch_shell_script_' + sbh.get_time_pid_random_string() + r'.sh'
	sbatch_script_path = r'Tmp/' + sbatch_script_name
	job_name = '--job-name=' + sbatch_script_name
	std_out_path = sbatch_script_path + '.txt'
	std_err_path = sbatch_script_path + '.err'
	output = '--output=' + std_out_path
	error = '--error=' + std_err_path
	array = '--array=0-' + str(total_job_num-1) + '%' + str(num_job_in_parallel)

	sbatch_options_list = [job_name, output, error, array]
	sbatch_options_list.extend(ssh.get_slurm_sbatch_default_options_list())
	sbatch_options_list.extend(ssh.get_slurm_sbatch_user_options_list())
	job_params_list = []

	for job in total_job_list:
		instance_path = job[0]
		solver_path = job[1]
		performance_measure = sgh.settings.get_general_performance_measure()
		job_params_list.append('--instance ' + instance_path + ' --solver ' + solver_path + ' --performance-measure ' + performance_measure.name)

	srun_options_str = '-N1 -n1'
	srun_options_str = srun_options_str + ' ' + ssh.get_slurm_srun_user_options_str()
	target_call_str = 'Commands/sparkle_help/run_solvers_core.py'

	ssh.generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list, job_params_list, srun_options_str, target_call_str)

	return sbatch_script_path, std_out_path, std_err_path


def running_solvers_parallel(
		performance_data_csv_path: str,
		num_job_in_parallel: int,
		recompute: bool = False,
		run_on: str = None
):
	""" Run the solvers in parallel.

	Parameters
	----------
	performance_data_csv_path: str
		The path the the performance data file
	num_job_in_parallel: int
		The maximum number of jobs to run in parallel
	recompute: bool
		Compute only solver not already run (False) or recompute all perf. data (True)
		False = compute the remaining jobs for performance computation
		True = re-compute all jobs for performance computation
	run_on: str
		Where to execute the solvers. Available: ['slurm', 'local']. Default: 'slurm'.
	"""
	# open the csv file in terms of performance data
	csv = spdcsv.Sparkle_Performance_Data_CSV(performance_data_csv_path)

	# list of jobs to do
	jobs = sjh.expand_total_job_from_list(
		csv.get_list_recompute_performance_computation_job() if recompute
		else csv.get_list_remaining_performance_computation_job()
	)

	cutoff_time_str = str(sgh.settings.get_general_target_cutoff_time())

	print(f"c Cutoff time for each solver run: {cutoff_time_str} seconds")
	print(f"c The number of total running jobs: {len(jobs)}")

	# If there are no jobs, stop
	if len(jobs) == 0:
		return ''
	# If there are jobs update performance data ID
	else:
		srs.update_performance_data_id()

	sbatch_script_path, std_out_path, std_err_path = generate_running_solvers_sbatch_shell_script(
		len(jobs), num_job_in_parallel, jobs)
	command_line = 'sbatch ' + sbatch_script_path
	####

	# Log output paths
	sl.add_output(sbatch_script_path, 'Slurm batch script to run solvers in parallel')
	sl.add_output(std_out_path, 'Standard output of Slurm batch script to run solvers in parallel')
	sl.add_output(std_err_path, 'Error output of Slurm batch script to run solvers in parallel')

	batch = SlurmBatch(sbatch_script_path)

	if run_on == "local":
		print("c Running the solvers locally")
		return rrr.add_to_local_queue(cmd=[
			f"{batch.cmd} {param}" for param in batch.params
		], name="run_solvers")
	elif run_on == "slurm":
		print("c Running the solvers on the clusters")
		output_list = os.popen(command_line).readlines()

		if len(output_list) > 0 and len(output_list[0].strip().split())>0:
			run_solvers_parallel_jobid = output_list[0].strip().split()[-1]
			# Add job to active job CSV
			sjh.write_active_job(run_solvers_parallel_jobid, CommandName.RUN_SOLVERS)
		else:
			run_solvers_parallel_jobid = ''
		return run_solvers_parallel_jobid
	else:
		# TODO: Print error message
		print("c '{run_on}' not a valid target to execute the code")
		exit(1)
