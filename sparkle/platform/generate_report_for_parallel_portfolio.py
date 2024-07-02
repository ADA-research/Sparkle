#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for parallel portfolio report generation."""
from pathlib import Path

import sparkle_logging as sl
from sparkle.platform import generate_report_for_selection as sgfs
from sparkle.types.objective import PerformanceMeasure, SparkleObjective
from sparkle.instance import InstanceSet


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

        latex_itemize += f"\\item \\textbf{{{sgfs.underscore_for_latex(solver_name)}}}\n"
        # Only include if we used more than one seed
        if solver_seeds > 1:
            seeds = ",".join(list[range(1, solver_seeds + 1)])
            latex_itemize += f"\\item[]With seeds: {seeds}\n"

    return latex_itemize


def get_dict_sbs_penalty_time_on_each_instance(
        solver_list: list[str],
        instance_list: list[str],
        results: dict[list[str, str]],
        cutoff: int,
        penalised_time: int) -> tuple[dict[str, float], str, dict[str, float]]:
    """Return the penalised run time for the single best solver and per solver.

    Args:
        solver_list: list of solvers
        instance_list: List of paths to instance sets
        results: dictionary of results of the portfolio

    Returns:
        A three-tuple:
            A dict containing the run time per instance for the single best solver.
            A string containing the name of the single best solver.
            A second dict containing penalised averaged run time per solver.
    """
    penalised_averaged_runtime = {solver: 0.0 for solver in solver_list}
    penalised_time = float(penalised_time)
    for instance in results:
        for (solver, status, runtime) in results[instance]:
            # Those that did not finish or exceed the thresh get the penalty
            if float(runtime) >= cutoff or status.lower() != "success":
                runtime = penalised_time
            penalised_averaged_runtime[solver] += (float(runtime) / len(instance_list))

    # Find the single best solver (SBS)
    sbs_name = min(penalised_averaged_runtime, key=penalised_averaged_runtime.get)
    sbs_name = Path(sbs_name).name
    sbs_dict = {Path(instance).name: penalised_time for instance in instance_list}

    for instance in results:
        instance_name = Path(instance).name
        found = False
        for result in results[instance_name]:
            if result[0] == sbs_name:
                found = True
                if float(result[2]) < penalised_time:
                    sbs_dict[instance_name] = float(result[2])
                break
        if not found:
            print(f"WARNING: No result found for instance: {instance_name}")
    return sbs_dict, sbs_name, penalised_averaged_runtime


def get_dict_actual_parallel_portfolio_penalty_time_on_each_instance(
        instance_list: list[str],
        results: dict[str, list[str]],
        cutoff_time: int,
        penalised_time: int) -> dict[str, float]:
    """Returns the instance names and corresponding penalised running times of the PaP.

    Args:
        instance_list: List of instances.

    Returns:
        A dict of instance names and the penalised running time of the PaP.
    """
    instance_penalty_dict = {}

    default_penalty = float(penalised_time)

    for instance in instance_list:
        instance_name = Path(instance).name
        if instance_name in results:
            selected_value = results[instance_name][0]
            for solver in results[instance_name]:
                if solver[2] < selected_value[2]:
                    selected_value = solver
            _, status, runtime = selected_value
            # Assign the measured result if exit status was not timeout
            # and measured time less then cutoff
            if float(runtime) < cutoff_time and status != "TIMEOUT":
                instance_penalty_dict[instance_name] = float(runtime)
            else:  # Assign the penalized result
                instance_penalty_dict[instance_name] = default_penalty
        else:
            instance_penalty_dict[instance_name] = default_penalty
    return instance_penalty_dict


