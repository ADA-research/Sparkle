#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''Helper functions for interaction with Slurm.'''

import os
import fcntl
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List

try:
    from sparkle_help import sparkle_global_help as sgh
    from sparkle_help import sparkle_basic_help as sbh
    from sparkle_help import sparkle_configure_solver_help as scsh
    from sparkle_help import sparkle_logging as sl
    from sparkle_help import sparkle_file_help as sfh
    from sparkle_help.sparkle_command_help import CommandName
    from sparkle_help import sparkle_job_help as sjh
except ImportError:
    import sparkle_global_help as sgh
    import sparkle_basic_help as sbh
    import sparkle_configure_solver_help as scsh
    import sparkle_logging as sl
    import sparkle_file_help as sfh
    from sparkle_command_help import CommandName
    import sparkle_job_help as sjh


def get_slurm_options_list(path_modifier=None):
    '''Return a list with the Slurm options given in the Slurm settings file.'''
    if path_modifier is None:
        path_modifier = ''

    slurm_options_list = []

    sparkle_slurm_settings_path = str(path_modifier) + sgh.sparkle_slurm_settings_path

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


def get_slurm_sbatch_user_options_list(path_modifier=None):
    '''Return a list with Slurm batch options given by the user.'''
    return get_slurm_options_list(path_modifier)


def get_slurm_sbatch_default_options_list():
    '''Return the default list of Slurm batch options.'''
    return ['--partition=graceADA']


def get_slurm_srun_user_options_list(path_modifier=None):
    '''Return a list with the Slurm run options given by the user.'''
    return get_slurm_options_list(path_modifier)


def get_slurm_srun_user_options_str(path_modifier=None) -> str:
    '''Return a str with the Slurm run option given by the user.'''
    srun_options_list = get_slurm_srun_user_options_list(path_modifier)
    srun_options_str = ''

    for i in srun_options_list:
        srun_options_str += i + ' '

    return srun_options_str


def check_slurm_option_compatibility(srun_option_string: str):
    '''Check if the given srun_option_string is compatible with the Slurm cluster'''
    # Check compatibility of slurm options
    args = shlex.split(srun_option_string)
    kwargs = {}

    for i in range(len(args)):
        arg = args[i]
        if '=' in arg:
            splitted = arg.split('=')
            kwargs[splitted[0]] = splitted[1]
        elif i < len(args) and '=' not in args[i + 1]:
            kwargs[arg] = args[i + 1]

    if not ('--partition' in kwargs.keys() or '-p' in kwargs.keys()):
        print('###Could not check slurm compatibility because no partition was '
              'specified; continuing###')
        return True, 'Could not Check'

    partition = kwargs.get('--partition', kwargs.get('-p', None))

    output = str(subprocess.check_output(['sinfo', '--nohead', '--format', '"%c;%m"',
                                          '--partition', partition]))
    cpus, memory = output[3:-4].split(';')
    cpus = int(cpus)
    memory = float(memory)

    if '--cpus-per-task' in kwargs.keys() or '-c' in kwargs.keys():
        requestedcpus = int(kwargs.get('--cpus-per-task', kwargs.get('-c', 0)))
        if requestedcpus > cpus:
            return False, f'CPU specification of {requestedcpus} cannot be ' \
                          f'satisfied for {partition}, only got {cpus}'

    if '--mem-per-cpu' in kwargs.keys() or '-m' in kwargs.keys():
        requestedmemory = float(kwargs.get('--mem-per-cpu', kwargs.get('-m', 0))) * \
            int(kwargs.get('--cpus-per-task', kwargs.get('-c', cpus)))
        if requestedmemory > memory:
            return False, f'Memory specification {requestedmemory}MB can not be ' \
                          f'satisfied for {partition}, only got {memory}MB'

    return True, 'Check successful'


