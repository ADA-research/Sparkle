#!/usr/bin/env python3
"""Sparkle command to validate a configured solver against its default configuration."""

import sys
import argparse
from pathlib import PurePath

from runrunner.base import Runner

from sparkle.CLI.help import global_variables as gv
from sparkle.solver import pcs
from sparkle.CLI.help import sparkle_logging as sl
from sparkle.platform.settings_objects import Settings, SettingState
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help.reporting_scenario import Scenario
from sparkle.configurator.configurator import Configurator
from sparkle.solver.validator import Validator
from sparkle.solver import Solver
from sparkle.instance import InstanceSet
from sparkle.platform import CommandName, COMMAND_DEPENDENCIES
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help.nicknames import resolve_object_name


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
    # Log command call
    sl.log_command(sys.argv)

    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    solver = resolve_object_name(args.solver,
                                 gv.solver_nickname_mapping,
                                 gv.settings().DEFAULT_solver_dir,
                                 Solver)
    instance_set_train = resolve_object_name(
        args.instance_set_train,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        gv.settings().DEFAULT_instance_dir, InstanceSet)
    instance_set_test = resolve_object_name(
        args.instance_set_test,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        gv.settings().DEFAULT_instance_dir, InstanceSet)

    if args.run_on is not None:
        gv.settings().set_run_on(
            args.run_on.value, SettingState.CMD_LINE)
    run_on = gv.settings().get_run_on()

    check_for_initialise(
        COMMAND_DEPENDENCIES[CommandName.VALIDATE_CONFIGURED_VS_DEFAULT]
    )
    if args.configurator is not None:
        gv.settings().set_general_sparkle_configurator(
            value=getattr(Configurator, args.configurator),
            origin=SettingState.CMD_LINE)
    if ac.set_by_user(args, "settings_file"):
        gv.settings().read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file

    if ac.set_by_user(args, "performance_measure"):
        set_str = ",".join([args.performance_measure + ":" + o.metric for o in
                            gv.settings().get_general_sparkle_objectives()])
        gv.settings().set_general_sparkle_objectives(
            set_str, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "target_cutoff_time"):
        gv.settings().set_general_target_cutoff_time(
            args.target_cutoff_time, SettingState.CMD_LINE
        )

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings(), prev_settings)

    # Make sure configuration results exist before trying to work with them
    configurator = gv.settings().get_general_sparkle_configurator()
    configurator.set_scenario_dirs(solver, instance_set_train)
    objective = gv.settings().get_general_sparkle_objectives()[0]
    # Record optimised configuration
    _, opt_config_str = configurator.get_optimal_configuration(
        solver, instance_set_train, objective.PerformanceMeasure)
    opt_config = Solver.config_str_to_dict(opt_config_str)

    pcs.write_configuration_pcs(solver, opt_config_str, gv.settings().DEFAULT_tmp_output)

    validator = Validator(gv.settings().DEFAULT_validation_output,
                          gv.settings().DEFAULT_tmp_output)
    all_validation_instances = [instance_set_train]
    if instance_set_test is not None:
        all_validation_instances.append(instance_set_test)
    validation = validator.validate(
        solvers=[solver] * 2,
        configurations=[None, opt_config],
        instance_sets=all_validation_instances,
        cut_off=gv.settings().get_general_target_cutoff_time(),
        sbatch_options=gv.settings().get_slurm_extra_options(as_args=True),
        run_on=run_on)

    if run_on == Runner.LOCAL:
        validation.wait()

    # Update latest scenario
    gv.latest_scenario().set_config_solver(solver)
    gv.latest_scenario().set_config_instance_set_train(instance_set_train.directory)
    gv.latest_scenario().set_latest_scenario(Scenario.CONFIGURATION)

    if instance_set_test is not None:
        gv.latest_scenario().set_config_instance_set_test(instance_set_test.directory)
    else:
        # Set to default to overwrite possible old path
        gv.latest_scenario().set_config_instance_set_test()

    # Write used settings to file
    gv.settings().write_used_settings()
    # Write used scenario to file
    gv.latest_scenario().write_scenario_ini()
