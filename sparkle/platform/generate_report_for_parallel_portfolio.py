#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for parallel portfolio report generation."""
from pathlib import Path
import csv
import operator

import plotly.express as px
import pandas as pd
import plotly.io as pio

from sparkle.platform import latex as stex
from sparkle.platform import generate_report_for_selection as sgfs
from sparkle.types import SparkleObjective, SolverStatus
from sparkle.instance import InstanceSet


pio.kaleido.scope.mathjax = None  # Bug fix for kaleido


def get_solver_list_latex(solver_list: list[str]) -> str:
    """Return the list of solvers as string, including each solver-seed combination.

    Args:
        solver_list: The solver list to convert

    Returns:
        A list of solvers in the parallel portfolio as str.
    """
    latex_itemize = ""

    for solver_str in solver_list:
        # Solver string may contain path and variation seed
        solver_split = solver_str.split(" ")
        solver_name = Path(solver_split[0]).name
        solver_seeds = int(solver_split[2]) if len(solver_split) == 3 else 0

        latex_itemize += f"\\item \\textbf{{{stex.underscore_for_latex(solver_name)}}}\n"
        # Only include if we used more than one seed
        if solver_seeds > 1:
            seeds = ",".join(list[range(1, solver_seeds + 1)])
            latex_itemize += f"\\item[]With seeds: {seeds}\n"

    return latex_itemize


def get_portfolio_metrics(
        solver_list: list[str],
        instance_set: InstanceSet,
        results: dict[list[str, str]],
        objective: SparkleObjective) -> tuple[dict[str, float], str, dict[str, float]]:
    """Return the portfolio metrics for SBS, aggregated results per solver and VBS.

    Args:
        solver_list: list of solvers
        instance_list: List of paths to instance sets
        results: dictionary of results of the portfolio

    Returns:
        A quatro-tuple:
            A dict containing the objective value per instance for the single best solver
            A string containing the name of the single best solver.
            A second dict with aggrated objective values over all instances per solver.
            A third dict containing the virtual best solver (Portfolio) per instance.
    """
    corrected_solver_results = {solver: [] for solver in solver_list}
    instance_worst = None
    op = operator.gt if objective.minimise else operator.lt
    for instance in results:
        for (solver, status, value) in results[instance]:
            if value == "None":
                corrected_solver_results[solver].append(None)
                continue  # Solver failed to return a value
            value = float(value)
            if instance_worst is None or op(value, instance_worst):
                instance_worst = value
            if SolverStatus(status) != SolverStatus.SUCCESS:
                # If the solver wasn't successful, we also assign the worst known value
                corrected_solver_results[solver].append(None)
                continue
            corrected_solver_results[solver].append(float(value))
        for solver in corrected_solver_results:
            if corrected_solver_results[solver][-1] is None:
                corrected_solver_results[solver][-1] = instance_worst
    aggregated_results_solvers = {solver: objective.instance_aggregator(
        corrected_solver_results[solver]) for solver in corrected_solver_results}
    vbs_results_instance = {instance: objective.solver_aggregator(
        [corrected_solver_results[solver][index] for solver in corrected_solver_results])
        for index, instance in enumerate(instance_set._instance_names)}
    # Find the single best solver (SBS)
    sbs_name = min(aggregated_results_solvers, key=aggregated_results_solvers.get)
    sbs_results = corrected_solver_results[sbs_name]
    sbs_dict = {name: sbs_results[index]
                for index, name in enumerate(instance_set._instance_names)}
    return sbs_dict, sbs_name, aggregated_results_solvers, vbs_results_instance


def get_figure_parallel_portfolio_sparkle_vs_sbs(
        target_directory: Path,
        solver_list: list[str],
        instance_set: InstanceSet,
        results: list[str],
        objective: SparkleObjective) -> tuple[
        str, dict[str, float], dict[str, float]]:
    """Generate PaP vs SBS figure and return a string to include it in LaTeX.

    Args:
        target_directory: Path where to place the files
        parallel_portfolio_path: Parallel portfolio path.
        instances: List of instances.

    Returns:
        a three tuple:
            str_value: A string to include the PaP vs SBS figure in LaTeX
            dict_all_solvers: A dict containing the penalised average run time per
                solver.
            dict_actual_parallel_portfolio_penalty_time_on_each_instance: A dict with
                instance names and the penalised running time of the PaP.
    """
    sbs_instance_results, sbs_solver, dict_all_solvers, vbs_instance_results =\
        get_portfolio_metrics(solver_list, instance_set, results, objective)
    figure_filename = "figure_parallel_portfolio_sparkle_vs_sbs"
    data = [[sbs_instance_results[instance], vbs_instance_results[instance]]
            for instance in sbs_instance_results]
    generate_figure(target_directory,
                    f"SBS ({stex.underscore_for_latex(sbs_solver)})",
                    "Parallel-Portfolio", figure_filename, objective.name, data)
    latex_include = f"\\includegraphics[width=0.6\\textwidth]{{{figure_filename}}}"
    return latex_include, dict_all_solvers, vbs_instance_results


