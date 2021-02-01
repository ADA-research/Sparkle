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
import re
from pathlib import Path
from pathlib import PurePath

from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_instances_help as sih
from sparkle_help import sparkle_configure_solver_help as scsh
from sparkle_help import sparkle_slurm_help as ssh
from sparkle_help import sparkle_add_solver_help as sash


'''
exec_path: overwrite of the default ablation path to put the scenario in
'''
def get_ablation_scenario_directory(solver_name, instance_train_name, instance_test_name,exec_path=False):
    instance_test_name = "_{}".format(instance_test_name) if instance_test_name is not None else ""

    ablation_scenario_dir = "" if exec_path else sgh.ablation_dir
    ablation_scenario_dir += "scenarios/{}_{}{}/".format(solver_name,
                                                        instance_train_name,
                                                        instance_test_name)
    return ablation_scenario_dir

def prepare_ablation_scenario(solver_name, instance_train_name, instance_test_name):
    ablation_scenario_dir = get_ablation_scenario_directory(solver_name,
                                                            instance_train_name,
                                                            instance_test_name)
    ablation_scenario_solver_dir = PurePath(ablation_scenario_dir, "solver/")

    sfh.checkout_directory(ablation_scenario_dir)
    sfh.checkout_directory(str(ablation_scenario_solver_dir))

    #copy ablation executables to isolated scenario directory
    copy_candidates = ["conf/","lib/","ablationAnalysis","ablationAnalysis.jar","ablationValidation","LICENSE.txt","README.txt"]
    for candidate in copy_candidates:
        recursive = "-r" if candidate[-1] == "/" else ""
        candidate_path = str(PurePath(sgh.ablation_dir,candidate))
        cmd = "cp {} {} {}".format(recursive, candidate_path, ablation_scenario_dir)
        os.system(cmd)

    #copy solver
    solver_directory = r'Solvers/' + solver_name + r'/*'
    cmd = "cp -r {} {}".format(solver_directory, ablation_scenario_solver_dir)
    os.system(cmd)

    return ablation_scenario_dir

def print_ablation_help():
    call = "./{}/ablationAnalysis -h".format(sgh.ablation_dir)
    print(os.system(call))

''' DEPRICATED
def get_ablation_settings(path_modifier = None):
    #TODO: Remove
    ablation_settings = {
        "deterministic": "0",
        "run_obj": "runtime",
        "overall_obj": "mean10",
        "cutoff_time": 60,
        "cutoff_length": "max",
        "seed": "1234",
        "cli-concurrent-execution": "true",
        "cli-cores": 32,
        "useRacing": "false",
        "consoleLogLevel": "INFO",
    }

    if path_modifier is None:
        path_modifier = ''

    sparkle_ablation_settings_path = str(path_modifier) + sgh.sparkle_ablation_settings_path

    settings_file = open(sparkle_ablation_settings_path, 'r')
    for line in settings_file:
        line = line.strip()
        if len(line) > 2:
            if line[:2] == "--":
                setting = line[2:].split("=")
                if len(setting) == 2:
                    ablation_settings[setting[0].strip()] = setting[1].strip()
    settings_file.close()

    return ablation_settings
'''

def get_slurm_params(solver_name, instance_train_name, instance_test_name, postfix="",dependency=None):
    if instance_test_name is not None:
        sbatch_script_name = "ablation_{}_{}_{}".format(solver_name, instance_train_name, instance_test_name)
    else:
        sbatch_script_name = "ablation_{}_{}".format(solver_name, instance_train_name)
    sbatch_script_name += "{}".format(postfix)

    scenario_dir = get_ablation_scenario_directory(solver_name, instance_train_name, instance_test_name, exec_path=True)
    concurrent_clis = sgh.settings.get_slurm_clis_per_node()

    job_name = '--job-name=' + sbatch_script_name
    output = '--output=' + sbatch_script_name + '.txt'
    error = '--error=' + sbatch_script_name + '.err'
    cpus = '--cpus-per-task={}'.format(concurrent_clis)

    sbatch_options_list = [job_name, output, error, cpus]

    if dependency is not None:
        sbatch_options_list.append("--dependency=afterany:{}".format(dependency))

    sbatch_options_list.extend(ssh.get_slurm_sbatch_user_options_list())

    return (scenario_dir, sbatch_script_name,sbatch_options_list)

def generate_slurm_script(solver_name, instance_train_name, instance_test_name, dependency=None):
    scenario_dir, sbatch_script_name, sbatch_options_list = get_slurm_params(solver_name,
                                                                             instance_train_name,
                                                                             instance_test_name,
                                                                             postfix="",
                                                                             dependency=dependency)
    sbatch_script_name = sbatch_script_name + ".sh"
    sbatch_script_path = scenario_dir + sbatch_script_name

    concurrent_clis = sgh.settings.get_slurm_clis_per_node()
    srun_options_str = "-N1 -n1 -c{}".format(concurrent_clis)
    target_call_str = "./ablationAnalysis --optionFile ablation_config.txt".format(sgh.ablation_dir, scenario_dir)

    job_params_list = []
    ssh.generate_sbatch_script_generic(sgh.ablation_dir+sbatch_script_path, sbatch_options_list, job_params_list, srun_options_str, target_call_str)

    return sbatch_script_name

