#!/usr/bin/env python3
"""Sparkle command to configure a solver."""

import argparse
import sys
import os
from pathlib import Path
from pandas import DataFrame

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
from sparkle_help import sparkle_slurm_help as ssh
from sparkle_help.configurator import Configurator
from sparkle_help.configuration_scenario import Configuration_Scenario
from sparkle_help.solver import Solver


def parser_function() -> None:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Configure a solver in the Sparkle platform.",
        epilog=("Note that the test instance set is only used if the ``--ablation``"
                " or ``--validation`` flags are given"))
    parser.add_argument(
        "--configurator",
        type=Path,
        help="path to configurator"
    )
    parser.add_argument(
        "--solver",
        type=Path,
        required=True,
        help="path to solver"
    )
    parser.add_argument(
        "--instance-set-train",
        type=Path,
        required=True,
        help="path to training instance set",
    )
    parser.add_argument(
        "--instance-set-test",
        type=Path,
        required=False,
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

    return parser


def apply_settings_from_args(args) -> None:
    """Apply command line arguments to settings."""
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


def write_latest_config_file(file_path: Path, solver_path: Path, instance_set_path: Path) -> None:
    fout = open(file_path, "w+")
    fout.write(f"solver {solver_path}\n")
    fout.write(f"train {instance_set_path}\n")
    fout.close()


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

    apply_settings_from_args(args)

    validate = args.validate
    ablation = args.ablation
    solver_path = args.solver
    instance_set_train = args.instance_set_train
    instance_set_test = args.instance_set_test
    use_features = args.use_features
    if args.configurator is not None:
        configurator_path = args.configurator
    else:
        configurator_path = Path("smac-v2.10.03-master-778")

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

    sah.clean_ablation_scenarios(solver_path.name, instance_set_train.name)

    full_configurator_path = "Configurators" / configurator_path
    solver = Solver(solver_path)

    feature_file = None
    if use_features:
        feature_file = solver.directory / f"{instance_set_train.name}_features.csv"
        feature_data_df.to_csv(feature_file, index_label="INSTANCE_NAME")

    config_scenario = Configuration_Scenario(solver, instance_set_train, use_features, feature_file)
    configurator = Configurator(full_configurator_path, config_scenario)

    configurator.create_sbatch_script()
    configure_jobid = configurator.configure()

    # Write most recent run to file
    config_file_path = config_scenario.directory / sgh.sparkle_last_configuration_file_name
    write_latest_config_file(config_file_path, solver.directory, instance_set_train)

    # Update latest scenario
    sgh.latest_scenario.set_config_solver(solver.directory)
    sgh.latest_scenario.set_config_instance_set_train(instance_set_train)
    sgh.latest_scenario.set_latest_scenario(Scenario.CONFIGURATION)

    if instance_set_test is not None:
        sgh.latest_scenario.set_config_instance_set_test(instance_set_test)
    else:
        # Set to default to overwrite possible old path
        sgh.latest_scenario.set_config_instance_set_test()

    dependency_jobid_list = [configure_jobid]

    # Set validation to wait until configuration is done
    if validate:
        validate_jobid = ssh.generate_validation_callback_slurm_script(
            solver_path, instance_set_train, instance_set_test, configure_jobid
        )
        dependency_jobid_list.append(validate_jobid)

    if ablation:
        ablation_jobid = ssh.generate_ablation_callback_slurm_script(
            solver_path, instance_set_train, instance_set_test, configure_jobid
        )
        dependency_jobid_list.append(ablation_jobid)

    job_id_str = ",".join(dependency_jobid_list)
    print(f"Running configuration in parallel. Waiting for Slurm job(s) with id(s): "
          f"{job_id_str}")

    # Write used settings to file
    sgh.settings.write_used_settings()
    # Write used scenario to file
    sgh.latest_scenario.write_scenario_ini()
