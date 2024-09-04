#!/usr/bin/env python3
"""Sparkle command to execute ablation analysis."""

import argparse
import sys
from pathlib import PurePath

from runrunner.base import Runner

from sparkle.solver.ablation import AblationScenario
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.platform.settings_objects import Settings, SettingState
from sparkle.solver import Solver
from sparkle.instance import instance_set
from sparkle.CLI.help import argparse_custom as ac
from sparkle.platform import CommandName, COMMAND_DEPENDENCIES
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help.nicknames import resolve_object_name


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
    parser.add_argument(*ac.SparkleObjectiveArgument.names,
                        **ac.SparkleObjectiveArgument.kwargs)
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
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    solver_path = resolve_object_name(args.solver,
                                      gv.solver_nickname_mapping,
                                      gv.settings().DEFAULT_solver_dir)
    solver = Solver(solver_path)
    instance_set_train = resolve_object_name(
        args.instance_set_train,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        gv.settings().DEFAULT_instance_dir, instance_set)
    instance_set_test = resolve_object_name(
        args.instance_set_test,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        gv.settings().DEFAULT_instance_dir, instance_set)

    if args.run_on is not None:
        gv.settings().set_run_on(
            args.run_on.value, SettingState.CMD_LINE)
    run_on = gv.settings().get_run_on()

    check_for_initialise(COMMAND_DEPENDENCIES[CommandName.RUN_ABLATION])

    if ac.set_by_user(args, "settings_file"):
        # Do first, so other command line options can override settings from the file
        gv.settings().read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "objectives"):
        gv.settings().set_general_sparkle_objectives(
            args.objectives, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "target_cutoff_time"):
        gv.settings().set_general_target_cutoff_time(
            args.target_cutoff_time, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "wallclock_time"):
        gv.settings().set_config_wallclock_time(
            args.wallclock_time, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "number_of_runs"):
        gv.settings().set_config_number_of_runs(
            args.number_of_runs, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "racing"):
        gv.settings().set_ablation_racing_flag(
            args.number_of_runs, SettingState.CMD_LINE
        )

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings(), prev_settings)

    instance_set_train_name = instance_set_train.name
    configurator = gv.settings().get_general_sparkle_configurator()
    configurator.set_scenario_dirs(solver, instance_set_train)
    if instance_set_test is not None:
        instance_set_test_name = instance_set_test.name
    else:
        instance_set_test = instance_set_train
        instance_set_test_name = instance_set_train.name

    if not configurator.scenario.result_directory.is_dir():
        print("Error: No configuration results found for the given solver and training"
              " instance set. Ablation needs to have a target configuration.")
        print("Please run configuration first")
        sys.exit(-1)
    else:
        print("Configuration exists!")

    ablation_scenario = AblationScenario(
        solver, instance_set_train, instance_set_test,
        gv.settings().DEFAULT_ablation_output,
        gv.settings().DEFAULT_ablation_exec,
        gv.settings().DEFAULT_ablation_validation_exec, override_dirs=True)

    # Instances
    ablation_scenario.create_instance_file()
    ablation_scenario.create_instance_file(test=True)

    # Configurations
    ablation_scenario.create_configuration_file()
    print("Submiting ablation run...")
    runs = ablation_scenario.submit_ablation(run_on=run_on)

    if run_on == Runner.LOCAL:
        print("Ablation analysis finished!")
    else:
        job_id_str = ",".join([run.run_id for run in runs])
        print(f"Ablation analysis running. Waiting for Slurm job(s) with id(s): "
              f"{job_id_str}")
