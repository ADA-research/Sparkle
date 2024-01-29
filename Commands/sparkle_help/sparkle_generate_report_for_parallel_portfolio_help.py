#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for parallel portfolio report generation."""

import subprocess
import sys
from pathlib import Path

from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_file_help as sfh
from Commands.sparkle_help import sparkle_logging as sl
from Commands.sparkle_help import sparkle_generate_report_help as sgrh
from Commands.sparkle_help import sparkle_tex_help as stex
from Commands.sparkle_help.sparkle_settings import PerformanceMeasure


def get_num_solvers(parallel_portfolio_path: Path) -> str:
    """Return the number of solvers as string, counting each solver-seed combination.

    Args:
        parallel_portfolio_path: Path to the parallel portfolio.

    Returns:
        The number of solvers as string.
    """
    solver_list = sfh.get_solver_list_from_parallel_portfolio(parallel_portfolio_path)
    num_solvers = len(solver_list)

    # If a solver contains multiple solver_variations.
    for solver in solver_list:
        if " " in solver:
            num_solvers += int(solver[solver.rfind(" ") + 1:]) - 1

    if num_solvers < 1:
        print("ERROR: No solvers found, report generation failed!")
        sys.exit(-1)

    return str(num_solvers)


def get_solver_list(parallel_portfolio_path: Path) -> str:
    """Return the list of solvers as string, including each solver-seed combination.

    Args:
        parallel_portfolio_path: Path to the parallel portfolio.

    Returns:
        A list of solvers in the parallel portfolio as str.
    """
    str_value = ""
    solver_list = sfh.get_solver_list_from_parallel_portfolio(parallel_portfolio_path)

    for solver_path in solver_list:
        solver_variations = 0

        if " " in solver_path:
            solver_variations = int(solver_path[solver_path.rfind(" ") + 1:])
            solver_path = solver_path[:solver_path.rfind(" ")]

        solver_name = sfh.get_file_name(solver_path)

        if solver_name == "":
            solver_name = sfh.get_last_level_directory_name(solver_path)

        x = solver_name.rfind("_")

        if str(x) != "-1":
            solver_name = solver_name[:x] + "\\" + solver_name[x:]

        str_value += r"\item \textbf{" + f"{sgrh.underscore_for_latex(solver_name)}}}\n"

        if solver_variations > 1:
            seed_number = ""

            for instances in range(1, solver_variations + 1):
                seed_number += str(instances)

                if instances != solver_variations:
                    seed_number += ","

            str_value += r"\item[]" + f"With seeds: {seed_number}\n"

    return str_value


def get_num_instance_sets(instance_list: list[str]) -> str:
    """Return the number of instance sets in the given list as string.

    Args:
        instance_list: list of instance sets

    Returns:
        Number of instance sets in the given list as string
    """
    list_instance_sets = []

    for instance_path in instance_list:
        instance_set = sfh.get_current_directory_name(instance_path)

        if instance_set not in list_instance_sets:
            list_instance_sets.append(instance_set)

    n_sets = len(list_instance_sets)

    if n_sets < 1:
        print("ERROR: No instance sets found, report generation failed!\n"
              "Please execute run_sparkle_parallel_portfolio.py before generating a "
              "parallel portfolio report.")
        sys.exit(-1)

    return str(n_sets)


def get_instance_set_list(instance_list: list[str]) -> tuple[str, int]:
    """Retrieve a list of instance sets in LaTeX format.

    Args:
        instance_list: List of paths to instance sets.

    Returns:
        The instance sets as itemize elements, and the number of instances in the set.
    """
    str_value = ""
    n_instances = 0
    list_instance_sets = []
    dict_n_instances_in_sets = {}

    for instance_path in instance_list:
        instance_set = sfh.get_current_directory_name(instance_path)

        if instance_set not in list_instance_sets:
            list_instance_sets.append(instance_set)
            dict_n_instances_in_sets[instance_set] = 1
        else:
            dict_n_instances_in_sets[instance_set] += 1

    for instance_set in list_instance_sets:
        str_value += (r"\item \textbf{" + sgrh.underscore_for_latex(instance_set)
                      + "}, number of instances: "
                      + str(dict_n_instances_in_sets[instance_set]) + "\n")
        n_instances += dict_n_instances_in_sets[instance_set]

    return str_value, n_instances


