#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl
            Jeroen Rook, j.g.rook@umail.leidenuniv.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import os
import sys
import fcntl
from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_record_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help import sparkle_run_solvers_help as srs
from sparkle_help import sparkle_experiments_related_help as ser
from sparkle_help import sparkle_add_train_instances_help as satih
from sparkle_help import sparkle_configure_solver_help as scsh

def get_ablation_scenario_directory(solver_name, instance_train_name, instance_test_name):
    ablation_scenario_dir = sgh.ablation_dir + "scenarios/{}_{}_{}/".format(solver_name,
                                                                            instance_train_name,
                                                                            instance_test_name)
    return ablation_scenario_dir

def prepare_ablation_scenario(solver_name, instance_train_name, instance_test_name):
    ablation_scenario_dir = get_ablation_scenario_directory(solver_name, instance_train_name, instance_test_name)
    sfh.checkout_directory(ablation_scenario_dir)
    return ablation_scenario_dir

def create_configuration_file(solver_name, instance_train_name, instance_test_name):
    ablation_scenario_dir = get_ablation_scenario_directory(solver_name, instance_train_name, instance_test_name)

    (optimised_configuration_params, _, _) = scsh.get_optimised_configuration(solver_name, instance_train_name)

    with open("{}/ablation_config.txt".format(ablation_scenario_dir), 'w') as fout:
        fout.write('algo = ./sparkle_smac_wrapper.py\n')
        fout.write('execdir = Solvers/' + solver_name + '\n')
        fout.write('experimentDir = ./{}\n'.format(ablation_scenario_dir))
        fout.write('deterministic = 0\n') #Get from solver
        fout.write('run_obj = runtime\n') #Get from settings
        fout.write('overall_obj = mean\n') #Get from settings
        fout.write('cutoff_time = 600\n')  #Get from settings
        fout.write('cutoff_length = max\n')
        fout.write('seed = 1234\n')
        fout.write('cli-concurrent-execution = true\n')
        fout.write('cli-cores = 32\n')
        fout.write('useRacing = false\n')
        fout.write('paramfile = Solvers/' + solver_name + '/ganak_params.pcs\n') #Get from solver
        fout.write('instance_file = {}/instances_train.txt\n'.format(ablation_scenario_dir))
        fout.write('test_instance_file = {}/instances_test.txt\n'.format(ablation_scenario_dir))
        fout.write('sourceConfiguration=DEFAULT\n')
        fout.write('targetConfiguration="' + optimised_configuration_params + '"')
        fout.close()

    return


def create_instance_file(instances_directory, ablation_scenario_dir, train_or_test):
    file_suffix = r''
    if train_or_test == r'train':
        file_suffix = r'_train.txt'
    elif train_or_test == r'test':
        file_suffix = r'_test.txt'
    else:
        print(r'c Invalid function call of \'copy_instances_to_ablation\'; aborting execution')
        sys.exit()

    list_all_path = satih.get_list_all_path(instances_directory)
    file_instance_path = ablation_scenario_dir + "instances" + file_suffix
    with open(file_instance_path,"w") as fh:
        for instance in list_all_path:
            fh.write("{}\n".format(instance))
        fh.close()
