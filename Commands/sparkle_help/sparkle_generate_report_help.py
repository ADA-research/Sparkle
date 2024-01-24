#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for report generation."""

import os
import sys
import numpy as np
from shutil import which
from pathlib import Path
import subprocess

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_file_help as sfh
from Commands.sparkle_help import sparkle_performance_data_csv_help as spdcsv
from Commands.sparkle_help import sparkle_compute_marginal_contribution_help as scmch
from Commands.sparkle_help import sparkle_logging as sl
from Commands.sparkle_help import sparkle_tex_help as stex
from Commands.sparkle_help.sparkle_settings import PerformanceMeasure


def underscore_for_latex(string: str) -> str:
    """Return the input str with the underscores escaped for use in LaTeX.

    Args:
        string: A given str with underscores.

    Returns:
        The corresponding str with underscores escaped.
    """
    updated_string = string.replace("_", "\\_")

    return updated_string


def get_custom_commands() -> str:
    """Return an empty str.

    NOTE: Re-evaluate the need for this.
    """
    str_value = ""
    return str_value


def get_sparkle() -> str:
    """Return Sparkle as LaTeX str.

    NOTE: Consider deprecating, could easily be in the LaTeX tempalte itself.
    """
    str_value = r"\emph{Sparkle}"
    return str_value


def get_num_solvers() -> str:
    """Get the number of solvers.

    Returns:
        The number of solvers in solver_list as a string value.
    """
    num_solvers = len(sgh.solver_list)
    str_value = str(num_solvers)

    if int(str_value) < 1:
        print("ERROR: No solvers found, report generation failed!")
        sys.exit(-1)

    return str_value


def get_solver_list() -> str:
    """Get the list of solvers for use in a LaTeX document.

    Returns:
        The list of solver names as LaTeX str.
    """
    str_value = ""
    solver_list = sgh.solver_list

    for solver_path in solver_list:
        solver_name = sfh.get_file_name(solver_path)
        str_value += r"\item \textbf{" + solver_name + r"}\n"

    return str_value


def get_num_feature_extractors() -> str:
    """Get the number of feature extractors.

    Returns:
        The number of feature extractors.
    """
    num_feature_extractors = len(sgh.extractor_list)
    str_value = str(num_feature_extractors)

    if int(str_value) < 1:
        print("ERROR: No feature extractors found, report generation failed!")
        sys.exit(-1)

    return str_value


def get_feature_extractor_list() -> str:
    """Get the feature extractors for use in a LaTeX document.

    Returns:
        The list of feature extractors as LaTeX str.
    """
    str_value = ""
    extractor_list = sgh.extractor_list

    for extractor_path in extractor_list:
        extractor_name = sfh.get_file_name(extractor_path)
        str_value += r"\item \textbf{" + extractor_name + r"}\n"

    return str_value


def get_num_instance_classes() -> str:
    """Get the number of instance sets.

    Returns:
        The number of instance sets as LaTeX str.
    """
    list_instance_class = []
    instance_list = sgh.instance_list

    for instance_path in instance_list:
        instance_class = sfh.get_current_directory_name(instance_path)

        if instance_class not in list_instance_class:
            list_instance_class.append(instance_class)

    str_value = str(len(list_instance_class))

    if int(str_value) < 1:
        print("ERROR: No instance sets found, report generation failed!")
        sys.exit(-1)

    return str_value


def get_instance_class_list() -> str:
    """Get the instance sets for use in a LaTeX document.

    Returns:
        The list of instance sets as LaTeX str.
    """
    str_value = ""
    list_instance_class = []
    dict_number_of_instances_in_instance_class = {}
    instance_list = sgh.instance_list

    for instance_path in instance_list:
        instance_class = sfh.get_current_directory_name(instance_path)

        if instance_class not in list_instance_class:
            list_instance_class.append(instance_class)
            dict_number_of_instances_in_instance_class[instance_class] = 1
        else:
            dict_number_of_instances_in_instance_class[instance_class] += 1

    for instance_class in list_instance_class:
        str_value += (r"\item \textbf{" + instance_class + r"}, consisting of "
                      + str(dict_number_of_instances_in_instance_class[instance_class])
                      + " instances\n")

    return str_value


