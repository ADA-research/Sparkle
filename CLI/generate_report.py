#!/usr/bin/env python3
"""Sparkle command to generate a report for an executed experiment."""

import sys
import argparse
from pathlib import Path

from CLI.help.status_info import GenerateReportStatusInfo
import global_variables as sgh
from sparkle.platform import generate_report_help as sgrh
from sparkle.platform import \
    generate_report_for_configuration as sgrfch
import sparkle_logging as sl
from sparkle.platform import settings_help
from sparkle.types.objective import PerformanceMeasure
from sparkle.platform.settings_help import SettingState
from CLI.help import argparse_custom as ac
from CLI.help.reporting_scenario import Scenario
from sparkle.platform import \
    generate_report_for_parallel_portfolio as sgrfpph
from CLI.help import command_help as ch
from CLI.initialise import check_for_initialise


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description=("Without any arguments a report for the most recent algorithm "
                     "selection or algorithm configuration procedure is generated."),
        epilog=("Note that if a test instance set is given, the training instance set "
                "must also be given."))
    # Configuration arguments
    parser.add_argument(
        "--solver",
        required=False,
        type=str,
        default=None,
        help="path to solver for an algorithm configuration report",
    )
    parser.add_argument(
        "--instance-set-train",
        required=False,
        type=str,
        help=("path to training instance set included in Sparkle for an algorithm"
              " configuration report"),
    )
    parser.add_argument(
        "--instance-set-test",
        required=False,
        type=str,
        help=("path to testing instance set included in Sparkle for an algorithm"
              " configuration report"),
    )
    parser.add_argument(
        "--no-ablation",
        required=False,
        dest="flag_ablation",
        default=True,
        const=False,
        nargs="?",
        help="turn off reporting on ablation for an algorithm configuration report",
    )
    # Selection arguments
    parser.add_argument(
        "--selection",
        action="store_true",
        help="set to generate a normal selection report",
    )
    parser.add_argument(
        "--test-case-directory",
        type=str,
        default=None,
        help="Path to test case directory of an instance set for a selection report",
    )
    # Common arguments
    parser.add_argument(
        "--performance-measure",
        choices=PerformanceMeasure.__members__,
        default=sgh.settings.DEFAULT_general_sparkle_objective.PerformanceMeasure,
        action=ac.SetByUser,
        help="the performance measure, e.g. runtime",
    )
    parser.add_argument(
        "--settings-file",
        type=Path,
        default=sgh.settings.DEFAULT_settings_path,
        action=ac.SetByUser,
        help=("specify the settings file to use in case you want to use one other than"
              " the default"),
    )
    return parser


if __name__ == "__main__":
    # Initialise settings
    global settings
    sgh.settings = settings_help.Settings()

    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args()
    selection = args.selection
    test_case_directory = args.test_case_directory

    solver = args.solver
    instance_set_train = args.instance_set_train
    instance_set_test = args.instance_set_test

    check_for_initialise(sys.argv,
                         ch.COMMAND_DEPENDENCIES[ch.CommandName.GENERATE_REPORT])

    # Do first, so other command line options can override settings from the file
    if ac.set_by_user(args, "settings_file"):
        sgh.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "performance_measure"):
        sgh.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE)

    # If no arguments are set get the latest scenario
    if not selection and test_case_directory is None and solver is None:
        scenario = sgh.latest_scenario().get_latest_scenario()
        if scenario == Scenario.SELECTION:
            selection = True
            test_case_directory = (
                sgh.latest_scenario().get_selection_test_case_directory()
            )
        elif scenario == Scenario.CONFIGURATION:
            solver = str(sgh.latest_scenario().get_config_solver())
            instance_set_train = sgh.latest_scenario().get_config_instance_set_train()
            instance_set_test = sgh.latest_scenario().get_config_instance_set_test()
        elif scenario == Scenario.PARALLEL_PORTFOLIO:
            parallel_portfolio_path = sgh.latest_scenario().get_parallel_portfolio_path()
            pap_instance_list = (
                sgh.latest_scenario().get_parallel_portfolio_instance_list())

    flag_instance_set_train = instance_set_train is not None
    flag_instance_set_test = instance_set_test is not None

    # Reporting for algorithm selection
    if selection or test_case_directory is not None:
        performance_measure =\
            sgh.settings.get_general_sparkle_objectives()[0].PerformanceMeasure
        if performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION or \
           performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION:
            print("ERROR: The generate_report command is not yet implemented for the"
                  " QUALITY_ABSOLUTE performance measure! (functionality coming soon)")
            sys.exit(-1)

        if not Path(sgh.sparkle_algorithm_selector_path).is_file():
            print("Before generating a Sparkle report, please first construct the "
                  "Sparkle portfolio selector!")
            print("Not generating a Sparkle report, stopping execution!")
            sys.exit(-1)

        print("Generating report for selection...")
        status_info = GenerateReportStatusInfo()
        status_info.set_report_type(sgh.ReportType.ALGORITHM_SELECTION)
        status_info.save()
        sgrh.generate_report_selection(test_case_directory)
        if test_case_directory is None:
            print("Report generated ...")
        else:
            print("Report for test generated ...")
        status_info.delete()

    elif sgh.latest_scenario().get_latest_scenario() == Scenario.PARALLEL_PORTFOLIO:
        # Reporting for parallel portfolio
        status_info = GenerateReportStatusInfo()
        status_info.set_report_type(sgh.ReportType.PARALLEL_PORTFOLIO)
        status_info.save()

        sgrfpph.generate_report_parallel_portfolio(
            parallel_portfolio_path, pap_instance_list)
        print("Parallel portfolio report generated ...")
        status_info.delete()
    else:
        status_info = GenerateReportStatusInfo()
        status_info.set_report_type(sgh.ReportType.ALGORITHM_CONFIGURATION)
        status_info.save()
        # Reporting for algorithm configuration
        if solver is None:
            print("Error! No Solver found for configuration report generation.")
            sys.exit(-1)
        solver_name = Path(solver).name

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

        instance_set_train_name = Path(instance_set_train).name
        instance_set_test_name = None
        sgh.settings.get_general_sparkle_configurator()\
            .set_scenario_dirs(solver_name, instance_set_train_name)
        # Generate a report depending on which instance sets are provided
        if flag_instance_set_train and flag_instance_set_test:
            instance_set_test_name = Path(instance_set_test).name
            sgrfch.check_results_exist(
                solver_name, instance_set_train_name, instance_set_test_name
            )
        elif flag_instance_set_train:
            sgrfch.check_results_exist(solver_name, instance_set_train_name)
        else:
            print("Error: No results from validate_configured_vs_default found that "
                  "can be used in the report!")
            sys.exit(-1)

        sgrfch.generate_report_for_configuration(
            solver_name,
            instance_set_train_name,
            instance_set_test_name,
            ablation=args.flag_ablation,
        )

        status_info.delete()

    # Write used settings to file
    sgh.settings.write_used_settings()
