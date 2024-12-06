#!/usr/bin/env python3
"""Sparkle command to execute a configured solver."""
import sys
import argparse
from pathlib import PurePath

from runrunner.base import Runner

from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.platform.settings_objects import Settings, SettingState
from sparkle.structures import PerformanceDataFrame
from sparkle.instance import Instance_Set
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help.nicknames import resolve_object_name


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Command to run a configured solver on an instance (set).")
    parser.add_argument(*ac.InstancePathPositional.names,
                        **ac.InstancePathPositional.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    parser.add_argument(*ac.SparkleObjectiveArgument.names,
                        **ac.SparkleObjectiveArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    return parser


def main(argv: list[str]) -> None:
    """Main function of the run configured solver command."""
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)

    check_for_initialise()

    if args.settings_file is not None:
        # Do first, so other command line options can override settings from the file
        gv.settings().read_settings_ini(args.settings_file, SettingState.CMD_LINE)
    if args.objectives is not None:
        gv.settings().set_general_sparkle_objectives(
            args.objectives, SettingState.CMD_LINE
        )
    if args.run_on is not None:
        gv.settings().set_run_on(
            args.run_on.value, SettingState.CMD_LINE)

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings(), prev_settings)

    # Try to resolve the instance path (Dir or list instance paths)
    data_set = resolve_object_name(
        args.instance_path,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        gv.settings().DEFAULT_instance_dir, Instance_Set)
    if data_set is None:
        print(f"Could not resolve instance (set): {args.instance_path}! Exiting...")
        sys.exit(-1)

    run_on = gv.settings().get_run_on()
    # Get the name of the configured solver and the training set
    solver = gv.latest_scenario().get_config_solver()
    train_set = gv.latest_scenario().get_config_instance_set_train()
    custom_cutoff = gv.settings().get_general_target_cutoff_time()
    if solver is None or train_set is None:
        # Print error and stop execution
        print("ERROR: No configured solver found! Stopping execution.")
        sys.exit(-1)
    # Get optimised configuration
    configurator = gv.settings().get_general_sparkle_configurator()
    objectives = gv.settings().get_general_sparkle_objectives()
    configuration_scenario = gv.latest_scenario().get_configuration_scenario(
        configurator.scenario_class())
    performance_data = PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path)
    config, _ = performance_data.best_configuration(
        str(solver.directory),
        objective=configuration_scenario.sparkle_objective,
        instances=[str(p) for p in train_set.instance_paths],)
    # Call the configured solver
    sbatch_options = gv.settings().get_slurm_extra_options(as_args=True)
    if run_on == Runner.LOCAL:
        print(f"Start running solver on {data_set.size} instances...")
    run = solver.run(instance=data_set,
                     objectives=objectives,
                     seed=gv.get_seed(),
                     cutoff_time=custom_cutoff,
                     configuration=config,
                     run_on=run_on,
                     sbatch_options=sbatch_options,
                     log_dir=sl.caller_log_dir)

    # Print result
    if run_on == Runner.SLURM:
        print(f"Running configured solver. Waiting for Slurm "
              f"job(s) with id(s): {run.run_id}")
    else:
        if isinstance(run, dict):
            run = [run]
        # Resolve objective keys
        status_key = [key for key in run[0] if key.lower().startswith("status")][0]
        time_key = [key for key in run[0] if key.lower().startswith("cpu_time")][0]
        for i, solver_output in enumerate(run):
            print(f"Execution of {solver.name} on instance "
                  f"{data_set.instance_names[i]} completed with status "
                  f"{solver_output[status_key]} in {solver_output[time_key]} seconds.")
        print("Running configured solver done!")

    # Write used settings to file
    gv.settings().write_used_settings()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
