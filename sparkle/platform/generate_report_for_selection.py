#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for selection report generation."""
import sys
import numpy as np
from pathlib import Path
import ast
from collections import Counter

import plotly.express as px
import pandas as pd
import plotly.io as pio

from sparkle.platform import latex as stex
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.types.objective import SparkleObjective

pio.kaleido.scope.mathjax = None  # Bug fix for kaleido


def get_num_instance_sets(instance_list: list[str]) -> int:
    """Get the number of instance sets.

    Args:
        instance_list: List of instances to use

    Returns:
        The number of instance sets as LaTeX str.
    """
    return len(set([Path(instance_path).parent.name
                    for instance_path in instance_list]))


def get_instance_set_count_list(instance_list: list[str] = None) -> str:
    """Get the instance sets for use in a LaTeX document.

    Returns:
        The list of instance sets as LaTeX str.
    """
    instance_list = [Path(instance_path).parent.name
                     for instance_path in instance_list]
    count = Counter(instance_list)
    return "".join(f"\\item \\textbf{ {inst_key} }, consisting of {count[inst_key]} "
                   "instances\n" for inst_key in count)


def solver_ranked_latex_list(solver_performance_ranking: list[tuple[str, float]],
                             objective: SparkleObjective = None) -> str:
    """Convert a list of the solvers ranked by performance to LaTeX.

    Returns:
        The list of solvers ranked as LaTeX str.
    """
    objective_str = f"{objective.metric} :" if objective is not None else ""
    return "".join(f"\\item \\textbf{{{row[0]}}},{objective_str} {row[1]}\n"
                   for row in solver_performance_ranking)


def get_portfolio_selector_performance(selection_scenario: Path) -> PerformanceDataFrame:
    """Creates a dictionary with the portfolio selector performance on each instance.

    Returns:
        A dict that maps instance name str to performance.
    """
    portfolio_selector_performance_path = selection_scenario / "performance.csv"
    if not portfolio_selector_performance_path.exists():
        print(f"ERROR: {portfolio_selector_performance_path} does not exist.")
        sys.exit(-1)
    return PerformanceDataFrame(portfolio_selector_performance_path)


def get_figure_portfolio_selector_vs_sbs(
        output_dir: Path,
        objective: SparkleObjective,
        train_data: PerformanceDataFrame,
        portfolio_selector_performance: PerformanceDataFrame,
        sbs_solver: str,
        penalty: int) -> str:
    """Create a LaTeX plot comparing the selector and the SBS.

    The plot compares the performance on each instance of the portfolio selector created
    by Sparkle and the SBS (single best solver).

    Returns:
        LaTeX str to include the comparison plot in a LaTeX report.
    """
    # We create a point of x,y form (SBS performance, portfolio performance)
    selector = portfolio_selector_performance.solvers[0]
    points = [[train_data.get_value(sbs_solver, instance),
               portfolio_selector_performance.get_value(selector, instance)]
              for instance in portfolio_selector_performance.instances]

    figure_filename = "figure_portfolio_selector_sparkle_vs_sbs"
    sbs_solver_name = Path(sbs_solver).name

    generate_comparison_plot(points,
                             figure_filename,
                             xlabel=f"SBS ({sbs_solver_name}) [{objective.metric}]",
                             ylabel=f"Sparkle Selector [{objective.metric}]",
                             limit="magnitude",
                             limit_min=0.25,
                             limit_max=0.25,
                             penalty_time=penalty,
                             replace_zeros=True,
                             output_dir=output_dir)
    return f"\\includegraphics[width=0.6\\textwidth]{{{figure_filename}}}"


def get_figure_portfolio_selector_sparkle_vs_vbs(
        output_dir: Path,
        objective: SparkleObjective,
        train_data: PerformanceDataFrame,
        actual_portfolio_selector_penalty: PerformanceDataFrame,
        penalty: int) -> str:
    """Create a LaTeX plot comparing the selector and the VBS.

    The plot compares the performance on each instance of the portfolio selector created
    by Sparkle and the VBS (virtual best solver).

    Returns:
        LaTeX str to include the comparison plot in a LaTeX report.
    """
    vbs_performance = train_data.get_best_performance()
    instances = actual_portfolio_selector_penalty.instances
    solver = actual_portfolio_selector_penalty.solvers[0]
    points = [(vbs_performance[instance],
               actual_portfolio_selector_penalty.get_value(solver, instance))
              for instance in instances]

    figure_filename = "figure_portfolio_selector_sparkle_vs_vbs"

    generate_comparison_plot(points,
                             figure_filename,
                             xlabel=f"VBS [{objective.metric}]",
                             ylabel=f"Sparkle Selector [{objective.name}]",
                             limit="magnitude",
                             limit_min=0.25,
                             limit_max=0.25,
                             penalty_time=penalty,
                             replace_zeros=True,
                             output_dir=output_dir)

    return f"\\includegraphics[width=0.6\\textwidth]{{{figure_filename}}}"


