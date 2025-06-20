#!/usr/bin/env python3
"""Sparkle command to generate a report for an executed experiment."""
import sys
import shutil
import argparse
from pathlib import Path
import time

import pylatex as pl
from sparkle import __version__ as __sparkle_version__

from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import resolve_object_name
from sparkle.CLI.help import logging as sl
# from sparkle.platform.settings_objects import Settings, SettingState
from sparkle.CLI.help import argparse_custom as ac

# from sparkle.solver import Solver
from sparkle.selector import Extractor
# from sparkle.instance import Instance_Set
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
# from sparkle.configurator.ablation import AblationScenario
from sparkle.configurator.configurator import ConfigurationScenario
from sparkle.selector.selector import SelectionScenario
from sparkle.types import SolverStatus

from sparkle.platform import latex
from sparkle.platform.output.configuration_output import ConfigurationOutput
from sparkle.platform.output.selection_output import SelectionOutput
# from sparkle.platform.output.parallel_portfolio_output import ParallelPortfolioOutput


MAX_DEC = 4  # Maximum decimals used for each reported value


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generates a report for all known selection, configuration and "
                    "parallel portfolio scenarios will be generated.",
        epilog="If you wish to filter specific solvers, instance sets, ... have a look "
               "at the command line arguments.")
    # Add argument for filtering solvers
    # Add argument for filtering instance sets (Both train and test)
    # Add argument for filtering configurators
    # Add argument for filtering selectors
    # Add argument for filtering ??? scenario ids? configuration ids?
    parser.add_argument(*ac.GenerateJSONArgument.names,
                        **ac.GenerateJSONArgument.kwargs)
    return parser