def get_results() -> dict[str, list[str, str]]:
    """Return a dict with the performance results on each instance.

    Returns:
        A dict consists of a string indicating the instance name, and a list which
        contains the solver name followed by the performance (both as string).
    """
    solutions_dir = sgh.pap_performance_data_tmp_path
    results = sfh.get_list_all_result_filename(solutions_dir)
    if len(results) == 0:
        print("ERROR: No result files found for parallel portfolio! Stopping execution.")
        print(solutions_dir)
        sys.exit(-1)

    results_dict = dict()

    for result in results:
        result_path = Path(solutions_dir / result)

        with Path(result_path).open("r") as result_file:
            lines = result_file.readlines()

        result_lines = [line.strip() for line in lines]

        if len(result_lines) == 3:
            instance = Path(result_lines[0]).name

            if instance in results_dict:
                if float(results_dict[instance][1]) > float(result_lines[2]):
                    results_dict[instance][0] = result_lines[1]
                    results_dict[instance][1] = result_lines[2]
            else:
                results_dict[instance] = [result_lines[1], result_lines[2]]
    return results_dict


def get_solvers_with_solution() -> tuple[str, dict[str, int], int]:
    """Retrieve the number of solved and unsolved instances per solver.

    Returns:
        A three-tuple:
            str_value: a string with the number of instances solved per successful
                solver.
            solver_dict: a dict with solver name as key, and number of solved instances
                for the corresponding solver as value
            unsolved_instances: number of unsolved instances.
    """
    results_on_instances = get_results()
    str_value = ""

    # Count the number of solved instances per solver, and the unsolved instances
    if sgh.settings.get_general_performance_measure() == PerformanceMeasure.RUNTIME:
        solver_dict = dict()
        unsolved_instances = 0

        for instances in results_on_instances:
            solver_name = sfh.get_file_name(results_on_instances[instances][0])
            cutoff_time = str(sgh.settings.get_penalised_time())

            if results_on_instances[instances][1] != cutoff_time:
                if "_seed_" in solver_name:
                    solver_name = solver_name[:solver_name.rfind("_seed_") + 7]
                if solver_name in solver_dict:
                    solver_dict[solver_name] = solver_dict[solver_name] + 1
                else:
                    solver_dict[solver_name] = 1
            else:
                unsolved_instances += 1
    if (sgh.settings.get_general_performance_measure()
            == PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION):
        print("*** ERROR: Parallel Portfolio is not available currently for"
              f" performance measure: {sgh.settings.get_general_performance_measure()}")
    elif (sgh.settings.get_general_performance_measure()
            == PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION):
        for instances in results_on_instances:
            str_value += (r"\item \textbf{" + sgrh.underscore_for_latex(instances)
                          + "}, was scored by: " + r"\textbf{"
                          + sgrh.underscore_for_latex(sfh.get_last_level_directory_name(
                              results_on_instances[instances][0]))
                          + "} with a score of "
                          + str(results_on_instances[instances][1]))
    else:
        for solver in solver_dict:
            str_value += (r"\item Solver \textbf{" + sgrh.underscore_for_latex(solver)
                          + "}, was the best solver on " + r"\textbf{"
                          + str(solver_dict[solver]) + "} instance(s)")
        if unsolved_instances:
            str_value += (r"\item \textbf{" + str(unsolved_instances)
                          + "} instance(s) remained unsolved")

    return str_value, solver_dict, unsolved_instances


