#!/usr/bin/env python3
"""Sparkle command to execute a portfolio selector."""

import sys
import argparse

from runrunner import Runner

from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import logging as sl
from sparkle.platform.settings_objects import Settings
from sparkle.CLI.help import argparse_custom as ac
from sparkle.structures import FeatureDataFrame
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help.nicknames import resolve_object_name
from sparkle.instance import Instance_Set, InstanceSet
from sparkle.CLI.compute_features import compute_features
from sparkle.selector import SelectionScenario, Extractor


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run a portfolio selector on instance (set): Determine which solver "
        "is most likely to perform well and run it on the instance (set)."
    )
    parser.add_argument(
        *ac.SelectionScenarioArgument.names, **ac.SelectionScenarioArgument.kwargs
    )
    parser.add_argument(
        *ac.InstanceSetRequiredArgument.names, **ac.InstanceSetRequiredArgument.kwargs
    )
    # Settings arguments
    parser.add_argument(*ac.SettingsFileArgument.names, **ac.SettingsFileArgument.kwargs)
    parser.add_argument(*Settings.OPTION_run_on.args, **Settings.OPTION_run_on.kwargs)
    return parser


def main(argv: list[str]) -> None:
    """Main function of the run portfolio selector command."""
    # Define command line arguments
    parser = parser_function()
    # Process command line arguments
    args = parser.parse_args(argv)
    settings = gv.settings(args)

    # Log command call
    sl.log_command(sys.argv, settings.random_state)
    check_for_initialise()

    # Compare current settings to latest.ini
    prev_settings = Settings(Settings.DEFAULT_previous_settings_path)
    Settings.check_settings_changes(settings, prev_settings)

    data_set: InstanceSet = resolve_object_name(
        args.instance,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        settings.DEFAULT_instance_dir,
        Instance_Set,
    )

    if data_set is None:
        print(
            "ERROR: The instance (set) could not be found. Please make sure the "
            "path is correct."
        )
        sys.exit(-1)

    run_on = settings.run_on
    selector_scenario = SelectionScenario.from_file(args.selection_scenario)
    # Create a new feature dataframe for this run, compute the features
    test_case_path = selector_scenario.directory / data_set.name
    test_case_path.mkdir(exist_ok=True)
    feature_dataframe = FeatureDataFrame(test_case_path / "feature_data.csv")
    feature_dataframe.remove_instances(feature_dataframe.instances)
    for extractor_name in selector_scenario.feature_extractors:
        extractor = resolve_object_name(
            extractor_name,
            gv.file_storage_data_mapping[gv.instances_nickname_path],
            settings.DEFAULT_extractor_dir,
            Extractor,
        )
        feature_dataframe.add_extractor(extractor_name, extractor.features)

    feature_dataframe.add_instances(data_set.instances)
    feature_dataframe.save_csv()
    feature_runs = compute_features(feature_dataframe, recompute=False, run_on=run_on)

    # Results need to be stored in the performance data object of the scenario:
    # Add the instance set to it
    for instance in data_set.instance_names:
        selector_scenario.selector_performance_data.add_instance(str(instance))
    selector_scenario.selector_performance_data.save_csv()

    selector_run = selector_scenario.selector.run_cli(
        scenario_path=selector_scenario.scenario_file,
        instance_set=data_set,
        feature_data=feature_dataframe.csv_filepath,
        run_on=run_on,
        slurm_prepend=settings.slurm_job_prepend,
        sbatch_options=settings.sbatch_settings,
        dependencies=feature_runs,
        log_dir=sl.caller_log_dir,
    )

    if run_on == Runner.LOCAL:
        selector_run.wait()
        print("Running Sparkle portfolio selector done!")
    else:
        print("Sparkle portfolio selector is running ...")

    # Write used settings to file
    settings.write_used_settings()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
