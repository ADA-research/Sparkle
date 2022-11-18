#!/usr/bin/env python3
"""Sparkle command to configure a solver."""

import argparse
import sys
import os
from pathlib import Path
from pandas import DataFrame

from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_add_solver_help as sash
from sparkle_help import sparkle_configure_solver_help as scsh
from sparkle_help import sparkle_instances_help as sih
from sparkle_help import sparkle_logging as sl
from sparkle_help import sparkle_settings
from sparkle_help import sparkle_run_ablation_help as sah
from sparkle_help.sparkle_settings import PerformanceMeasure
from sparkle_help.sparkle_settings import SettingState
from sparkle_help import argparse_custom as ac
from sparkle_help.reporting_scenario import ReportingScenario
from sparkle_help.reporting_scenario import Scenario
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv


def parser_function():
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Configure a solver in the Sparkle platform.",
        epilog=("Note that the test instance set is only used if the ``-–ablation`"
                " or ``–-validation`` flags are given"))
    parser.add_argument(
        "--validate",
        required=False,
        action="store_true",
        help="validate after configuration",
    )
    parser.add_argument(
        "--ablation",
        required=False,
        action="store_true",
        help="run ablation after configuration",
    )
    parser.add_argument(
        "--solver",
        required=True,
        type=str,
        help="path to solver"
    )
    parser.add_argument(
        "--instance-set-train",
        required=True,
        type=str,
        help="path to training instance set",
    )
    parser.add_argument(
        "--instance-set-test",
        required=False,
        type=str,
        help="path to testing instance set (only for validating)",
    )
    parser.add_argument(
        "--performance-measure",
        choices=PerformanceMeasure.__members__,
        default=sgh.settings.DEFAULT_general_performance_measure,
        action=ac.SetByUser,
        help="the performance measure, e.g. runtime",
    )
    parser.add_argument(
        "--target-cutoff-time",
        type=int,
        default=sgh.settings.DEFAULT_general_target_cutoff_time,
        action=ac.SetByUser,
        help="cutoff time per target algorithm run in seconds",
    )
    parser.add_argument(
        "--budget-per-run",
        type=int,
        default=sgh.settings.DEFAULT_config_budget_per_run,
        action=ac.SetByUser,
        help="configuration budget per configurator run in seconds",
    )
    parser.add_argument(
        "--number-of-runs",
        type=int,
        default=sgh.settings.DEFAULT_config_number_of_runs,
        action=ac.SetByUser,
        help="number of configuration runs to execute",
    )
    parser.add_argument(
        "--settings-file",
        type=Path,
        default=sgh.settings.DEFAULT_settings_path,
        action=ac.SetByUser,
        help="specify the settings file to use instead of the default",
    )
    parser.add_argument(
        "--use-features",
        required=False,
        action="store_true",
        help="use the training set's features for configuration",
    )

    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    sgh.settings = sparkle_settings.Settings()

    # Initialise latest scenario
    global latest_scenario
    sgh.latest_scenario = ReportingScenario()

    # Log command call
    sl.log_command(sys.argv)

    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    validate = args.validate
    ablation = args.ablation
    solver = args.solver
    instance_set_train = args.instance_set_train
    instance_set_test = args.instance_set_test
    use_features = args.use_features

    if use_features:
        feature_data_csv = sfdcsv.SparkleFeatureDataCSV(sgh.feature_data_csv_path)

        if not Path(instance_set_train).is_dir():  # Path has to be a directory
            print("given training set path is not an existing directory")
            sys.exit()

        # Takes folder/instance set name from training set path
        set_name = os.path.split(os.path.split(instance_set_train)[0])[1]
        data_dict = {}
        feature_data_df = feature_data_csv.dataframe

        for label, row in feature_data_df.iterrows():
            # os.path.split(os.path.split(label)[0])[1] gives the dir/instance set name
            if os.path.split(os.path.split(label)[0])[1] == set_name:
                if row.empty:
                    print("No feature data exists for the given training set, please "
                          "run add_feature_extractor.py, then compute_features.py")
                    sys.exit()

                new_label = f"../../instances/{set_name}/{os.path.split(label)[1]}"
                data_dict[new_label] = row

        feature_data_df = DataFrame.from_dict(data_dict, orient="index",
                                              columns=feature_data_df.columns)

        if feature_data_df.isnull().values.any():
            print("You have unfinished feature computation jobs, please run "
                  "compute_features.py")
            sys.exit()

        for index, column in enumerate(feature_data_df):
            feature_data_df.rename(columns={column: f"Feature{index+1}"}, inplace=True)

    if ac.set_by_user(args, "settings_file"):
        sgh.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file
    if ac.set_by_user(args, "performance_measure"):
        sgh.settings.set_general_performance_measure(
            PerformanceMeasure.from_str(args.performance_measure), SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "target_cutoff_time"):
        sgh.settings.set_general_target_cutoff_time(
            args.target_cutoff_time, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "budget_per_run"):
        sgh.settings.set_config_budget_per_run(
            args.budget_per_run, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "number_of_runs"):
        sgh.settings.set_config_number_of_runs(
            args.number_of_runs, SettingState.CMD_LINE
        )

    solver_name = sfh.get_last_level_directory_name(solver)
    instance_set_train_name = sfh.get_last_level_directory_name(instance_set_train)
    instance_set_test_name = None

    if instance_set_test is not None:
        instance_set_test_name = sfh.get_last_level_directory_name(instance_set_test)

    # Check if solver has pcs file and is configurable
    solver_directory = sash.get_solver_directory(solver_name)
    if not sash.check_adding_solver_contain_pcs_file(solver_directory):
        print(
            "None or multiple .pcs files found. Solver is not valid for configuration."
        )
        sys.exit()

    # Clean the configuration and ablation directories for this solver to make sure
    # we start with a clean slate
    scsh.clean_configuration_directory(solver_name, instance_set_train_name)
    sah.clean_ablation_scenarios(solver_name, instance_set_train_name)

    # Copy instances to smac directory
    instances_directory = "Instances/" + instance_set_train_name
    list_all_path = sih.get_list_all_path(instances_directory)
    smac_inst_dir_prefix = (
        sgh.smac_dir
        + "/"
        + "example_scenarios/"
        + "instances/"
        + sfh.get_last_level_directory_name(instances_directory)
    )
    sih.copy_instances_to_smac(
        list_all_path, instances_directory, smac_inst_dir_prefix, "train"
    )
    if use_features:
        smac_solver_dir = scsh.get_smac_solver_dir(solver_name, instance_set_train_name)
        feature_file_name = f"{smac_solver_dir}{instance_set_train_name}_features.csv"
        feature_data_df.to_csv(feature_file_name, index_label="INSTANCE_NAME")

    scsh.handle_file_instance(
        solver_name, instance_set_train_name, instance_set_train_name, "train"
    )
    scsh.create_file_scenario_configuration(solver_name, instance_set_train_name,
                                            use_features)
    scsh.prepare_smac_execution_directories_configuration(
        solver_name, instance_set_train_name
    )
    smac_configure_sbatch_script_name = scsh.create_smac_configure_sbatch_script(
        solver_name, instance_set_train_name
    )
    configure_jobid = scsh.submit_smac_configure_sbatch_script(
        smac_configure_sbatch_script_name
    )

    dependency_jobid_list = [configure_jobid]

    # Write most recent run to file
    last_configuration_file_path = (
        sgh.smac_dir
        + "/example_scenarios/"
        + solver_name
        + "_"
        + instance_set_train_name
        + "/"
        + sgh.sparkle_last_configuration_file_name
    )

    fout = open(last_configuration_file_path, "w+")
    fout.write("solver " + str(solver) + "\n")
    fout.write("train " + str(instance_set_train) + "\n")
    fout.close()

    # Update latest scenario
    sgh.latest_scenario.set_config_solver(Path(solver))
    sgh.latest_scenario.set_config_instance_set_train(Path(instance_set_train))
    sgh.latest_scenario.set_latest_scenario(Scenario.CONFIGURATION)

    if instance_set_test is not None:
        sgh.latest_scenario.set_config_instance_set_test(Path(instance_set_test))
    else:
        # Set to default to overwrite possible old path
        sgh.latest_scenario.set_config_instance_set_test()

    # Set validation to wait until configuration is done
    if validate:
        validate_jobid = scsh.generate_validation_callback_slurm_script(
            solver, instance_set_train, instance_set_test, configure_jobid
        )
        dependency_jobid_list.append(validate_jobid)

    if ablation:
        ablation_jobid = scsh.generate_ablation_callback_slurm_script(
            solver, instance_set_train, instance_set_test, configure_jobid
        )
        dependency_jobid_list.append(ablation_jobid)

    job_id_str = ",".join(dependency_jobid_list)
    print(f"Running configuration in parallel. Waiting for Slurm job(s) with id(s): "
          f"{job_id_str}")

    # Write used settings to file
    sgh.settings.write_used_settings()
    # Write used scenario to file
    sgh.latest_scenario.write_scenario_ini()