def get_figure_parallel_portfolio_sparkle_vs_sbs(
        target_directory: Path,
        solver_list: list[str],
        instances: list[str],
        results: list[str],
        objective: SparkleObjective,
        cutoff: int,
        penalised_time: int) -> tuple[
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
    dict_sbs_penalty_time_on_each_instance, sbs_solver, dict_all_solvers =\
        get_dict_sbs_penalty_time_on_each_instance(solver_list, instances, results,
                                                   cutoff, penalised_time)
    dict_actual_parallel_portfolio_penalty_time_on_each_instance =\
        get_dict_actual_parallel_portfolio_penalty_time_on_each_instance(instances,
                                                                         results,
                                                                         cutoff,
                                                                         penalised_time)

    figure_filename = "figure_parallel_portfolio_sparkle_vs_sbs"
    data_filename = "data_parallel_portfolio_sparkle_vs_sbs.dat"
    data_filepath = target_directory / data_filename

    with data_filepath.open("w") as outfile:
        for instance in dict_sbs_penalty_time_on_each_instance:
            sbs_penalty_time = dict_sbs_penalty_time_on_each_instance[instance]
            sparkle_penalty_time = (
                dict_actual_parallel_portfolio_penalty_time_on_each_instance[instance])
            outfile.write(str(sbs_penalty_time) + " " + str(sparkle_penalty_time) + "\n")

    generate_figure(target_directory, data_filename, float(penalised_time),
                    f"SBS ({sgfs.underscore_for_latex(sbs_solver)})",
                    "Parallel-Portfolio", figure_filename, objective.metric)
    latex_include = f"\\includegraphics[width=0.6\\textwidth]{{{figure_filename}}}"
    return (latex_include, dict_all_solvers,
            dict_actual_parallel_portfolio_penalty_time_on_each_instance)


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
        f"{sgfs.underscore_for_latex(parallel_portfolio_path.name)} & "
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
                f"{sgfs.underscore_for_latex(solver_name)} & "
                f"{round(dict_all_solvers[line], 2)} & {n_unsolved_instances} & "
                f"{cancelled} & 0 \\\\ ")
        else:
            cancelled = (n_instances - n_unsolved_instances
                         - solver_with_solutions[solver_name])
            table_string += (
                f"{sgfs.underscore_for_latex(solver_name)} & "
                f"{round(dict_all_solvers[line], 2)} & {n_unsolved_instances} & "
                f"{cancelled} & {solver_with_solutions[solver_name]} \\\\ ")
    table_string += "\\end{tabular}"

    return table_string


def parallel_report_variables(target_directory: Path,
                              parallel_portfolio_path: Path,
                              bibliograpghy_path: Path,
                              objective: SparkleObjective,
                              cutoff: int,
                              penalised_time: int,
                              instances: list[str]) -> dict[str, str]:
    """Returns a mapping between LaTeX report variables and their values.

    Args:
        target_directory: Path to where to place the generated files.
        parallel_portfolio_path: Parallel portfolio path.
        bibliograpghy_path: Path to the bib file
        instances: List of instances.

    Returns:
        A dictionary that maps variables used in the LaTeX report to values.
    """
    variables_dict = {"bibliographypath":
                      str(bibliograpghy_path.absolute())}
    # Get the results data
    csv_data = [line.split(",") for line in
                (parallel_portfolio_path / "results.csv").open("r").readlines()]
    solver_list = list(set([line[1] for line in csv_data]))  # Unique set of solvers
    results = {Path(instance).name: [] for instance in instances}
    for row in csv_data:
        if row[0] in results.keys():
            results[row[0]].append([row[1], row[2], row[3]])

    variables_dict["numSolvers"] = str(len(solver_list))
    variables_dict["solverList"] = get_solver_list_latex(solver_list)
    variables_dict["numInstanceClasses"] = str(len(set(
        [Path(instance_path).parent.name for instance_path in instances])))
    variables_dict["cutoffTime"] = str(cutoff)
    variables_dict["performanceMetric"] = objective.metric
    variables_dict["instanceClassList"] = sgfs.get_instance_set_count_list(instances)

    # Produce some statistics on the parallel portfolio
    solvers_solutions = {solver: 0 for solver in solver_list}
    instances_copy = [Path(instance).name for instance in instances]
    for line in csv_data:
        if line[0] in instances_copy and line[2].lower() == "success":
            solvers_solutions[line[1]] += 1
            instances_copy.remove(line[0])
    unsolved_instances = len(instances) - sum([solvers_solutions[key]
                                               for key in solvers_solutions])
    inst_succes = []
    for solver in solvers_solutions:
        inst_succes.append("\\item Solver "
                           f"\\textbf{{{sgfs.underscore_for_latex(solver)}}}, was the "
                           "best solver on "
                           f"\\textbf{{{solvers_solutions[solver]}}} instance(s)")
    if unsolved_instances > 0:
        inst_succes.append(f"\\item \\textbf{{{unsolved_instances}}} instances(s) "
                           "remained unsolved")

    variables_dict["solversWithSolution"] = "\n".join(inst_succes)

    (figure_name, dict_all_solvers,
        dict_actual_parallel_portfolio_penalty_time_on_each_instance) =\
        get_figure_parallel_portfolio_sparkle_vs_sbs(target_directory, solver_list,
                                                     instances, results, objective,
                                                     cutoff, penalised_time)

    variables_dict["figure-parallel-portfolio-sparkle-vs-sbs"] = figure_name

    variables_dict["resultsTable"] = get_results_table(
        results, dict_all_solvers, parallel_portfolio_path,
        dict_actual_parallel_portfolio_penalty_time_on_each_instance,
        solvers_solutions, unsolved_instances, len(instances), objective.metric)

    if objective.PerformanceMeasure == PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION:
        variables_dict["decisionBool"] = "\\decisionfalse"
    else:
        variables_dict["decisionBool"] = "\\decisiontrue"
    return variables_dict


