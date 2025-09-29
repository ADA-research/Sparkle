#!/usr/bin/env python3
"""Sparkle command to generate a report for an executed experiment."""

import sys
import shutil
import argparse
from pathlib import Path
import time
import json
import pandas as pd

from pylatex import NoEscape, NewPage
import pylatex as pl
from sparkle import __version__ as __sparkle_version__

from sparkle.CLI.help import global_variables as gv
from sparkle.CLI.help import resolve_object_name
from sparkle.CLI.help import logging as sl
from sparkle.CLI.help import argparse_custom as ac

from sparkle.solver import Solver
from sparkle.instance import Instance_Set
from sparkle.selector import Extractor
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.configurator.configurator import ConfigurationScenario
from sparkle.selector.selector import SelectionScenario
from sparkle.types import SolverStatus
from sparkle.platform import Settings

from sparkle.platform import latex
from sparkle.platform.output.configuration_output import ConfigurationOutput
from sparkle.platform.output.selection_output import SelectionOutput


MAX_DEC = 4  # Maximum decimals used for each reported value
MAX_COLS_PER_TABLE = 2  # number of value columns extra to number of key columns
WIDE_TABLE_THRESHOLD = 4  # columns above which we switch to landscape
NUM_KEYS_PDF = 3
NUM_KEYS_FDF = 3
MAX_CELL_LEN = 17


