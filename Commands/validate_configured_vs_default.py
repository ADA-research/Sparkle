#!/usr/bin/env python3
"""Sparkle command to validate a configured solver against its default configuration."""

import sys
import argparse
from pathlib import Path

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_configure_solver_help as scsh
from Commands.sparkle_help import sparkle_instances_help as sih
from Commands.sparkle_help import sparkle_slurm_help as ssh
from Commands.sparkle_help import sparkle_logging as sl
from Commands.sparkle_help import sparkle_settings
from Commands.sparkle_help.sparkle_settings import PerformanceMeasure
from Commands.sparkle_help.sparkle_settings import SettingState
from Commands.sparkle_help import argparse_custom as ac
from Commands.sparkle_help.reporting_scenario import ReportingScenario
from Commands.sparkle_help.reporting_scenario import Scenario
from Commands.sparkle_help.sparkle_command_help import CommandName
from Commands.sparkle_help import sparkle_command_help as sch

from sparkle.slurm_parsing import SlurmBatch
from runrunner.base import Runner
import runrunner as rrr


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description=("Test the performance of the configured solver and the default "
                     "solver by doing validation experiments on the training and test "
                     "sets."))
    parser.add_argument(
        "--solver",
        required=True,
        type=Path,
        help="path to solver"
    )
    parser.add_argument(
        "--instance-set-train",
        required=True,
        type=Path,
        help="path to training instance set",
    )
    parser.add_argument(
        "--instance-set-test",
        required=False,
        type=Path,
        help="path to testing instance set",
    )
    parser.add_argument(
        "--configurator",
        type=Path,
        help="path to configurator"
    )
    parser.add_argument(
        "--performance-measure",
        choices=PerformanceMeasure.__members__,
        default=sgh.settings.DEFAULT_general_sparkle_objective.PerformanceMeasure,
        action=ac.SetByUser,
        help="the performance measure, e.g. runtime",
    )
    parser.add_argument(
        "--target-cutoff-time",
        type=int,
        default=sgh.settings.DEFAULT_general_target_cutoff_time,
        action=ac.SetByUser,
        help="cutoff time per target algorithm run in seconds",
    )
    parser.add_argument(
        "--settings-file",
        type=Path,
        default=sgh.settings.DEFAULT_settings_path,
        action=ac.SetByUser,
        help="specify the settings file to use instead of the default",
    )
    parser.add_argument(
        "--run-on",
        default=Runner.SLURM,
        help=("On which computer or cluster environment to execute the calculation."
              "Available: local, slurm. Default: slurm")
    )
    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    sgh.settings = sparkle_settings.Settings()

    # Initialise latest scenario
    global latest_scenario
    sgh.latest_scenario = ReportingScenario()

    # Log command call
    sl.log_command(sys.argv)

    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    solver = args.solver
    instance_set_train = args.instance_set_train
    instance_set_test = args.instance_set_test
    run_on = args.run_on
    if args.configurator is not None:
        configurator_path = Path(args.configurator)
    else:
        configurator_path = Path("Components", "smac-v2.10.03-master-778")

    sch.check_for_initialise(sys.argv, sch.COMMAND_DEPENDENCIES[
                             sch.CommandName.VALIDATE_CONFIGURED_VS_DEFAULT])

    if ac.set_by_user(args, "settings_file"):
        sgh.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file
    args.performance_measure = PerformanceMeasure.from_str(args.performance_measure)
    if ac.set_by_user(args, "performance_measure"):
        sgh.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "target_cutoff_time"):
        sgh.settings.set_general_target_cutoff_time(
            args.target_cutoff_time, SettingState.CMD_LINE
        )

    instance_set_test_name = None

    # Make sure configuration results exist before trying to work with them
    scsh.check_validation_prerequisites(solver.name, instance_set_train.name)

    # Record optimised configuration
    scsh.write_optimised_configuration_str(solver.name, instance_set_train.name)
    scsh.write_optimised_configuration_pcs(solver.name, instance_set_train.name)

    if instance_set_test is not None:
        instance_set_test_name = instance_set_test.name

        # Copy test instances to smac directory (train should already be there from
        # configuration)
        instances_directory_test = Path("Instances/", instance_set_test_name)
        list_path = sih.get_list_all_path(instances_directory_test)
        inst_dir_prefix = instances_directory_test
        smac_inst_dir_prefix = Path(configurator_path, "scenarios/instances",
                                    instance_set_test_name)
        sih.copy_instances_to_smac(
            list_path, inst_dir_prefix, smac_inst_dir_prefix, "test"
        )

        # Copy file listing test instances to smac solver directory
        scsh.copy_file_instance(
            solver.name, instance_set_train.name, instance_set_test_name, "test"
        )

    # Create solver execution directories, and copy necessary files there
    scsh.prepare_smac_execution_directories_validation(
        solver.name, instance_set_train.name, instance_set_test_name
    )

    # Generate and run sbatch script for validation runs
    sbatch_script_name = ssh.generate_sbatch_script_for_validation(
        solver.name, instance_set_train.name, instance_set_test_name
    )
    sbatch_script_path = configurator_path / sbatch_script_name
    scenario_dir = "scenarios/" + solver.name + "_" + instance_set_train.name
    scenario_file_name = scsh.create_file_scenario_validate(
        solver.name, instance_set_train.name, instance_set_train.name,
        scsh.InstanceType.TRAIN, default=True)
        
    batch = SlurmBatch(sbatch_script_path)
    n_jobs = int(len(batch.cmd_params) / 2)
    parallel_jobs = min(sgh.settings.get_slurm_number_of_runs_in_parallel(), n_jobs)
    cmd = [f"{batch.cmd} {batch.cmd_params[i]}" for i in range(n_jobs)]
    dest = batch.cmd_params[n_jobs:]  # destination files for bash output

     # Adjust maximum number of cores to be the maximum of the instances we validate on
    instance_sizes = []
    # Get instance set sizes
    for instance_set_name, inst_type in [(instance_set_train.name, "train"),
                                         (instance_set_test_name, "test")]:
        if instance_set_name is not None:
            smac_instance_file = (f"{sgh.smac_dir}{scenario_dir}/{instance_set_name}_"
                                  f"{inst_type}.txt")
            if Path(smac_instance_file).is_file():
                instance_count = sum(1 for _ in open(smac_instance_file, "r"))
                instance_sizes.append(instance_count)

    # Number of cores available on a CPU of this cluster
    n_cpus = sgh.settings.get_slurm_clis_per_node()

    # Adjust cpus when nessacery
    if len(instance_sizes) > 0:
        max_instance_count = (max(*instance_sizes) if len(instance_sizes) > 1
                              else instance_sizes[0])
        n_cpus = min(n_cpus, max_instance_count)
    
    # Extend sbatch options
    sbatch_options_list = [f"--cpus-per-task={n_cpus}"]
    sbatch_options_list.extend(ssh.get_slurm_sbatch_default_options_list())
    # Get user options second to overrule defaults
    sbatch_options_list.extend(ssh.get_slurm_sbatch_user_options_list())

    # Set srun options
    srun_options = ["--nodes=1", "--ntasks=1", f"--cpus-per-task={n_cpus}"]
    srun_options.extend(ssh.get_slurm_srun_user_options_list())

    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd,
        name=CommandName.VALIDATE_CONFIGURED_VS_DEFAULT,
        path=configurator_path,
        base_dir=sgh.sparkle_tmp_path,
        parallel_jobs=parallel_jobs,
        sbatch_options=sbatch_options_list,
        srun_options=srun_options,
        output_path=dest)

    if run_on == Runner.SLURM:
        print(f"Running validation in parallel. Waiting for Slurm job with id: "
                f"{run.run_id}")
    else:
        run.wait()
    print("Running validation done!")

    # Write most recent run to file
    last_test_file_path = Path(
        configurator_path,
        "scenarios",
        f"{solver.name}_{sgh.sparkle_last_test_file_name}"
    )

    with Path(last_test_file_path).open("w+") as fout:
        fout.write(f"solver {solver}\n"
                   f"train {instance_set_train}\n")
        if instance_set_test is not None:
            fout.write(f"test {instance_set_test}\n")

    # Update latest scenario
    sgh.latest_scenario.set_config_solver(Path(solver))
    sgh.latest_scenario.set_config_instance_set_train(Path(instance_set_train))
    sgh.latest_scenario.set_latest_scenario(Scenario.CONFIGURATION)

    if instance_set_test is not None:
        sgh.latest_scenario.set_config_instance_set_test(Path(instance_set_test))
    else:
        # Set to default to overwrite possible old path
        sgh.latest_scenario.set_config_instance_set_test()

    # Write used settings to file
    sgh.settings.write_used_settings()
    # Write used scenario to file
    sgh.latest_scenario.write_scenario_ini()