def generate_sbatch_script_generic(sbatch_script_path: str,
                                   sbatch_options_list: List[str],
                                   job_params_list: List[str], srun_options_str: str,
                                   target_call_str: str,
                                   job_output_list: List[str] = None):
    '''Generate the generic components of a Slurm batch script.'''
    fout = open(sbatch_script_path, 'w+')  # open the file of sbatch script
    # using the UNIX file lock to prevent other attempts to visit this sbatch script
    fcntl.flock(fout.fileno(), fcntl.LOCK_EX)

    # specify the options of sbatch in the top of this sbatch script
    fout.write('#!/bin/bash' + '\n')  # use bash to execute this script
    fout.write('###' + '\n')
    fout.write('###' + '\n')

    for i in sbatch_options_list:
        fout.write('#SBATCH ' + str(i) + '\n')

    fout.write('###' + '\n')

    # specify the array of parameters for each command
    if len(job_params_list) > 0:
        fout.write('params=( \\' + '\n')

        for i in range(0, len(job_params_list)):
            fout.write(f"'{job_params_list[i]}' \\\n")

        fout.write(')' + '\n')

    # if there is a list of output file paths, write the output parameter
    if job_output_list is not None:
        fout.write('output=( \\' + '\n')

        for i in range(0, len(job_output_list)):
            fout.write(f"'{job_output_list[i]}' \\\n")

        fout.write(')' + '\n')

    # specify the prefix of the executing command
    command_prefix = 'srun ' + srun_options_str + ' ' + target_call_str
    # specify the complete command
    command_line = command_prefix
    if len(job_params_list) > 0:
        command_line += ' ' + '${params[$SLURM_ARRAY_TASK_ID]}'

    # add output file paths to the command if given
    if job_output_list is not None:
        command_line += ' > ${output[$SLURM_ARRAY_TASK_ID]}'

    # write the complete command in this sbatch script
    fout.write(command_line + '\n')
    fout.close()  # close the file of the sbatch script

    return


def get_sbatch_options_list(sbatch_script_path: Path, num_jobs: int,
                            job: str, smac: bool = True) -> list[str]:
    '''Return and write output paths for a list of standardised Slurm batch options.'''
    if smac:
        tmp_dir = 'tmp/'
    else:
        tmp_dir = 'Tmp/'

    sbatch_script_name = sfh.get_file_name(str(sbatch_script_path))

    # Set sbatch options
    max_jobs = sgh.settings.get_slurm_number_of_runs_in_parallel()
    if num_jobs < max_jobs:
        max_jobs = num_jobs
    std_out = f'{tmp_dir}{sbatch_script_name}.txt'
    std_err = f'{tmp_dir}{sbatch_script_name}.err'
    job_name = f'--job-name={sbatch_script_name}'
    output = f'--output={std_out}'
    error = f'--error={std_err}'
    array = f'--array=0-{str(num_jobs - 1)}%{str(max_jobs)}'
    sbatch_options_list = [job_name, output, error, array]

    # Log script and output paths
    sl.add_output(str(sbatch_script_path), f'Slurm batch script for {job}')
    sl.add_output(sgh.smac_dir + std_out,
                  f'Standard output of Slurm batch script for {job}')
    sl.add_output(sgh.smac_dir + std_err,
                  f'Error output of Slurm batch script for {job}')

    # Remove possible old output
    if smac:
        sfh.rmfile(Path(sgh.smac_dir + std_out))
        sfh.rmfile(Path(sgh.smac_dir + std_err))
    else:
        sfh.rmfile(Path(std_out))
        sfh.rmfile(Path(std_err))

    return sbatch_options_list


