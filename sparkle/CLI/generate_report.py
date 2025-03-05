#!/usr/bin/env python3
"""Sparkle command to generate a report for an executed experiment."""
import sys
import argparse
import ast
from pathlib import Path, PurePath

from sparkle.CLI.help import global_variables as gv
from sparkle.configurator.ablation import AblationScenario
from sparkle.platform import generate_report_for_selection as sgfs
from sparkle.platform import \
    generate_report_for_configuration as sgrfch
from sparkle.CLI.help import logging as sl
from sparkle.platform.settings_objects import Settings, SettingState
from sparkle.CLI.help import argparse_custom as ac
from sparkle.CLI.help.reporting_scenario import Scenario
from sparkle.platform import \
    generate_report_for_parallel_portfolio as sgrfpph
from sparkle.solver import Solver
from sparkle.instance import Instance_Set
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.platform.output.configuration_output import ConfigurationOutput
from sparkle.platform.output.selection_output import SelectionOutput
from sparkle.platform.output.parallel_portfolio_output import ParallelPortfolioOutput

from sparkle.CLI.initialise import check_for_initialise
from sparkle.CLI.help.nicknames import resolve_object_name


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Without any arguments a report for the most recent algorithm "
                    "selection or algorithm configuration procedure is generated.",
        epilog="Note that if a test instance set is given, the training instance set "
               "must also be given.")
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
    parser.add_argument(*ac.ObjectivesArgument.names,
                        **ac.ObjectivesArgument.kwargs)
    parser.add_argument(*ac.SettingsFileArgument.names,
                        **ac.SettingsFileArgument.kwargs)
    parser.add_argument(*ac.GenerateJSONArgument.names,
                        **ac.GenerateJSONArgument.kwargs)
    return parser