def generate_configuration_section(report: pl.Document, scenario: ConfigurationScenario,
                                   scenario_output: ConfigurationOutput) -> None:
    """Generate a section for a configuration scenario."""
    report_dir = Path(report.default_filepath).parent
    time_stamp = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    plot_dir = report_dir /\
        f"{scenario.configurator.__name__}_{scenario.name}_plots_{time_stamp}"
    plot_dir.mkdir(exist_ok=True)

    # 1. Write section intro
    report.append(pl.Section(
        f"{scenario.configurator.__name__} Configuration: "
        f"{scenario.solver.name} on {scenario.instance_set.name}"))
    report.append("In this scenario, ")
    report.append(pl.UnsafeCommand(
        f"textbf{{{scenario.configurator.__name__}}} "
        f"({scenario.configurator.full_name})~\\cite"
        f"{{{scenario.configurator.__name__}}} with version "
        f"{scenario.configurator.version} was used for configuration. "))
    report.append(
        f"The Solver {scenario.solver} was optimised on training set "
        f"{scenario.instance_set}. The scenario was run {scenario.number_of_runs} "
        f"times independently with different seeds, yielding {scenario.number_of_runs} "
        f"configurations. The cutoff time for the solver was set to "
        f"{scenario.solver_cutoff_time} seconds. The optimised objective is "
        f"{scenario.sparkle_objectives[0]}. Each Configuration was evaluated on the "
        "training set to determine the best configuration, e.g. the best "
        f"{scenario.sparkle_objectives[0]} value on the training set.")

    # 2. Report all the configurator settings in table format
    report.append(pl.Subsection("Configurator Settings"))
    report.append("The following settings were used for "
                  f"{scenario.configurator.__name__}:\n")
    tabular = pl.Tabular("l|r")
    tabular.add_row("Setting", "Value")
    tabular.add_hline()
    for setting, value in scenario.serialise().items():
        tabular.add_row([setting, str(value)])
    table_conf_settings = pl.Table(position="h")
    table_conf_settings.append(pl.UnsafeCommand("centering"))
    table_conf_settings.append(tabular)
    table_conf_settings.add_caption("Configurator Settings")
    report.append(table_conf_settings)

    # 3. Report details on instance and solver used
    report.append(pl.Subsection("Solver & Instance Set(s) Details"))
    cs = scenario_output.solver.get_configuration_space()
    report.append(f"The solver {scenario_output.solver} was configured using "
                  f"{len(cs.values())} configurable (hyper)parameters. "
                  f"The configuration space has {len(cs.conditions)} conditions. ")
    report.append("The following instance sets were used for the scenario:")
    with report.create(pl.Itemize()) as instance_set_latex_list:
        for instance_set in [
                scenario_output.instance_set_train] + scenario_output.test_instance_sets:
            training_set_name = instance_set.name.replace("_", " ")  # Latex fix
            instance_set_latex_list.add_item(
                pl.UnsafeCommand(
                    f"textbf{{{training_set_name}}} ({instance_set.size} instances)"))

    # Function to generate a results summary of default vs best on an instance set
    def instance_set_summary(instance_set_name: str) -> None:
        """Generate a results summary of default vs best on an instance set."""
        instance_set_results = scenario_output.instance_set_results[instance_set_name]
        report.append(f"The {scenario.sparkle_objectives[0]} value of the Default "
                      f"Configuration on {instance_set_name} was ")
        report.append(pl.UnsafeCommand(
            f"textbf{{{round(instance_set_results.default_performance, MAX_DEC)}}}.\n"))
        report.append(f"The {scenario.sparkle_objectives[0]} value of the Best "
                      f"Configuration on {instance_set_name} was ")
        report.append(pl.UnsafeCommand(
            f"textbf{{{round(instance_set_results.best_performance, MAX_DEC)}}}.\n"))
        report.append("In ")
        report.append(latex.AutoRef(f"fig:bestvsdefault{instance_set_name}{time_stamp}"))
        report.append(pl.utils.bold(" "))  # Force white space
        report.append("the results are plotted per instance.")
        # Create graph to compare best configuration vs default on the instance set
        import pandas as pd
        df = pd.DataFrame(
            [instance_set_results.default_instance_performance,
             instance_set_results.best_instance_performance],
            index=["Default Configuration", "Best Configuration"], dtype=float).T
        plot = latex.comparison_plot(df, None)
        plot_path = plot_dir /\
            f"{scenario_output.best_configuration_key}_vs_"\
            f"Default_{instance_set_name}.pdf"
        plot.write_image(plot_path)
        with report.create(pl.Figure(position="h")) as figure:
            figure.add_image(str(plot_path.relative_to(report_dir)),
                             width=pl.utils.NoEscape(r"0.6\textwidth"))
            figure.add_caption(
                f"Best vs Default Performance on {instance_set_name} "
                f"({scenario.sparkle_objectives[0]})")
            figure.append(pl.UnsafeCommand(
                r"label{"
                f"fig:bestvsdefault{instance_set_name}{time_stamp}"
                r"}"))
        if scenario.sparkle_objectives[0].time:  # Write status table
            report.append("The following Solver status were found per instance:")
            tabular = pl.Tabular("l|c|c|c")
            tabular.add_row("Status", "Default", "Best", "Overlap")
            tabular.add_hline()
            # Count the statuses
            for status in SolverStatus:
                default_count, best_count, overlap_count = 0, 0, 0
                for instance in instance_set_results.instance_status_default.keys():
                    instance = str(instance)
                    default_hit = instance_set_results.instance_status_default[
                        instance] == status
                    best_hit = instance_set_results.instance_status_best[
                        instance] == status
                    default_count += default_hit
                    best_count += best_hit
                    overlap_count += (default_hit and best_hit)
                if default_count or best_count:
                    tabular.add_row(
                        status, default_count, best_count, overlap_count
                    )
            table_status_values = pl.Table(position="h")
            table_status_values.append(pl.UnsafeCommand("centering"))
            table_status_values.append(tabular)
            table_status_values.add_caption(
                "Status count for the best and default configuration.")
            report.append(table_status_values)

    # 4. Report the results of the best configuration on the training set vs the default
    report.append(pl.Subsection(
        f"Comparison of Default and Best Configuration on Training Set "
        f"{scenario_output.instance_set_train.name}"))
    instance_set_summary(scenario_output.instance_set_train.name)

    # 5. Report the actual config values
    report.append(pl.Subsubsection("Best Configuration Values"))
    if scenario_output.best_configuration_key ==\
            PerformanceDataFrame.default_configuration:
        report.append("The configurator failed to find a better configuration than the "
                      "default configuration on the training set in this scenario.")
    else:
        report.append("The following parameter values "
                      "were found to be the best on the training set:\n")
        tabular = pl.Tabular("l|r")
        tabular.add_row("Parameter", "Value")
        tabular.add_hline()
        for parameter, value in scenario_output.best_configuration.items():
            tabular.add_row([parameter, str(value)])
        table_best_values = pl.Table(position="h")
        table_best_values.append(pl.UnsafeCommand("centering"))
        table_best_values.append(tabular)
        table_best_values.add_caption("Best found configuration values")
        report.append(table_best_values)

    # 6. Report the results of best vs default conf on the test sets

    for test_set in scenario_output.test_instance_sets:
        report.append(pl.Subsection(
            f"Comparison of Default and Best Configuration on Test Set "
            f"{test_set.name}"))
        instance_set_summary(test_set.name)

    # 7. Report the parameter ablation scenario if present
    # TODO write parameter ablation if present
    # if scenario_output.ablation_scenario:
    #    ...


