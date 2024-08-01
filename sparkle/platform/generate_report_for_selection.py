#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for selection report generation."""
import sys
import numpy as np
from pathlib import Path
from collections import Counter

import plotly.express as px
import pandas as pd
import plotly.io as pio

from sparkle.platform import latex as stex
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.CLI.support import compute_marginal_contribution_help as scmch
from sparkle.types.objective import PerformanceMeasure, SparkleObjective

pio.kaleido.scope.mathjax = None  # Bug fix for kaleido


def get_num_instance_sets(instance_list: list[str]) -> str:
    """Get the number of instance sets.

    Args:
        instance_list: List of instances to use

    Returns:
        The number of instance sets as LaTeX str.
    """
    return str(len(set([Path(instance_path).parent.name
                        for instance_path in instance_list])))


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


def solver_rank_list_latex(rank_list: list[tuple[str, float]]) -> str:
    """Convert solvers ranked by marginal contribution to latex.

    Returns:
        Solvers in the VBS (virtual best solver) ranked by marginal contribution as LaTeX
        str.
    """
    return "".join(f"\\item \\textbf{ {Path(solver).name} }, marginal contribution: "
                   f"{value}\n" for solver, value, _ in rank_list)


def get_par_ranking_list(performance_data: PerformanceDataFrame,
                         objective: SparkleObjective) -> str:
    """Get a list of the solvers ranked by PAR (Penalised Average Runtime).

    Returns:
        The list of solvers ranked by PAR as LaTeX str.
    """
    solver_penalty_ranking = performance_data.get_solver_penalty_time_ranking()
    return "".join(f"\\item \\textbf{{{solver}}}, {objective.metric}: {solver_penalty}\n"
                   for solver, solver_penalty in solver_penalty_ranking)


def get_par(performance: dict | PerformanceDataFrame) -> str:
    """PAR (Penalised Average Runtime) of the Sparkle portfolio selector.

    Returns:
        The PAR (Penalised Average Runtime) of the Sparkle portfolio selector over a set
        of instances.
    """
    if isinstance(performance, dict):
        mean_performance = sum(performance.values()) / len(performance)
    else:
        # Selecting the first solver because in this case its the Selector (Only solver)
        solver = performance.solvers[0]
        performance.dataframe[solver].sum() / performance.num_instances
    return str(mean_performance)


def get_dict_sbs_penalty_time_on_each_instance(
        performance_data: PerformanceDataFrame) -> dict[str, int]:
    """Returns a dictionary with the penalised performance of the Single Best Solver.

    Returns:
        A dict that maps instance name str to their penalised performance int.
    """
    solver_penalty_time_ranking_list =\
        performance_data.get_solver_penalty_time_ranking()
    sbs_solver = solver_penalty_time_ranking_list[0][0]
    return {instance: performance_data.get_value(sbs_solver, instance)
            for instance in performance_data.instances}


def get_actual_portfolio_selector_performance_per_instance(
        performance_data: PerformanceDataFrame,
        selection_scenario: Path,
        feature_data: FeatureDataFrame,
        capvalue: int,
        penalised_time: int) -> dict[str, int]:
    """Creates a dictionary with the portfolio selector performance on each instance.

    Returns:
        A dict that maps instance name str to their penalised performance int.
    """
    objective = SparkleObjective(performance_data.objective_names[0])
    minimise =\
        objective.PerformanceMeasure != PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION

    actual_portfolio_selector_path = selection_scenario / "portfolio_selector"
    actual_selector_penalty = {}
    for instance in performance_data.instances:
        used_time_for_this_instance, flag_successfully_solving = \
            scmch.compute_actual_performance_for_instance(
                actual_portfolio_selector_path, instance, feature_data,
                performance_data, minimise, objective.PerformanceMeasure, capvalue)

        if flag_successfully_solving:
            actual_selector_penalty[instance] = used_time_for_this_instance
        else:
            actual_selector_penalty[instance] = penalised_time

    return actual_selector_penalty