def get_feature_computation_cutoff_time() -> str:
    """Get the cutoff time used for feature computation.

    Returns:
        The feature computation cutoff time as str.
    """
    return str(sgh.settings.get_general_extractor_cutoff_time())


def get_performance_computation_cutoff_time() -> str:
    """Get the cutoff time used for performance computation.

    Returns:
        The performance computation cutoff time as str.
    """
    return str(sgh.settings.get_general_target_cutoff_time())


def get_solver_perfect_ranking_list() -> str:
    """Get solvers ranked by marginal contribution to the VBS (virtual best solver).

    Returns:
        Solvers in the VBS (virtual best solver) ranked by marginal contribution as LaTeX
        str.
    """
    # TODO: This method call is missing arguments?
    rank_list = scmch.compute_perfect_selector_marginal_contribution()
    str_value = ""

    for i in range(0, len(rank_list)):
        solver = rank_list[i][0]
        solver = sfh.get_file_name(solver)
        marginal_contribution = str(rank_list[i][1])
        str_value += (r"\item \textbf{" + solver + r"}, marginal contribution: "
                      + f"{marginal_contribution}\n")
    return str_value


def get_solver_actual_ranking_list() -> str:
    """Get solvers ranked by marginal contribution to the Sparkle portfolio selector.

    Returns:
        Solvers in the Sparkle portfolio selector ranked by marginal contribution as
        LaTeX str.
    """
    # TODO: This method call is missing arguments?
    rank_list = scmch.compute_actual_selector_marginal_contribution()
    str_value = ""

    for i in range(0, len(rank_list)):
        solver = rank_list[i][0]
        solver = sfh.get_file_name(solver)
        marginal_contribution = str(rank_list[i][1])
        str_value += (r"\item \textbf{" + solver + r"}, marginal contribution: "
                      + f"{marginal_contribution}\n")
    return str_value


def get_par_ranking_list() -> str:
    """Get a list of the solvers ranked by PAR (Penalised Average Runtime).

    Returns:
        The list of solvers ranked by PAR as LaTeX str.
    """
    str_value = ""
    performance_data_csv = (
        spdcsv.SparklePerformanceDataCSV(sgh.performance_data_csv_path))

    solver_penalty_time_ranking_list = (
        performance_data_csv.get_solver_penalty_time_ranking_list())

    for solver, this_penalty_time in solver_penalty_time_ranking_list:
        solver = sfh.get_file_name(solver)
        penalty = sgh.settings.get_general_penalty_multiplier()
        str_value += (rf"\item \textbf{{{solver}}}, PAR{penalty}: {this_penalty_time}\n")

    return str_value


def get_vbs_par() -> str:
    """PAR (Penalised Average Runtime) of the VBS (virtual best solver).

    Returns:
        The PAR (Penalised Average Runtime) of the VBS (virtual best solver) over a set
        of instances.
    """
    str_value = ""
    performance_data_csv = (
        spdcsv.SparklePerformanceDataCSV(sgh.performance_data_csv_path))
    vbs_penalty_time = performance_data_csv.calc_vbs_penalty_time()

    str_value = str(vbs_penalty_time)

    return str_value


def get_actual_par() -> str:
    """PAR (Penalised Average Runtime) of the Sparkle portfolio selector.

    Returns:
        The PAR (Penalised Average Runtime) of the Sparkle portfolio selector over a set
        of instances.
    """
    performance_dict = get_dict_actual_portfolio_selector_penalty_time_on_each_instance()
    mean_performance = sum(performance_dict.values()) / len(performance_dict)

    return str(mean_performance)


def get_dict_sbs_penalty_time_on_each_instance() -> dict[str, int]:
    """Returns a dictionary with the penalised performance of the SBS on each instance.

    Returns:
        A dict that maps instance name str to their penalised performance int.
    """
    mydict = {}
    performance_data_csv = (
        spdcsv.SparklePerformanceDataCSV(sgh.performance_data_csv_path))
    cutoff_time = sgh.settings.get_general_target_cutoff_time()

    solver_penalty_time_ranking_list = (
        performance_data_csv.get_solver_penalty_time_ranking_list())
    sbs_solver = solver_penalty_time_ranking_list[0][0]

    for instance in performance_data_csv.list_rows():
        this_run_time = performance_data_csv.get_value(instance, sbs_solver)

        if this_run_time <= cutoff_time:
            mydict[instance] = this_run_time
        else:
            mydict[instance] = sgh.settings.get_penalised_time()

    return mydict


