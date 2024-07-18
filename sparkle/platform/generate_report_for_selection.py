#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for selection report generation."""
import os
import sys
import numpy as np
from shutil import which
from pathlib import Path
from collections import Counter
import subprocess

from sparkle.platform import file_help as sfh, tex_help as stex
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from CLI.support import compute_marginal_contribution_help as scmch
from sparkle.types.objective import PerformanceMeasure, SparkleObjective


def underscore_for_latex(string: str) -> str:
    """Return the input str with the underscores escaped for use in LaTeX.

    Args:
        string: A given str with underscores.

    Returns:
        The corresponding str with underscores escaped.
    """
    return string.replace("_", "\\_")


def get_solver_list_latex(solver_list: list[str] = None) -> str:
    """Get the list of solvers for use in a LaTeX document.

    Returns:
        The list of solver names as LaTeX str.
    """
    return "".join(f"\\item \\textbf{{{Path(solver_path).name}}}\n"
                   for solver_path in solver_list)


def get_feature_extractor_list(extractor_dir: Path) -> str:
    """Get the feature extractors for use in a LaTeX document.

    Returns:
        The list of feature extractors as LaTeX str.
    """
    return "".join(f"\\item \\textbf{{{Path(extractor_path).name}}}\n"
                   for extractor_path in extractor_dir.iterdir())


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


def get_actual_par(performance_dict: dict) -> str:
    """PAR (Penalised Average Runtime) of the Sparkle portfolio selector.

    Returns:
        The PAR (Penalised Average Runtime) of the Sparkle portfolio selector over a set
        of instances.
    """
    mean_performance = sum(performance_dict.values()) / len(performance_dict)
    return str(mean_performance)


def get_test_actual_par(performance_data: PerformanceDataFrame) -> str:
    """Return the true PAR (Penalised Average Runtime) score on a test set.

    Args:
        test_case_directory: Path to the test case directory.

    Returns:
        PAR score (Penalised Average Runtime) as string.
    """
    # Its selecting the first solver because in this case its the Selector (Only solver)
    solver = performance_data.solvers[0]
    return str(performance_data.dataframe[solver].sum() / performance_data.num_instances)


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
        actual_portfolio_selector_path: Path,
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
        actual_portfolio_selector_path: Path,
        feature_data: FeatureDataFrame,
        extractor_cutoff: int,
        cutoff: int,
        penalty: int,
        train_data: PerformanceDataFrame,
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
        train_data, actual_portfolio_selector_path, feature_data, cutoff, penalty)
    latex_dict = {"bibliographypath": str(bibliograpghy_path.absolute()),
                  "numSolvers": str(train_data.num_solvers),
                  "solverList": get_solver_list_latex(train_data.solvers)}
    latex_dict["numFeatureExtractors"] = str(len(
        [p for p in extractor_path.iterdir() if p.is_dir()]))
    latex_dict["featureExtractorList"] = get_feature_extractor_list(extractor_path)
    latex_dict["numInstanceClasses"] = get_num_instance_sets(train_data.instances)
    latex_dict["instanceClassList"] = get_instance_set_count_list(train_data.instances)
    latex_dict["featureComputationCutoffTime"] = str(extractor_cutoff)
    latex_dict["performanceComputationCutoffTime"] = str(cutoff)
    rank_list_perfect = scmch.compute_perfect_selector_marginal_contribution(train_data)
    rank_list_actual = scmch.compute_actual_selector_marginal_contribution(
        train_data, feature_data, performance_cutoff=cutoff)
    latex_dict["solverPerfectRankingList"] = solver_rank_list_latex(rank_list_perfect)
    latex_dict["solverActualRankingList"] = solver_rank_list_latex(rank_list_actual)
    latex_dict["PARRankingList"] = get_par_ranking_list(train_data, objective)
    latex_dict["VBSPAR"] = str(train_data.calc_vbs_penalty_time())
    latex_dict["actualPAR"] = get_actual_par(actual_performance_dict)
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
        latex_dict["testActualPAR"] = get_test_actual_par(test_case_data)
        latex_dict["testBool"] = r"\testtrue"

    return latex_dict


