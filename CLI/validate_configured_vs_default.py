#!/usr/bin/env python3
"""Sparkle command to validate a configured solver against its default configuration."""

import sys
import argparse
import fcntl
from pathlib import Path

from runrunner.base import Runner
import runrunner as rrr

from CLI.sparkle_help import sparkle_global_help as sgh
from CLI.sparkle_help import sparkle_configure_solver_help as scsh
from CLI.sparkle_help import sparkle_instances_help as sih
from CLI.sparkle_help import sparkle_slurm_help as ssh
from CLI.sparkle_help import sparkle_logging as sl
from CLI.sparkle_help import sparkle_settings
from sparkle.types.objective import PerformanceMeasure
from CLI.sparkle_help.sparkle_settings import SettingState
from CLI.sparkle_help import argparse_custom as ac
from CLI.help.reporting_scenario import Scenario
from sparkle.configurator.configurator import Configurator
from CLI.help.command_help import CommandName
from CLI.help import command_help as ch
from sparkle.platform import file_help as sfh
from CLI.initialise import check_for_initialise


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
        choices=[Runner.LOCAL, Runner.SLURM],
        help=("On which computer or cluster environment to execute the calculation.")
    )
    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    sgh.settings = sparkle_settings.Settings()

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
        sgh.settings.set_general_sparkle_configurator(
            value=getattr(Configurator, args.configurator),
            origin=SettingState.CMD_LINE)
    configurator = sgh.settings.get_general_sparkle_configurator()
    configurator.set_scenario_dirs(Path(solver).name, instance_set_train.name)

    check_for_initialise(
        sys.argv,
        ch.COMMAND_DEPENDENCIES[ch.CommandName.VALIDATE_CONFIGURED_VS_DEFAULT]
    )

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

    instance_set_test_name = None

    # Make sure configuration results exist before trying to work with them
    scsh.check_validation_prerequisites()

    # Record optimised configuration
    scsh.write_optimised_configuration_str(solver.name, instance_set_train.name)
    scsh.write_optimised_configuration_pcs(solver.name, instance_set_train.name)

    if instance_set_test is not None:
        instance_set_test_name = instance_set_test.name

        # Create instance file list for test set in configurator
        instances_directory_test = sgh.instance_dir / instance_set_test_name
        list_path = sih.get_list_all_path(instances_directory_test)
        instance_list_test_path = configurator.instances_path\
            / instance_set_test_name / (instance_set_test_name + "_test.txt")
        instance_list_test_path.parent.mkdir(parents=True, exist_ok=True)
        with instance_list_test_path.open("w+") as fout:
            for instance in list_path:
                fout.write(f"{instance.absolute()}\n")

    # Create solver execution directories, and copy necessary files there
    scsh.prepare_smac_execution_directories_validation(instance_set_test_name)
    configurator = sgh.settings.get_general_sparkle_configurator()
    # Set up scenarios
    # 1. Set up the validation scenario for the training set
    cmd_base = "./smac-validate --use-scenario-outdir true --num-run 1 --cli-cores 8"
    scenario_dir = configurator.scenario.directory.relative_to(
        configurator.configurator_path)

    scenario_fn_train = scsh.create_file_scenario_validate(
        solver.name, instance_set_train.name, instance_set_train.name,
        scsh.InstanceType.TRAIN, default=True)
    cmd_list = [f"{cmd_base} --scenario-file {scenario_dir / scenario_fn_train} "
                f"--execdir {scenario_dir} "
                f"--configuration DEFAULT"]
    dest = [Path("results") / (solver.name + "_validation_" + scenario_fn_train)]

    # If given, also validate on the test set
    if instance_set_test_name is not None:
        # 2. Test default
        scenario_fn_tdef = scsh.create_file_scenario_validate(
            solver.name, instance_set_train.name, instance_set_test_name,
            scsh.InstanceType.TEST, default=True)
        exec_dir_def = scenario_dir / f"validate_{instance_set_test_name}_test_default/"

        # 3. Test configured
        scenario_fn_tconf = scsh.create_file_scenario_validate(
            solver.name, instance_set_train.name, instance_set_test_name,
            scsh.InstanceType.TEST, default=False)
        dir_name = f"validate_{instance_set_test_name}_test_configured/"
        exec_dir_conf = scenario_dir / dir_name

        # Write configuration to file to be used by smac-validate
        config_file_path = configurator.scenario.directory /\
            "configuration_for_validation.txt"
        # open the file of sbatch script
        with config_file_path.open("w+") as fout:
            fcntl.flock(fout.fileno(), fcntl.LOCK_EX)
            optimised_configuration_str, _, _ = scsh.get_optimised_configuration(
                solver.name, instance_set_train.name)
            fout.write(optimised_configuration_str + "\n")

        # Extend job list
        cmd_list.extend([f"{cmd_base} --scenario-file {scenario_dir / scenario_fn_tdef} "
                         f"--execdir {scenario_dir} "
                         f"--configuration DEFAULT",
                         f"{cmd_base} --scenario-file {scenario_dir / scenario_fn_tconf}"
                         f" --execdir {scenario_dir}"
                         f" --configuration-list {config_file_path.absolute()}"])

        dest.extend([f"results/{solver.name}_validation_{scenario_fn_tdef}",
                     f"results/{solver.name}_validation_{scenario_fn_tconf}"])

    # Adjust maximum number of cores to be the maximum of the instances we validate on
    instance_sizes = [sgh.settings.get_slurm_clis_per_node()]
    # Get instance set sizes
    for instance_set_name, inst_type in [(instance_set_train.name, "train"),
                                         (instance_set_test_name, "test")]:
        if instance_set_name is not None:
            dir = configurator.scenarios_path / instance_set_name
            smac_instance_file = f"{dir}_{inst_type}.txt"
            if Path(smac_instance_file).is_file():
                instance_count = sum(1 for _ in open(smac_instance_file, "r"))
                instance_sizes.append(instance_count)

    # Maximum number of cpus we can use
    n_cpus = min(sgh.settings.get_slurm_clis_per_node(), max(instance_sizes))

    # Extend sbatch options
    sbatch_options_list = [f"--cpus-per-task={n_cpus}"] + ssh.get_slurm_options_list()

    # Set srun options
    srun_options = ["-N1", "-n1", f"--cpus-per-task={n_cpus}"] +\
        ssh.get_slurm_options_list()
    success, msg = ssh.check_slurm_option_compatibility(" ".join(srun_options))
    if not success:
        print(f"Slurm config Error: {msg}")
        sys.exit(-1)
    # Clear out possible existing destination files
    sfh.rmfiles(dest)
    parallel_jobs = min(sgh.settings.get_slurm_number_of_runs_in_parallel(),
                        len(cmd_list))

    run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=CommandName.VALIDATE_CONFIGURED_VS_DEFAULT,
        path=configurator.configurator_path,
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

    # Write most recent run to file
    last_test_file_path =\
        configurator.scenarios_path / f"{solver.name}_{sgh.sparkle_last_test_file_name}"

    with Path(last_test_file_path).open("w+") as fout:
        fout.write(f"solver {solver}\n"
                   f"train {instance_set_train}\n")
        if instance_set_test is not None:
            fout.write(f"test {instance_set_test}\n")

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