def generate_callback_slurm_script(solver_name, instance_train_name, instance_test_name, dependency=None):
    scenario_dir, sbatch_script_name, sbatch_options_list = get_slurm_params(solver_name,
                                                                             instance_train_name,
                                                                             instance_test_name,
                                                                             postfix="_callback",
                                                                             dependency=dependency)
    sbatch_script_name = sbatch_script_name + ".sh"
    sbatch_script_path = scenario_dir + sbatch_script_name

    callback_script_name =  "callback.sh"
    callback_script_path = scenario_dir + callback_script_name
    log_path = sgh.sparkle_global_log_dir + "Ablation/" + sbatch_script_name + "/"

    sfh.checkout_directory(log_path)
    with open(sgh.ablation_dir + callback_script_path, "w") as fh:
        fh.write("#!/bin/bash\n")
        fh.write("# Automatically generated by SPARKLE\n\n")
        #fh.write("cd {}\n".format(sgh.ablation_dir))
        fh.write("cp log/ablation-run1234.txt ablationPath.txt\n".format(scenario_dir))
        rollback = "../"*(len(scenario_dir.split("/"))+1)
        fh.write("cp -r log/ {0}{1}\n".format(rollback, log_path))
        fh.close()
    os.system("chmod 755 {}".format(sgh.ablation_dir + callback_script_path))

    srun_options_str = "-N1 -n1 -c1 --mem-per-cpu=1000"
    target_call_str = callback_script_name


    job_params_list = []
    ssh.generate_sbatch_script_generic(sgh.ablation_dir+sbatch_script_path, sbatch_options_list, job_params_list, srun_options_str,
                                       target_call_str)

    return sbatch_script_name

def generate_validation_slurm_script(solver_name, instance_train_name, instance_test_name, dependency=None):
    scenario_dir, sbatch_script_name, sbatch_options_list = get_slurm_params(solver_name,
                                                                             instance_train_name,
                                                                             instance_test_name,
                                                                             postfix="_validation",
                                                                             dependency=dependency)
    sbatch_script_name = sbatch_script_name + ".sh"
    sbatch_script_path = scenario_dir + sbatch_script_name

    concurrent_clis = sgh.settings.get_slurm_clis_per_node()
    srun_options_str = "-N1 -n1 -c{}".format(concurrent_clis)
    target_call_str = "./ablationValidation --optionFile ablation_config.txt --ablationLogFile ablationPath.txt".format(sgh.ablation_dir, scenario_dir)

    job_params_list = []
    ssh.generate_sbatch_script_generic(sgh.ablation_dir+sbatch_script_path, sbatch_options_list, job_params_list, srun_options_str, target_call_str)

    return sbatch_script_name

def generate_validation_callback_slurm_script(solver_name, instance_train_name, instance_test_name, dependency=None):
    scenario_dir, sbatch_script_name, sbatch_options_list = get_slurm_params(solver_name,
                                                                             instance_train_name,
                                                                             instance_test_name,
                                                                             postfix="_validation_callback",
                                                                             dependency=dependency)
    sbatch_script_name = sbatch_script_name + ".sh"
    sbatch_script_path = scenario_dir + sbatch_script_name

    callback_script_name = "validation_callback.sh"
    callback_script_path = scenario_dir + callback_script_name

    log_path = sgh.sparkle_global_log_dir + "Ablation/" + sbatch_script_name + "_validation/"

    sfh.checkout_directory(log_path)
    with open(sgh.ablation_dir + callback_script_path, "w") as fh:
        fh.write("#!/bin/bash\n")
        fh.write("# Automatically generated by SPARKLE\n\n")
        #fh.write("cd {}\n".format(sgh.ablation_dir))
        fh.write("cp log/ablation-validation-run1234.txt ablationValidation.txt\n".format(scenario_dir))
        rollback = "../"*(len(sgh.ablation_dir.split("/"))+1)
        fh.write("cp -r log/ {0}{1}\n".format(rollback, log_path))
        fh.close()
    os.system("chmod 755 {}".format(sgh.ablation_dir + callback_script_path))

    srun_options_str = "-N1 -n1 -c1 --mem-per-cpu=1000"
    target_call_str = callback_script_name


    job_params_list = []
    ssh.generate_sbatch_script_generic(sgh.ablation_dir+sbatch_script_path, sbatch_options_list, job_params_list, srun_options_str,
                                       target_call_str)

    return sbatch_script_name