def main(argv: list[str]) -> None:
    """Generate a report for an executed experiment."""
    # Log command call
    sl.log_command(sys.argv)
    check_for_initialise()

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)

    # Do first, so other command line options can override settings from the file
    if ac.set_by_user(args, "settings_file"):
        gv.settings().read_settings_ini(
            args.settings_file, SettingState.CMD_LINE
        )
    if args.objectives is not None:
        gv.settings().set_general_sparkle_objectives(
            args.objectives, SettingState.CMD_LINE)
    selection = args.selection
    test_case_dir = args.test_case_directory
    only_json = args.only_json

    solver = resolve_object_name(
        args.solver,
        gv.file_storage_data_mapping[gv.solver_nickname_list_path],
        gv.settings().DEFAULT_solver_dir, Solver)
    instance_set_train = resolve_object_name(
        args.instance_set_train,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        gv.settings().DEFAULT_instance_dir, Instance_Set)
    instance_set_test = resolve_object_name(
        args.instance_set_train,
        gv.file_storage_data_mapping[gv.instances_nickname_path],
        gv.settings().DEFAULT_instance_dir, Instance_Set)

    Settings.check_settings_changes(gv.settings(),
                                    Settings(PurePath("Settings/latest.ini")))
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
        objective = gv.settings().get_general_sparkle_objectives()[0]
        if not objective.time:
            print("ERROR: The selection report is not implemented for "
                  " non-runtime objectives!")
            sys.exit(-1)
        selection_scenario = gv.latest_scenario().get_selection_scenario_path()
        actual_portfolio_selector_path = selection_scenario / "portfolio_selector"
        if not actual_portfolio_selector_path.is_file():
            print("Before generating a Sparkle report, please first construct the "
                  "Sparkle portfolio selector. Not generating a Sparkle report, stopping"
                  " execution!")
            sys.exit(-1)

        print("Generating report for selection...")
        train_data = PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path)
        feature_data = FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)
        test_data = None
        test_case_path = Path(test_case_dir) if test_case_dir is not None else None
        if test_case_dir is not None and (test_case_path
                                          / "performance_data.csv").exists():
            test_data = PerformanceDataFrame(test_case_path / "performance_data.csv")
        # Create machine readable selection output
        instance_dirs = set(Path(instance).parent for instance in train_data.instances)
        instance_sets = []
        for dir in instance_dirs:
            instance_sets.append(Instance_Set(dir))
        test_set = None if test_case_dir is None else Instance_Set(Path(test_case_dir))
        cutoff_time = gv.settings().get_general_target_cutoff_time()
        output = gv.settings().DEFAULT_selection_output_analysis
        selection_output = SelectionOutput(
            selection_scenario, train_data, feature_data,
            instance_sets, test_set, objective, cutoff_time,
            output)
        selection_output.write_output()
        print("Machine readable output is placed at:", selection_output.output)

        if not only_json:
            sgfs.generate_report_selection(
                gv.settings().DEFAULT_selection_output_analysis,
                gv.settings().DEFAULT_latex_source,
                "template-Sparkle-for-selection.tex",
                gv.settings().DEFAULT_latex_bib,
                gv.settings().DEFAULT_extractor_dir,
                selection_scenario,
                feature_data,
                train_data,
                objective,
                gv.settings().get_general_extractor_cutoff_time(),
                gv.settings().get_general_target_cutoff_time(),
                test_data
            )
            if test_case_dir is None:
                print("Report generated ...")
            else:
                print("Report for test generated ...")

    elif gv.latest_scenario().get_latest_scenario() == Scenario.PARALLEL_PORTFOLIO:
        # Reporting for parallel portfolio
        # Machine readable Output
        cutoff_time = gv.settings().get_general_target_cutoff_time()
        objective = gv.settings().get_general_sparkle_objectives()[0]
        output = gv.settings().DEFAULT_parallel_portfolio_output_analysis
        parallel_portfolio_output = ParallelPortfolioOutput(parallel_portfolio_path,
                                                            pap_instance_set,
                                                            objective,
                                                            output)
        parallel_portfolio_output.write_output()
        print("Machine readable output is placed at:", parallel_portfolio_output.output)

        if not only_json:
            sgrfpph.generate_report_parallel_portfolio(
                parallel_portfolio_path,
                gv.settings().DEFAULT_parallel_portfolio_output_analysis,
                gv.settings().DEFAULT_latex_source,
                gv.settings().DEFAULT_latex_bib,
                gv.settings().get_general_sparkle_objectives()[0],
                gv.settings().get_general_target_cutoff_time(),
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
        # Extract config scenario data for report, but this should be read from the
        # scenario file instead as we can't know wether features were used or not now
        configurator = gv.settings().get_general_sparkle_configurator()
        config_scenario = gv.latest_scenario().get_configuration_scenario(
            configurator.scenario_class())
        ablation_scenario = None
        if args.flag_ablation:
            ablation_scenario = AblationScenario(
                config_scenario, instance_set_test,
                gv.settings().DEFAULT_ablation_output)
        performance_data = PerformanceDataFrame(
            gv.settings().DEFAULT_performance_data_path)
        # Filter the performance data to solver/instance sets
        performance_data = performance_data
        if performance_data.num_solvers > 1:
            performance_data.remove_solver(
                [s for s in performance_data.solvers
                 if s != solver.directory])

        used_instances = [str(i) for i in instance_set_train.instance_paths]
        if instance_set_test:
            used_instances += [str(i) for i in instance_set_test.instance_paths]
        for i in performance_data.instances:
            if i not in used_instances:
                performance_data.remove_instance(i)

        # Verify the data in the Performance DataFrame
        # Check that each run has produced a valid configuration
        for instance in instance_set_train.instance_paths:
            configurations = performance_data.get_value(
                str(solver.directory),
                str(instance),
                objective=config_scenario.sparkle_objective.name,
                solver_fields=[PerformanceDataFrame.column_configuration])
            for i, config in enumerate(configurations):
                try:
                    config = ast.literal_eval(config)
                    if config == {}:
                        print(f"WARNING: No configuration found for {instance}, run {i}")
                except ValueError:
                    continue

        # Check that all jobs have been executed
        configuration_jobs = performance_data.get_job_list()
        if len(configuration_jobs) > 0:
            print(f"ERROR: {(len(configuration_jobs))} jobs for configuration were not "
                  "executed! Please run 'sparkle run solvers --performance-data' before "
                  "continuing.")
            sys.exit(-1)
        # Create machine readable output
        output = gv.settings().DEFAULT_configuration_output_analysis
        config_output = ConfigurationOutput(config_scenario.directory,
                                            configurator,
                                            config_scenario,
                                            performance_data,
                                            instance_set_test,
                                            output)
        config_output.write_output()
        print("Machine readable output is placed at:", config_output.output)

        if not only_json:
            sgrfch.generate_report_for_configuration(
                config_scenario,
                config_output,
                gv.settings().DEFAULT_extractor_dir,
                gv.settings().DEFAULT_configuration_output_analysis,
                gv.settings().DEFAULT_latex_source,
                gv.settings().DEFAULT_latex_bib,
                gv.settings().get_general_extractor_cutoff_time(),
                ablation=ablation_scenario,
            )

    # Write used settings to file
    gv.settings().write_used_settings()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