def get_dict_vbs_penalty_time_on_each_instance() -> dict[str, int]:
    """Returns a dictionary with the penalised performance of the VBS on each instance.

    Returns:
        A dict that maps instance name str to their penalised performance int.
    """
    performance_data_csv = (
        spdcsv.SparklePerformanceDataCSV(sgh.performance_data_csv_path))
    mydict = performance_data_csv.get_dict_vbs_penalty_time_on_each_instance()

    return mydict


def get_dict_actual_portfolio_selector_penalty_time_on_each_instance() -> dict[str, int]:
    """Returns a dictionary with the portfolio selector performance on each instance.

    Returns:
        A dict that maps instance name str to their penalised performance int.
    """
    mydict = {}
    performance_data_csv = (
        spdcsv.SparklePerformanceDataCSV(sgh.performance_data_csv_path))
    actual_portfolio_selector_path = sgh.sparkle_algorithm_selector_path
    minimise = True
    performance_measure = sgh.settings.get_general_performance_measure()
    capvalue = sgh.settings.get_general_cap_value()

    if performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION:
        minimise = False

    for instance in performance_data_csv.list_rows():
        used_time_for_this_instance, flag_successfully_solving = \
            scmch.compute_actual_performance_for_instance(
                actual_portfolio_selector_path, instance, sgh.feature_data_csv_path,
                performance_data_csv, minimise, performance_measure, capvalue)

        if flag_successfully_solving:
            mydict[instance] = used_time_for_this_instance
        else:
            mydict[instance] = sgh.settings.get_penalised_time()

    return mydict


def get_figure_portfolio_selector_sparkle_vs_sbs() -> str:
    """Create a LaTeX plot comparing the selector and the SBS.

    The plot compares the performance on each instance of the portfolio selector created
    by Sparkle and the SBS (single best solver).

    Returns:
        LaTeX str to include the comparison plot in a LaTeX report.
    """
    dict_sbs_penalty_time_on_each_instance = get_dict_sbs_penalty_time_on_each_instance()
    dict_actual_portfolio_selector_penalty_time_on_each_instance = (
        get_dict_actual_portfolio_selector_penalty_time_on_each_instance())

    instances = (dict_sbs_penalty_time_on_each_instance.keys()
                 & dict_actual_portfolio_selector_penalty_time_on_each_instance.keys())
    if (len(dict_sbs_penalty_time_on_each_instance) != len(instances)):
        print("ERROR: Number of penalty times for the single best solver does not match "
              "the number of instances")
        sys.exit(-1)
    points = []
    for instance in instances:
        point = [dict_sbs_penalty_time_on_each_instance[instance],
                 dict_actual_portfolio_selector_penalty_time_on_each_instance[instance]]
        points.append(point)

    latex_directory_path = "Components/Sparkle-latex-generator/"
    figure_portfolio_selector_sparkle_vs_sbs_filename = (
        "figure_portfolio_selector_sparkle_vs_sbs")

    performance_data_csv = (
        spdcsv.SparklePerformanceDataCSV(sgh.performance_data_csv_path))
    solver_penalty_time_ranking_list = (
        performance_data_csv.get_solver_penalty_time_ranking_list())
    sbs_solver = solver_penalty_time_ranking_list[0][0]
    sbs_solver = sfh.get_file_name(sbs_solver)
    penalty = sgh.settings.get_general_penalty_multiplier()

    generate_comparison_plot(points,
                             figure_portfolio_selector_sparkle_vs_sbs_filename,
                             xlabel=f"SBS ({sbs_solver}) [PAR{penalty}]",
                             ylabel=f"Sparkle Selector [PAR{penalty}]",
                             limit="magnitude",
                             limit_min=0.25,
                             limit_max=0.25,
                             penalty_time=sgh.settings.get_penalised_time(),
                             replace_zeros=True,
                             cwd=latex_directory_path)
    str_value = (
        "\\includegraphics[width=0.6\\textwidth]"
        f"{figure_portfolio_selector_sparkle_vs_sbs_filename}"
    )

    return str_value