def get_results_table(results: dict[str, str, str],
                      dict_all_solvers: dict[str, float], parallel_portfolio_path: Path,
                      dict_portfolio: dict[str, float],
                      solver_with_solutions: dict[str, int],
                      n_unsolved_instances: int, n_instances: int,
                      performance_metric: str) -> str:
    """Returns a LaTeX table with the portfolio results.

    Args:
        results: The total results with status and runtime per solver
        dict_all_solvers: A dict containing the penalised average run time per solver.
        parallel_portfolio_path: Parallel portfolio path
        dict_portfolio: A dict with instance names and the penalised running time of the
            PaP.
        solver_with_solutions: A dict with solver name as key, and number of solved
            instances for the corresponding solver as value, see
            get_solvers_with_solution.
        n_unsolved_instances: Number of unsolved instances.
        n_instances: Number of instances.

    Returns:
        A string containing LaTeX code for a table with the portfolio results.
    """
    portfolio_par = 0.0
    for instance in dict_portfolio:
        portfolio_par += dict_portfolio[instance]
    portfolio_par = portfolio_par / n_instances
    total_killed = 0
    for instance in results:
        for (_, status, _) in results[instance]:
            total_killed += (status.lower() == "killed")
    # Table 1: Portfolio results
    table_string = (
        "\\caption{\\textbf{Portfolio results}} \\label{tab:portfolio_results} ")
    table_string += "\\begin{tabular}{rrrrr}"
    table_string += (
        "\\textbf{Portfolio nickname} & \\textbf{"
        f"{performance_metric}"
        "} & \\textbf{\\#Timeouts} & "
        "\\textbf{\\#Cancelled} & \\textbf{\\# Solved} \\\\ \\hline ")
    table_string += (
        f"{stex.underscore_for_latex(parallel_portfolio_path.name)} & "
        f"{round(portfolio_par,2)} & {n_unsolved_instances} & {total_killed} & "
        f"{n_instances-n_unsolved_instances} \\\\ ")
    table_string += "\\end{tabular}"
    table_string += "\\bigskip"
    # Table 2: Solver results
    table_string += "\\caption{\\textbf{Solver results}} \\label{tab:solver_results} "
    table_string += "\\begin{tabular}{rrrrr}"

    for i, line in enumerate(dict_all_solvers):
        solver_name = Path(line).name

        if i == 0:
            table_string += (
                "\\textbf{Solver} & \\textbf{"
                f"{performance_metric}"
                "} & \\textbf{\\#Timeouts} & "
                "\\textbf{\\#Cancelled} & \\textbf{\\#Best solver} \\\\ \\hline ")

        if solver_name not in solver_with_solutions:
            cancelled = n_instances - n_unsolved_instances
            table_string += (
                f"{stex.underscore_for_latex(solver_name)} & "
                f"{round(dict_all_solvers[line], 2)} & {n_unsolved_instances} & "
                f"{cancelled} & 0 \\\\ ")
        else:
            cancelled = (n_instances - n_unsolved_instances
                         - solver_with_solutions[solver_name])
            table_string += (
                f"{stex.underscore_for_latex(solver_name)} & "
                f"{round(dict_all_solvers[line], 2)} & {n_unsolved_instances} & "
                f"{cancelled} & {solver_with_solutions[solver_name]} \\\\ ")
    table_string += "\\end{tabular}"
    return table_string


