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
from sparkle.structures import FeatureDataFrame
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help.nicknames import resolve_object_name
from sparkle.instance import Instance_Set
from sparkle.CLI.compute_features import compute_features
from sparkle.selector import SelectionScenario, Extractor


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run a portfolio selector on instance (set): Determine which solver "
                    "is most likely to perform well and run it on the instance (set).")
    parser.add_argument(*ac.SelectionScenarioArgument.names,
                        **ac.SelectionScenarioArgument.kwargs)
    parser.add_argument(*ac.InstanceSetRequiredArgument.names,
                        **ac.InstanceSetRequiredArgument.kwargs)
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
        args.instance,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        gv.settings().DEFAULT_instance_dir, Instance_Set)

    if data_set is None:
        print("ERROR: The instance (set) could not be found. Please make sure the "
              "path is correct.")
        sys.exit(-1)

    run_on = gv.settings().get_run_on()
    selector_scenario = SelectionScenario.from_file(args.selection_scenario)
    # Create a new feature dataframe for this run, compute the features
    test_case_path = selector_scenario.directory / data_set.name
    test_case_path.mkdir(exist_ok=True)
    feature_dataframe = FeatureDataFrame(test_case_path / "feature_data.csv")
    for extractor_name in selector_scenario.feature_extractors:
        extractor = resolve_object_name(
            extractor_name,
            gv.file_storage_data_mapping[gv.instances_nickname_path],
            gv.settings().DEFAULT_extractor_dir, Extractor)
        feature_dataframe.add_extractor(extractor_name, extractor.features)

    feature_dataframe.add_instances(data_set.instance_paths)
    feature_dataframe.save_csv()
    feature_run = compute_features(feature_dataframe, recompute=False, run_on=run_on)

    if run_on == Runner.LOCAL:
        feature_run.wait()
    # Results need to be stored in the performance data object of the scenario:
    # Add the instance set to it
    for instance in data_set.instance_paths:
        selector_scenario.selector_performance_data.add_instance(str(instance))
    selector_scenario.selector_performance_data.save_csv()

    run_core = Path(__file__).parent.parent.resolve() /\
        "CLI" / "core" / "run_portfolio_selector_core.py"
    cmd_list = [
        f"python3 {run_core} "
        f"--selector-scenario {args.selection_scenario} "
        f"--feature-data-csv {feature_dataframe.csv_filepath} "
        f"--instance {instance_path} "
        f"--log-dir {sl.caller_log_dir} "
        for instance_path in data_set.instance_paths]

    import subprocess
    selector_run = rrr.add_to_queue(
        runner=run_on,
        cmd=cmd_list,
        name=f"Portfolio Selector: {selector_scenario.selector.name} on {data_set.name}",
        stdout=None if run_on == Runner.LOCAL else subprocess.PIPE,  # Print to screen
        stderr=None if run_on == Runner.LOCAL else subprocess.PIPE,  # Print to screen
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