def get_figure_portfolio_selector_sparkle_vs_vbs() -> str:
    """Create a LaTeX plot comparing the selector and the VBS.

    The plot compares the performance on each instance of the portfolio selector created
    by Sparkle and the VBS (virtual best solver).

    Returns:
        LaTeX str to include the comparison plot in a LaTeX report.
    """
    dict_vbs_penalty_time_on_each_instance = get_dict_vbs_penalty_time_on_each_instance()
    dict_actual_portfolio_selector_penalty_time_on_each_instance = (
        get_dict_actual_portfolio_selector_penalty_time_on_each_instance())

    instances = (dict_vbs_penalty_time_on_each_instance.keys()
                 & dict_actual_portfolio_selector_penalty_time_on_each_instance.keys())
    if (len(dict_vbs_penalty_time_on_each_instance) != len(instances)):
        print("ERROR: Number of penalty times for the virtual best solver does not"
              "match the number of instances")
        sys.exit(-1)
    points = []
    for instance in instances:
        point = [dict_vbs_penalty_time_on_each_instance[instance],
                 dict_actual_portfolio_selector_penalty_time_on_each_instance[instance]]
        points.append(point)

    latex_directory_path = "Components/Sparkle-latex-generator/"
    figure_portfolio_selector_sparkle_vs_vbs_filename = (
        "figure_portfolio_selector_sparkle_vs_vbs")
    penalty = sgh.settings.get_general_penalty_multiplier()

    generate_comparison_plot(points,
                             figure_portfolio_selector_sparkle_vs_vbs_filename,
                             xlabel=f"VBS [PAR{penalty}]",
                             ylabel=f"Sparkle Selector [PAR{penalty}]",
                             limit="magnitude",
                             limit_min=0.25,
                             limit_max=0.25,
                             penalty_time=sgh.settings.get_penalised_time(),
                             replace_zeros=True,
                             cwd=latex_directory_path)

    str_value = (
        "\\includegraphics[width=0.6\\textwidth]"
        f"{figure_portfolio_selector_sparkle_vs_vbs_filename}"
    )

    return str_value


def get_test_instance_class(test_case_directory: str) -> str:
    """Get the name of the test instance set.

    Args:
        test_case_directory: Path to the test case directory.

    Returns:
        The name of the test instance set.
    """
    str_value = sfh.get_last_level_directory_name(test_case_directory)
    str_value = r"\textbf{" + str_value + r"}"

    return str_value


def get_num_instance_in_test_instance_class(test_case_directory: str) -> str:
    """Return the number of instances in a test instance set.

    Args:
        test_case_directory: Path to the test case directory.

    Returns:
        The number of instances in a test instance set as string.
    """
    str_value = ""
    performance_data_csv = spdcsv.SparklePerformanceDataCSV(
        test_case_directory + "sparkle_performance_data.csv")
    str_value = str(len(performance_data_csv.list_rows()))

    return str_value


def get_test_actual_par(test_case_directory: str) -> str:
    """Return the true PAR (Penalised Average Runtime) score on a test set.

    Args:
        test_case_directory: Path to the test case directory.

    Returns:
        PAR score (Penalised Average Runtime) as string.
    """
    str_value = ""
    performance_data_csv = spdcsv.SparklePerformanceDataCSV(
        test_case_directory + "sparkle_performance_data.csv")
    solver = performance_data_csv.list_columns()[0]

    cutoff_time_each_run = sgh.settings.get_general_target_cutoff_time()

    sparkle_penalty_time = 0.0
    sparkle_penalty_time_count = 0

    for instance in performance_data_csv.list_rows():
        this_run_time = performance_data_csv.get_value(instance, solver)
        sparkle_penalty_time_count += 1
        if this_run_time <= cutoff_time_each_run:
            sparkle_penalty_time += this_run_time
        else:
            sparkle_penalty_time += sgh.settings.get_penalised_time()

    sparkle_penalty_time = sparkle_penalty_time / sparkle_penalty_time_count
    str_value = str(sparkle_penalty_time)
    return str_value