def generate_figure(
        target_directory: Path, data_parallel_portfolio_sparkle_vs_sbs_filename: str,
        penalty_time: float, sbs_name: str, parallel_portfolio_sparkle_name: str,
        figure_parallel_portfolio_sparkle_vs_sbs_filename: str,
        performance_measure: str) -> None:
    """Generates image for parallel portfolio report."""
    upper_bound = penalty_time * 1.5
    lower_bound = 0.01

    output_eps_file =\
        f"{figure_parallel_portfolio_sparkle_vs_sbs_filename}.eps"
    sbs_name = sbs_name.replace("/", "_")
    output_gnuplot_script = f"{parallel_portfolio_sparkle_name}_vs_{sbs_name}.plt"

    with (target_directory / output_gnuplot_script).open("w+") as outfile:
        outfile.write(f"set xlabel '{sbs_name}, {performance_measure}'\n"
                      f"set ylabel '{parallel_portfolio_sparkle_name}, "
                      f"{performance_measure}'\n"
                      f"set title '{parallel_portfolio_sparkle_name} vs {sbs_name}'\n"
                      "unset key\n"
                      f"set xrange [{lower_bound}:{upper_bound}]\n"
                      f"set yrange [{lower_bound}:{upper_bound}]\n"
                      "set logscale x\n"
                      "set logscale y\n"
                      "set grid\n"
                      "set size square\n"
                      f"set arrow from {lower_bound},{lower_bound} to {upper_bound},"
                      f"{upper_bound} nohead lc rgb 'black'\n")

        if performance_measure == "PAR10":
            # Cutoff time x axis
            outfile.write(f"set arrow from {penalty_time},{lower_bound} to "
                          f"{penalty_time},{upper_bound} nohead lc rgb 'black' lt 2\n")
            # Cutoff time y axis
            outfile.write(f"set arrow from {lower_bound},{penalty_time} to {upper_bound}"
                          f",{penalty_time} nohead lc rgb 'black' lt 2\n")

        outfile.write('set terminal postscript eps color dashed linewidth "Helvetica"'
                      " 20\n")
        outfile.write(f"set output '{output_eps_file}'\n"
                      f"plot '{data_parallel_portfolio_sparkle_vs_sbs_filename}' with "
                      "points pt 2 ps 2\n")

    sgfs.generate_gnuplot(output_gnuplot_script, target_directory)
    sgfs.generate_pdf(output_eps_file, target_directory)
    Path(output_gnuplot_script).unlink(missing_ok=True)


def generate_report_parallel_portfolio(parallel_portfolio_path: Path,
                                       target_path: Path,
                                       latex_template: Path,
                                       bibliograpghy_path: Path,
                                       objective: SparkleObjective,
                                       cutoff: int,
                                       penalised_time: int,
                                       instances: InstanceSet) -> None:
    """Generate a report for a parallel algorithm portfolio.

    Args:
        parallel_portfolio_path: Parallel portfolio path.
        target_path: Where the report data will be placed.
        latex_template: Path to the latex template path used
        bibliograpghy_path: Path to the bib file
        objective: The objective of the portfolio
        cutoff: The cutoff time for each solver
        penalised_time: The penalty for TIMEOUT solvers
        instances: List of instances.
    """
    target_path.mkdir(parents=True, exist_ok=True)
    dict_variable_to_value = parallel_report_variables(
        target_path, parallel_portfolio_path, bibliograpghy_path, objective,
        cutoff, penalised_time, instances)

    sgfs.generate_report(latex_template,
                         "template-Sparkle-for-parallel-portfolio.tex",
                         target_path,
                         "Sparkle_Report_Parallel_Portfolio",
                         dict_variable_to_value)
    sl.add_output(str(target_path), "Sparkle parallel portfolio report")
