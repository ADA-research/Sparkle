#!/usr/bin/env python3
"""Sparkle command to execute ablation analysis."""

import argparse
import sys
import shutil
from pathlib import PurePath

from runrunner.base import Runner

from sparkle.configurator import ablation as sah
import global_variables as gv
import sparkle_logging as sl
from sparkle.platform import settings_help
from sparkle.platform.settings_help import SettingState, Settings
from CLI.help import argparse_custom as ac
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise
from CLI.help.nicknames import resolve_object_name


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description=("Runs parameter importance between the default and configured "
                     "parameters with ablation. This command requires a finished "
                     "configuration for the solver instance pair."),
        epilog=("Note that if no test instance set is given, the validation is performed"
                " on the training set."))
    parser.add_argument("--solver", required=False, type=str, help="path to solver")
    parser.add_argument(*ac.InstanceSetTrainAblationArgument.names,
                        **ac.InstanceSetTrainAblationArgument.kwargs)
    parser.add_argument(*ac.InstanceSetTestAblationArgument.names,
                        **ac.InstanceSetTestAblationArgument.kwargs)
    parser.add_argument(*ac.AblationSettingsHelpArgument.names,
                        **ac.AblationSettingsHelpArgument.kwargs)
    parser.add_argument(*ac.PerformanceMeasureArgument.names,
                        **ac.PerformanceMeasureArgument.kwargs)
    parser.add_argument(*ac.TargetCutOffTimeAblationArgument.names,
                        **ac.TargetCutOffTimeAblationArgument.kwargs)
    parser.add_argument(*ac.WallClockTimeArgument.names,
                        **ac.WallClockTimeArgument.kwargs)
    parser.add_argument(*ac.NumberOfRunsAblationArgument.names,
                        **ac.NumberOfRunsAblationArgument.kwargs)
    parser.add_argument(*ac.RacingArgument.names,
                        **ac.RacingArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    parser.set_defaults(ablation_settings_help=False)
    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    gv.settings = settings_help.Settings()

    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    if args.ablation_settings_help:
        sah.print_ablation_help()
        sys.exit()

    solver = resolve_object_name(args.solver, gv.solver_nickname_mapping, gv.solver_dir)
    instance_set_train = resolve_object_name(args.instance_set_train,
                                             target_dir=gv.instance_dir)
    instance_set_test = resolve_object_name(args.instance_set_test,
                                            target_dir=gv.instance_dir)
    run_on = args.run_on

    check_for_initialise(sys.argv,
                         ch.COMMAND_DEPENDENCIES[ch.CommandName.RUN_ABLATION])

    if ac.set_by_user(args, "settings_file"):
        # Do first, so other command line options can override settings from the file
        gv.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "performance_measure"):
        gv.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "target_cutoff_time"):
        gv.settings.set_general_target_cutoff_time(
            args.target_cutoff_time, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "wallclock_time"):
        gv.settings.set_config_wallclock_time(
            args.wallclock_time, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "number_of_runs"):
        gv.settings.set_config_number_of_runs(
            args.number_of_runs, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "racing"):
        gv.settings.set_ablation_racing_flag(
            args.number_of_runs, SettingState.CMD_LINE
        )

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings, prev_settings)

    solver_name = solver.name
    instance_set_train_name = instance_set_train.name
    configurator = gv.settings.get_general_sparkle_configurator()
    configurator.set_scenario_dirs(solver_name, instance_set_train_name)
    if instance_set_test is not None:
        instance_set_test_name = instance_set_test.name
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
        shutil.rmtree(gv.ablation_dir + ablation_scenario_dir)

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