def get_dict_sbs_penalty_time_on_each_instance(
        parallel_portfolio_path: Path,
        instance_list: list[str]) -> tuple[dict[str, float], str, dict[str, float]]:
    """Return the penalised run time for the single best solver and per solver.

    Args:
        parallel_portfolio_path: Path to the parallel portfolio.
        instance_list: List of paths to instance sets.

    Returns:
        A three-tuple:
            A dict containing the run time per instance for the single best solver.
            A string containing the name of the single best solver.
            A second dict containing penalised average run time per solver.
    """
    # Collect full solver list, including solver variants
    solver_list = sfh.get_solver_list_from_parallel_portfolio(parallel_portfolio_path)
    full_solver_list = []

    for lines in solver_list:
        if " " in lines:
            for solver_variations in range(1, int(lines[lines.rfind(" ") + 1:]) + 1):
                solver_path = Path(lines[:lines.rfind(" ")])
                solver_variant_name = solver_path.name

                if "/" in solver_variant_name:
                    solver_variant_name = (
                        solver_variant_name[:solver_variant_name.rfind("/")])

                solver_variant_name = (
                    f"{sgh.sparkle_tmp_path}{solver_variant_name}_seed_"
                    f"{str(solver_variations)}")
                full_solver_list.append(solver_variant_name)
        else:
            full_solver_list.append(lines)

    # Collect penalised average run time (PAR) results for all solvers
    all_solvers_dict = {}
    results = get_results()

    for instance in instance_list:
        instance_name = Path(instance).name
        penalised_time = float(sgh.settings.get_penalised_time())

        if instance_name in results:
            run_time = float(results[instance_name][1])

            if run_time <= sgh.settings.get_general_target_cutoff_time():
                for solver in full_solver_list:
                    # in because the solver name contains the instance name as well,
                    # or the solver can have an additional '/' at the end of the path
                    if (solver in results[instance_name][0]
                            or results[instance_name][0] in solver):
                        if solver in all_solvers_dict:
                            all_solvers_dict[solver] += run_time
                        else:
                            all_solvers_dict[solver] = run_time
                    else:
                        if solver in all_solvers_dict:
                            all_solvers_dict[solver] += penalised_time
                        else:
                            all_solvers_dict[solver] = penalised_time
            else:
                for solver in full_solver_list:
                    if solver in all_solvers_dict:
                        all_solvers_dict[solver] += penalised_time
                    else:
                        all_solvers_dict[solver] = penalised_time
        else:
            for solver in full_solver_list:
                if solver in all_solvers_dict:
                    all_solvers_dict[solver] += penalised_time
                else:
                    all_solvers_dict[solver] = penalised_time

    # Find the single best solver (SBS)
    sbs_name = min(all_solvers_dict, key=all_solvers_dict.get)
    sbs_name = Path(sbs_name).name
    sbs_dict = {}

    for instance in instance_list:
        instance_name = sfh.get_last_level_directory_name(instance)

        if instance_name in results:
            if sbs_name in results[instance_name][0]:
                sbs_dict[instance_name] = results[instance_name][1]
            else:
                sbs_dict[instance_name] = sgh.settings.get_penalised_time()
        else:
            print(f"WARNING: No result found for instance: {instance_name}")

    return sbs_dict, sbs_name, all_solvers_dict


def get_dict_actual_parallel_portfolio_penalty_time_on_each_instance(
        instance_list: list[str]) -> dict[str, float]:
    """Returns the instance names and corresponding penalised running times of the PaP.

    Args:
        instance_list: List of instances.

    Returns:
        A dict of instance names and the penalised running time of the PaP.
    """
    mydict = {}

    cutoff_time = sgh.settings.get_general_target_cutoff_time()
    results = get_results()

    for instance in instance_list:
        instance_name = sfh.get_last_level_directory_name(instance)

        if instance_name in results:
            if float(results[instance_name][1]) <= cutoff_time:
                mydict[instance_name] = float(results[instance_name][1])
            else:
                mydict[instance_name] = float(sgh.settings.get_penalised_time())
        else:
            mydict[instance_name] = float(sgh.settings.get_penalised_time())

    return mydict


