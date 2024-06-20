#!/usr/bin/env python3
"""Sparkle command to generate a report for an executed experiment."""

import sys
import argparse
from pathlib import Path, PurePath

from CLI.help.status_info import GenerateReportStatusInfo
import global_variables as gv
from sparkle.platform import generate_report_help as sgrh
from sparkle.platform import \
    generate_report_for_configuration as sgrfch
import sparkle_logging as sl
from sparkle.platform import settings_help
from sparkle.types.objective import PerformanceMeasure
from sparkle.platform.settings_help import SettingState, Settings
from CLI.help import argparse_custom as ac
from CLI.help.reporting_scenario import Scenario
from sparkle.platform import \
    generate_report_for_parallel_portfolio as sgrfpph
from sparkle.solver.solver import Solver
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise
from CLI.help.nicknames import resolve_object_name


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description=("Without any arguments a report for the most recent algorithm "
                     "selection or algorithm configuration procedure is generated."),
        epilog=("Note that if a test instance set is given, the training instance set "
                "must also be given."))
    # Configuration arguments
    parser.add_argument(*ac.SolverReportArgument.names,
                        **ac.SolverReportArgument.kwargs)
    parser.add_argument(*ac.InstanceSetTrainReportArgument.names,
                        **ac.InstanceSetTrainReportArgument.kwargs)
    parser.add_argument(*ac.InstanceSetTestReportArgument.names,
                        **ac.InstanceSetTestReportArgument.kwargs)
    parser.add_argument(*ac.NoAblationReportArgument.names,
                        **ac.NoAblationReportArgument.kwargs)
    # Selection arguments
    parser.add_argument(*ac.SelectionReportArgument.names,
                        **ac.SelectionReportArgument.kwargs)
    parser.add_argument(*ac.TestCaseDirectoryArgument.names,
                        **ac.TestCaseDirectoryArgument.kwargs)
    # Common arguments
    parser.add_argument(*ac.PerformanceMeasureArgument.names,
                        **ac.PerformanceMeasureArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    gv.settings = settings_help.Settings()

    # Compare current settings to latest.ini
    prev_settings = Settings(PurePath("Settings/latest.ini"))
    Settings.check_settings_changes(gv.settings, prev_settings)

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    selection = args.selection
    test_case_directory = args.test_case_directory

    solver_path = resolve_object_name(args.solver,
                                      gv.solver_nickname_mapping, gv.solver_dir)
    solver = Solver(solver_path)
    instance_set_train = resolve_object_name(args.instance_set_train,
                                             target_dir=gv.instance_dir)
    instance_set_test = resolve_object_name(args.instance_set_test,
                                            target_dir=gv.instance_dir)

    check_for_initialise(sys.argv,
                         ch.COMMAND_DEPENDENCIES[ch.CommandName.GENERATE_REPORT])

    # Do first, so other command line options can override settings from the file
    if ac.set_by_user(args, "settings_file"):
        gv.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "performance_measure"):
        gv.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE)

    # If no arguments are set get the latest scenario
    if not selection and test_case_directory is None and solver_path is None:
        scenario = gv.latest_scenario().get_latest_scenario()
        if scenario == Scenario.SELECTION:
            selection = True
            test_case_directory = (
                gv.latest_scenario().get_selection_test_case_directory()
            )
        elif scenario == Scenario.CONFIGURATION:
            solver_path = str(gv.latest_scenario().get_config_solver())
            instance_set_train = gv.latest_scenario().get_config_instance_set_train()
            instance_set_test = gv.latest_scenario().get_config_instance_set_test()
        elif scenario == Scenario.PARALLEL_PORTFOLIO:
            parallel_portfolio_path = gv.latest_scenario().get_parallel_portfolio_path()
            pap_instance_list = (
                gv.latest_scenario().get_parallel_portfolio_instance_list())

    flag_instance_set_train = instance_set_train is not None
    flag_instance_set_test = instance_set_test is not None

    # Reporting for algorithm selection
    if selection or test_case_directory is not None:
        performance_measure =\
            gv.settings.get_general_sparkle_objectives()[0].PerformanceMeasure
        if performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION or \
           performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION:
            print("ERROR: The generate_report command is not yet implemented for the"
                  " QUALITY_ABSOLUTE performance measure! (functionality coming soon)")
            sys.exit(-1)

        if not Path(gv.sparkle_algorithm_selector_path).is_file():
            print("Before generating a Sparkle report, please first construct the "
                  "Sparkle portfolio selector!")
            print("Not generating a Sparkle report, stopping execution!")
            sys.exit(-1)

        print("Generating report for selection...")
        status_info = GenerateReportStatusInfo()
        status_info.set_report_type(gv.ReportType.ALGORITHM_SELECTION)
        status_info.save()
        sgrh.generate_report_selection(test_case_directory)
        if test_case_directory is None:
            print("Report generated ...")
        else:
            print("Report for test generated ...")
        status_info.delete()

    elif gv.latest_scenario().get_latest_scenario() == Scenario.PARALLEL_PORTFOLIO:
        # Reporting for parallel portfolio
        status_info = GenerateReportStatusInfo()
        status_info.set_report_type(gv.ReportType.PARALLEL_PORTFOLIO)
        status_info.save()

        sgrfpph.generate_report_parallel_portfolio(
            parallel_portfolio_path, pap_instance_list)
        print("Parallel portfolio report generated ...")
        status_info.delete()
    else:
        status_info = GenerateReportStatusInfo()
        status_info.set_report_type(gv.ReportType.ALGORITHM_CONFIGURATION)
        status_info.save()
        # Reporting for algorithm configuration
        if solver_path is None:
            print("Error! No Solver found for configuration report generation.")
            sys.exit(-1)
        elif isinstance(solver_path, str):
            solver_path = Path(solver_path)
        solver_name = solver_path.name

        # If no instance set(s) is/are given, try to retrieve them from the last run of
        # validate_configured_vs_default
        if not flag_instance_set_train and not flag_instance_set_test:
            (
                instance_set_train,
                instance_set_test,
                flag_instance_set_train,
                flag_instance_set_test,
            ) = sgrfch.get_most_recent_test_run()

        # If only the testing set is given return an error
        elif not flag_instance_set_train and flag_instance_set_test:
            print("Argument Error! Only a testing set was provided, please also "
                  "provide a training set")
            print(f"Usage: {sys.argv[0]} --solver <solver> [--instance-set-train "
                  "<instance-set-train>] [--instance-set-test <instance-set-test>]")
            sys.exit(-1)

        instance_set_train_name = instance_set_train.name
        instance_set_test_name = None
        gv.settings.get_general_sparkle_configurator()\
            .set_scenario_dirs(solver_name, instance_set_train_name)
        # Generate a report depending on which instance sets are provided
        if flag_instance_set_train and flag_instance_set_test:
            instance_set_test_name = instance_set_test.name
            sgrfch.check_results_exist(
                solver, instance_set_train_name, instance_set_test_name
            )
        elif flag_instance_set_train:
            sgrfch.check_results_exist(solver, instance_set_train_name)
        else:
            print("Error: No results from validate_configured_vs_default found that "
                  "can be used in the report!")
            sys.exit(-1)

        sgrfch.generate_report_for_configuration(
            solver,
            instance_set_train_name,
            instance_set_test_name,
            ablation=args.flag_ablation,
        )

        status_info.delete()

    # Write used settings to file
    gv.settings.write_used_settings()