def generate_selection_section(report: pl.Document, scenario: SelectionScenario,
                               scenario_output: SelectionOutput) -> None:
    """Generate a section for a selection scenario."""
    # TODO: Should this section name be more unique?
    report_dir = Path(report.default_filepath).parent
    time_stamp = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    plot_dir = report_dir / f"{scenario.name}_plots_{time_stamp}"
    plot_dir.mkdir(exist_ok=True)
    report.append(pl.Section(
        f"Selection: {scenario.selector.model_class.__name__} on "
        f"{' '.join([s[0] for s in scenario_output.training_instance_sets])}"))
    report.append(f"In this scenario, a {scenario.selector.model_class.__name__} "
                  f" ({scenario.selector.selector_class.__name__}) was trained on the "
                  "performance and feature data using ASF-lib. The following solvers "
                  f"were run with a cutoff time of {scenario.solver_cutoff} seconds:")
    with report.create(pl.Itemize()) as solver_latex_list:
        for solver_name in scenario_output.solvers.keys():
            solver_name = solver_name.replace("_", " ")
            solver_latex_list.add_item(
                pl.UnsafeCommand(
                    f"textbf{{{solver_name}}} "
                    f"({len(scenario_output.solvers[solver_name])} configurations)"))
    # Report training instance sets
    report.append("The following training instance sets were used:")
    with report.create(pl.Itemize()) as instance_set_latex_list:
        for training_set_name, set_size in scenario_output.training_instance_sets:
            training_set_name = training_set_name.replace("_", " ")  # Latex fix
            instance_set_latex_list.add_item(
                pl.UnsafeCommand(
                    f"textbf{{{training_set_name}}} "
                    f"({set_size} instances)"))
    # Report feature extractors
    report.append("The following feature extractors were used with a extractor cutoff "
                  f"time of {scenario.extractor_cutoff} seconds:")
    with report.create(pl.Itemize()) as feature_extractor_latex_list:
        for feature_extractor_name in scenario.feature_extractors:
            extractor = resolve_object_name(
                feature_extractor_name,
                gv.file_storage_data_mapping[gv.extractor_nickname_list_path],
                gv.settings().DEFAULT_extractor_dir, class_name=Extractor)
            feature_extractor_name = feature_extractor_name.replace("_", " ")  # Latex
            feature_extractor_latex_list.add_item(
                pl.UnsafeCommand(f"textbf{{{feature_extractor_name}}} "
                                 f"({extractor.output_dimension} features)"))

    # Report Training results
    report.append(pl.Subsection("Training Results"))
    # 1. Report VBS and selector performance,  create ranking list of the solvers
    # TODO Add ref here to the training sets section?
    report.append(f"In this section, the {scenario.objective.name} results for the "
                  "portfolio selector on solving the training instance set(s) listed "
                  "is reported. ")
    report.append(f"The {scenario.objective.name} values for the Virtual Best Solver "
                  "(VBS), i.e., the perfect portfolio selector is ")
    report.append(pl.utils.bold(f"{round(scenario_output.vbs_performance, MAX_DEC)}"))
    report.append(", the actual portfolio selector performance is ")
    report.append(
        pl.utils.bold(f"{round(scenario_output.actual_performance, MAX_DEC)}.\n"))

    report.append("Below, the solvers are ranked based on "
                  f"{scenario.objective.name} performance:")
    with report.create(pl.Enumerate()) as ranking_list:
        for solver_name, conf_id, value in scenario_output.solver_performance_ranking:
            value = round(value, MAX_DEC)
            solver_name = solver_name.replace("_", " ")  # Latex fix
            ranking_list.add_item(
                pl.UnsafeCommand(f"textbf{{{solver_name}}} ({conf_id}): {value}"))

    # 2. Marginal contribution ranking list VBS
    report.append(pl.Subsubsection("Marginal Contribution Ranking List"))
    report.append(
        "The following list shows the marginal contribution ranking list for the VBS:")
    with report.create(pl.Enumerate()) as ranking_list:
        for (solver_name, conf_id,
             contribution, performance) in scenario_output.marginal_contribution_perfect:
            contribution, performance =\
                round(contribution, MAX_DEC), round(performance, MAX_DEC)
            ranking_list.add_item(pl.UnsafeCommand(
                f"textbf{{{solver_name}}} ({conf_id}): {contribution} ({performance})"))

    # 3. Marginal contribution ranking list actual selector
    report.append("The following list shows the marginal contribution ranking list for "
                  "the actual portfolio selector:")
    with report.create(pl.Enumerate()) as ranking_list:
        for (solver_name, conf_id,
             contribution, performance) in scenario_output.marginal_contribution_actual:
            contribution, performance =\
                round(contribution, MAX_DEC), round(performance, MAX_DEC)
            ranking_list.add_item(pl.UnsafeCommand(
                f"textbf{{{solver_name}}} ({conf_id}): {contribution} ({performance})"))

    # 4. Create scatter plot analysis
    report.append(pl.Subsubsection("Scatter Plot Analysis"))
    report.append(latex.AutoRef(f"fig:sbsvsselector{time_stamp}"))
    report.append(pl.utils.bold(" "))  # Trick to force a white space
    report.append("shows the empirical comparison between the portfolio "
                  "selector and the single best solver (SBS). ")
    report.append(latex.AutoRef("fig:vbsvsselector"))
    report.append(pl.utils.bold(" "))  # Trick to force a white space
    report.append("shows the empirical comparison between the actual portfolio selector "
                  "and the virtual best solver (VBS).")
    # Create figure on SBS versus the selector
    sbs_name, sbs_config, _ = scenario_output.solver_performance_ranking[0]
    # sbs_plot_name = f"{Path(sbs_name).name} ({sbs_config})"
    sbs_performance = scenario_output.sbs_performance
    selector_performance = scenario_output.actual_performance_data

    # Join the data together
    import pandas as pd
    df = pd.DataFrame(
        [sbs_performance, selector_performance],
        index=[f"{Path(sbs_name).name} ({sbs_config})", "Selector"], dtype=float).T
    plot = latex.comparison_plot(df, "Single Best Solver vs Selector")
    plot_path = plot_dir /\
        f"{Path(sbs_name).name}_{sbs_config}_vs_"\
        f"Selector_{scenario.selector.model_class.__name__}.pdf"
    plot.write_image(plot_path)
    with report.create(pl.Figure()) as figure:
        figure.add_image(str(plot_path.relative_to(report_dir)),
                         width=pl.utils.NoEscape(r"0.6\textwidth"))
        figure.add_caption("Empirical comparison between the Single Best Solver and the "
                           "Selector")
        label = r"label{fig:sbsvsselector" + str(time_stamp) + r"}"
        figure.append(pl.UnsafeCommand(f"{label}"))

    # Comparison between the actual portfolio selector in Sparkle and the VBS.
    vbs_performance = scenario_output.vbs_performance_data.tolist()
    df = pd.DataFrame([vbs_performance, selector_performance],
                      index=["Virtual Best Solver", "Selector"], dtype=float).T
    plot = latex.comparison_plot(df, "Virtual Best Solver vs Selector")
    plot_path = plot_dir /\
        f"Virtual_Best_Solver_vs_Selector_{scenario.selector.model_class.__name__}.pdf"
    plot.write_image(plot_path)
    with report.create(pl.Figure()) as figure:
        figure.add_image(str(plot_path.relative_to(report_dir)),
                         width=pl.utils.NoEscape(r"0.6\textwidth"))
        figure.add_caption(
            "Empirical comparison between the Virtual Best Solver and the Selector")
        figure.append(pl.UnsafeCommand(r"label{fig:vbsvsselector}"))

    if scenario_output.test_sets:
        report.append(pl.Subsection("Test Results"))
        report.append("The following results are reported on the test set(s):")
        with report.create(pl.Itemize()) as latex_list:
            for test_set_name, test_set_size in scenario_output.test_sets:
                result = round(scenario_output.test_set_performance[test_set_name],
                               MAX_DEC)
                latex_list.add_item(pl.UnsafeCommand(
                    f"textbf{{{test_set_name}}} ({test_set_size} instances): {result}"))


