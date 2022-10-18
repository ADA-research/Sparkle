#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_basic_help as sbh
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_slurm_help as ssh
from sparkle_help.sparkle_command_help import CommandName
from sparkle_help import sparkle_job_help as sjh


def get_dependency_list_str(dependency_jobid_list: list[str]) -> str:
    '''Return a list of dependencies as a single str of Slurm dependencies.'''
    dependency_list_str = ''

    for dependency_jobid in dependency_jobid_list:
        dependency_list_str += f'afterany:{dependency_jobid},'

    # Remove trailing comma
    dependency_list_str = dependency_list_str[:-1]

    return dependency_list_str


def generate_job_sbatch_shell_script(sbatch_script_path: str, job_script: str,
                                     dependency_jobid_list: list[str]):
    '''Generate a Slurm batch script for the given job and dependencies.'''
    sbatch_script_name = sfh.get_file_name(sbatch_script_path)
    job_name = '--job-name=' + sbatch_script_name
    output = '--output=' + sbatch_script_path + '.txt'
    error = '--error=' + sbatch_script_path + '.err'
    dependency = '--dependency='
    dependency_list_str = get_dependency_list_str(dependency_jobid_list)

    if dependency_list_str.strip() != '':
        dependency += dependency_list_str

    sbatch_options_list = [job_name, output, error, dependency]
    sbatch_options_list.extend(ssh.get_slurm_sbatch_default_options_list())
    sbatch_options_list.extend(ssh.get_slurm_sbatch_user_options_list())
    job_params_list = ['']

    srun_options_str = '-N1 -n1'
    srun_options_str = srun_options_str + ' ' + ssh.get_slurm_srun_user_options_str()
    target_call_str = job_script

    ssh.generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list,
                                       job_params_list, srun_options_str,
                                       target_call_str)

    return


def running_job_parallel(job_script: str, dependency_jobid_list: list[str],
                         command_name: CommandName) -> str:
    '''Queues a Slurm job with given dependencies. Returns a Slurm job ID as str.'''
    sbatch_shell_script_path = (f'{sgh.sparkle_tmp_path}running_job_parallel_'
                                f'{sbh.get_time_pid_random_string()}.sh')
    generate_job_sbatch_shell_script(sbatch_shell_script_path, job_script,
                                     dependency_jobid_list)
    os.system('chmod a+x ' + sbatch_shell_script_path)
    command_line = 'sbatch ' + sbatch_shell_script_path
    output_list = os.popen(command_line).readlines()

    if len(output_list) > 0 and len(output_list[0].strip().split()) > 0:
        run_job_parallel_jobid = output_list[0].strip().split()[-1]
        # Add job to active job CSV
        sjh.write_active_job(run_job_parallel_jobid, command_name)
    else:
        run_job_parallel_jobid = ''

    return run_job_parallel_jobid
