#!/usr/bin/env python3
"""Sparkle command to configure a solver."""

import argparse
import sys
import os
from pathlib import Path
from pandas import DataFrame

from Commands.Structures.status_info import ConfigureSolverStatusInfo
from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_logging as sl
from Commands.sparkle_help import sparkle_settings
from Commands.sparkle_help import sparkle_run_ablation_help as sah
from Commands.sparkle_help.sparkle_settings import PerformanceMeasure
from Commands.sparkle_help.sparkle_settings import SettingState
from Commands.sparkle_help.reporting_scenario import ReportingScenario
from Commands.sparkle_help.reporting_scenario import Scenario
from Commands.sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from Commands.sparkle_help import sparkle_slurm_help as ssh
from Commands.sparkle_help import sparkle_command_help as sch
from Commands.sparkle_help.configurator import Configurator
from Commands.sparkle_help.configuration_scenario import ConfigurationScenario
from Commands.sparkle_help.solver import Solver

from runrunner.base import Runner


def parser_function() -> argparse.ArgumentParser:
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
        help="the performance measure, e.g. runtime",
    )
    parser.add_argument(
        "--target-cutoff-time",
        type=int,
        help="cutoff time per target algorithm run in seconds",
    )
    parser.add_argument(
        "--budget-per-run",
        type=int,
        help="configuration budget per configurator run in seconds",
    )
    parser.add_argument(
        "--number-of-runs",
        type=int,
        help="number of configuration runs to execute",
    )
    parser.add_argument(
        "--settings-file",
        type=Path,
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
    parser.add_argument(
        "--run-on",
        default=Runner.SLURM,
        help=("On which computer or cluster environment to execute the calculation."
              "Available: local, slurm. Default: slurm"))

    return parser


def apply_settings_from_args(args: argparse.Namespace) -> None:
    """Apply command line arguments to settings.

    Args:
        args: Arguments object created by ArgumentParser.
    """
    if args.settings_file is not None:
        sgh.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)
    if args.performance_measure is not None:
        sgh.settings.set_general_performance_measure(
            PerformanceMeasure.from_str(args.performance_measure), SettingState.CMD_LINE)
    if args.target_cutoff_time is not None:
        sgh.settings.set_general_target_cutoff_time(
            args.target_cutoff_time, SettingState.CMD_LINE)
    if args.budget_per_run is not None:
        sgh.settings.set_config_budget_per_run(
            args.budget_per_run, SettingState.CMD_LINE)
    if args.number_of_runs is not None:
        sgh.settings.set_config_number_of_runs(
            args.number_of_runs, SettingState.CMD_LINE)


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
    run_on = args.run_on
    if args.configurator is not None:
        configurator_path = args.configurator
        configurator_target = [x for x in os.listdir(configurator_path)
                               if x.endswith("_target_algorithm.py")]
        if len(configurator_target) != 1:
            print("Configurator Error: "
                  f"Could not determine target script for {configurator_path}\n"
                  "Please check target script file '*_target_algorithm.py'")
            sys.exit(-1)
        configurator_target = configurator_target[0]
    else:
        # SMAC is the default configurator
        configurator_path = Path(sgh.smac_dir)
        configurator_target = sgh.smac_target_algorithm

    sch.check_for_initialise(sys.argv, sch.COMMAND_DEPENDENCIES[
                             sch.CommandName.CONFIGURE_SOLVER])

    feature_data_df = None
    if use_features:
        feature_data_csv = sfdcsv.SparkleFeatureDataCSV(sgh.feature_data_csv_path)

        if not Path(instance_set_train).is_dir():  # Path has to be a directory
            print("Given training set path is not an existing directory")
            sys.exit(-1)

        data_dict = {}
        feature_data_df = feature_data_csv.dataframe

        for label, row in feature_data_df.iterrows():
            # os.path.split(os.path.split(label)[0])[1] gives the dir/instance set name
            if os.path.split(os.path.split(label)[0])[1] == instance_set_train.name:
                if row.empty:
                    print("No feature data exists for the given training set, please "
                          "run add_feature_extractor.py, then compute_features.py")
                    sys.exit()

                new_label = (f"../../../instances/{instance_set_train.name}/"
                             + os.path.split(label)[1])
                data_dict[new_label] = row

        feature_data_df = DataFrame.from_dict(data_dict, orient="index",
                                              columns=feature_data_df.columns)

        if feature_data_df.isnull().values.any():
            print("You have unfinished feature computation jobs, please run "
                  "compute_features.py")
            sys.exit(-1)

        for index, column in enumerate(feature_data_df):
            feature_data_df.rename(columns={column: f"Feature{index+1}"}, inplace=True)

    sah.clean_ablation_scenarios(solver_path.name, instance_set_train.name)

    solver = Solver(solver_path)

    status_info = ConfigureSolverStatusInfo()
    status_info.set_solver(str(solver.name))
    status_info.set_instance_set_train(str(instance_set_train.name))
    ins_t_str = instance_set_test.name if instance_set_test is not None else "_"
    status_info.set_instance_set_test(str(instance_set_test))
    status_info.save()

    number_of_runs = sgh.settings.get_config_number_of_runs()
    config_scenario = ConfigurationScenario(solver, instance_set_train, number_of_runs,
                                            use_features, configurator_target,
                                            feature_data_df)
    configurator = Configurator(configurator_path)

    configurator.create_sbatch_script(config_scenario)
    configure_jobid = configurator.configure(run_on=run_on)

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

    callback_jobid = configurator.configuration_callback(configure_jobid, run_on=run_on)

    # Set validation to wait until configuration is done
    if validate:
        validate_jobid = ssh.run_validation_callback(
            solver, instance_set_train, instance_set_test, configure_jobid, run_on=run_on
        )
        dependency_jobid_list.append(validate_jobid)

    if ablation:
        ablation_jobid = ssh.run_ablation_callback(
            solver, instance_set_train, instance_set_test, configure_jobid, run_on=run_on
        )
        dependency_jobid_list.append(ablation_jobid)

    if run_on == Runner.SLURM:
        job_id_str = ",".join(dependency_jobid_list)
        print(f"Running configuration in parallel. Waiting for Slurm job(s) with id(s): "
              f"{job_id_str}")
    else:
        print("Running configuration finished!")

    status_info.delete()
    # Write used settings to file
    sgh.settings.write_used_settings()
    # Write used scenario to file
    sgh.latest_scenario.write_scenario_ini()