def parser_function() -> argparse.ArgumentParser:
    """Define the command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generates a report for all known selection, configuration and "
        "parallel portfolio scenarios will be generated.",
        epilog="If you wish to filter specific solvers, instance sets, ... have a look "
        "at the command line arguments.",
    )
    # Add argument for filtering solvers
    parser.add_argument(
        *ac.SolversReportArgument.names, **ac.SolversReportArgument.kwargs
    )
    # Add argument for filtering instance sets
    parser.add_argument(
        *ac.InstanceSetsReportArgument.names, **ac.InstanceSetsReportArgument.kwargs
    )

    # Add argument for filtering appendix
    parser.add_argument(
        *Settings.OPTION_appendices.args, **Settings.OPTION_appendices.kwargs
    )

    # Add argument for filtering configurators?
    # Add argument for filtering selectors?
    # Add argument for filtering ??? scenario ids? configuration ids?
    parser.add_argument(*ac.GenerateJSONArgument.names, **ac.GenerateJSONArgument.kwargs)
    return parser


def generate_configuration_section(
    report: pl.Document,
    scenario: ConfigurationScenario,
    scenario_output: ConfigurationOutput,
) -> None:
    """Generate a section for a configuration scenario."""
    report_dir = Path(report.default_filepath).parent
    time_stamp = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    plot_dir = (
        report_dir
        / f"{scenario.configurator.__name__}_{scenario.name}_plots_{time_stamp}"
    )
    plot_dir.mkdir(exist_ok=True)

    # 1. Write section intro
    report.append(
        pl.Section(
            f"{scenario.configurator.__name__} Configuration: "
            f"{scenario.solver.name} on {scenario.instance_set.name}"
        )
    )
    report.append("In this scenario, ")
    report.append(
        pl.UnsafeCommand(
            f"textbf{{{scenario.configurator.__name__}}} "
            f"({scenario.configurator.full_name})~\\cite"
            f"{{{scenario.configurator.__name__}}} with version "
            f"{scenario.configurator.version} was used for configuration. "
        )
    )
    report.append(
        f"The Solver {scenario.solver} was optimised on training set "
        f"{scenario.instance_set}. The scenario was run {scenario.number_of_runs} "
        f"times independently with different seeds, yielding {scenario.number_of_runs} "
        f"configurations. The cutoff time for the solver was set to "
        f"{scenario.solver_cutoff_time} seconds. The optimised objective is "
        f"{scenario.sparkle_objectives[0]}. Each Configuration was evaluated on the "
        "training set to determine the best configuration, e.g. the best "
        f"{scenario.sparkle_objectives[0]} value on the training set."
    )

    # 2. Report all the configurator settings in table format
    report.append(pl.Subsection("Configurator Settings"))
    report.append(
        f"The following settings were used for {scenario.configurator.__name__}:\n"
    )
    tabular = pl.Tabular("l|r")
    tabular.add_row("Setting", "Value")
    tabular.add_hline()
    for setting, value in scenario.serialise().items():
        # Keep only the last path segment for paths
        # Otherwise tables get too wide and we can't see other values
        t = str(value).strip().replace("\\", "/")
        parts = [p for p in t.split("/") if p]
        if parts[-1]:
            tabular.add_row([setting, parts[-1]])
        else:
            tabular.add_row([setting, "None"])
    table_conf_settings = pl.Table(position="h")
    table_conf_settings.append(pl.UnsafeCommand("centering"))
    table_conf_settings.append(tabular)
    table_conf_settings.add_caption("Configurator Settings")
    report.append(table_conf_settings)

    # 3. Report details on instance and solver used
    report.append(pl.Subsection("Solver & Instance Set(s) Details"))
    cs = scenario_output.solver.get_configuration_space()
    report.append(
        f"The solver {scenario_output.solver} was configured using "
        f"{len(cs.values())} configurable (hyper)parameters. "
        f"The configuration space has {len(cs.conditions)} conditions. "
    )
    report.append("The following instance sets were used for the scenario:")
    with report.create(pl.Itemize()) as instance_set_latex_list:
        for instance_set in [
            scenario_output.instance_set_train
        ] + scenario_output.test_instance_sets:
            training_set_name = instance_set.name.replace("_", " ")  # Latex fix
            instance_set_latex_list.add_item(
                pl.UnsafeCommand(
                    f"textbf{{{training_set_name}}} ({instance_set.size} instances)"
                )
            )

    # Function to generate a results summary of default vs best on an instance set
    def instance_set_summary(instance_set_name: str) -> None:
        """Generate a results summary of default vs best on an instance set."""
        instance_set_results = scenario_output.instance_set_results[instance_set_name]
        report.append(
            f"The {scenario.sparkle_objectives[0]} value of the Default "
            f"Configuration on {instance_set_name} was "
        )
        report.append(
            pl.UnsafeCommand(
                f"textbf{{{round(instance_set_results.default_performance, MAX_DEC)}}}.\n"
            )
        )
        report.append(
            f"The {scenario.sparkle_objectives[0]} value of the Best "
            f"Configuration on {instance_set_name} was "
        )
        report.append(
            pl.UnsafeCommand(
                f"textbf{{{round(instance_set_results.best_performance, MAX_DEC)}}}.\n"
            )
        )
        report.append("In ")
        report.append(latex.AutoRef(f"fig:bestvsdefault{instance_set_name}{time_stamp}"))
        report.append(pl.utils.bold(" "))  # Force white space
        report.append("the results are plotted per instance.")
        # Create graph to compare best configuration vs default on the instance set

        df = pd.DataFrame(
            [
                instance_set_results.default_instance_performance,
                instance_set_results.best_instance_performance,
            ],
            index=["Default Configuration", "Best Configuration"],
            dtype=float,
        ).T
        plot = latex.comparison_plot(df, None)
        plot_path = (
            plot_dir / f"{scenario_output.best_configuration_key}_vs_"
            f"Default_{instance_set_name}.pdf"
        )
        plot.write_image(plot_path, width=500, height=500)
        with report.create(pl.Figure(position="h")) as figure:
            figure.add_image(
                str(plot_path.relative_to(report_dir)),
                width=pl.utils.NoEscape(r"0.6\textwidth"),
            )
            figure.add_caption(
                f"Best vs Default Performance on {instance_set_name} "
                f"({scenario.sparkle_objectives[0]})"
            )
            figure.append(
                pl.UnsafeCommand(
                    r"label{"
                    f"fig:bestvsdefault{instance_set_name}{time_stamp}"
                    r"}"
                )
            )
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
                    default_hit = (
                        instance_set_results.instance_status_default[instance] == status
                    )
                    best_hit = (
                        instance_set_results.instance_status_best[instance] == status
                    )
                    default_count += default_hit
                    best_count += best_hit
                    overlap_count += default_hit and best_hit
                if default_count or best_count:
                    tabular.add_row(status, default_count, best_count, overlap_count)
            table_status_values = pl.Table(position="h")
            table_status_values.append(pl.UnsafeCommand("centering"))
            table_status_values.append(tabular)
            table_status_values.add_caption(
                "Status count for the best and default configuration."
            )
            report.append(table_status_values)

    # 4. Report the results of the best configuration on the training set vs the default
    report.append(
        pl.Subsection(
            f"Comparison of Default and Best Configuration on Training Set "
            f"{scenario_output.instance_set_train.name}"
        )
    )
    instance_set_summary(scenario_output.instance_set_train.name)

    # 5. Report the actual config values
    report.append(pl.Subsubsection("Best Configuration Values"))
    if (
        scenario_output.best_configuration_key
        == PerformanceDataFrame.default_configuration
    ):
        report.append(
            "The configurator failed to find a better configuration than the "
            "default configuration on the training set in this scenario."
        )
    else:
        report.append(
            "The following parameter values "
            "were found to be the best on the training set:\n"
        )
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
        report.append(
            pl.Subsection(
                f"Comparison of Default and Best Configuration on Test Set "
                f"{test_set.name}"
            )
        )
        instance_set_summary(test_set.name)

    # 7. Report the parameter ablation scenario if present
    if scenario.ablation_scenario:
        report.append(pl.Subsection("Parameter importance via Ablation"))
        report.append("Ablation analysis ")
        report.append(pl.UnsafeCommand(r"cite{FawcettHoos16} "))
        test_set = scenario.ablation_scenario.test_set
        if not scenario.ablation_scenario.test_set:
            test_set = scenario.ablation_scenario.train_set
        report.append(
            f"is performed from the default configuration of {scenario.solver} to the "
            f"best found configuration ({scenario_output.best_configuration_key}) "
            "to see which parameter changes between them contribute most to the improved"
            " performance. The ablation path uses the training set "
            f"{scenario.ablation_scenario.train_set.name} and validation is performed "
            f"on the test set {test_set.name}. The set of parameters that differ in the "
            "two configurations will form the ablation path. Starting from the default "
            "configuration, the path is computed by performing a sequence of rounds. In"
            " a round, each available parameter is flipped in the configuration and is "
            "validated on its performance. The flipped parameter with the best "
            "performance in that round, is added to the configuration and the next round"
            " starts with the remaining parameters. This repeats until all parameters "
            "are flipped, which is the best found configuration. The analysis resulted "
            "in the ablation presented in "
        )
        report.append(latex.AutoRef("tab:ablationtable"))
        report.append(".")

        # Add ablation table
        tabular = pl.Tabular("r|l|r|r|r")
        data = scenario.ablation_scenario.read_ablation_table()
        for index, row in enumerate(data):
            tabular.add_row(*row)
            if index == 0:
                tabular.add_hline()
        table_ablation = pl.Table(position="h")
        table_ablation.append(pl.UnsafeCommand("centering"))
        table_ablation.append(tabular)
        table_ablation.add_caption("Ablation table")
        table_ablation.append(pl.UnsafeCommand(r"label{tab:ablationtable}"))
        report.append(table_ablation)


def generate_selection_section(
    report: pl.Document, scenario: SelectionScenario, scenario_output: SelectionOutput
) -> None:
    """Generate a section for a selection scenario."""
    report_dir = Path(report.default_filepath).parent
    time_stamp = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    plot_dir = report_dir / f"{scenario.name.replace(' ', '_')}_plots_{time_stamp}"
    plot_dir.mkdir(exist_ok=True)
    report.append(
        pl.Section(
            f"Selection: {scenario.selector.model_class.__name__} on "
            f"{' '.join([s[0] for s in scenario_output.training_instance_sets])}"
        )
    )
    report.append(
        f"In this scenario, a {scenario.selector.model_class.__name__} "
        f" ({scenario.selector.selector_class.__name__}) was trained on the "
        "performance and feature data using ASF-lib. The following solvers "
        f"were run with a cutoff time of {scenario.solver_cutoff} seconds:"
    )
    with report.create(pl.Itemize()) as solver_latex_list:
        for solver_name in scenario_output.solvers.keys():
            solver_name = solver_name.replace("_", " ")
            solver_latex_list.add_item(
                pl.UnsafeCommand(
                    f"textbf{{{solver_name}}} "
                    f"({len(scenario_output.solvers[solver_name])} configurations)"
                )
            )
    # Report training instance sets
    report.append("The following training instance sets were used:")
    with report.create(pl.Itemize()) as instance_set_latex_list:
        for training_set_name, set_size in scenario_output.training_instance_sets:
            training_set_name = training_set_name.replace("_", " ")  # Latex fix
            instance_set_latex_list.add_item(
                pl.UnsafeCommand(f"textbf{{{training_set_name}}} ({set_size} instances)")
            )
    # Report feature extractors
    report.append(
        "The following feature extractors were used with a extractor cutoff "
        f"time of {scenario.extractor_cutoff} seconds:"
    )
    with report.create(pl.Itemize()) as feature_extractor_latex_list:
        for feature_extractor_name in scenario.feature_extractors:
            extractor = resolve_object_name(
                feature_extractor_name,
                gv.file_storage_data_mapping[gv.extractor_nickname_list_path],
                gv.settings().DEFAULT_extractor_dir,
                class_name=Extractor,
            )
            feature_extractor_name = feature_extractor_name.replace("_", " ")  # Latex
            feature_extractor_latex_list.add_item(
                pl.UnsafeCommand(
                    f"textbf{{{feature_extractor_name}}} "
                    f"({extractor.output_dimension} features)"
                )
            )
    # Report Training results
    report.append(pl.Subsection("Training Results"))
    # 1. Report VBS and selector performance,  create ranking list of the solvers
    # TODO Add ref here to the training sets section?
    report.append(
        f"In this section, the {scenario.objective.name} results for the "
        "portfolio selector on solving the training instance set(s) listed "
        "is reported. "
    )
    report.append(
        f"The {scenario.objective.name} values for the Virtual Best Solver "
        "(VBS), i.e., the perfect portfolio selector is "
    )
    report.append(pl.utils.bold(f"{round(scenario_output.vbs_performance, MAX_DEC)}"))
    report.append(", the actual portfolio selector performance is ")
    report.append(
        pl.utils.bold(f"{round(scenario_output.actual_performance, MAX_DEC)}.\n")
    )

    report.append(
        f"Below, the solvers are ranked based on {scenario.objective.name} performance:"
    )
    with report.create(pl.Enumerate()) as ranking_list:
        for solver_name, conf_id, value in scenario_output.solver_performance_ranking:
            value = round(value, MAX_DEC)
            solver_name = solver_name.replace("_", " ")  # Latex fix
            conf_id = conf_id.replace("_", " ")  # Latex fix
            ranking_list.add_item(
                pl.UnsafeCommand(f"textbf{{{solver_name}}} ({conf_id}): {value}")
            )

    # 2. Marginal contribution ranking list VBS
    report.append(pl.Subsubsection("Marginal Contribution Ranking List"))
    report.append(
        "The following list shows the marginal contribution ranking list for the VBS:"
    )
    with report.create(pl.Enumerate()) as ranking_list:
        for (
            solver_name,
            conf_id,
            contribution,
            performance,
        ) in scenario_output.marginal_contribution_perfect:
            contribution, performance = (
                round(contribution, MAX_DEC),
                round(performance, MAX_DEC),
            )
            solver_name = solver_name.replace("_", " ")  # Latex fix
            conf_id = conf_id.replace("_", " ")  # Latex fix
            ranking_list.add_item(
                pl.UnsafeCommand(
                    f"textbf{{{solver_name}}} ({conf_id}): {contribution} ({performance})"
                )
            )

    # 3. Marginal contribution ranking list actual selector
    report.append(
        "The following list shows the marginal contribution ranking list for "
        "the actual portfolio selector:"
    )
    with report.create(pl.Enumerate()) as ranking_list:
        for (
            solver_name,
            conf_id,
            contribution,
            performance,
        ) in scenario_output.marginal_contribution_actual:
            contribution, performance = (
                round(contribution, MAX_DEC),
                round(performance, MAX_DEC),
            )
            solver_name = solver_name.replace("_", " ")  # Latex fix
            conf_id = conf_id.replace("_", " ")  # Latex fix
            ranking_list.add_item(
                pl.UnsafeCommand(
                    f"textbf{{{solver_name}}} ({conf_id}): {contribution} ({performance})"
                )
            )

    # 4. Create scatter plot analysis
    report.append(pl.Subsubsection("Scatter Plot Analysis"))
    report.append(latex.AutoRef(f"fig:sbsvsselector{time_stamp}"))
    report.append(pl.utils.bold(" "))  # Trick to force a white space
    report.append(
        "shows the empirical comparison between the portfolio "
        "selector and the single best solver (SBS). "
    )
    report.append(latex.AutoRef("fig:vbsvsselector"))
    report.append(pl.utils.bold(" "))  # Trick to force a white space
    report.append(
        "shows the empirical comparison between the actual portfolio selector "
        "and the virtual best solver (VBS)."
    )
    # Create figure on SBS versus the selector
    sbs_name, sbs_config, _ = scenario_output.solver_performance_ranking[0]
    # sbs_plot_name = f"{Path(sbs_name).name} ({sbs_config})"
    sbs_performance = scenario_output.sbs_performance
    selector_performance = scenario_output.actual_performance_data

    # Join the data together

    df = pd.DataFrame(
        [sbs_performance, selector_performance],
        index=[f"{Path(sbs_name).name} ({sbs_config})", "Selector"],
        dtype=float,
    ).T
    plot = latex.comparison_plot(df, "Single Best Solver vs Selector")
    plot_path = (
        plot_dir / f"{Path(sbs_name).name}_{sbs_config}_vs_"
        f"Selector_{scenario.selector.model_class.__name__}.pdf"
    )
    plot.write_image(plot_path, width=500, height=500)
    with report.create(pl.Figure()) as figure:
        figure.add_image(
            str(plot_path.relative_to(report_dir)),
            width=pl.utils.NoEscape(r"0.6\textwidth"),
        )
        figure.add_caption(
            "Empirical comparison between the Single Best Solver and the Selector"
        )
        label = r"label{fig:sbsvsselector" + str(time_stamp) + r"}"
        figure.append(pl.UnsafeCommand(f"{label}"))

    # Comparison between the actual portfolio selector in Sparkle and the VBS.
    vbs_performance = scenario_output.vbs_performance_data.tolist()
    df = pd.DataFrame(
        [vbs_performance, selector_performance],
        index=["Virtual Best Solver", "Selector"],
        dtype=float,
    ).T
    plot = latex.comparison_plot(df, "Virtual Best Solver vs Selector")
    plot_path = (
        plot_dir
        / f"Virtual_Best_Solver_vs_Selector_{scenario.selector.model_class.__name__}.pdf"
    )
    plot.write_image(plot_path, width=500, height=500)
    with report.create(pl.Figure()) as figure:
        figure.add_image(
            str(plot_path.relative_to(report_dir)),
            width=pl.utils.NoEscape(r"0.6\textwidth"),
        )
        figure.add_caption(
            "Empirical comparison between the Virtual Best Solver and the Selector"
        )
        figure.append(pl.UnsafeCommand(r"label{fig:vbsvsselector}"))

    if scenario_output.test_sets:
        report.append(pl.Subsection("Test Results"))
        report.append("The following results are reported on the test set(s):")
        with report.create(pl.Itemize()) as latex_list:
            for test_set_name, test_set_size in scenario_output.test_sets:
                result = round(
                    scenario_output.test_set_performance[test_set_name], MAX_DEC
                )
                latex_list.add_item(
                    pl.UnsafeCommand(
                        f"textbf{{{test_set_name}}} ({test_set_size} instances): {result}"
                    )
                )


def generate_parallel_portfolio_section(
    report: pl.Document, scenario: PerformanceDataFrame
) -> None:
    """Generate a section for a parallel portfolio scenario."""
    report_dir = Path(report.default_filepath).parent
    portfolio_name = scenario.csv_filepath.parent.name
    time_stamp = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    plot_dir = report_dir / f"{portfolio_name.replace(' ', '_')}_plots_{time_stamp}"
    plot_dir.mkdir()
    report.append(pl.Section(f"Parallel Portfolio {portfolio_name}"))
    report.append(
        "In this scenario, Sparkle runs the portfolio of Solvers on each instance in "
        "parallel with "
        f"{gv.settings().parallel_portfolio_num_seeds_per_solver} different "
        "seeds. The cutoff time for each solver run is set to "
        f"{gv.settings().solver_cutoff_time} seconds."
    )
    report.append(pl.Subsection("Solvers & Instance Sets"))
    report.append("The following Solvers were used in the portfolio:")
    # 1. Report on the Solvers and Instance Sets used for the portfolio
    with report.create(pl.Itemize()) as solver_latex_list:
        configs = scenario.configurations
        for solver in scenario.solvers:
            solver_name = solver.replace("_", " ")
            solver_latex_list.add_item(
                pl.UnsafeCommand(
                    f"textbf{{{solver_name}}} ({len(configs[solver])} configurations)"
                )
            )
    report.append("The following Instance Sets were used in the portfolio:")
    instance_sets = set(Path(instance).parent.name for instance in scenario.instances)
    instance_set_count = [
        len([i for i in scenario.instances if Path(i).parent.name == s])
        for s in instance_sets
    ]
    with report.create(pl.Itemize()) as instance_set_latex_list:
        for set_name, set_size in zip(instance_sets, instance_set_count):
            set_name = set_name.replace("_", " ")  # Latex fix
            instance_set_latex_list.add_item(
                pl.UnsafeCommand(f"textbf{{{set_name}}} ({set_size} instances)")
            )
    # 2. List which solver was the best on how many instances
    report.append(pl.Subsection("Portfolio Performance"))
    objective = scenario.objectives[0]
    report.append(
        f"The objective for the portfolio is {objective}. The "
        "following performance of the solvers was found over the instances: "
    )
    best_solver_count = {solver: 0 for solver in scenario.solvers}
    for instance in scenario.instances:
        ranking = scenario.get_solver_ranking(objective=objective, instances=[instance])
        best_solver_count[ranking[0][0]] += 1

    with report.create(pl.Itemize()) as latex_list:
        for solver, count in best_solver_count.items():
            solver_name = solver.replace("_", " ")
            latex_list.add_item(
                pl.UnsafeCommand(
                    f"textbf{{{solver_name}}} was the best solver on {count} instance(s)."
                )
            )
        # TODO Report how many instances remained unsolved

    # 3. Create table showing the performance of the portfolio vs and all solvers,
    # by showing the status count and number of times the solver was best
    solver_cancelled_count = {solver: 0 for solver in scenario.solvers}
    solver_timeout_count = {solver: 0 for solver in scenario.solvers}
    status_objective = [
        o for o in scenario.objective_names if o.lower().startswith("status")
    ][0]
    cancelled_status = [
        SolverStatus.UNKNOWN,
        SolverStatus.CRASHED,
        SolverStatus.WRONG,
        SolverStatus.ERROR,
        SolverStatus.KILLED,
    ]
    for solver in scenario.solvers:
        status = scenario.get_value(solver=solver, objective=status_objective)
        for status in scenario.get_value(solver=solver, objective=status_objective):
            status = SolverStatus(status)
            if status in cancelled_status:
                solver_cancelled_count[solver] += 1
            elif status == SolverStatus.TIMEOUT:
                solver_timeout_count[solver] += 1

    report.append(latex.AutoRef("tab:parallelportfoliotable"))
    report.append(pl.utils.bold(" "))
    report.append(" shows the performance of the portfolio on the test set(s).")
    tabular = pl.Tabular("r|rrrr")
    tabular.add_row(["Solver", objective, "# Timeouts", "# Cancelled", "# Best"])
    tabular.add_hline()
    solver_performance = {
        solver: round(performance, MAX_DEC)
        for solver, _, performance in scenario.get_solver_ranking(objective=objective)
    }
    for solver in scenario.solvers:
        tabular.add_row(
            solver,
            solver_performance[solver],
            solver_timeout_count[solver],
            solver_cancelled_count[solver],
            best_solver_count[solver],
        )
    tabular.add_hline()
    portfolio_performance = round(
        scenario.best_performance(objective=objective), MAX_DEC
    )
    tabular.add_row(
        portfolio_name,
        portfolio_performance,
        sum(solver_timeout_count.values()),
        sum(solver_cancelled_count.values()),
        sum(best_solver_count.values()),
    )
    table_portfolio = pl.Table(position="h")
    table_portfolio.append(pl.UnsafeCommand("centering"))
    table_portfolio.append(tabular)
    table_portfolio.add_caption("Parallel Portfolio Performance")
    table_portfolio.append(pl.UnsafeCommand(r"label{tab:parallelportfoliotable}"))
    report.append(table_portfolio)

    # 4. Create scatter plot analysis between the portfolio and the single best solver
    sbs_name = scenario.get_solver_ranking(objective=objective)[0][0]
    sbs_instance_performance = scenario.get_value(
        solver=sbs_name, objective=objective.name
    )
    sbs_name = Path(sbs_name).name
    report.append(latex.AutoRef("fig:portfoliovssbs"))
    report.append(pl.utils.bold(" "))
    report.append(
        " shows the emprical comparison between the portfolio and the single "
        f"best solver (SBS) {sbs_name}."
    )
    portfolio_instance_performance = scenario.best_instance_performance(
        objective=objective.name
    ).tolist()

    df = pd.DataFrame(
        [sbs_instance_performance, portfolio_instance_performance],
        index=[f"SBS ({sbs_name}) Performance", "Portfolio Performance"],
        dtype=float,
    ).T
    plot = latex.comparison_plot(df, None)
    plot_path = plot_dir / f"sbs_{sbs_name}_vs_parallel_portfolio.pdf"
    plot.write_image(plot_path, width=500, height=500)
    with report.create(pl.Figure(position="h")) as figure:
        figure.add_image(
            str(plot_path.relative_to(report_dir)),
            width=pl.utils.NoEscape(r"0.6\textwidth"),
        )
        figure.add_caption(f"Portfolio vs SBS Performance ({objective})")
        figure.append(pl.UnsafeCommand(r"label{fig:portfoliovssbs}"))


def append_dataframe_longtable(
    report: pl.Document,
    df: pd.DataFrame,
    caption: str,
    label: str,
    max_cols: int = MAX_COLS_PER_TABLE,
    wide_threshold: int = WIDE_TABLE_THRESHOLD,
    num_keys: int = NUM_KEYS_PDF,
) -> None:
    """Appends a pandas DataFrame to a PyLaTeX document as one or more LaTeX longtables.

    Args:
        report: The PyLaTeX document to which the table(s) will be appended.
        df: The DataFrame to be rendered as LaTeX longtable(s).
        caption: The caption for the table(s).
        label: The LaTeX label for referencing the table(s).
        max_cols: Maximum number of columns per table chunk.
                  Defaults to MAX_COLS_PER_TABLE.
        wide_threshold: Number of columns above which the table is rotated
                        to landscape. Defaults to WIDE_TABLE_THRESHOLD.
        num_keys: Number of key columns to include in each table chunk.
                  Defaults to NUM_KEYS_PDF.

    Returns:
        None
    """
    import math
    from typing import Union

    def latex_escape_text(s: str) -> str:
        """Escape special LaTeX characters in a string."""
        # escape text, but insert our own LaTeX macro around it
        return (
            s.replace("\\", r"\textbackslash{}")
            .replace("&", r"\&")
            .replace("%", r"\%")
            .replace("$", r"\$")
            .replace("#", r"\#")
            .replace("_", r"\_")
            .replace("{", r"\{")
            .replace("}", r"\}")
            .replace("~", r"\textasciitilde{}")
            .replace("^", r"\textasciicircum{}")
        )

    def last_path_segment(text: str) -> str:
        """Keep only the last non-empty path-like segment. Handles both back and forwardslashes. Removes any leading/trailing slashes."""
        t = str(text).strip().replace("\\", "/")
        parts = [p for p in t.split("/") if p]  # ignore empty segments
        return parts[-1] if parts else ""

    def wrap_fixed_shortstack(cell: str, width: int = MAX_CELL_LEN) -> str:
        """Wrap long text to a fixed width for LaTeX tables."""
        string_cell = last_path_segment(cell)
        if len(string_cell) <= width:
            return latex_escape_text(string_cell)
        chunks = [
            latex_escape_text(string_cell[index : index + width])
            for index in range(0, len(string_cell), width)
        ]
        # left-aligned shortstack: forces line breaks and grows row height
        return r"\shortstack[l]{" + r"\\ ".join(chunks) + "}"

    def wrap_header_labels(
        df: pd.DataFrame, width_per_cell: int = MAX_CELL_LEN
    ) -> pd.DataFrame:
        """Wrap long header labels to a fixed width for LaTeX tables."""
        df_copy = df.copy()
        if isinstance(df_copy.columns, pd.MultiIndex):
            new_cols = []
            for tup in df_copy.columns:
                new_cols.append(
                    tuple(
                        wrap_fixed_shortstack(last_path_segment(index), width_per_cell)
                        if isinstance(index, str)
                        else index
                        for index in tup
                    )
                )
            names = [
                (
                    wrap_fixed_shortstack(last_path_segment(name), width_per_cell)
                    if isinstance(name, str)
                    else name
                )
                for name in (df_copy.columns.names or [])
            ]
            df_copy.columns = pd.MultiIndex.from_tuples(new_cols, names=names)
        else:
            df_copy.columns = [
                wrap_fixed_shortstack(last_path_segment(column), width_per_cell)
                if isinstance(column, str)
                else column
                for column in df_copy.columns
            ]
        return df_copy

    def format_cell(cell: Union[int, float, str]) -> str:
        """Format a cell for printing in a LaTeX table."""
        try:
            float_cell = float(cell)
        except (TypeError, ValueError):
            return wrap_fixed_shortstack(last_path_segment(str(cell)), MAX_CELL_LEN)

        if not math.isfinite(float_cell):
            return "NaN"

        if float_cell.is_integer():
            return str(int(float_cell))
        # round to MAX_DEC, then strip trailing zeros
        s = f"{round(float_cell, MAX_DEC):.{MAX_DEC}f}".rstrip("0").rstrip(".")
        return s

    df_copy = df.copy()

    # Inorder to be able to show the key columns, we need to reset the index
    if not isinstance(df_copy.index, pd.RangeIndex) and df_copy.index.name in (
        None,
        "index",
        "",
    ):
        df_copy = df_copy.reset_index()

    # Remove the Seed column from the performance dataframe since it is not
    # very informative and clutters the table
    if isinstance(df, PerformanceDataFrame):
        mask = df_copy.columns.get_level_values("Meta") == "Seed"
        df_copy = df_copy.loc[:, ~mask]

    # For performance dataframe, we want to show values of objectives with their corresponding instance and run.
    # Since objective, instance and run are indexes in the performance dataframe,
    # they will be part of the index and we need to reset the index to get them
    # as columns.
    # We'll name them as key columns, since they are the key to identify the value of the objective
    # for a given instance and run.
    # (Respectively FeatureGroup, FeatureName, Extractor in feature dataframe)
    keys = df_copy.iloc[:, :num_keys]  # Key columns

    # Split the dataframe into chunks of max_cols per page
    number_column_chunks = max((df_copy.shape[1] - 1) // max_cols + 1, 1)
    for i in range(number_column_chunks):
        report.append(NewPage())
        full_part = None
        start_col = i * max_cols
        end_col = (i + 1) * max_cols

        # Select the value columns for this chunk
        values = df_copy.iloc[
            :,
            start_col + num_keys : end_col + num_keys,
        ]

        # Concatenate the key and value columns
        full_part = pd.concat([keys, values], axis=1)

        # If there are no value columns left, we are done
        if (full_part.shape[1]) <= num_keys:
            break

        full_part_wrapped = wrap_header_labels(full_part, MAX_CELL_LEN)

        # tell pandas how to print numbers
        formatters = {col: format_cell for col in full_part_wrapped.columns}

        tex = full_part_wrapped.to_latex(
            longtable=True,
            index=False,
            escape=False,  # We want to split the long words, not escape them
            caption=caption + (f" (part {i + 1})" if number_column_chunks > 1 else ""),
            label=label + f"-p{i + 1}" if number_column_chunks > 1 else label,
            float_format=None,
            multicolumn=True,
            multicolumn_format="c",
            multirow=False,
            column_format="c" * full_part_wrapped.shape[1],
            formatters=formatters,
        )

        # centre the whole table horizontally
        centred_tex = "\\begin{center}\n" + tex + "\\end{center}\n"

        # rotate if still too wide
        if full_part_wrapped.shape[1] > wide_threshold:
            report.append(NoEscape(r"\begin{landscape}"))
            report.append(NoEscape(centred_tex))
            report.append(NoEscape(r"\end{landscape}"))
        else:
            report.append(NoEscape(centred_tex))


def generate_appendix(
    report: pl.Document,
    performance_data: PerformanceDataFrame,
    feature_data: FeatureDataFrame,
) -> None:
    """Appendix.

    Args:
        report: The LaTeX document object to which the appendix will be added.
        performance_data: The performance data to be included in the appendix.
        feature_data: The feature data to be included in the appendix.

    Returns:
        None
    """
    # preamble
    for pkg in ("longtable", "pdflscape", "caption", "booktabs", "placeins"):
        p = pl.Package(pkg)
        if p not in report.packages:
            report.packages.append(p)

    report.append(pl.NewPage())
    report.append(pl.NoEscape(r"\clearpage"))
    report.append(pl.NoEscape(r"\FloatBarrier"))
    report.append(pl.UnsafeCommand("appendix"))
    report.append(pl.Section("Performance DataFrame"))

    append_dataframe_longtable(
        report,
        performance_data,
        caption="Performance DataFrame",
        label="tab:perf_data",
        max_cols=MAX_COLS_PER_TABLE,
        wide_threshold=WIDE_TABLE_THRESHOLD,
        num_keys=NUM_KEYS_PDF,
    )

    report.append(pl.Section("Feature DataFrame"))
    append_dataframe_longtable(
        report,
        feature_data,
        caption="Feature DataFrame",
        label="tab:feature_data",
        max_cols=MAX_COLS_PER_TABLE,
        wide_threshold=WIDE_TABLE_THRESHOLD,
        num_keys=NUM_KEYS_FDF,
    )

    report.append(pl.NoEscape(r"\FloatBarrier"))


def main(argv: list[str]) -> None:
    """Generate a report for executed experiments in the platform."""
    # Log command call
    sl.log_command(sys.argv, gv.settings().random_state)

    # Define command line arguments
    parser = parser_function()

    # Process command line arguments
    args = parser.parse_args(argv)

    performance_data = PerformanceDataFrame(gv.settings().DEFAULT_performance_data_path)
    feature_data = FeatureDataFrame(gv.settings().DEFAULT_feature_data_path)

    # Fetch all known scenarios
    configuration_scenarios = gv.configuration_scenarios(refresh=True)
    selection_scenarios = gv.selection_scenarios(refresh=True)
    parallel_portfolio_scenarios = gv.parallel_portfolio_scenarios()

    # Filter scenarios based on args
    if args.solvers:
        solvers = [
            resolve_object_name(
                s, gv.solver_nickname_mapping, gv.settings().DEFAULT_solver_dir, Solver
            )
            for s in args.solvers
        ]
        configuration_scenarios = [
            s
            for s in configuration_scenarios
            if s.solver.directory in [s.directory for s in solvers]
        ]
        selection_scenarios = [
            s
            for s in selection_scenarios
            if set(s.solvers).intersection([str(s.directory) for s in solvers])
        ]
        parallel_portfolio_scenarios = [
            s
            for s in parallel_portfolio_scenarios
            if set(s.solvers).intersection([str(s.directory) for s in solvers])
        ]
    if args.instance_sets:
        instance_sets = [
            resolve_object_name(
                s,
                gv.instance_set_nickname_mapping,
                gv.settings().DEFAULT_instance_dir,
                Instance_Set,
            )
            for s in args.instance_sets
        ]
        configuration_scenarios = [
            s
            for s in configuration_scenarios
            if s.instance_set.directory in [s.directory for s in instance_sets]
        ]
        selection_scenarios = [
            s
            for s in selection_scenarios
            if set(s.instance_sets).intersection([str(s.name) for s in instance_sets])
        ]
        parallel_portfolio_scenarios = [
            s
            for s in parallel_portfolio_scenarios
            if set(s.instance_sets).intersection([str(s.name) for s in instance_sets])
        ]

    processed_configuration_scenarios = []
    processed_selection_scenarios = []
    possible_test_sets = [
        Instance_Set(p) for p in gv.settings().DEFAULT_instance_dir.iterdir()
    ]
    for configuration_scenario in configuration_scenarios:
        processed_configuration_scenarios.append(
            (
                ConfigurationOutput(
                    configuration_scenario, performance_data, possible_test_sets
                ),
                configuration_scenario,
            )
        )
    for selection_scenario in selection_scenarios:
        processed_selection_scenarios.append(
            (SelectionOutput(selection_scenario), selection_scenario)
        )

    raw_output = gv.settings().DEFAULT_output_analysis / "JSON"
    if raw_output.exists():  # Clean
        shutil.rmtree(raw_output)
    raw_output.mkdir()

    # Write JSON
    output_json = {}
    for output, configuration_scenario in processed_configuration_scenarios:
        output_json[configuration_scenario.name] = output.serialise()
    for output, selection_scenario in processed_selection_scenarios:
        output_json[selection_scenario.name] = output.serialise()
    # TODO: We do not have an output object for parallel portfolios

    raw_output_json = raw_output / "output.json"
    with raw_output_json.open("w") as f:
        json.dump(output_json, f, indent=4)

    print(f"Machine readable output written to: {raw_output_json}")

    if args.only_json:  # Done
        sys.exit(0)

    # TODO: Group scenarios based on:
    # - Configuration / Selection / Parallel Portfolio
    # - Training Instance Set / Testing Instance Set
    # - Configurators can be merged as long as we can match their budgets clearly
    report_directory = gv.settings().DEFAULT_output_analysis / "report"
    if report_directory.exists():  # Clean it
        shutil.rmtree(report_directory)
    report_directory.mkdir()
    target_path = report_directory / "report"
    report = pl.document.Document(
        default_filepath=str(target_path), document_options=["british"]
    )
    bibpath = gv.settings().bibliography_path
    newbibpath = report_directory / "report.bib"
    shutil.copy(bibpath, newbibpath)
    # BUGFIX for unknown package load in PyLatex
    p = pl.package.Package("lastpage")
    if p in report.packages:
        report.packages.remove(p)
    report.packages.append(
        pl.package.Package(
            "geometry",
            options=[
                "verbose",
                "tmargin=3.5cm",
                "bmargin=3.5cm",
                "lmargin=3cm",
                "rmargin=3cm",
            ],
        )
    )
    # Unsafe command for \emph{Sparkle}
    report.preamble.extend(
        [
            pl.UnsafeCommand("title", r"\emph{Sparkle} Algorithm Portfolio report"),
            pl.UnsafeCommand(
                "author",
                r"Generated by \emph{Sparkle} "
                f"(version: {__sparkle_version__})",
            ),
        ]
    )
    report.append(pl.Command("maketitle"))
    report.append(pl.Section("Introduction"))
    # TODO: A quick overview to the introduction on whats considered in the report
    # regarding Solvers, Instance Sets and Feature Extractors
    report.append(
        pl.UnsafeCommand(
            r"emph{Sparkle}~\cite{Hoos15} is a multi-agent problem-solving platform based on"
            r" Programming by Optimisation (PbO)~\cite{Hoos12}, and would provide a number "
            "of effective algorithm optimisation techniques (such as automated algorithm "
            "configuration, portfolio-based algorithm selection, etc.) to accelerate the "
            "existing solvers."
        )
    )

    for scenario_output, scenario in processed_configuration_scenarios:
        generate_configuration_section(report, scenario, scenario_output)

    for scenario_output, scenario in processed_selection_scenarios:
        generate_selection_section(report, scenario, scenario_output)

    for parallel_dataframe in parallel_portfolio_scenarios:
        generate_parallel_portfolio_section(report, parallel_dataframe)

    # Check if user wants to add appendix and
    settings = gv.settings(args)
    if settings.appendices:
        generate_appendix(report, performance_data, feature_data)

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
    subprocess.run(
        ["bibtex", newbibpath.with_suffix("")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    report.generate_pdf(target_path, clean=False, clean_tex=False, compiler="pdflatex")
    report.generate_pdf(target_path, clean=False, clean_tex=False, compiler="pdflatex")
    print(f"Report generated at {target_path}.pdf")
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
