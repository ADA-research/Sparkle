#!/usr/bin/env python3
"""Sparkle command to validate a configured solver against its default configuration."""

import sys
import argparse
from pathlib import Path, PurePath

import global_variables as gv
from sparkle.solver import pcs
import sparkle_logging as sl
from sparkle.platform.settings_help import SettingState, Settings
from CLI.help import argparse_custom as ac
from CLI.help.reporting_scenario import Scenario
from sparkle.configurator.configurator import Configurator
from sparkle.solver.validator import Validator
from sparkle.solver import Solver
from CLI.help import command_help as ch
from sparkle.platform import settings_help
from CLI.initialise import check_for_initialise
from CLI.help.nicknames import resolve_object_name


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description=("Test the performance of the configured solver and the default "
                     "solver by doing validation experiments on the training and test "
                     "sets."))
    parser.add_argument(*ac.SolverArgument.names,
                        **ac.SolverArgument.kwargs)
    parser.add_argument(*ac.InstanceSetTrainArgument.names,
                        **ac.InstanceSetTrainArgument.kwargs)
    parser.add_argument(*ac.InstanceSetTestArgument.names,
                        **ac.InstanceSetTestArgument.kwargs)
    parser.add_argument(*ac.ConfiguratorArgument.names,
                        **ac.ConfiguratorArgument.kwargs)
    parser.add_argument(*ac.PerformanceMeasureArgument.names,
                        **ac.PerformanceMeasureArgument.kwargs)
    parser.add_argument(*ac.TargetCutOffTimeValidationArgument.names,
                        **ac.TargetCutOffTimeValidationArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    gv.settings = settings_help.Settings()

    # Log command call
    sl.log_command(sys.argv)

    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    solver_path = resolve_object_name(args.solver,
                                      gv.solver_nickname_mapping, gv.solver_dir)
    solver = Solver(solver_path)
    instance_set_train = resolve_object_name(args.instance_set_train,
                                             target_dir=gv.instance_dir)
    instance_set_test = resolve_object_name(args.instance_set_test,
                                            target_dir=gv.instance_dir)
    run_on = args.run_on

    check_for_initialise(
        sys.argv,
        ch.COMMAND_DEPENDENCIES[ch.CommandName.VALIDATE_CONFIGURED_VS_DEFAULT]
    )
    if args.configurator is not None:
        gv.settings.set_general_sparkle_configurator(
            value=getattr(Configurator, args.configurator),
            origin=SettingState.CMD_LINE)
    if ac.set_by_user(args, "settings_file"):
        gv.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file

    if ac.set_by_user(args, "performance_measure"):
        set_str = ",".join([args.performance_measure + ":" + o.metric for o in
                            gv.settings.get_general_sparkle_objectives()])
        gv.settings.set_general_sparkle_objectives(
            set_str, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "target_cutoff_time"):
        gv.settings.set_general_target_cutoff_time(
            args.target_cutoff_time, SettingState.CMD_LINE
        )

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings, prev_settings)

    # Make sure configuration results exist before trying to work with them
    configurator = gv.settings.get_general_sparkle_configurator()
    configurator.set_scenario_dirs(solver, instance_set_train.name)

    # Record optimised configuration
    _, opt_config_str = configurator.get_optimal_configuration(
        solver, instance_set_train)
    pcs.write_configuration_pcs(solver, opt_config_str,
                                Path(gv.sparkle_tmp_path))

    validator = Validator(gv.validation_output_general)
    all_validation_instances = [instance_set_train]
    if instance_set_test is not None:
        all_validation_instances.append(instance_set_test)
    validator.validate(solvers=[solver] * 2, configurations=[None, opt_config_str],
                       instance_sets=all_validation_instances)

    # Update latest scenario
    gv.latest_scenario().set_config_solver(solver.directory)
    gv.latest_scenario().set_config_instance_set_train(instance_set_train)
    gv.latest_scenario().set_latest_scenario(Scenario.CONFIGURATION)

    if instance_set_test is not None:
        gv.latest_scenario().set_config_instance_set_test(instance_set_test)
    else:
        # Set to default to overwrite possible old path
        gv.latest_scenario().set_config_instance_set_test()

    # Write used settings to file
    gv.settings.write_used_settings()
    # Write used scenario to file
    gv.latest_scenario().write_scenario_ini()
