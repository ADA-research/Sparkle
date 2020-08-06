#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl
            Jeroen Rook, j.g.rook@umail.leidenuniv.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import argparse
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_run_ablation_help as sah
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_configure_solver_help as scsh
from sparkle_help import sparkle_add_train_instances_help as satih


if __name__ == r'__main__':
	#Load solver and test instances
    parser = argparse.ArgumentParser()
    parser.add_argument('--solver', required=True, type=str, help='path to solver')
    parser.add_argument('--instance-set-train', required=True, type=str, help='path to training instance set')
    parser.add_argument('--instance-set-test', required=False, type=str, help='path to testing instance set')
    args = parser.parse_args()

    solver = args.solver
    instance_set_train = args.instance_set_train
    instance_set_test = args.instance_set_test

    solver_name = sfh.get_last_level_directory_name(solver)
    instance_set_train_name = sfh.get_last_level_directory_name(instance_set_train)
    instance_set_test_name = None
    if instance_set_test is not None:
        instance_set_test_name = sfh.get_last_level_directory_name(instance_set_test)
    print(solver_name, instance_set_train_name, instance_set_test_name)

    #Prepare ablation scenario directory

    ablation_scenario_dir = sah.prepare_ablation_scenario(solver_name, instance_set_train_name, instance_set_test_name)
    print(ablation_scenario_dir)

    #Instances
    sah.create_instance_file(instance_set_train, ablation_scenario_dir, "train")
    sah.create_instance_file(instance_set_test, ablation_scenario_dir, "test")

    #Configurations
    sah.create_configuration_file(solver_name, instance_set_train_name, instance_set_test_name)
    #Add instances

    #Submit ablation run