def fill_template_tex(template_tex: str, variables: dict) -> str:
    """Given a latex template, replaces all the @@ variables using the dict.

    Args:
        template_tex: The template to be populated
        variables: Variable names (key) with their target (value)

    Returns:
        The populated latex string.
    """
    for variable_key, target_value in variables.items():
        variable = "@@" + variable_key + "@@"
        # We don't modify variable names in the Latex file
        if "\\includegraphics" not in target_value and "\\label" not in target_value:
            # Rectify underscores in target_value
            target_value = target_value.replace("_", r"\textunderscore ")
        template_tex = template_tex.replace(variable, target_value)
    return template_tex


def generate_report(latex_source_path: Path,
                    latex_template_name: str,
                    target_path: Path,
                    report_name: str,
                    variable_dict: dict) -> None:
    """General steps to generate a report.

    Args:
        latex_source_path: The path to the template
        latex_template_name: The template name
        target_path: The directory where the result should be placed
        report_name: The name of the pdf (without suffix)
        variable_dict: TBD
    """
    latex_template_filepath = latex_source_path / latex_template_name

    report_content = latex_template_filepath.open("r").read()
    report_content = fill_template_tex(report_content, variable_dict)

    target_path.mkdir(parents=True, exist_ok=True)
    latex_report_filepath = target_path / report_name
    latex_report_filepath = latex_report_filepath.with_suffix(".tex")
    Path(latex_report_filepath).open("w+").write(report_content)

    stex.check_tex_commands_exist(target_path)
    report_path = stex.compile_pdf(target_path, report_name)

    print(f"Report is placed at: {report_path}")


def generate_gnuplot(output_gnuplot_script: str,
                     output_dir: Path = None) -> None:
    """Generates plot from script using GNU plot."""
    subprocess_plot = subprocess.run(["gnuplot", output_gnuplot_script],
                                     capture_output=True,
                                     cwd=output_dir)

    if subprocess_plot.returncode != 0:
        print(f"(GnuPlot) Error whilst plotting {output_gnuplot_script}:\n"
              f"{subprocess_plot.stderr.decode()}\n")


def generate_pdf(eps_file: str,
                 output_dir: Path = None) -> None:
    """Generate PDF using epstopdf."""
    # Some systems are missing epstopdf so a copy is included
    epsbackup = Path(os.path.abspath(Path.cwd())) / "sparkle/Components/epstopdf.pl"
    epstopdf = which("epstopdf") or epsbackup
    subprocess_epstopdf = subprocess.run([epstopdf, eps_file],
                                         capture_output=True,
                                         cwd=output_dir)

    if subprocess_epstopdf.returncode != 0:
        print(f"(Eps To PDF) Error whilst converting Eps to PDF {eps_file}"
              f"{subprocess_epstopdf.stderr.decode()}")


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
    if output_dir is None:
        output_dir = Path()
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

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

    output_data_file = f"{figure_filename}.dat"
    output_gnuplot_script = f"{figure_filename}.plt"
    output_eps_file = f"{figure_filename}.eps"

    # Create data file
    with (output_dir / output_data_file).open("w") as fout:
        for point in points:
            fout.write(" ".join([str(c) for c in point]) + "\n")

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

    generate_gnuplot(output_gnuplot_script, output_dir)
    generate_pdf(output_eps_file, output_dir)
    sfh.rmfiles(output_gnuplot_script)


def generate_report_selection(target_path: Path,
                              latex_dir: Path,
                              latex_template: Path,
                              bibliography_path: Path,
                              extractor_path: Path,
                              selector_path: Path,
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
        selector_path: Path to the selector
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
                                                        selector_path,
                                                        feature_data,
                                                        extractor_cutoff,
                                                        cutoff,
                                                        penalty,
                                                        train_data,
                                                        test_case_data)
    generate_report(latex_dir,
                    latex_template,
                    target_path,
                    latex_report_filename,
                    dict_variable_to_value)
