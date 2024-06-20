#!/usr/bin/env python3
"""Sparkle command to configure a solver."""
from __future__ import annotations

import argparse
import sys
import os
from pathlib import Path
from pandas import DataFrame

from runrunner.base import Runner
import runrunner as rrr

from CLI.help.status_info import ConfigureSolverStatusInfo
import global_variables as gv
import sparkle_logging as sl
from sparkle.platform import settings_help
from CLI.support import ablation as sah
from sparkle.platform.settings_help import SettingState
from CLI.help.reporting_scenario import Scenario
from sparkle.structures import feature_data_csv_help as sfdcsv
from CLI.help import slurm_help as ssh
from CLI.help import command_help as ch
from sparkle.configurator.configurator import Configurator
from sparkle.configurator.configuration_scenario import ConfigurationScenario
from CLI.help.nicknames import resolve_object_name
from sparkle.solver.solver import Solver
from CLI.help.command_help import CommandName
from CLI.initialise import check_for_initialise
from CLI.help import argparse_custom as ac


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
    parser.add_argument(*ac.PerformanceMeasureSimpleArgument.names,
                        **ac.PerformanceMeasureSimpleArgument.kwargs)
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
        gv.settings.read_settings_ini(args.settings_file, SettingState.CMD_LINE)
    if args.performance_measure is not None:
        gv.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE)
    if args.target_cutoff_time is not None:
        gv.settings.set_general_target_cutoff_time(
            args.target_cutoff_time, SettingState.CMD_LINE)
    if args.wallclock_time is not None:
        gv.settings.set_config_wallclock_time(
            args.wallclock_time, SettingState.CMD_LINE)
    if args.cpu_time is not None:
        gv.settings.set_config_cpu_time(
            args.cpu_time, SettingState.CMD_LINE)
    if args.solver_calls is not None:
        gv.settings.set_config_solver_calls(
            args.solver_calls, SettingState.CMD_LINE)
    if args.number_of_runs is not None:
        gv.settings.set_config_number_of_runs(
            args.number_of_runs, SettingState.CMD_LINE)


def run_after(solver: Path,
              instance_set_train: Path,
              instance_set_test: Path,
              dependency: list[rrr.SlurmRun | rrr.LocalRun],
              command: CommandName,
              run_on: Runner = Runner.SLURM) -> rrr.SlurmRun | rrr.LocalRun:
    """Add a command to run after configuration to RunRunner queue.

    Args:
      solver: Path (object) to solver.
      instance_set_train: Path (object) to instances used for training.
      instance_set_test: Path (object) to instances used for testing.
      dependency: String of job dependencies.
      command: The command to run. Currently supported: Validation and Ablation.
      run_on: Whether the job is executed on Slurm or locally.

    Returns:
      RunRunner Run object regarding the callback
    """
    cmd_file = "validate_configured_vs_default.py"
    if command == CommandName.RUN_ABLATION:
        cmd_file = "run_ablation.py"

    command_line = f"./CLI/{cmd_file} --settings-file Settings/latest.ini "\
                   f"--solver {solver.name} --instance-set-train {instance_set_train}"\
                   f" --run-on {run_on}"
    if instance_set_test is not None:
        command_line += f" --instance-set-test {instance_set_test}"

    run = rrr.add_to_queue(runner=run_on,
                           cmd=command_line,
                           name=command,
                           dependencies=dependency,
                           base_dir=gv.sparkle_tmp_path,
                           srun_options=["-N1", "-n1"],
                           sbatch_options=ssh.get_slurm_options_list())

    if run_on == Runner.LOCAL:
        print("Waiting for the local calculations to finish.")
        run.wait()
    return run


if __name__ == "__main__":
    # Initialise settings
    global settings
    gv.settings = settings_help.Settings()

    # Log command call
    sl.log_command(sys.argv)

    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    apply_settings_from_args(args)

    validate = args.validate
    ablation = args.ablation
    solver_path = resolve_object_name(args.solver,
                                      gv.solver_nickname_mapping, gv.solver_dir)
    instance_set_train = resolve_object_name(args.instance_set_train,
                                             target_dir=gv.instance_dir)
    instance_set_test = args.instance_set_test
    if instance_set_test is not None:
        instance_set_test = Path(instance_set_test)
    use_features = args.use_features
    run_on = args.run_on
    if args.configurator is not None:
        gv.settings.set_general_sparkle_configurator(
            value=getattr(Configurator, args.configurator),
            origin=SettingState.CMD_LINE)

    # Check if Solver and instance sets were resolved
    check_for_initialise(sys.argv,
                         ch.COMMAND_DEPENDENCIES[ch.CommandName.CONFIGURE_SOLVER])

    feature_data_df = None
    if use_features:
        feature_data_csv = sfdcsv.SparkleFeatureDataCSV(gv.feature_data_csv_path)

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
                    sys.exit(-1)

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

    number_of_runs = gv.settings.get_config_number_of_runs()
    solver_calls = gv.settings.get_config_solver_calls()
    cpu_time = gv.settings.get_config_cpu_time()
    wallclock_time = gv.settings.get_config_wallclock_time()
    cutoff_time = gv.settings.get_general_target_cutoff_time()
    cutoff_length = gv.settings.get_smac_target_cutoff_length()
    sparkle_objective =\
        gv.settings.get_general_sparkle_objectives()[0]
    configurator = gv.settings.get_general_sparkle_configurator()
    config_scenario = ConfigurationScenario(
        solver, instance_set_train, number_of_runs, solver_calls, cpu_time,
        wallclock_time, cutoff_time, cutoff_length, sparkle_objective, use_features,
        configurator.configurator_target, feature_data_df)

    sbatch_options = ssh.get_slurm_options_list() if run_on == Runner.SLURM else []
    dependency_job_list = configurator.configure(scenario=config_scenario,
                                                 sbatch_options=sbatch_options,
                                                 run_on=run_on)

    # Update latest scenario
    gv.latest_scenario().set_config_solver(solver.directory)
    gv.latest_scenario().set_config_instance_set_train(instance_set_train)
    gv.latest_scenario().set_latest_scenario(Scenario.CONFIGURATION)

    if instance_set_test is not None:
        gv.latest_scenario().set_config_instance_set_test(instance_set_test)
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
        print(f"Running configuration in parallel. Waiting for Slurm job(s) with id(s): "
              f"{job_id_str}")
    else:
        print("Running configuration finished!")

    status_info.delete()
    # Write used settings to file
    gv.settings.write_used_settings()
    # Write used scenario to file
    gv.latest_scenario().write_scenario_ini()
