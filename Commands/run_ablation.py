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
import os
import sys
from pathlib import Path

from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_run_ablation_help as sah
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_configure_solver_help as scsh
from sparkle_help import sparkle_add_train_instances_help as satih
from sparkle_help import sparkle_slurm_help as ssh
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings
from sparkle_help.sparkle_settings import PerformanceMeasure
from sparkle_help.sparkle_settings import SettingState
from sparkle_help import argparse_custom as ac

if __name__ == r'__main__':
    # Initialise settings
    global settings
    sgh.settings = sparkle_settings.Settings()

    sl.log_command(sys.argv)

    #Load solver and test instances
    parser = argparse.ArgumentParser()
    parser.add_argument('--solver', required=False, type=str, help='path to solver')
    parser.add_argument('--instance-set-train', required=False, type=str, help='path to training instance set')
    parser.add_argument('--instance-set-test', required=False, type=str, help='path to testing instance set')
    parser.add_argument('--ablation-settings-help', required=False, dest="ablation_settings_help", action="store_true", help='prints a list of setting that can be used for the ablation analysis')
    parser.add_argument('--performance-measure', choices=PerformanceMeasure.__members__, default=sgh.settings.DEFAULT_general_performance_measure, action=ac.SetByUser, help='the performance measure, e.g. runtime')
    parser.add_argument('--target-cutoff-time', type=int, default=sgh.settings.DEFAULT_general_target_cutoff_time, action=ac.SetByUser, help='cutoff time per target algorithm run in seconds')
    parser.add_argument('--budget-per-run', type=int, default=sgh.settings.DEFAULT_config_budget_per_run, action=ac.SetByUser, help='configuration budget per configurator run in seconds')
    parser.add_argument('--number-of-runs', type=int, default=sgh.settings.DEFAULT_config_number_of_runs, action=ac.SetByUser, help='number of configuration runs to execute')
    parser.add_argument('--racing', type=bool, default=sgh.settings.DEFAULT_ablation_racing, action=ac.SetByUser, help='performs abaltion analysis with racing')
    parser.add_argument('--settings-file', type=Path, default=sgh.settings.DEFAULT_settings_path, action=ac.SetByUser, help='specify the settings file to use in case you want to use one other than the default')
    parser.set_defaults(ablation_settings_help=False)
    args = parser.parse_args()

    if(args.ablation_settings_help):
        sah.print_ablation_help()
        exit()

    solver = args.solver
    instance_set_train = args.instance_set_train
    instance_set_test = args.instance_set_test

    if ac.set_by_user(args, 'settings_file'):
        sgh.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)  # Do first, so other command line options can override settings from the file
        args.performance_measure = PerformanceMeasure.from_str(args.performance_measure)
    if ac.set_by_user(args, 'performance_measure'): sgh.settings.set_general_performance_measure(args.performance_measure, SettingState.CMD_LINE)
    if ac.set_by_user(args, 'target_cutoff_time'): sgh.settings.set_general_target_cutoff_time(args.target_cutoff_time, SettingState.CMD_LINE)
    if ac.set_by_user(args, 'budget_per_run'): sgh.settings.set_config_budget_per_run(args.budget_per_run, SettingState.CMD_LINE)
    if ac.set_by_user(args, 'number_of_runs'): sgh.settings.set_config_number_of_runs(args.number_of_runs, SettingState.CMD_LINE)
    if ac.set_by_user(args, 'racing'): sgh.settings.set_ablation_racing_flag(args.number_of_runs, SettingState.CMD_LINE)

    solver_name = sfh.get_last_level_directory_name(solver)
    instance_set_train_name = sfh.get_last_level_directory_name(instance_set_train)
    instance_set_test_name = None
    if instance_set_test is not None:
        instance_set_test_name = sfh.get_last_level_directory_name(instance_set_test)
    else:
        instance_set_test = instance_set_train
        instance_set_test_name = instance_set_train_name
    #print(solver_name, instance_set_train_name, instance_set_test_name)

    if not scsh.check_configuration_exists(solver_name, instance_set_train_name):
        print('c Error: No configuration results found for the given solver and training instance set. Ablation needs to have a target configuration. Please run configuration first')
        sys.exit(-1)
    else:
        print("c Configuration exists!")

    #REMOVE SCENARIO
    ablation_scenario_dir = sah.get_ablation_scenario_directory(solver_name, instance_set_train_name, instance_set_test_name)
    if sah.check_for_ablation(solver_name, instance_set_train_name, instance_set_test_name):
        print("c Warning: found existing ablation scenario for this combination. This will be removed.")
        os.system("rm -rf {}".format(sgh.ablation_dir+ablation_scenario_dir))

    #Prepare ablation scenario directory
    ablation_scenario_dir = sah.prepare_ablation_scenario(solver_name, instance_set_train_name, instance_set_test_name)
    print("c Scenario dir: {}".format(ablation_scenario_dir))

    #Instances
    sah.create_instance_file(instance_set_train, ablation_scenario_dir, "train")
    if instance_set_test_name is not None:
        sah.create_instance_file(instance_set_test, ablation_scenario_dir, "test")
    else:
        #TODO: check if needed
        sah.create_instance_file(instance_set_train, ablation_scenario_dir, "test")

    print("c Create config file")
    #Configurations
    sah.create_configuration_file(solver_name, instance_set_train_name, instance_set_test_name)
    print("c Submit ablation run")
    #Submit ablation run
    #TODO: Move to help
    sbatch_script_path = sah.generate_slurm_script(solver_name, instance_set_train_name, instance_set_test_name)
    print("c Created {}".format(sbatch_script_path))

    jobid = ssh.submit_sbatch_script(sbatch_script_path, ablation_scenario_dir)
    print("c Launched sbatch script '{}' with jobid {}".format(sbatch_script_path,jobid))

    #Submit intermediate actions (copy path from log)
    sbatch_script_path = sah.generate_callback_slurm_script(solver_name, instance_set_train_name, instance_set_test_name,
                                                            dependency=jobid)
    jobid = ssh.submit_sbatch_script(sbatch_script_path, ablation_scenario_dir)
    print("c Launched callback sbatch script '{}' with jobid {}".format(sbatch_script_path, jobid))

    #Submit ablation validation run when nessesary
    if instance_set_test is not None:
        sbatch_script_path = sah.generate_validation_slurm_script(solver_name, instance_set_train_name, instance_set_test_name,
                                                                  dependency=jobid)
        jobid = ssh.submit_sbatch_script(sbatch_script_path, ablation_scenario_dir)
        print("c Launched validation sbatch script '{}' with jobid {}".format(sbatch_script_path, jobid))

        # Submit intermediate actions (copy validation table from log)
        sbatch_script_path = sah.generate_validation_callback_slurm_script(solver_name, instance_set_train_name,
                                                                           instance_set_test_name, dependency=jobid)
        jobid = ssh.submit_sbatch_script(sbatch_script_path, ablation_scenario_dir)
        print("c Launched validation callback sbatch script '{}' with jobid {}".format(sbatch_script_path, jobid))