def selection_report_variables(
        target_dir: Path,
        bibliograpghy_path: Path,
        extractor_path: Path,
        selection_scenario: Path,
        train_data: PerformanceDataFrame,
        feature_data: FeatureDataFrame,
        extractor_cutoff: int,
        cutoff: int,
        penalty: int,
        test_case_data: PerformanceDataFrame = None) -> dict[str, str]:
    """Returns: a dict matching variables in the LaTeX template with their values.

    Args:
        target_dir: Output path
        bibliography_path: Path to the bib file
        test_case_directory: Path to the test case directory.

    Returns:
        A dict matching str variables in the LaTeX template with their value str.
    """
    objective = SparkleObjective(train_data.objective_names[0])
    actual_performance_data = get_portfolio_selector_performance(selection_scenario)
    solver_performance_ranking = train_data.get_solver_ranking()
    single_best_solver = solver_performance_ranking[0][0]
    latex_dict = {"bibliographypath": bibliograpghy_path.absolute(),
                  "numSolvers": train_data.num_solvers,
                  "solverList": stex.get_directory_list(train_data.solvers)}
    latex_dict["numFeatureExtractors"] = len(
        [p for p in extractor_path.iterdir() if p.is_dir()])
    latex_dict["featureExtractorList"] = stex.get_directory_list(extractor_path)
    latex_dict["numInstanceClasses"] = get_num_instance_sets(train_data.instances)
    latex_dict["instanceClassList"] = get_instance_set_count_list(train_data.instances)
    latex_dict["featureComputationCutoffTime"] = extractor_cutoff
    latex_dict["performanceComputationCutoffTime"] = cutoff
    rank_list_perfect = train_data.marginal_contribution(sort=True)
    mg_actual_path = selection_scenario / "marginal_contribution_actual.txt"
    rank_list_actual = ast.literal_eval(mg_actual_path.open().read())
    latex_dict["solverPerfectRankingList"] = solver_ranked_latex_list(rank_list_perfect)
    latex_dict["solverActualRankingList"] = solver_ranked_latex_list(rank_list_actual)
    latex_dict["PARRankingList"] = solver_ranked_latex_list(solver_performance_ranking,
                                                            objective)
    latex_dict["VBSPAR"] = train_data.get_best_performance().mean()
    latex_dict["actualPAR"] = actual_performance_data.mean()
    latex_dict["metric"] = objective.metric
    latex_dict["figure-portfolio-selector-sparkle-vs-sbs"] =\
        get_figure_portfolio_selector_vs_sbs(
            target_dir, objective, train_data,
            actual_performance_data, single_best_solver, penalty)
    latex_dict["figure-portfolio-selector-sparkle-vs-vbs"] =\
        get_figure_portfolio_selector_sparkle_vs_vbs(target_dir, objective, train_data,
                                                     actual_performance_data, penalty)
    latex_dict["testBool"] = r"\testfalse"

    # Train and test
    if test_case_data is not None:
        latex_dict["testInstanceClass"] =\
            f"\\textbf{ {test_case_data.csv_filepath.parent.name} }"
        latex_dict["numInstanceInTestInstanceClass"] =\
            test_case_data.num_instances
        latex_dict["testActualPAR"] = test_case_data.mean()
        latex_dict["testBool"] = r"\testtrue"

    return latex_dict


