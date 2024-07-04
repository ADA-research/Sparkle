#!/usr/bin/env python3
"""Sparkle command to execute a portfolio selector."""

import sys
import argparse
from pathlib import Path, PurePath

import global_variables as gv
from CLI.support import run_portfolio_selector_help as srpsh
import sparkle_logging as sl
from sparkle.platform import settings_help
from sparkle.platform.settings_help import SettingState, Settings
from CLI.help import argparse_custom as ac
from sparkle.types.objective import PerformanceMeasure
from sparkle.structures.performance_dataframe import PerformanceDataFrame
from CLI.help import command_help as ch
from CLI.help.reporting_scenario import Scenario
from CLI.initialise import check_for_initialise
from CLI.help.nicknames import resolve_object_name
from sparkle.instance import InstanceSet


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(*ac.InstancePathPositional.names,
                        **ac.InstancePathPositional.kwargs)
    parser.add_argument(*ac.RunOnArgument.names,
                        **ac.RunOnArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    parser.add_argument(*ac.PerformanceMeasureArgument.names,
                        **ac.PerformanceMeasureArgument.kwargs)

    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    gv.settings = settings_help.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()

    if args.run_on is not None:
        gv.settings.set_run_on(
            args.run_on, SettingState.CMD_LINE)
    run_on = gv.settings.get_run_on()

    instance_set = resolve_object_name(
        args.instance_path,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        gv.instance_dir, InstanceSet)

    check_for_initialise(
        sys.argv,
        ch.COMMAND_DEPENDENCIES[ch.CommandName.RUN_SPARKLE_PORTFOLIO_SELECTOR]
    )

    if ac.set_by_user(args, "settings_file"):
        gv.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )  # Do first, so other command line options can override settings from the file
    if ac.set_by_user(args, "performance_measure"):
        gv.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE
        )

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings, prev_settings)

    if gv.settings.get_general_sparkle_objectives()[0].PerformanceMeasure\
            == PerformanceMeasure.QUALITY_ABSOLUTE:
        print(
            "ERROR: The run_sparkle_portfolio_selector command is not yet implemented"
            " for the QUALITY_ABSOLUTE performance measure! (functionality coming soon)"
        )
        sys.exit(-1)
    selector_path = Path("Sparkle_Portfolio_Selector",
                         "sparkle_portfolio_selector__@@SPARKLE@@__")
    if not selector_path.exists() or not selector_path.is_file():
        print("ERROR: The portfolio selector could not be found. Please make sure to "
              "first construct a portfolio selector.")
        sys.exit(-1)

    # Multipe
    if instance_set.size > 1:
        test_case_path = Path("Test_Cases") / instance_set.name
        test_case_path.mkdir(parents=True, exist_ok=True)
        # Update latest scenario
        gv.latest_scenario().set_selection_test_case_directory(test_case_path)
        gv.latest_scenario().set_latest_scenario(Scenario.SELECTION)
        # Write used scenario to file
        gv.latest_scenario().write_scenario_ini()
        test_performance_data = PerformanceDataFrame(
            test_case_path / "sparkle_performance_data.csv")
        srpsh.run_portfolio_selector_on_instances(
            instance_set.instance_paths, test_performance_data, selector_path,
            run_on=run_on)
    # Single instance
    elif instance_set.size == 1:
        srpsh.call_sparkle_portfolio_selector_solve_instance(
            instance_set.instance_paths[0])
        print("Running Sparkle portfolio selector done!")
    else:
        print("Input instance or instance directory error!")

    # Write used settings to file
    gv.settings.write_used_settings()