def generate_sbatch_script_for_validation(solver_name: str, instance_set_train_name: str,
                                          instance_set_test_name: str = None) -> str:
    '''Generate a Slurm batch script for algorithm configuration validation.'''
    # Set script name and path
    if instance_set_test_name is not None:
        sbatch_script_name = (f'{solver_name}_{instance_set_train_name}_'
                              f'{instance_set_test_name}_validation_sbatch.sh')
    else:
        sbatch_script_name = (f'{solver_name}_{instance_set_train_name}_validation_'
                              'sbatch.sh')

    sbatch_script_path = sgh.smac_dir + sbatch_script_name

    # Get sbatch options
    num_jobs = 3
    job = 'validation'
    sbatch_options_list = get_sbatch_options_list(Path(sbatch_script_path), num_jobs,
                                                  job)

    scenario_dir = 'example_scenarios/' + solver_name + '_' + instance_set_train_name

    # Train default
    default = True
    scenario_file_name = scsh.create_file_scenario_validate(
        solver_name, instance_set_train_name, instance_set_train_name,
        scsh.InstanceType.TRAIN, default)
    scenario_file_path = scenario_dir + '/' + scenario_file_name
    exec_dir = scenario_dir + '/validate_train_default/'
    configuration_str = 'DEFAULT'
    train_default_out = 'results/' + solver_name + '_validation_' + scenario_file_name

    train_default = (f'--scenario-file {scenario_file_path} --execdir {exec_dir}'
                     f' --configuration {configuration_str}')

    # Create job list
    job_params_list = [train_default]
    job_output_list = [train_default_out]

    # If given, also validate on the test set
    if instance_set_test_name is not None:
        # Test default
        default = True
        scenario_file_name = scsh.create_file_scenario_validate(
            solver_name, instance_set_train_name, instance_set_test_name,
            scsh.InstanceType.TEST, default)
        scenario_file_path = scenario_dir + '/' + scenario_file_name
        exec_dir = f'{scenario_dir}/validate_{instance_set_test_name}_test_default/'
        configuration_str = 'DEFAULT'
        test_default_out = 'results/' + solver_name + '_validation_' + scenario_file_name

        test_default = (f'--scenario-file {scenario_file_path} --execdir {exec_dir}'
                        f' --configuration {configuration_str}')

        # Test configured
        default = False
        scenario_file_name = scsh.create_file_scenario_validate(
            solver_name, instance_set_train_name, instance_set_test_name,
            scsh.InstanceType.TEST, default)
        scenario_file_path = scenario_dir + '/' + scenario_file_name
        optimised_configuration_str, _, _ = scsh.get_optimised_configuration(
            solver_name, instance_set_train_name)
        exec_dir = f'{scenario_dir}/validate_{instance_set_test_name}_test_configured/'
        configuration_str = '"' + str(optimised_configuration_str) + '"'

        # Write configuration to file to be used by smac-validate
        config_file_path = scenario_dir + '/configuration_for_validation.txt'
        # open the file of sbatch script
        fout = open(sgh.smac_dir + config_file_path, 'w+')
        # using the UNIX file lock to prevent other attempts to visit this sbatch script
        fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
        fout.write(optimised_configuration_str + '\n')

        test_configured_out = f'results/{solver_name}_validation_{scenario_file_name}'

        test_configured = (f'--scenario-file {scenario_file_path} --execdir {exec_dir}'
                           f' --configuration-list {config_file_path}')

        # Extend job list
        job_params_list.extend([test_default, test_configured])
        job_output_list.extend([test_default_out, test_configured_out])

    # Number of cores available on a Grace CPU
    n_cpus = sgh.settings.get_slurm_clis_per_node()

    # Adjust maximum number of cores to be the maximum of the instances we validate on
    instance_sizes = []
    # Get instance set sizes
    for instance_set_name, inst_type in [(instance_set_train_name, 'train'),
                                         (instance_set_test_name, 'test')]:
        if instance_set_name is not None:
            smac_instance_file = (f'{sgh.smac_dir}{scenario_dir}/{instance_set_name}_'
                                  f'{inst_type}.txt')
            if Path(smac_instance_file).is_file():
                instance_count = sum(1 for _ in open(smac_instance_file, 'r'))
                instance_sizes.append(instance_count)

    # Adjust cpus when nessacery
    if len(instance_sizes) > 0:
        max_instance_count = (max(*instance_sizes) if len(instance_sizes) > 1
                              else instance_sizes[0])
        n_cpus = min(n_cpus, max_instance_count)

    # Extend sbatch options
    cpus = '--cpus-per-task=' + str(n_cpus)
    sbatch_options_list.append(cpus)
    sbatch_options_list.extend(get_slurm_sbatch_default_options_list())
    # Get user options second to overrule defaults
    sbatch_options_list.extend(get_slurm_sbatch_user_options_list())

    # Set srun options
    srun_options_str = '--nodes=1 --ntasks=1 --cpus-per-task ' + str(n_cpus)
    srun_options_str = srun_options_str + ' ' + get_slurm_srun_user_options_str()

    result, msg = check_slurm_option_compatibility(srun_options_str)

    if not result:
        print(f'Slurm config Error: {msg}')
        sys.exit()

    # Create target call
    target_call_str = ('./smac-validate --use-scenario-outdir true --num-run 1 '
                       f'--cli-cores {str(n_cpus)}')

    # Remove possible old results
    for result_output_file in job_output_list:
        sfh.rmfile(Path(result_output_file))

    # Generate script
    generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list,
                                   job_params_list, srun_options_str, target_call_str,
                                   job_output_list)

    return sbatch_script_name


