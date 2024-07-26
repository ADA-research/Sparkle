#!/usr/bin/env python3
"""Sparkle command to generate a report for an executed experiment."""

import sys
import argparse
from pathlib import Path, PurePath

from sparkle.CLI.help import global_variables as gv
from sparkle.solver.ablation import AblationScenario
from sparkle.platform import generate_report_for_selection as sgfs
from sparkle.platform import \
    generate_report_for_configuration as sgrfch
from sparkle.CLI.help import sparkle_logging as sl
from sparkle.types.objective import PerformanceMeasure
from sparkle.platform.settings_objects import Settings, SettingState
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help.reporting_scenario import Scenario
from sparkle.platform import \
    generate_report_for_parallel_portfolio as sgrfpph
from sparkle.solver import Solver
from sparkle.solver.validator import Validator
from sparkle.instance import InstanceSet
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.configurator.configuration_scenario import ConfigurationScenario

from sparkle.CLI.help import command_help as ch
from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help.nicknames import resolve_object_name


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
    gv.settings = Settings()

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
    test_case_dir = args.test_case_directory

    solver = resolve_object_name(args.solver,
                                 gv.solver_nickname_mapping,
                                 gv.settings.DEFAULT_solver_dir, Solver)
    instance_set_train = resolve_object_name(
        args.instance_set_train,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        gv.settings.DEFAULT_instance_dir, InstanceSet)
    instance_set_test = resolve_object_name(
        args.instance_set_train,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        gv.settings.DEFAULT_instance_dir, InstanceSet)

    check_for_initialise(ch.COMMAND_DEPENDENCIES[ch.CommandName.GENERATE_REPORT])

    # Do first, so other command line options can override settings from the file
    if ac.set_by_user(args, "settings_file"):
        gv.settings.read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )
    if ac.set_by_user(args, "performance_measure"):
        gv.settings.set_general_sparkle_objectives(
            args.performance_measure, SettingState.CMD_LINE)

    # If no arguments are set get the latest scenario
    if not selection and test_case_dir is None and solver is None:
        scenario = gv.latest_scenario().get_latest_scenario()
        if scenario == Scenario.SELECTION:
            selection = True
            test_case_dir = gv.latest_scenario().get_selection_test_case_directory()
        elif scenario == Scenario.CONFIGURATION:
            solver = gv.latest_scenario().get_config_solver()
            instance_set_train = gv.latest_scenario().get_config_instance_set_train()
            instance_set_test = gv.latest_scenario().get_config_instance_set_test()
        elif scenario == Scenario.PARALLEL_PORTFOLIO:
            parallel_portfolio_path = gv.latest_scenario().get_parallel_portfolio_path()
            pap_instance_set =\
                gv.latest_scenario().get_parallel_portfolio_instance_set()

    flag_instance_set_train = instance_set_train is not None
    flag_instance_set_test = instance_set_test is not None

    # Reporting for algorithm selection
    if selection or test_case_dir is not None:
        performance_measure =\
            gv.settings.get_general_sparkle_objectives()[0].PerformanceMeasure
        if performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION or \
           performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION:
            print("ERROR: The generate_report command is not yet implemented for the"
                  " QUALITY_ABSOLUTE performance measure! (functionality coming soon)")
            sys.exit(-1)

        if not gv.settings.DEFAULT_algorithm_selector_path.is_file():
            print("Before generating a Sparkle report, please first construct the "
                  "Sparkle portfolio selector!")
            print("Not generating a Sparkle report, stopping execution!")
            sys.exit(-1)

        print("Generating report for selection...")
        train_data = PerformanceDataFrame(gv.performance_data_csv_path)
        feature_data = FeatureDataFrame(gv.feature_data_csv_path)
        train_data.penalise(gv.settings.get_general_target_cutoff_time(),
                            gv.settings.get_penalised_time())
        test_data = None
        test_case_path = Path(test_case_dir) if test_case_dir is not None else None
        if test_case_dir is not None and (test_case_path
                                          / "sparkle_performance_data.csv").exists():
            test_data = PerformanceDataFrame(
                test_case_path / "sparkle_performance_data.csv")
            test_data.penalise(gv.settings.get_general_target_cutoff_time(),
                               gv.settings.get_penalised_time())
        actual_portfolio_selector_path = gv.settings.DEFAULT_algorithm_selector_path
        sgfs.generate_report_selection(gv.selection_output_analysis,
                                       gv.sparkle_latex_dir,
                                       "template-Sparkle-for-selection.tex",
                                       gv.sparkle_report_bibliography_path,
                                       gv.settings.DEFAULT_extractor_dir,
                                       actual_portfolio_selector_path,
                                       feature_data,
                                       train_data,
                                       gv.settings.get_general_extractor_cutoff_time(),
                                       gv.settings.get_general_target_cutoff_time(),
                                       gv.settings.get_penalised_time(),
                                       test_data)
        if test_case_dir is None:
            print("Report generated ...")
        else:
            print("Report for test generated ...")

    elif gv.latest_scenario().get_latest_scenario() == Scenario.PARALLEL_PORTFOLIO:
        # Reporting for parallel portfolio
        sgrfpph.generate_report_parallel_portfolio(
            parallel_portfolio_path,
            gv.parallel_portfolio_output_analysis,
            gv.sparkle_latex_dir,
            gv.sparkle_report_bibliography_path,
            gv.settings.get_general_sparkle_objectives()[0],
            gv.settings.get_general_target_cutoff_time(),
            gv.settings.get_penalised_time(),
            pap_instance_set)
        print("Parallel portfolio report generated ...")
    else:
        # Reporting for algorithm configuration
        if solver is None:
            print("Error! No Solver found for configuration report generation.")
            sys.exit(-1)

        # If only the testing set is given return an error
        if not flag_instance_set_train and flag_instance_set_test:
            print("Argument Error! Only a testing set was provided, please also "
                  "provide a training set")
            print(f"Usage: {sys.argv[0]} --solver <solver> [--instance-set-train "
                  "<instance-set-train>] [--instance-set-test <instance-set-test>]")
            sys.exit(-1)
        instance_set_train_name = instance_set_train.name
        gv.settings.get_general_sparkle_configurator()\
            .set_scenario_dirs(solver, instance_set_train)
        # Generate a report depending on which instance sets are provided
        if flag_instance_set_train or flag_instance_set_test:
            # Check if there are result to generate a report from
            validator = Validator(gv.validation_output_general)
            train_res = validator.get_validation_results(
                solver, instance_set_train)
            if instance_set_test is not None:
                test_res = validator.get_validation_results(solver,
                                                            instance_set_test)
            if len(train_res) == 0 or (instance_set_test is not None
                                       and len(test_res) == 0):
                print("Error: Results not found for the given solver and instance set(s)"
                      ' combination. Make sure the "configure_solver" and "validate_'
                      'configured_vs_default" commands were correctly executed. ')
                sys.exit(-1)
        else:
            print("Error: No results from validate_configured_vs_default found that "
                  "can be used in the report!")
            sys.exit(-1)
        # Extract config scenario data for report, but this should be read from the
        # scenario file instead as we can't know wether features were used or not now
        number_of_runs = gv.settings.get_config_number_of_runs()
        solver_calls = gv.settings.get_config_solver_calls()
        cpu_time = gv.settings.get_config_cpu_time()
        wallclock_time = gv.settings.get_config_wallclock_time()
        cutoff_time = gv.settings.get_general_target_cutoff_time()
        cutoff_length = gv.settings.get_configurator_target_cutoff_length()
        sparkle_objective =\
            gv.settings.get_general_sparkle_objectives()[0]
        configurator = gv.settings.get_general_sparkle_configurator()
        configurator.scenario = ConfigurationScenario(
            solver, instance_set_train, number_of_runs, solver_calls, cpu_time,
            wallclock_time, cutoff_time, cutoff_length, sparkle_objective)
        configurator.scenario._set_paths(configurator.output_path)
        ablation_scenario = None
        if args.flag_ablation:
            ablation_scenario = AblationScenario(
                solver, instance_set_train, instance_set_test,
                gv.ablation_output_general)
        sgrfch.generate_report_for_configuration(
            solver,
            gv.settings.get_general_sparkle_configurator(),
            Validator(gv.validation_output_general),
            gv.settings.DEFAULT_extractor_dir,
            gv.configuration_output_analysis,
            gv.sparkle_latex_dir,
            gv.sparkle_report_bibliography_path,
            instance_set_train,
            gv.settings.get_general_penalty_multiplier(),
            gv.settings.get_general_extractor_cutoff_time(),
            instance_set_test,
            ablation=ablation_scenario
        )

    # Write used settings to file
    gv.settings.write_used_settings()
