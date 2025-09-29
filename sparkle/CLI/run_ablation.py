#!/usr/bin/env python3
"""Sparkle command to execute ablation analysis."""

import argparse
import sys

from runrunner.base import Runner

from sparkle.configurator import AblationScenario
from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.platform.settings_objects import Settings
from sparkle.solver import Solver
from sparkle.structures import PerformanceDataFrame
from sparkle.instance import Instance_Set, InstanceSet
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help.nicknames import resolve_object_name


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Runs parameter importance between the default and configured "
        "parameters with ablation. This command requires a finished "
        "configuration for the solver instance pair.",
        epilog="Note that if no test instance set is given, the validation is performed"
        " on the training set.",
    )
    parser.add_argument("--solver", required=False, type=str, help="path to solver")
    parser.add_argument(
        *ac.InstanceSetTrainOptionalArgument.names,
        **ac.InstanceSetTrainOptionalArgument.kwargs,
    )
    parser.add_argument(
        *ac.InstanceSetTestAblationArgument.names,
        **ac.InstanceSetTestAblationArgument.kwargs,
    )
    # Settings arguments
    parser.add_argument(*ac.SettingsFileArgument.names, **ac.SettingsFileArgument.kwargs)
    parser.add_argument(
        *Settings.OPTION_ablation_racing.args, **Settings.OPTION_ablation_racing.kwargs
    )
    parser.add_argument(*Settings.OPTION_run_on.args, **Settings.OPTION_run_on.kwargs)
    parser.set_defaults(ablation_settings_help=False)
    return parser


def main(argv: list[str]) -> None:
    """Main function to run ablation analysis."""
    sl.log_command(sys.argv, gv.settings().random_state)
    check_for_initialise()

    if not AblationScenario.check_requirements(verbose=True):
        print("Ablation Analysis is not available.")
        if not AblationScenario.ablation_executable.exists():
            print("Would you like to download it? (Y/n)")
            if input().lower().strip() == "y":
                AblationScenario.download_requirements()
            else:
                sys.exit()
        else:
            print("Check that Java is available on your system.")
            sys.exit(-1)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)
    settings = gv.settings(args)

    # Compare current settings to latest.ini
    prev_settings = Settings(Settings.DEFAULT_previous_settings_path)
    Settings.check_settings_changes(settings, prev_settings)

    solver = resolve_object_name(
        args.solver, gv.solver_nickname_mapping, settings.DEFAULT_solver_dir, Solver
    )
    if solver is None:
        print(f"Could not resolve Solver path/name {args.solver}!")
        print([p for p in settings.DEFAULT_solver_dir.iterdir()])
        sys.exit(-1)

    instance_set_train: InstanceSet = resolve_object_name(
        args.instance_set_train,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        settings.DEFAULT_instance_dir,
        Instance_Set,
    )
    instance_set_test = resolve_object_name(
        args.instance_set_test,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        settings.DEFAULT_instance_dir,
        Instance_Set,
    )

    configurator = settings.configurator
    output_path = settings.get_configurator_output_path(configurator)

    config_scenario = configurator.scenario_class().find_scenario(
        output_path, solver, instance_set_train
    )

    performance_data = PerformanceDataFrame(settings.DEFAULT_performance_data_path)
    if config_scenario is None:
        print(
            "No configuration scenario found for combination:\n"
            f"{configurator.name} {solver.name} {instance_set_train.name}"
        )
        sys.exit(-1)
    best_configuration_key, _ = performance_data.best_configuration(
        str(solver.directory),
        config_scenario.sparkle_objective,
        instances=instance_set_train.instance_names,
    )
    best_configuration = performance_data.get_full_configuration(
        str(solver.directory), best_configuration_key
    )
    if instance_set_test is None:
        instance_set_test = instance_set_train

    if not config_scenario.results_directory.is_dir():
        print(
            "Error: No configuration results found for the given solver and training"
            " instance set. Ablation needs to have a target configuration. "
            "Please finish configuration first."
        )
        sys.exit(-1)
    else:
        print("Configuration exists!")

    ablation_scenario = AblationScenario(
        config_scenario,
        instance_set_test,
        cutoff_length=settings.smac2_target_cutoff_length,  # NOTE: SMAC2
        concurrent_clis=settings.slurm_jobs_in_parallel,
        best_configuration=best_configuration,
        ablation_racing=settings.ablation_racing_flag,
    )

    # Create scenario
    ablation_scenario.create_scenario(override_dirs=True)

    print("Submiting ablation run...")
    run_on = settings.run_on
    runs = ablation_scenario.submit_ablation(
        log_dir=sl.caller_log_dir,
        sbatch_options=settings.sbatch_settings,
        run_on=run_on,
    )

    if run_on == Runner.LOCAL:
        print("Ablation analysis finished!")
    else:
        job_id_str = ",".join([run.run_id for run in runs])
        print(f"Ablation analysis running through Slurm with job id(s): {job_id_str}")
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