def create_configuration_file(solver_name, instance_train_name, instance_test_name):
    ablation_scenario_dir = get_ablation_scenario_directory(solver_name,
                                                            instance_train_name,
                                                            instance_test_name)
    ablation_scenario_dir_exec = get_ablation_scenario_directory(solver_name,
                                                                 instance_train_name,
                                                                 instance_test_name,
                                                                 exec_path=True)

    (optimised_configuration_params, _, _) = scsh.get_optimised_configuration(solver_name, instance_train_name)

    smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time, smac_each_run_cutoff_length, num_of_smac_run_str, num_of_smac_run_in_parallel_str = scsh.get_smac_settings()
    concurrent_clis = sgh.settings.get_slurm_clis_per_node()
    ablation_racing = sgh.settings.get_ablation_racing_flag()

    with open("{}/ablation_config.txt".format(ablation_scenario_dir), 'w') as fout:
        fout.write('algo = ./sparkle_smac_wrapper.py\n')
        fout.write('execdir = ./solver/\n')
        fout.write('experimentDir = ./\n')

        #FROM SETTINGS FILE
        #for variable, param in ablation_settings.items():
        #    fout.write("{} = {}\n".format(variable,param))

        #USER SETTINGS
        fout.write('deterministic = ' + scsh.get_solver_deterministic(solver_name) + '\n')
        fout.write('run_obj = ' + smac_run_obj + '\n')
        fout.write('overall_obj = {}\n'.format("MEAN10"  if smac_run_obj == "RUNTIME" else "MEAN"))
        fout.write('cutoffTime = ' + str(smac_each_run_cutoff_time) + '\n')
        fout.write('cutoff_length = ' + str(smac_each_run_cutoff_length) + '\n')
        fout.write('cli-cores = {}\n'.format(concurrent_clis))
        fout.write('useRacing = {}\n'.format(ablation_racing))

        fout.write('seed = 1234\n')
        # Get PCS file name from solver directory
        solver_directory = 'Solvers/' + solver_name
        pcs_file_name = sash.get_pcs_file_from_solver_directory(solver_directory)
        pcs_file_path = './solver/' + pcs_file_name
        fout.write('paramfile = ' + pcs_file_path + '\n')
        fout.write('instance_file = instances_train.txt\n')
        fout.write('test_instance_file = instances_test.txt\n')
        fout.write('sourceConfiguration=DEFAULT\n')
        fout.write('targetConfiguration="' + optimised_configuration_params + '"')
        fout.close()
    return

def create_instance_file(instances_directory, ablation_scenario_dir, train_or_test):
    if train_or_test == r'train':
        file_suffix = r'_train.txt'
    elif train_or_test == r'test':
        file_suffix = r'_test.txt'
    else:
        print(r'c Invalid function call of \'copy_instances_to_ablation\'; aborting execution')
        sys.exit()

    if instances_directory[-1] != "/":
        instances_directory += "/"
    print("c create_instance_file ({}, {}, {})".format(instances_directory, ablation_scenario_dir, train_or_test))
    list_all_path = sih.get_list_all_path(instances_directory)
    #print(list_all_path)
    file_instance_path = ablation_scenario_dir + "instances" + file_suffix

    #relative path
    pwd = os.getcwd()
    full_ablation_scenario_dir = os.path.join(pwd, ablation_scenario_dir, "solver/")
    full_instances_directory = os.path.join(pwd, instances_directory)
    relative_instance_directory = os.path.relpath(full_instances_directory, full_ablation_scenario_dir)

    instance_set_name = Path(instances_directory).name

    # If a reference list does not exist this is a single-file instance
    if not sih.check_existence_of_reference_instance_list(instance_set_name):
        list_all_path = [instance[len(instances_directory):] for instance in list_all_path]
    
        with open(file_instance_path, "w") as fh:
            for instance in list_all_path:
                instance_path = "{}\n".format(os.path.join(relative_instance_directory, instance))
                fh.write(instance_path)

            fh.close()
    # Otherwise this is a multi-file instance, and instances need to be wrapped in quotes with function below
    # TODO: Check whether this function also works for single-file instances and can be used in all cases
    else:
        relative_instance_directory = relative_instance_directory + '/'
        sih.copy_reference_instance_list(Path(file_instance_path), instance_set_name, relative_instance_directory)

    return

def check_for_ablation(solver_name, instance_train_name, instance_test_name):
    scenario_dir = get_ablation_scenario_directory(solver_name, instance_train_name, instance_test_name, exec_path=False)
    table_file = Path(scenario_dir, "ablationValidation.txt")
    return table_file.is_file()

def get_ablation_table(solver_name, instance_train_name, instance_test_name):
    if not check_for_ablation(solver_name, instance_train_name, instance_test_name):
        #No ablation table exists for this solver-instance pair
        return dict()
    scenario_dir = get_ablation_scenario_directory(solver_name, instance_train_name, instance_test_name, exec_path=False)
    print(scenario_dir)
    table_file = os.path.join(scenario_dir, "ablationValidation.txt")

    results = [["Round", "Flipped parameter", "Source value", "Target value", "Validation result"]]

    with open(table_file, "r") as fh:
        for line in fh.readlines():
            values = re.sub("\s+"," ",line.strip())
            values = re.sub(", ",",",values)
            values = [val.replace(",",", ") for val in values.split(' ')]
            if len(values) == 5:
               results.append(values)

        fh.close()

    return results