def get_dict_variable_to_value(test_case_directory: str = None) -> dict[str, str]:
    """Returns: a dict matching variables in the LaTeX template with their values.

    Args:
        test_case_directory: Path to the test case directory.

    Returns:
        A dict matching str variables in the LaTeX template with their value str.
    """
    latex_dict = {}

    latex_dict["customCommands"] = get_custom_commands()
    latex_dict["sparkle"] = get_sparkle()
    latex_dict["numSolvers"] = get_num_solvers()
    latex_dict["solverList"] = get_solver_list()
    latex_dict["numFeatureExtractors"] = get_num_feature_extractors()
    latex_dict["featureExtractorList"] = get_feature_extractor_list()
    latex_dict["numInstanceClasses"] = get_num_instance_classes()
    latex_dict["instanceClassList"] = get_instance_class_list()
    latex_dict["featureComputationCutoffTime"] = get_feature_computation_cutoff_time()
    latex_dict["performanceComputationCutoffTime"] =\
        get_performance_computation_cutoff_time()
    latex_dict["solverPerfectRankingList"] = get_solver_perfect_ranking_list()
    latex_dict["solverActualRankingList"] = get_solver_actual_ranking_list()
    latex_dict["PARRankingList"] = get_par_ranking_list()
    latex_dict["VBSPAR"] = get_vbs_par()
    latex_dict["actualPAR"] = get_actual_par()
    latex_dict["penalty"] = str(sgh.settings.get_general_penalty_multiplier())
    latex_dict["figure-portfolio-selector-sparkle-vs-sbs"] =\
        get_figure_portfolio_selector_sparkle_vs_sbs()
    latex_dict["figure-portfolio-selector-sparkle-vs-vbs"] =\
        get_figure_portfolio_selector_sparkle_vs_vbs()
    latex_dict["testBool"] = r"\testfalse"

    # Train and test
    if test_case_directory is not None:
        latex_dict["testInstanceClass"] = get_test_instance_class(test_case_directory)
        latex_dict["numInstanceInTestInstanceClass"] =\
            get_num_instance_in_test_instance_class(test_case_directory)
        latex_dict["testActualPAR"] = get_test_actual_par(test_case_directory)
        latex_dict["testBool"] = r"\testtrue"

    return latex_dict