def generate_sbatch_script_for_feature_computation(n_jobs, feature_data_csv_path,
                                                   list_jobs):
    '''Generate a Slurm batch script for feature computation.'''
    # Set script name and path
    sbatch_script_name = (f'computing_features_sbatch_shell_script_{str(n_jobs)}_'
                          f'{sbh.get_time_pid_random_string()}.sh')
    sbatch_script_dir = sgh.sparkle_tmp_path
    sbatch_script_path = sbatch_script_dir + sbatch_script_name

    # Set sbatch options
    max_jobs = sgh.settings.get_slurm_number_of_runs_in_parallel()
    num_jobs = n_jobs
    if num_jobs < max_jobs:
        max_jobs = num_jobs
    job_name = '--job-name=' + sbatch_script_name
    output = '--output=' + sbatch_script_path + '.txt'
    error = '--error=' + sbatch_script_path + '.err'
    array = '--array=0-' + str(num_jobs - 1) + '%' + str(max_jobs)

    sbatch_options_list = [job_name, output, error, array]
    sbatch_options_list.extend(get_slurm_sbatch_default_options_list())
    # Get user options second to overrule defaults
    sbatch_options_list.extend(get_slurm_sbatch_user_options_list())

    # Create job list
    job_params_list = []

    for i in range(0, num_jobs):
        instance_path = list_jobs[i][0]
        extractor_path = list_jobs[i][1]
        job_params = (f'--instance {instance_path} --extractor {extractor_path} '
                      f'--feature-csv {feature_data_csv_path}')
        job_params_list.append(job_params)

    # Set srun options
    srun_options_str = '-N1 -n1'
    srun_options_str = srun_options_str + ' ' + get_slurm_srun_user_options_str()

    # Create target call
    target_call_str = 'Commands/sparkle_help/compute_features_core.py'

    # Generate script
    generate_sbatch_script_generic(sbatch_script_path, sbatch_options_list,
                                   job_params_list, srun_options_str, target_call_str)

    return sbatch_script_name, sbatch_script_dir


def submit_sbatch_script(sbatch_script_name: str, command_name: CommandName,
                         execution_dir: str = None) -> str:
    '''Submit a Slurm batch script.'''
    if execution_dir is None:
        execution_dir = sgh.smac_dir

    sbatch_script_path = sbatch_script_name
    ori_path = os.getcwd()
    os.system(f'cd {execution_dir} ; chmod a+x {sbatch_script_path} ; cd {ori_path}')
    command = f'cd {execution_dir} ; sbatch {sbatch_script_path} ; cd {ori_path}'

    output_list = os.popen(command).readlines()

    if len(output_list) > 0 and len(output_list[0].strip().split()) > 0:
        jobid = output_list[0].strip().split()[-1]
        # Add job to active job CSV
        sjh.write_active_job(jobid, command_name)
    else:
        jobid = ''

    return jobid
