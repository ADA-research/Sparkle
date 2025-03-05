#!/usr/bin/env python3
"""Sparkle command to execute a portfolio selector."""

import sys
import argparse
from pathlib import PurePath, Path

import runrunner as rrr
from runrunner import Runner

from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.platform.settings_objects import Settings, SettingState
from sparkle.CLI.help import argparse_custom as ac
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.CLI.help.reporting_scenario import Scenario
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help.nicknames import resolve_object_name
from sparkle.instance import Instance_Set
from sparkle.CLI.compute_features import compute_features


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run a portfolio selector on instance (set), determine which solver "
                    "is most likely to perform well and run it on the instance (set).")
    parser.add_argument(*ac.InstancePathPositional.names,
                        **ac.InstancePathPositional.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    return parser


def main(argv: list[str]) -> None:
    """Main function of the run portfolio selector command."""
    # Log command call
    sl.log_command(sys.argv)
    check_for_initialise()

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)

    if ac.set_by_user(args, "settings_file"):
        gv.settings().read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file
    if args.run_on is not None:
        gv.settings().set_run_on(args.run_on.value, SettingState.CMD_LINE)

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings(), prev_settings)

    data_set = resolve_object_name(
        args.instance_path,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        gv.settings().DEFAULT_instance_dir, Instance_Set)

    if data_set is None:
        print("ERROR: The instance (set) could not be found. Please make sure the "
              "path is correct.")
        sys.exit(-1)

    run_on = gv.settings().get_run_on()

    selector_scenario = gv.latest_scenario().get_selection_scenario_path()
    selector_path = selector_scenario / "portfolio_selector"
    if not selector_path.exists() or not selector_path.is_file():
        print("ERROR: The portfolio selector could not be found. Please make sure to "
              "first construct a portfolio selector.")
        sys.exit(-1)
    if len([p for p in gv.settings().DEFAULT_extractor_dir.iterdir()]) == 0:
        print("ERROR: No feature extractor added to Sparkle.")
        sys.exit(-1)

    # Compute the features of the incoming instances
    test_case_path = selector_scenario / data_set.name
    test_case_path.mkdir(exist_ok=True)
    feature_dataframe = FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)
    feature_dataframe.remove_instances(feature_dataframe.instances)
    feature_dataframe.csv_filepath = test_case_path / "feature_data.csv"
    feature_dataframe.add_instances(data_set.instance_paths)
    feature_dataframe.save_csv()
    feature_run = compute_features(feature_dataframe, recompute=False, run_on=run_on)

    if run_on == Runner.LOCAL:
        feature_run.wait()
    objectives = gv.settings().get_general_sparkle_objectives()
    # Prepare performance data
    performance_data = PerformanceDataFrame(
        test_case_path / "performance_data.csv",
        objectives=objectives)
    for instance_name in data_set.instance_names:
        if instance_name not in performance_data.instances:
            performance_data.add_instance(instance_name)
    performance_data.add_solver(selector_path.name)
    performance_data.save_csv()
    # Update latest scenario
    gv.latest_scenario().set_selection_test_case_directory(test_case_path)
    gv.latest_scenario().set_latest_scenario(Scenario.SELECTION)
    # Write used scenario to file
    gv.latest_scenario().write_scenario_ini()

    run_core = Path(__file__).parent.parent.resolve() /\
        "CLI" / "core" / "run_portfolio_selector_core.py"
    cmd_list = [f"python3 {run_core} "
                f"--selector {selector_path} "
                f"--feature-data-csv {feature_dataframe.csv_filepath} "
                f"--performance-data-csv {performance_data.csv_filepath} "
                f"--instance {instance_path} "
                f"--log-dir {sl.caller_log_dir}"
                for instance_path in data_set.instance_paths]

    import subprocess
    selector_run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=f"Portfolio Selector: {selector_path.name} on {data_set.name}",
        stdout=None if run_on == Runner.LOCAL else subprocess.PIPE,  # Print to screen
        base_dir=sl.caller_log_dir,
        dependencies=feature_run,
        sbatch_options=gv.settings().get_slurm_extra_options(as_args=True),
        prepend=gv.settings().get_slurm_job_prepend())

    if run_on == Runner.LOCAL:
        selector_run.wait()
        print("Running Sparkle portfolio selector done!")
    else:
        print("Sparkle portfolio selector is running ...")

    # Write used settings to file
    gv.settings().write_used_settings()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