def get_figure_parallel_portfolio_sparkle_vs_sbs(
        parallel_portfolio_path: Path, instances: list[str]) -> tuple[
        str, dict[str, float], dict[str, float]]:
    """Generate PaP vs SBS figure and return a string to include it in LaTeX.

    Args:
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
    str_value = ""
    dict_sbs_penalty_time_on_each_instance, sbs_solver, dict_all_solvers = (
        get_dict_sbs_penalty_time_on_each_instance(parallel_portfolio_path, instances))
    dict_actual_parallel_portfolio_penalty_time_on_each_instance = (
        get_dict_actual_parallel_portfolio_penalty_time_on_each_instance(instances))

    latex_directory_path = "Components/Sparkle-latex-generator-for-parallel-portfolio/"
    figure_filename = "figure_parallel_portfolio_sparkle_vs_sbs"
    data_filename = "data_parallel_portfolio_sparkle_vs_sbs.dat"
    data_filepath = latex_directory_path + data_filename

    with Path(data_filepath).open("w+") as outfile:
        for instance in dict_sbs_penalty_time_on_each_instance:
            sbs_penalty_time = dict_sbs_penalty_time_on_each_instance[instance]
            sparkle_penalty_time = (
                dict_actual_parallel_portfolio_penalty_time_on_each_instance[instance])
            outfile.write(str(sbs_penalty_time) + " " + str(sparkle_penalty_time) + "\n")

    penalised_time_str = str(sgh.settings.get_penalised_time())
    performance_metric_str = sgh.settings.get_performance_metric_for_report()

    gnuplot_cmd_list = ["python", "auto_gen_plot.py", data_filename, penalised_time_str,
                        "SBS", sgrh.underscore_for_latex(sbs_solver),
                        "Parallel-Portfolio", figure_filename, performance_metric_str]

    subprocess.run(gnuplot_cmd_list, cwd=latex_directory_path)

    str_value = f"\\includegraphics[width=0.6\\textwidth]{{{figure_filename}}}"

    return (str_value, dict_all_solvers,
            dict_actual_parallel_portfolio_penalty_time_on_each_instance)


def get_results_table(results: dict[str, float], parallel_portfolio_path: Path,
                      dict_portfolio: dict[str, float],
                      solver_with_solutions: dict[str, int],
                      n_unsolved_instances: int, n_instances: int) -> str:
    """Returns a LaTeX table with the portfolio results.

    Args:
        results: A dict containing the penalised average run time per solver.
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
    performance_metric_str = sgh.settings.get_performance_metric_for_report()

    for instance in dict_portfolio:
        portfolio_par += dict_portfolio[instance]

    # Table 1: Portfolio results
    table_string = (
        "\\caption *{\\textbf{Portfolio results}} \\label{tab:portfolio_results} ")
    table_string += "\\begin{tabular}{rrrrr}"
    table_string += (
        "\\textbf{Portfolio nickname} & \\textbf{"
        f"{performance_metric_str}"
        "} & \\textbf{\\#Timeouts} & "
        "\\textbf{\\#Cancelled} & \\textbf{\\#Best solver} \\\\ \\hline ")
    table_string += (
        f"{sgrh.underscore_for_latex(parallel_portfolio_path.name)} & "
        f"{str(round(portfolio_par,2))} & {str(n_unsolved_instances)} & 0 & "
        f"{str(n_instances-n_unsolved_instances)} \\\\ ")
    table_string += "\\end{tabular}"
    table_string += "\\bigskip"
    # Table 2: Solver results
    table_string += "\\caption *{\\textbf{Solver results}} \\label{tab:solver_results} "
    table_string += "\\begin{tabular}{rrrrr}"

    for i, line in enumerate(results):
        solver_name = sfh.get_last_level_directory_name(line)

        if i == 0:
            table_string += (
                "\\textbf{Solver} & \\textbf{"
                f"{performance_metric_str}"
                "} & \\textbf{\\#Timeouts} & "
                "\\textbf{\\#Cancelled} & \\textbf{\\#Best solver} \\\\ \\hline ")

        if solver_name not in solver_with_solutions:
            cancelled = n_instances - n_unsolved_instances
            table_string += (
                f"{sgrh.underscore_for_latex(solver_name)} & "
                f"{str(round(results[line], 2))} & {str(n_unsolved_instances)} & "
                f"{str(cancelled)} & 0 \\\\ ")
        else:
            cancelled = (n_instances - n_unsolved_instances
                         - solver_with_solutions[solver_name])
            table_string += (
                f"{sgrh.underscore_for_latex(solver_name)} & "
                f"{str(round(results[line], 2))} & {str(n_unsolved_instances)} & "
                f"{str(cancelled)} & {str(solver_with_solutions[solver_name])} \\\\ ")
    table_string += "\\end{tabular}"

    return table_string


