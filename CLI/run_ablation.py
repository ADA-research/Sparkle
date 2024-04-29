#!/usr/bin/env python3
"""Sparkle command to execute ablation analysis."""

import argparse
import sys
import shutil
from pathlib import Path

from runrunner.base import Runner

from sparkle.configurator import ablation as sah
import global_variables as sgh
import sparkle_logging as sl
from sparkle.platform import settings_help
from sparkle.types.objective import PerformanceMeasure
from sparkle.platform.settings_help import SettingState
from CLI.help import argparse_custom as ac
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description=("Runs parameter importance between the default and configured "
                     "parameters with ablation. This command requires a finished "
                     "configuration for the solver instance pair."),
        epilog=("Note that if no test instance set is given, the validation is performed"
                " on the training set."))
    parser.add_argument("--solver", required=False, type=str, help="path to solver")
    parser.add_argument(
        "--instance-set-train",
        required=False,
        type=str,
        help="Path to training instance set",
    )
    parser.add_argument(
        "--instance-set-test",
        required=False,
        type=str,
        help="Path to testing instance set",
    )
    parser.add_argument(
        "--ablation-settings-help",
        required=False,
        dest="ablation_settings_help",
        action="store_true",
        help="Prints a list of setting that can be used for the ablation analysis",
    )
    parser.add_argument(
        "--performance-measure",
        choices=PerformanceMeasure.__members__,
        default=sgh.settings.DEFAULT_general_sparkle_objective.PerformanceMeasure,
        action=ac.SetByUser,
        help="The performance measure, e.g. runtime",
    )
    parser.add_argument(
        "--target-cutoff-time",
        type=int,
        default=sgh.settings.DEFAULT_general_target_cutoff_time,
        action=ac.SetByUser,
        help="Cutoff time per target algorithm run in seconds",
    )
    parser.add_argument(
        "--budget-per-run",
        type=int,
        default=sgh.settings.DEFAULT_config_budget_per_run,
        action=ac.SetByUser,
        help="Configuration budget per configurator run in seconds",
    )
    parser.add_argument(
        "--number-of-runs",
        type=int,
        default=sgh.settings.DEFAULT_config_number_of_runs,
        action=ac.SetByUser,
        help="Number of configuration runs to execute",
    )
    parser.add_argument(
        "--racing",
        type=bool,
        default=sgh.settings.DEFAULT_ablation_racing,
        action=ac.SetByUser,
        help="Performs abaltion analysis with racing",
    )
    parser.add_argument(
        "--settings-file",
        type=Path,
        default=sgh.settings.DEFAULT_settings_path,
        action=ac.SetByUser,
        help=("Specify the settings file to use in case you want to use one other than "
              "the default"),
    )
    parser.add_argument(
        "--run-on",
        default=Runner.SLURM,
        choices=[Runner.LOCAL, Runner.SLURM],
        help=("On which computer or cluster environment to execute the calculation.")
    )
    parser.set_defaults(ablation_settings_help=False)
    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    sgh.settings = settings_help.Settings()

    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    if args.ablation_settings_help:
        sah.print_ablation_help()
        sys.exit()

    solver = args.solver
    instance_set_train = args.instance_set_train
    instance_set_test = args.instance_set_test
    run_on = args.run_on

    check_for_initialise(sys.argv,
                         ch.COMMAND_DEPENDENCIES[ch.CommandName.RUN_ABLATION])

    if ac.set_by_user(args, "settings_file"):
        # Do first, so other command line options can override settings from the file
        sgh.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "performance_measure"):
        sgh.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE
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
    if ac.set_by_user(args, "racing"):
        sgh.settings.set_ablation_racing_flag(
            args.number_of_runs, SettingState.CMD_LINE
        )

    solver_name = Path(solver).name
    instance_set_train_name = Path(instance_set_train).name
    instance_set_test_name = None
    configurator = sgh.settings.get_general_sparkle_configurator()
    configurator.set_scenario_dirs(solver_name, instance_set_train_name)
    if instance_set_test is not None:
        instance_set_test_name = Path(instance_set_test).name
    else:
        instance_set_test = instance_set_train
        instance_set_test_name = instance_set_train_name

    if not configurator.scenario.result_directory.is_dir():
        print("Error: No configuration results found for the given solver and training"
              " instance set. Ablation needs to have a target configuration.")
        print("Please run configuration first")
        sys.exit(-1)
    else:
        print("Configuration exists!")

    # REMOVE SCENARIO
    ablation_scenario_dir = sah.get_ablation_scenario_directory(
        solver_name, instance_set_train_name, instance_set_test_name
    )
    if sah.check_for_ablation(solver_name, instance_set_train_name,
                              instance_set_test_name):
        print("Warning: found existing ablation scenario for this combination. "
              "This will be removed.")
        shutil.rmtree(sgh.ablation_dir + ablation_scenario_dir)

    # Prepare ablation scenario directory
    ablation_scenario_dir = sah.prepare_ablation_scenario(
        solver_name, instance_set_train_name, instance_set_test_name
    )

    # Instances
    sah.create_instance_file(instance_set_train, ablation_scenario_dir, test=False)
    if instance_set_test_name is not None:
        sah.create_instance_file(instance_set_test, ablation_scenario_dir, test=True)
    else:
        # TODO: check if needed
        sah.create_instance_file(instance_set_train, ablation_scenario_dir, test=True)

    print("Create config file")
    # Configurations
    sah.create_configuration_file(
        solver_name, instance_set_train_name, instance_set_test_name
    )
    print("Submit ablation run")
    runs = sah.submit_ablation(
        ablation_scenario_dir=ablation_scenario_dir,
        instance_set_test=instance_set_test,
        run_on=run_on)

    if run_on == Runner.LOCAL:
        print("Ablation analysis finished!")
    else:
        job_id_str = ",".join([run.run_id for run in runs])
        print(f"Ablation analysis running. Waiting for Slurm job(s) with id(s): "
              f"{job_id_str}")