def parallel_report_variables(target_directory: Path,
                              parallel_portfolio_path: Path,
                              bibliograpghy_path: Path,
                              objective: SparkleObjective,
                              cutoff: int,
                              instance_set: InstanceSet) -> dict[str, str]:
    """Returns a mapping between LaTeX report variables and their values.

    Args:
        target_directory: Path to where to place the generated files.
        parallel_portfolio_path: Parallel portfolio path.
        bibliograpghy_path: Path to the bib file
        instances: List of instances.

    Returns:
        A dictionary that maps variables used in the LaTeX report to values.
    """
    variables_dict = {"bibliographypath": bibliograpghy_path.absolute(),
                      "cutoffTime": cutoff,
                      "performanceMetric": objective.name,
                      "numInstanceClasses": "1"}  # Currently no support for multi sets
    # Get the results data
    csv_data = [line for line in
                csv.reader((parallel_portfolio_path / "results.csv").open("r"))]
    header = csv_data[0]
    csv_data = csv_data[1:]
    solver_column = header.index("Solver")
    instance_column = header.index("Instance")
    status_column = [i for i, v in enumerate(header)
                     if v.startswith("status")][0]
    objective_column = header.index(objective.name)
    solver_list = list(set([line[solver_column]
                            for line in csv_data]))  # Unique set of solvers
    results = {name: [] for name in instance_set._instance_names}
    for row in csv_data:
        if row[instance_column] in results.keys():
            results[row[instance_column]].append(
                [row[solver_column], row[status_column], row[objective_column]])

    variables_dict["numSolvers"] = len(solver_list)
    variables_dict["solverList"] = get_solver_list_latex(solver_list)
    variables_dict["instanceClassList"] =\
        sgfs.get_instance_set_count_list(instance_set._instance_paths)

    # Produce some statistics on the parallel portfolio
    solvers_solutions = {solver: 0 for solver in solver_list}
    instance_names_copy = instance_set._instance_names.copy()
    for line in csv_data:
        if (line[instance_column] in instance_names_copy
                and SolverStatus(line[status_column]) == SolverStatus.SUCCESS):
            solvers_solutions[line[solver_column]] += 1
            instance_names_copy.remove(line[instance_column])
    unsolved_instances = instance_set.size - sum([solvers_solutions[key]
                                                  for key in solvers_solutions])
    inst_succes = []
    for solver in solvers_solutions:
        inst_succes.append("\\item Solver "
                           f"\\textbf{{{stex.underscore_for_latex(solver)}}}, was the "
                           "best solver on "
                           f"\\textbf{{{solvers_solutions[solver]}}} instance(s)")
    if unsolved_instances > 0:
        inst_succes.append(f"\\item \\textbf{{{unsolved_instances}}} instances(s) "
                           "remained unsolved")

    variables_dict["solversWithSolution"] = "\n".join(inst_succes)

    (figure_name, dict_all_solvers,
        dict_actual_parallel_portfolio_penalty_time_on_each_instance) =\
        get_figure_parallel_portfolio_sparkle_vs_sbs(target_directory, solver_list,
                                                     instance_set, results, objective)

    variables_dict["figure-parallel-portfolio-sparkle-vs-sbs"] = figure_name
    variables_dict["resultsTable"] = get_results_table(
        results, dict_all_solvers, parallel_portfolio_path,
        dict_actual_parallel_portfolio_penalty_time_on_each_instance,
        solvers_solutions, unsolved_instances, instance_set.size, objective.name)

    if objective.time:
        variables_dict["decisionBool"] = "\\decisiontrue"
    else:
        variables_dict["decisionBool"] = "\\decisionfalse"
    return variables_dict


def generate_figure(
        target_directory: Path,
        sbs_name: str, parallel_portfolio_name: str,
        figure_parallel_portfolio_vs_sbs_filename: str,
        performance_measure: str, data: list) -> None:
    """Generates image for parallel portfolio report."""
    upper_bound = max([x for xs in data for x in xs]) * 1.5
    lower_bound = 0.01

    output_plot = target_directory / f"{figure_parallel_portfolio_vs_sbs_filename}.pdf"

    xlabel = f"{sbs_name}, {performance_measure}"
    ylabel = f"{parallel_portfolio_name}"
    df = pd.DataFrame(data, columns=[xlabel, ylabel])
    fig = px.scatter(data_frame=df, x=xlabel, y=ylabel,
                     range_x=[lower_bound, upper_bound],
                     range_y=[lower_bound, upper_bound],
                     log_x=True, log_y=True,
                     width=500, height=500)
    # Add in the seperation line
    fig.add_shape(type="line", x0=0, y0=0, x1=upper_bound, y1=upper_bound,
                  line=dict(color="lightgrey", width=1))
    fig.update_traces(marker=dict(color="RoyalBlue", symbol="x"))
    fig.update_layout(
        plot_bgcolor="white"
    )
    fig.update_xaxes(
        type="log",
        mirror=True,
        dtick=1,
        ticks="outside",
        showline=True,
        showgrid=True,
        linecolor="black",
        gridcolor="lightgrey"
    )
    fig.update_yaxes(
        type="log",
        mirror=True,
        dtick=1,
        ticks="outside",
        showline=True,
        showgrid=True,
        linecolor="black",
        gridcolor="lightgrey"
    )
    fig.write_image(output_plot)


def generate_report_parallel_portfolio(parallel_portfolio_path: Path,
                                       target_path: Path,
                                       latex_template: Path,
                                       bibliograpghy_path: Path,
                                       objective: SparkleObjective,
                                       cutoff: int,
                                       instances: InstanceSet) -> None:
    """Generate a report for a parallel algorithm portfolio.

    Args:
        parallel_portfolio_path: Parallel portfolio path.
        target_path: Where the report data will be placed.
        latex_template: Path to the latex template path used
        bibliograpghy_path: Path to the bib file
        objective: The objective of the portfolio
        cutoff: The cutoff time for each solver
        instances: List of instances.
    """
    target_path.mkdir(parents=True, exist_ok=True)
    dict_variable_to_value = parallel_report_variables(
        target_path, parallel_portfolio_path, bibliograpghy_path, objective,
        cutoff, instances)

    stex.generate_report(latex_template,
                         "template-Sparkle-for-parallel-portfolio.tex",
                         target_path,
                         "Sparkle_Report_Parallel_Portfolio",
                         dict_variable_to_value)
