#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl
            Jeroen Rook, j.g.rook@umail.leidenuniv.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

#TODO: Read settingsfile
#TODO: Dedicated ablations settings file or copy from settings?
#TODO: Check for conflicts between settings (slurm vs ablation, smac vs ablation)
#TODO: SLURM and ABLATION run over multiple nodes (-n64 -c1 for example) -> srun in wrapper
#TODO: Move log files to dedicated directories
#TODO: Handle tmp files
#TODO: Add to logger made by Koen

import argparse
import os
import sys
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_run_ablation_help as sah
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_configure_solver_help as scsh
from sparkle_help import sparkle_add_train_instances_help as satih
from sparkle_help import sparkle_slurm_help as ssh
from sparkle_help import sparkle_logging as sl


if __name__ == r'__main__':
    sl.log_command(sys.argv)

	#Load solver and test instances
    parser = argparse.ArgumentParser()
    parser.add_argument('--solver', required=False, type=str, help='path to solver')
    parser.add_argument('--instance-set-train', required=False, type=str, help='path to training instance set')
    parser.add_argument('--instance-set-test', required=False, type=str, help='path to testing instance set')
    parser.add_argument('--ablation-settings-help', required=False, dest="ablation_settings_help", action="store_true", help='prints a list of setting that can be used for the ablation analysis')
    parser.set_defaults(ablation_settings_help=False)
    args = parser.parse_args()

    if(args.ablation_settings_help):
        sah.print_ablation_help()
        exit()

    solver = args.solver
    instance_set_train = args.instance_set_train
    instance_set_test = args.instance_set_test

    solver_name = sfh.get_last_level_directory_name(solver)
    instance_set_train_name = sfh.get_last_level_directory_name(instance_set_train)
    instance_set_test_name = None
    if instance_set_test is not None:
        instance_set_test_name = sfh.get_last_level_directory_name(instance_set_test)
    print(solver_name, instance_set_train_name, instance_set_test_name)

    #DEVELOP: REMOVE SCENARIO
    ablation_scenario_dir = sah.get_ablation_scenario_directory(solver_name, instance_set_train_name, instance_set_test_name)
    os.system("rm -rf {}".format(sgh.ablation_dir+ablation_scenario_dir))

    #Prepare ablation scenario directory
    ablation_scenario_dir = sah.prepare_ablation_scenario(solver_name, instance_set_train_name, instance_set_test_name)
    print(ablation_scenario_dir)

    #Instances
    sah.create_instance_file(instance_set_train, ablation_scenario_dir, "train")
    if instance_set_test_name is not None:
        sah.create_instance_file(instance_set_test, ablation_scenario_dir, "test")
    else:
        sah.create_instance_file(instance_set_train, ablation_scenario_dir, "test")

    print("c Create config file")
    #Configurations
    sah.create_configuration_file(solver_name, instance_set_train_name, instance_set_test_name)
    #Add instances

    print("c Submit ablation run")
    #Submit ablation run
    #TODO: Move to help
    sbatch_script_path = sah.generate_slurm_script(solver_name, instance_set_train_name, instance_set_test_name)
    print("c Created {}".format(sbatch_script_path))
    jobid = ssh.submit_sbatch_script(sbatch_script_path, sgh.ablation_dir)
    print("c Launched sbatch script '{}' with jobid {}".format(sbatch_script_path,jobid))

    #Submit intermediate actions (copy path from log)
    sbatch_script_path = sah.generate_callback_slurm_script(solver_name, instance_set_train_name, instance_set_test_name,
                                                   dependency=jobid)
    jobid = ssh.submit_sbatch_script(sbatch_script_path, sgh.ablation_dir)
    print("c Launched callback sbatch script '{}' with jobid {}".format(sbatch_script_path, jobid))

    #Submit ablation validation run when nessesary
    if instance_set_test is not None:
        sbatch_script_path = sah.generate_validation_slurm_script(solver_name, instance_set_train_name, instance_set_test_name,
                                                       dependency=jobid)
        jobid = ssh.submit_sbatch_script(sbatch_script_path, sgh.ablation_dir)
        print("c Launched validation sbatch script '{}' with jobid {}".format(sbatch_script_path, jobid))

        # Submit intermediate actions (copy validation table from log)
        sbatch_script_path = sah.generate_validation_callback_slurm_script(solver_name, instance_set_train_name,
                                                                instance_set_test_name, dependency=jobid)
        jobid = ssh.submit_sbatch_script(sbatch_script_path, sgh.ablation_dir)
        print("c Launched validation callback sbatch script '{}' with jobid {}".format(sbatch_script_path, jobid))