def get_dict_variable_to_value(parallel_portfolio_path: Path,
                               instances: list[str]) -> dict[str, str]:
    """Returns a mapping between LaTeX report variables and their values.

    Args:
        parallel_portfolio_path: Parallel portfolio path.
        instances: List of instances.

    Returns:
        A dictionary that maps variables used in the LaTeX report to values.
    """
    mydict = {}

    variable = "customCommands"
    str_value = sgrh.get_custom_commands()
    mydict[variable] = str_value

    variable = "sparkle"
    str_value = sgrh.get_sparkle()
    mydict[variable] = str_value

    variable = "numSolvers"
    str_value = get_num_solvers(parallel_portfolio_path)
    mydict[variable] = str_value

    variable = "solverList"
    str_value = get_solver_list(parallel_portfolio_path)
    mydict[variable] = str_value

    variable = "numInstanceClasses"
    str_value = get_num_instance_sets(instances)
    mydict[variable] = str_value

    variable = "instanceClassList"
    str_value, nr_of_instances = get_instance_set_list(instances)
    mydict[variable] = str_value

    variable = "cutoffTime"
    str_value = str(sgh.settings.get_general_target_cutoff_time())
    mydict[variable] = str_value

    variable = "solversWithSolution"
    str_value, solvers_with_solution, unsolved_instances = get_solvers_with_solution()
    mydict[variable] = str_value

    variable = "figure-parallel-portfolio-sparkle-vs-sbs"
    (str_value, dict_all_solvers,
        dict_actual_parallel_portfolio_penalty_time_on_each_instance) = (
        get_figure_parallel_portfolio_sparkle_vs_sbs(parallel_portfolio_path, instances))
    mydict[variable] = str_value

    variable = "resultsTable"
    str_value = get_results_table(
        dict_all_solvers, parallel_portfolio_path,
        dict_actual_parallel_portfolio_penalty_time_on_each_instance,
        solvers_with_solution, unsolved_instances, nr_of_instances)
    mydict[variable] = str_value

    variable = "decisionBool"
    str_value = r"\decisiontrue"

    if (sgh.settings.get_general_performance_measure()
            == PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION):
        str_value = r"\decisionfalse"
    mydict[variable] = str_value

    variable = "performanceMetric"
    str_value = sgh.settings.get_performance_metric_for_report()
    mydict[variable] = str_value

    return mydict


def generate_report(parallel_portfolio_path: Path, instances: list[str]) -> None:
    """Generate a report for a parallel algorithm portfolio.

    Args:
        parallel_portfolio_path: Parallel portfolio path.
        instances: List of instances.
    """
    latex_report_filename = Path("Sparkle_Report")
    dict_variable_to_value = get_dict_variable_to_value(parallel_portfolio_path,
                                                        instances)

    latex_directory_path = Path(
        "Components/Sparkle-latex-generator-for-parallel-portfolio/")
    latex_template_filename = Path("template-Sparkle.tex")
    latex_template_filepath = Path(latex_directory_path / latex_template_filename)
    report_content = ""

    with Path(latex_template_filepath).open("r") as infile:
        for line in infile:
            report_content += line

    for variable_key, str_value in dict_variable_to_value.items():
        variable = "@@" + variable_key + "@@"
        report_content = report_content.replace(variable, str_value)

    latex_report_filepath = Path(latex_directory_path / latex_report_filename)
    latex_report_filepath = latex_report_filepath.with_suffix(".tex")

    with Path(latex_report_filepath).open("w+") as outfile:
        for line in report_content:
            outfile.write(line)

    stex.check_tex_commands_exist(latex_directory_path)

    report_path = stex.compile_pdf(latex_directory_path, latex_report_filename)

    print(f"Report is placed at: {report_path}")
    sl.add_output(str(report_path), "Sparkle parallel portfolio report")
