#!/usr/bin/env python3
"""Sparkle command to validate a configured solver against its default configuration."""

import sys
import argparse
from pathlib import Path

from runrunner.base import Runner

import global_variables as sgh
from CLI.support import configure_solver_help as scsh
from sparkle.solver import pcs
import sparkle_logging as sl
from sparkle.types.objective import PerformanceMeasure
from sparkle.platform.settings_help import SettingState
from CLI.help import argparse_custom as ac
from CLI.help.reporting_scenario import Scenario
from sparkle.configurator.configurator import Configurator
from sparkle.solver.validator import Validator
from CLI.help import command_help as ch
from sparkle.platform import settings_help
from CLI.initialise import check_for_initialise


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
    sgh.settings = settings_help.Settings()

    # Log command call
    sl.log_command(sys.argv)

    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    solver = args.solver
    instance_set_train = args.instance_set_train
    instance_set_test = args.instance_set_test
    run_on = args.run_on

    check_for_initialise(
        sys.argv,
        ch.COMMAND_DEPENDENCIES[ch.CommandName.VALIDATE_CONFIGURED_VS_DEFAULT]
    )
    if args.configurator is not None:
        sgh.settings.set_general_sparkle_configurator(
            value=getattr(Configurator, args.configurator),
            origin=SettingState.CMD_LINE)
    if ac.set_by_user(args, "settings_file"):
        sgh.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file

    if ac.set_by_user(args, "performance_measure"):
        set_str = ",".join([args.performance_measure + ":" + o.metric for o in
                            sgh.settings.get_general_sparkle_objectives()])
        sgh.settings.set_general_sparkle_objectives(
            set_str, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "target_cutoff_time"):
        sgh.settings.set_general_target_cutoff_time(
            args.target_cutoff_time, SettingState.CMD_LINE
        )

    # Make sure configuration results exist before trying to work with them
    configurator = sgh.settings.get_general_sparkle_configurator()
    configurator.set_scenario_dirs(Path(solver).name, instance_set_train.name)
    scsh.check_validation_prerequisites()

    # Record optimised configuration
    optimised_configuration_str, _, _ = scsh.get_optimised_configuration(
        solver.name, instance_set_train.name)
    scsh.write_configuration_str(optimised_configuration_str)
    pcs.write_configuration_pcs(solver.name, optimised_configuration_str,
                                Path(sgh.sparkle_tmp_path))

    validator = Validator()
    all_validation_instances = [instance_set_train]
    if instance_set_test is not None:
        all_validation_instances.append(instance_set_test)
    config_str = scsh.get_optimised_configuration_params(solver, instance_set_train)
    validator.validate(solvers=[solver] * 2, config_str_list=[None, config_str],
                       instance_sets=all_validation_instances)

    # Update latest scenario
    sgh.latest_scenario().set_config_solver(Path(solver))
    sgh.latest_scenario().set_config_instance_set_train(Path(instance_set_train))
    sgh.latest_scenario().set_latest_scenario(Scenario.CONFIGURATION)

    if instance_set_test is not None:
        sgh.latest_scenario().set_config_instance_set_test(Path(instance_set_test))
    else:
        # Set to default to overwrite possible old path
        sgh.latest_scenario().set_config_instance_set_test()

    # Write used settings to file
    sgh.settings.write_used_settings()
    # Write used scenario to file
    sgh.latest_scenario().write_scenario_ini()