# def generate_parallel_portfolio_section(report: pl.Document,
# scenario: ParallelPortfolioScenario) -> None:
#    """Generate a section for a parallel portfolio scenario."""
#    pass


def main(argv: list[str]) -> None:
    """Generate a report for executed experiments in the platform."""
    # Log command call
    sl.log_command(sys.argv)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)

    """
    filter_solvers = None
    if args.solvers:
        filter_solvers = ...
    filter_training_sets = None
    if args.instance_set_train:
        filter_training_sets = ...
    filter_testing_sets = None
    if args.instance_set_test:
        filter_testing_sets = ...
    filter_configurators = None
    if args.configurators:
        filter_configurators = ...
    filter_selectors = None
    if args.selectors:
        selectors = ...
    """

    performance_data = PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path)
    feature_data = FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)

    # Fetch all known scenarios
    configuration_scenarios = gv.configuration_scenarios()
    selection_scenarios = gv.selection_scenarios()
    # TODO: Write and fetch parallel portfolios
    # parallel_portfolio_scenarios = ...

    # TODO: Filter scenarios based on args

    # TODO: Serialize each scenario and write to output
    processed_configuration_scenarios = []
    processed_selection_scenarios = []
    for configuration_scenario in configuration_scenarios:
        # TODO: Detect test set of the configuration scenario?
        # Or should it just be in there?
        # This leaves some questions how to resolve..
        processed_configuration_scenarios.append(
            (ConfigurationOutput(configuration_scenario,
                                 performance_data), configuration_scenario))
    for selection_scenario in selection_scenarios:
        # TODO: Detect test set of the selection scenario?
        processed_selection_scenarios.append(
            (SelectionOutput(selection_scenario,
                             feature_data), selection_scenario))

    # TODO write the serialisation
    raw_output = gv.settings().DEFAULT_output_analysis / "JSON"
    if raw_output.exists():  # Clean
        shutil.rmtree(raw_output)
    raw_output.mkdir()

    # TODO Write serialisation

    if args.only_json:  # Done
        sys.exit(0)

    # TODO: Group scenarios based on:
    # - Configuration / Selection / Parallel Portfolio
    #   - Training Instance Set / Testing Instance Set
    #   - Configurators can be merged as long as we can match their budgets clearly
    report_directory = gv.settings().DEFAULT_output_analysis / "report"
    if report_directory.exists():  # Clean it
        shutil.rmtree(report_directory)
    report_directory.mkdir()
    target_path = report_directory / "report"
    report = pl.document.Document(
        default_filepath=str(target_path),
        document_options=["british"])
    # TODO cleanup hard coded path
    bibpath = Path("sparkle/Components/latex_source/report.bib")
    newbibpath = report_directory / "report.bib"
    shutil.copy(bibpath, newbibpath)
    # BUGFIX for unknown package load in PyLatex
    p = pl.package.Package("lastpage")
    if p in report.packages:
        report.packages.remove(p)
    report.packages.append(pl.package.Package("geometry",
                                              options=["verbose",
                                                       "tmargin=3.5cm",
                                                       "bmargin=3.5cm",
                                                       "lmargin=3cm",
                                                       "rmargin=3cm"]))
    # Unsafe command for \emph{Sparkle}
    report.preamble.extend([
        pl.UnsafeCommand(
            "title",
            r"\emph{Sparkle} Algorithm Portfolio report"),
        pl.UnsafeCommand(
            "author",
            r"Generated by \emph{Sparkle} "
            f"(version: {__sparkle_version__})")])
    report.append(pl.Command("maketitle"))
    report.append(pl.Section("Introduction"))
    # TODO: A quick overview to the introduction on whats considered in the report
    # regarding Solvers, Instance Sets and Feature Extractors
    report.append(pl.UnsafeCommand(
        r"emph{Sparkle}~\cite{Hoos15} is a multi-agent problem-solving platform based on"
        r" Programming by Optimisation (PbO)~\cite{Hoos12}, and would provide a number "
        "of effective algorithm optimisation techniques (such as automated algorithm "
        "configuration, portfolio-based algorithm selection, etc.) to accelerate the "
        "existing solvers."))

    for (scenario_output, scenario) in processed_configuration_scenarios:
        generate_configuration_section(report, scenario, scenario_output)

    for (scenario_output, scenario) in processed_selection_scenarios:
        generate_selection_section(report, scenario, scenario_output)

    # TODO Parallel Portfolio sections

    # Adding bibliography
    report.append(pl.NewPage())  # Ensure it starts on new page
    report.append(pl.Command("bibliographystyle", arguments=["plain"]))
    report.append(pl.Command("bibliography", arguments=[str(newbibpath)]))
    # Generate the report .tex and .pdf
    report.generate_pdf(target_path, clean=False, clean_tex=False, compiler="pdflatex")
    # TODO: This should be done by PyLatex. Generate the bib and regenerate the report
    # Reference for the (terrible) solution: https://tex.stackexchange.com/
    # questions/63852/question-mark-or-bold-citation-key-instead-of-citation-number
    import subprocess
    # Run BibTex silently
    subprocess.run(["bibtex", newbibpath.with_suffix("")],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    report.generate_pdf(target_path, clean=False, clean_tex=False, compiler="pdflatex")
    report.generate_pdf(target_path, clean=False, clean_tex=False, compiler="pdflatex")
    print(f"Report generated at {target_path}.pdf")


if __name__ == "__main__":
    main(sys.argv[1:])
