#!/usr/bin/env python3
"""Sparkle command to configure a solver."""
from __future__ import annotations

import argparse
import sys
import os
from pathlib import Path
from pandas import DataFrame

from runrunner.base import Runner, Run
import runrunner as rrr

from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.platform.settings_objects import SettingState
from sparkle.CLI.help.reporting_scenario import Scenario
from sparkle.structures import FeatureDataFrame
from sparkle.platform import CommandName, COMMAND_DEPENDENCIES
from sparkle.configurator.configurator import Configurator
from sparkle.CLI.help.nicknames import resolve_object_name
from sparkle.solver import Solver
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help import argparse_custom as ac
from sparkle.instance import instance_set, InstanceSet


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Configure a solver in the Sparkle platform.",
        epilog=("Note that the test instance set is only used if the ``--ablation``"
                " or ``--validation`` flags are given"))
    parser.add_argument(*ac.ConfiguratorArgument.names,
                        **ac.ConfiguratorArgument.kwargs)
    parser.add_argument(*ac.SolverArgument.names,
                        **ac.SolverArgument.kwargs)
    parser.add_argument(*ac.InstanceSetTrainArgument.names,
                        **ac.InstanceSetTrainArgument.kwargs)
    parser.add_argument(*ac.InstanceSetTestArgument.names,
                        **ac.InstanceSetTestArgument.kwargs)
    parser.add_argument(*ac.SparkleObjectiveArgument.names,
                        **ac.SparkleObjectiveArgument.kwargs)
    parser.add_argument(*ac.TargetCutOffTimeConfigurationArgument.names,
                        **ac.TargetCutOffTimeConfigurationArgument.kwargs)
    parser.add_argument(*ac.WallClockTimeArgument.names,
                        **ac.WallClockTimeArgument.kwargs)
    parser.add_argument(*ac.CPUTimeArgument.names,
                        **ac.CPUTimeArgument.kwargs)
    parser.add_argument(*ac.SolverCallsArgument.names,
                        **ac.SolverCallsArgument.kwargs)
    parser.add_argument(*ac.NumberOfRunsConfigurationArgument.names,
                        **ac.NumberOfRunsConfigurationArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    parser.add_argument(*ac.UseFeaturesArgument.names,
                        **ac.UseFeaturesArgument.kwargs)
    parser.add_argument(*ac.ValidateArgument.names,
                        **ac.ValidateArgument.kwargs)
    parser.add_argument(*ac.AblationArgument.names,
                        **ac.AblationArgument.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    return parser


def apply_settings_from_args(args: argparse.Namespace) -> None:
    """Apply command line arguments to settings.

    Args:
        args: Arguments object created by ArgumentParser.
    """
    if args.settings_file is not None:
        gv.settings().read_settings_ini(args.settings_file, SettingState.CMD_LINE)
    if args.objectives is not None:
        gv.settings().set_general_sparkle_objectives(
            args.objectives, SettingState.CMD_LINE)
    if args.target_cutoff_time is not None:
        gv.settings().set_general_target_cutoff_time(
            args.target_cutoff_time, SettingState.CMD_LINE)
    if args.wallclock_time is not None:
        gv.settings().set_config_wallclock_time(
            args.wallclock_time, SettingState.CMD_LINE)
    if args.cpu_time is not None:
        gv.settings().set_config_cpu_time(
            args.cpu_time, SettingState.CMD_LINE)
    if args.solver_calls is not None:
        gv.settings().set_config_solver_calls(
            args.solver_calls, SettingState.CMD_LINE)
    if args.number_of_runs is not None:
        gv.settings().set_config_number_of_runs(
            args.number_of_runs, SettingState.CMD_LINE)
    if args.run_on is not None:
        gv.settings().set_run_on(
            args.run_on.value, SettingState.CMD_LINE)


def run_after(solver: Path,
              train_set: InstanceSet,
              test_set: InstanceSet,
              dependency: list[Run],
              command: CommandName,
              run_on: Runner = Runner.SLURM) -> Run:
    """Add a command to run after configuration to RunRunner queue.

    Args:
      solver: Path (object) to solver.
      train_set: Instances used for training.
      test_set: Instances used for testing.
      dependency: List of job dependencies.
      command: The command to run. Currently supported: Validation and Ablation.
      run_on: Whether the job is executed on Slurm or locally.

    Returns:
      RunRunner Run object regarding the callback
    """
    cmd_file = "validate_configured_vs_default.py"
    if command == CommandName.RUN_ABLATION:
        cmd_file = "run_ablation.py"

    command_line = f"./sparkle/CLI/{cmd_file} --settings-file Settings/latest.ini "\
                   f"--solver {solver.name} --instance-set-train {train_set.directory}"\
                   f" --run-on {run_on}"
    if test_set is not None:
        command_line += f" --instance-set-test {test_set.directory}"

    run = rrr.add_to_queue(
        runner=run_on,
        cmd=command_line,
        name=command,
        dependencies=dependency,
        base_dir=sl.caller_log_dir,
        srun_options=["-N1", "-n1"],
        sbatch_options=gv.settings().get_slurm_extra_options(as_args=True))

    if run_on == Runner.LOCAL:
        print("Waiting for the local calculations to finish.")
        run.wait()
    return run


if __name__ == "__main__":
    # Log command call
    sl.log_command(sys.argv)

    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    apply_settings_from_args(args)

    validate = args.validate
    ablation = args.ablation
    solver = resolve_object_name(
        args.solver,
        gv.file_storage_data_mapping[gv.solver_nickname_list_path],
        gv.settings().DEFAULT_solver_dir, class_name=Solver)
    instance_set_train = resolve_object_name(
        args.instance_set_train,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        gv.settings().DEFAULT_instance_dir, instance_set)
    instance_set_test = args.instance_set_test
    if instance_set_test is not None:
        instance_set_test = resolve_object_name(
            args.instance_set_test,
            gv.file_storage_data_mapping[gv.instances_nickname_path],
            gv.settings().DEFAULT_instance_dir, instance_set)
    use_features = args.use_features
    run_on = gv.settings().get_run_on()
    if args.configurator is not None:
        gv.settings().set_general_sparkle_configurator(
            value=getattr(Configurator, args.configurator),
            origin=SettingState.CMD_LINE)

    # Check if Solver and instance sets were resolved
    check_for_initialise(COMMAND_DEPENDENCIES[CommandName.CONFIGURE_SOLVER])

    feature_data_df = None
    if use_features:
        feature_data = FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)

        data_dict = {}
        feature_data_df = feature_data.dataframe

        for label, row in feature_data_df.iterrows():
            # os.path.split(os.path.split(label)[0])[1] gives the dir/instance set name
            if os.path.split(os.path.split(label)[0])[1] == instance_set_train.name:
                if row.empty:
                    print("No feature data exists for the given training set, please "
                          "run add_feature_extractor.py, then compute_features.py")
                    sys.exit(-1)

                new_label = (f"../../../instances/{instance_set_train.name}/"
                             + os.path.split(label)[1])
                data_dict[new_label] = row

        feature_data_df = DataFrame.from_dict(data_dict, orient="index",
                                              columns=feature_data_df.columns)

        if feature_data.has_missing_value():
            print("You have unfinished feature computation jobs, please run "
                  "`sparkle compute features`")
            sys.exit(-1)

        for index, column in enumerate(feature_data_df):
            feature_data_df.rename(columns={column: f"Feature{index+1}"}, inplace=True)

    number_of_runs = gv.settings().get_config_number_of_runs()
    solver_calls = gv.settings().get_config_solver_calls()
    cpu_time = gv.settings().get_config_cpu_time()
    wallclock_time = gv.settings().get_config_wallclock_time()
    cutoff_time = gv.settings().get_general_target_cutoff_time()
    cutoff_length = gv.settings().get_configurator_target_cutoff_length()
    sparkle_objectives =\
        gv.settings().get_general_sparkle_objectives()
    configurator = gv.settings().get_general_sparkle_configurator()
    config_scenario = configurator.scenario_class(
        solver, instance_set_train, number_of_runs, solver_calls, cpu_time,
        wallclock_time, cutoff_time, cutoff_length, sparkle_objectives, use_features,
        configurator.configurator_target, feature_data_df)

    sbatch_options = gv.settings().get_slurm_extra_options(as_args=True)
    dependency_job_list = configurator.configure(
        scenario=config_scenario,
        sbatch_options=sbatch_options,
        num_parallel_jobs=gv.settings().get_number_of_jobs_in_parallel(),
        base_dir=sl.caller_log_dir,
        run_on=run_on)

    # Update latest scenario
    gv.latest_scenario().set_config_solver(solver)
    gv.latest_scenario().set_config_instance_set_train(instance_set_train.directory)
    gv.latest_scenario().set_latest_scenario(Scenario.CONFIGURATION)

    if instance_set_test is not None:
        gv.latest_scenario().set_config_instance_set_test(instance_set_test.directory)
    else:
        # Set to default to overwrite possible old path
        gv.latest_scenario().set_config_instance_set_test()

    # Set validation to wait until configuration is done
    if validate:
        validate_jobid = run_after(
            solver, instance_set_train, instance_set_test, dependency_job_list,
            command=CommandName.VALIDATE_CONFIGURED_VS_DEFAULT, run_on=run_on
        )
        dependency_job_list.append(validate_jobid)

    if ablation:
        ablation_jobid = run_after(
            solver, instance_set_train, instance_set_test, dependency_job_list,
            command=CommandName.RUN_ABLATION, run_on=run_on
        )
        dependency_job_list.append(ablation_jobid)

    if run_on == Runner.SLURM:
        job_id_str = ",".join([run.run_id for run in dependency_job_list])
        print(f"Running configuration. Waiting for Slurm job(s) with id(s): "
              f"{job_id_str}")
    else:
        print("Running configuration finished!")

    # Write used settings to file
    gv.settings().write_used_settings()
    # Write used scenario to file
    gv.latest_scenario().write_scenario_ini()