def get_figure_portfolio_selector_sparkle_vs_sbs(output_dir: Path,
                                                 objective: SparkleObjective,
                                                 train_data: PerformanceDataFrame,
                                                 actual_portfolio_selector_penalty: dict,
                                                 penalty: int) -> str:
    """Create a LaTeX plot comparing the selector and the SBS.

    The plot compares the performance on each instance of the portfolio selector created
    by Sparkle and the SBS (single best solver).

    Returns:
        LaTeX str to include the comparison plot in a LaTeX report.
    """
    sbs_penalty_time = get_dict_sbs_penalty_time_on_each_instance(train_data)

    instances = sbs_penalty_time.keys() & actual_portfolio_selector_penalty.keys()
    if (len(sbs_penalty_time) != len(instances)):
        print("ERROR: Number of penalty times for the single best solver does not match "
              "the number of instances")
        sys.exit(-1)
    points = [[sbs_penalty_time[instance], actual_portfolio_selector_penalty[instance]]
              for instance in instances]

    figure_filename = "figure_portfolio_selector_sparkle_vs_sbs"

    solver_penalty_time_ranking_list =\
        train_data.get_solver_penalty_time_ranking()
    sbs_solver = Path(solver_penalty_time_ranking_list[0][0]).name

    generate_comparison_plot(points,
                             figure_filename,
                             xlabel=f"SBS ({sbs_solver}) [{objective.metric}]",
                             ylabel=f"Sparkle Selector [{objective.metric}]",
                             limit="magnitude",
                             limit_min=0.25,
                             limit_max=0.25,
                             penalty_time=penalty,
                             replace_zeros=True,
                             output_dir=output_dir)
    return f"\\includegraphics[width=0.6\\textwidth]{{{figure_filename}}}"


def get_figure_portfolio_selector_sparkle_vs_vbs(output_dir: Path,
                                                 objective: SparkleObjective,
                                                 train_data: PerformanceDataFrame,
                                                 actual_portfolio_selector_penalty: dict,
                                                 penalty: int) -> str:
    """Create a LaTeX plot comparing the selector and the VBS.

    The plot compares the performance on each instance of the portfolio selector created
    by Sparkle and the VBS (virtual best solver).

    Returns:
        LaTeX str to include the comparison plot in a LaTeX report.
    """
    vbs_penalty_time = train_data.get_dict_vbs_penalty_time_on_each_instance(penalty)

    instances = vbs_penalty_time.keys() & actual_portfolio_selector_penalty.keys()
    if (len(vbs_penalty_time) != len(instances)):
        print("ERROR: Number of penalty times for the virtual best solver does not"
              "match the number of instances")
        sys.exit(-1)
    points = [[vbs_penalty_time[instance], actual_portfolio_selector_penalty[instance]]
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
    actual_performance_dict = get_actual_portfolio_selector_performance_per_instance(
        train_data, selection_scenario, feature_data, cutoff, penalty)
    latex_dict = {"bibliographypath": str(bibliograpghy_path.absolute()),
                  "numSolvers": str(train_data.num_solvers),
                  "solverList": stex.get_directory_list(train_data.solvers)}
    latex_dict["numFeatureExtractors"] = str(len(
        [p for p in extractor_path.iterdir() if p.is_dir()]))
    latex_dict["featureExtractorList"] = stex.get_directory_list(extractor_path)
    latex_dict["numInstanceClasses"] = get_num_instance_sets(train_data.instances)
    latex_dict["instanceClassList"] = get_instance_set_count_list(train_data.instances)
    latex_dict["featureComputationCutoffTime"] = str(extractor_cutoff)
    latex_dict["performanceComputationCutoffTime"] = str(cutoff)
    rank_list_perfect = scmch.compute_perfect_selector_marginal_contribution(train_data)
    rank_list_actual = scmch.compute_actual_selector_marginal_contribution(
        train_data, feature_data, selection_scenario, performance_cutoff=cutoff)
    latex_dict["solverPerfectRankingList"] = solver_rank_list_latex(rank_list_perfect)
    latex_dict["solverActualRankingList"] = solver_rank_list_latex(rank_list_actual)
    latex_dict["PARRankingList"] = get_par_ranking_list(train_data, objective)
    latex_dict["VBSPAR"] = str(train_data.calc_vbs_penalty_time())
    latex_dict["actualPAR"] = get_par(actual_performance_dict)
    latex_dict["metric"] = objective.metric
    latex_dict["figure-portfolio-selector-sparkle-vs-sbs"] =\
        get_figure_portfolio_selector_sparkle_vs_sbs(target_dir, objective, train_data,
                                                     actual_performance_dict, penalty)
    latex_dict["figure-portfolio-selector-sparkle-vs-vbs"] =\
        get_figure_portfolio_selector_sparkle_vs_vbs(target_dir, objective, train_data,
                                                     actual_performance_dict, penalty)
    latex_dict["testBool"] = r"\testfalse"

    # Train and test
    if test_case_data is not None:
        latex_dict["testInstanceClass"] =\
            f"\\textbf{ {test_case_data.csv_filepath.parent.name} }"
        latex_dict["numInstanceInTestInstanceClass"] =\
            str(test_case_data.num_instances)
        latex_dict["testActualPAR"] = get_par(test_case_data)
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