def generate_report(test_case_directory: str = None) -> None:
    """Generate a report for algorithm selection.

    Args:
        test_case_directory: Path to the test case directory. Defaults to None.
    """
    # Include results on the test set if a test case directory is given
    if test_case_directory is not None:
        if not Path(test_case_directory).exists():
            print("ERROR: The given directory", test_case_directory, "does not exist!")
            sys.exit(-1)

        if test_case_directory[-1] != "/":
            test_case_directory += "/"

        latex_report_filename = Path("Sparkle_Report_for_Test")
        dict_variable_to_value = get_dict_variable_to_value(test_case_directory)
    # Only look at the training instance set(s)
    else:
        latex_report_filename = Path("Sparkle_Report")
        dict_variable_to_value = get_dict_variable_to_value()

    latex_directory_path = Path("Components/Sparkle-latex-generator/")

    latex_template_filepath = latex_directory_path / "template-Sparkle.tex"
    report_content = Path(latex_template_filepath).open("r").read()

    for variable_key, str_value in dict_variable_to_value.items():
        variable = r"@@" + variable_key + r"@@"
        if (variable_key != "figure-portfolio-selector-sparkle-vs-sbs"
           and variable_key != "figure-portfolio-selector-sparkle-vs-vbs"):
            str_value = str_value.replace("_", r"\textunderscore ")
        report_content = report_content.replace(variable, str_value)

    latex_report_filepath = Path(latex_directory_path / latex_report_filename)
    latex_report_filepath = latex_report_filepath.with_suffix(".tex")

    Path(latex_report_filepath).open("w+").write(report_content)

    stex.check_tex_commands_exist(latex_directory_path)

    report_path = stex.compile_pdf(latex_directory_path, latex_report_filename)

    print(f"Report is placed at: {report_path}")
    sl.add_output(str(report_path), "Sparkle portfolio selector report")


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
                             magnitude_lines: int = sgh.sparkle_maximum_int,
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
    if output_dir is None:
        output_dir = Path()
    elif type(output_dir) is str:
        output_dir = Path(output_dir)

    points = np.array(points)
    if replace_zeros:
        zero_runtime = 0.000001  # Microsecond
        check_zeros = np.count_nonzero(points <= 0)
        if check_zeros != 0:
            print("WARNING: Zero or negative valued performance values detected. Setting"
                  f" these values to {zero_runtime}.")
        points[points == 0] = zero_runtime

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

    output_data_file = f"{figure_filename}.dat"
    output_gnuplot_script = f"{figure_filename}.plt"
    output_eps_file = f"{figure_filename}.eps"

    # Create data file
    with (output_dir / output_data_file).open("w") as fout:
        for point in points:
            fout.write(" ".join([str(c) for c in point]) + "\n")
        fout.close()

    # Generate plot script
    with (output_dir / output_gnuplot_script).open("w") as fout:
        fout.write(f"set xlabel '{xlabel}'\n"
                   f"set ylabel '{ylabel}'\n"
                   f"set title '{title}'\n"
                   "unset key\n"
                   f"set xrange [{min_value}:{max_value}]\n"
                   f"set yrange [{min_value}:{max_value}]\n")
        if scale == "log":
            fout.write("set logscale x\n"
                       "set logscale y\n")
        fout.write("set grid lc rgb '#CCCCCC' lw 2\n"
                   "set size square\n"
                   f"set arrow from {min_value},{min_value} to {max_value},{max_value}"
                   " nohead lc rgb '#AAAAAA'\n")
        # TODO magnitude lines for linear scale
        if magnitude_lines > 0 and scale == "log":
            for order in range(1, magnitude_lines + 1):
                min_shift = min_value * 10 ** order
                max_shift = 10**(np.log10(max_value) - order)
                if min_shift >= max_value:  # Outside plot
                    # Only print magnitude lines if the fall within the visible plotting
                    # area.
                    break

                fout.write(f"set arrow from {min_value},{min_shift} to {max_shift},"
                           f"{max_value} nohead lc rgb '#CCCCCC' dashtype '-'\n"
                           f"set arrow from {min_shift},{min_value} to {max_value},"
                           f"{max_shift} nohead lc rgb '#CCCCCC' dashtype '-'\n")

        if penalty_time is not None:
            fout.write(f"set arrow from {min_value},{penalty_time} to {max_value},"
                       f"{penalty_time} nohead lc rgb '#AAAAAA'\n"
                       f"set arrow from {penalty_time},{min_value} to {penalty_time},"
                       f"{max_value} nohead lc rgb '#AAAAAA'\n")

        fout.write('set terminal postscript eps color solid linewidth "Helvetica" 20\n'
                   f"set output '{output_eps_file}\n"
                   "set style line 1 pt 2 ps 1.5 lc rgb 'royalblue' \n"
                   f"plot '{output_data_file}' ls 1\n")

    subprocess_plot = subprocess.run(["gnuplot", output_gnuplot_script],
                                     capture_output=True,
                                     cwd=output_dir)

    if subprocess_plot.returncode != 0:
        print(f"(GnuPlot) Error whilst plotting {output_gnuplot_script}:\n"
              f"{subprocess_plot.stderr.decode()}\n")

    # Some systems are missing epstopdf so a copy is included
    epsbackup = Path(os.path.abspath(Path.cwd())) / "Components/epstopdf.pl"
    epstopdf = which("epstopdf") or epsbackup
    subprocess_epstopdf = subprocess.run([epstopdf, output_eps_file],
                                         capture_output=True,
                                         cwd=output_dir)

    if subprocess_epstopdf.returncode != 0:
        print(f"(Eps To PDF) Error whilst converting Eps to PDF {output_eps_file}"
              f"{subprocess_epstopdf.stderr.decode()}")

    sfh.rmfiles(output_gnuplot_script)