def generate_comparison_plot(points: list,
                             figure_filename: str,
                             xlabel: str = "default",
                             ylabel: str = "optimised",
                             title: str = "",
                             scale: str = "log",
                             limit: str = "magnitude",
                             limit_min: float = 0.2,
                             limit_max: float = 0.2,
                             penalty_time: float = None,
                             replace_zeros: bool = True,
                             magnitude_lines: int = 2147483647,
                             output_dir: Path = None) -> None:
    """Create comparison plots between two different solvers/portfolios.

    Args:
        points: list of points which represents with the performance results of
        (solverA, solverB)
        figure_filename: filename without filetype (e.g., .jpg) to save the figure to.
        xlabel: Name of solverA (default: default)
        ylabel: Name of solverB (default: optimised)
        title: Display title in the image (default: None)
        scale: [linear, log] (default: linear)
        limit: The method to compute the axis limits in the figure
            [absolute, relative, magnitude] (default: relative)
            absolute: Uses the limit_min/max values as absolute values
            relative: Decreases/increases relatively to the min/max values found in the
            points. E.g., min/limit_min and max*limit_max
            magnitude: Increases the order of magnitude(10) of the min/max values in the
            points. E.g., 10**floor(log10(min)-limit_min)
            and 10**ceil(log10(max)+limit_max)
        limit_min: Value used to compute the minimum limit
        limit_max: Value used to compute the maximum limit
        penalty_time: Acts as the maximum value the figure takes in consideration for
        computing the figure limits. This is only relevant for runtime objectives
        replace_zeros: Replaces zeros valued performances to a very small value to make
        plotting on log-scale possible
        magnitude_lines: Draw magnitude lines (only supported for log scale)
        output_dir: directory path to place the figure and its intermediate files in
            (default: current working directory)
    """
    output_dir = Path() if output_dir is None else Path(output_dir)

    points = np.array(points)
    if replace_zeros:
        zero_runtime = 0.000001  # Microsecond
        if np.any(points <= 0):
            print("WARNING: Zero or negative valued performance values detected. Setting"
                  f" these values to {zero_runtime}.")
        points[points <= 0] = zero_runtime

    # process labels
    # LaTeX safe formatting
    xlabel = xlabel.replace("_", "\\_").replace("$", "\\$").replace("^", "\\^")
    ylabel = ylabel.replace("_", "\\_").replace("$", "\\$").replace("^", "\\^")

    # process range values
    min_point_value = np.min(points)
    max_point_value = np.max(points)
    if penalty_time is not None:
        if (penalty_time < max_point_value):
            print("ERROR: Penalty time too small for the given performance data.")
            sys.exit(-1)
        max_point_value = penalty_time

    if limit == "absolute":
        min_value = limit_min
        max_value = limit_max
    elif limit == "relative":
        min_value = (min_point_value * (1 / limit_min) if min_point_value > 0
                     else min_point_value * limit_min)
        max_value = (max_point_value * limit_max if max_point_value > 0
                     else max_point_value * (1 / limit_max))
    elif limit == "magnitude":
        min_value = 10 ** (np.floor(np.log10(min_point_value)) - limit_min)
        max_value = 10 ** (np.ceil(np.log10(max_point_value)) + limit_max)

    if scale == "log" and np.min(points) <= 0:
        raise Exception("Cannot plot negative and zero values on a log scales")

    output_plot = output_dir / f"{figure_filename}.pdf"

    df = pd.DataFrame(points, columns=[xlabel, ylabel])
    log_scale = scale == "log"
    fig = px.scatter(data_frame=df, x=xlabel, y=ylabel,
                     range_x=[min_value, max_value], range_y=[min_value, max_value],
                     title=title, log_x=log_scale, log_y=log_scale,
                     width=500, height=500)
    # Add in the seperation line
    fig.add_shape(type="line", x0=0, y0=0, x1=max_value, y1=max_value,
                  line=dict(color="lightgrey", width=1))
    fig.update_traces(marker=dict(color="RoyalBlue", symbol="x"))
    fig.update_layout(
        plot_bgcolor="white"
    )
    fig.update_xaxes(
        type="linear" if not log_scale else "log",
        mirror=True,
        tickmode="linear",
        ticks="outside",
        tick0=0,
        dtick=100 if not log_scale else 1,
        showline=True,
        linecolor="black",
        gridcolor="lightgrey"
    )
    fig.update_yaxes(
        type="linear" if not log_scale else "log",
        mirror=True,
        tickmode="linear",
        ticks="outside",
        tick0=0,
        dtick=100 if not log_scale else 1,
        showline=True,
        linecolor="black",
        gridcolor="lightgrey"
    )
    fig.write_image(output_plot)


def generate_report_selection(target_path: Path,
                              latex_dir: Path,
                              latex_template: Path,
                              bibliography_path: Path,
                              extractor_path: Path,
                              selection_scenario: Path,
                              feature_data: FeatureDataFrame,
                              train_data: PerformanceDataFrame,
                              extractor_cutoff: int,
                              cutoff: int,
                              penalty: int,
                              test_case_data: PerformanceDataFrame = None) -> None:
    """Generate a report for algorithm selection.

    Args:
        target_path: Path where the outputfiles will be placed.
        latex_dir: The latex dir
        latex_template: The template for the report
        bibliography_path: Path to the bib file.
        extractor_path: Path to the extractor used
        selection_scenario: Path to the selector scenario
        feature_data: Feature data created by extractor
        train_data: The performance input data for the selector
        extractor_cutoff: The maximum time for the selector to run
        cutoff: The cutoff per solver
        penalty: The penalty for solvers TIMEOUT
        test_case_data: Path to the test case directory. Defaults to None.
    """
    # Include results on the test set if a test case directory is given
    latex_report_filename = Path("Sparkle_Report")
    if test_case_data is not None:
        latex_report_filename = Path("Sparkle_Report_for_Test")

    target_path.mkdir(parents=True, exist_ok=True)
    dict_variable_to_value = selection_report_variables(target_path,
                                                        bibliography_path,
                                                        extractor_path,
                                                        selection_scenario,
                                                        train_data,
                                                        feature_data,
                                                        extractor_cutoff,
                                                        cutoff,
                                                        penalty,
                                                        test_case_data)
    stex.generate_report(latex_dir,
                         latex_template,
                         target_path,
                         latex_report_filename,
                         dict_variable_to_value)
