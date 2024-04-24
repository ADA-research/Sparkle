#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for parallel portfolio report generation."""
from pathlib import Path

import global_variables as sgh
from sparkle.platform import file_help as sfh
import sparkle_logging as sl
from sparkle.platform import generate_report_help as sgrh
from sparkle.types.objective import PerformanceMeasure


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

        latex_itemize += f"\\item \\textbf{{{sgrh.underscore_for_latex(solver_name)}}}\n"
        # Only include if we used more than one seed
        if solver_seeds > 1:
            seeds = ",".join(list[range(1, solver_seeds + 1)])
            latex_itemize += f"\\item[]With seeds: {seeds}\n"

    return latex_itemize


def get_results() -> dict[str, list[str, str]]:
    """Return a dict with the performance results on each instance.

    Returns:
        A dict consists of a string indicating the instance name, and a list which
        contains the solver name followed by the performance (both as string).
    """
    solutions_dir = sgh.pap_performance_data_tmp_path
    results = sfh.get_list_all_extensions(solutions_dir, "result")
    results_dict = dict()

    if len(results) == 0:
        print(f"WARNING No parallel portfolio in result files found: {solutions_dir}")

    for result_path in results:
        lines = Path(result_path).open("r").readlines()
        lines = [line.strip() for line in lines]

        if len(lines) == 3:
            instance = Path(lines[0]).name

            if instance in results_dict:
                if float(results_dict[instance][1]) > float(lines[2]):
                    results_dict[instance][0] = lines[1]
                    results_dict[instance][1] = lines[2]
            else:
                results_dict[instance] = [lines[1], lines[2]]
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
    latex_itemize = ""
    perf_measure = sgh.settings.get_general_sparkle_objectives()[0].PerformanceMeasure
    # Count the number of solved instances per solver, and the unsolved instances
    if perf_measure == PerformanceMeasure.RUNTIME:
        solver_dict = dict()
        unsolved_instances = 0

        for instances in results_on_instances:
            solver_name = Path(results_on_instances[instances][0]).name
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
    if perf_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION:
        print("*** ERROR: Parallel Portfolio is not available currently for"
              f" performance measure: {perf_measure}")
    elif perf_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION:
        for instance in results_on_instances:
            solver_name = sgrh.underscore_for_latex(
                Path(results_on_instances[instances][0]).name)
            score = results_on_instances[instances][1]
            latex_itemize += (f"\\item \\textbf{{{sgrh.underscore_for_latex(instance)}}}"
                              f", was scored by: \\textbf{{{solver_name}}} with a score "
                              f"of {score}")
    else:
        for solver in solver_dict:
            latex_itemize += \
                f"\\item Solver \\textbf{{{sgrh.underscore_for_latex(solver)}}}, "\
                f"was the best solver on \\textbf{{{solver_dict[solver]}}} instance(s)"
        if unsolved_instances:
            latex_itemize += \
                f"\\item \\textbf{{{unsolved_instances}}} instances(s) remained unsolved"

    return latex_itemize, solver_dict, unsolved_instances


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
        instance_name = Path(instance).name

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
    instance_penalty_dict = {}

    cutoff_time = sgh.settings.get_general_target_cutoff_time()
    results = get_results()
    default_penalty = float(sgh.settings.get_penalised_time())

    for instance in instance_list:
        instance_name = Path(instance).name
        if instance_name in results:
            if float(results[instance_name][1]) <= cutoff_time:
                instance_penalty_dict[instance_name] = float(results[instance_name][1])
            else:
                instance_penalty_dict[instance_name] = default_penalty
        else:
            instance_penalty_dict[instance_name] = default_penalty

    return instance_penalty_dict


def get_figure_parallel_portfolio_sparkle_vs_sbs(
        target_directory: Path,
        parallel_portfolio_path: Path, instances: list[str]) -> tuple[
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
    dict_sbs_penalty_time_on_each_instance, sbs_solver, dict_all_solvers = (
        get_dict_sbs_penalty_time_on_each_instance(parallel_portfolio_path, instances))
    dict_actual_parallel_portfolio_penalty_time_on_each_instance = (
        get_dict_actual_parallel_portfolio_penalty_time_on_each_instance(instances))

    figure_filename = "figure_parallel_portfolio_sparkle_vs_sbs"
    data_filename = "data_parallel_portfolio_sparkle_vs_sbs.dat"
    data_filepath = target_directory / data_filename

    with data_filepath.open("w") as outfile:
        for instance in dict_sbs_penalty_time_on_each_instance:
            sbs_penalty_time = dict_sbs_penalty_time_on_each_instance[instance]
            sparkle_penalty_time = (
                dict_actual_parallel_portfolio_penalty_time_on_each_instance[instance])
            outfile.write(str(sbs_penalty_time) + " " + str(sparkle_penalty_time) + "\n")

    penalised_time_str = str(sgh.settings.get_penalised_time())
    performance_metric_str = sgh.settings.get_performance_metric_for_report()

    generate_figure(target_directory, data_filename, penalised_time_str,
                    f"SBS ({sgrh.underscore_for_latex(sbs_solver)})",
                    "Parallel-Portfolio", figure_filename, performance_metric_str)
    latex_include = f"\\includegraphics[width=0.6\\textwidth]{{{figure_filename}}}"
    return (latex_include, dict_all_solvers,
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
        solver_name = Path(line).name

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


def parallel_report_variables(target_directory: Path,
                              parallel_portfolio_path: Path,
                              instances: list[str]) -> dict[str, str]:
    """Returns a mapping between LaTeX report variables and their values.

    Args:
        target_directory: Path to where to place the generated files.
        parallel_portfolio_path: Parallel portfolio path.
        instances: List of instances.

    Returns:
        A dictionary that maps variables used in the LaTeX report to values.
    """
    variables_dict = {"bibliographypath":
                      str(sgh.sparkle_report_bibliography_path.absolute())}
    solver_list = sfh.get_solver_list_from_parallel_portfolio(parallel_portfolio_path)
    variables_dict["numSolvers"] = str(len(solver_list))
    variables_dict["solverList"] = get_solver_list_latex(solver_list)
    variables_dict["numInstanceClasses"] = str(len(set(
        [Path(instance_path).parent.name for instance_path in instances])))
    variables_dict["cutoffTime"] = str(sgh.settings.get_general_target_cutoff_time())
    variables_dict["performanceMetric"] =\
        sgh.settings.get_performance_metric_for_report()

    variables_dict["instanceClassList"] = sgrh.get_instance_set_count_list(instances)

    inst_succes, solvers_with_solution, unsolved_instances = get_solvers_with_solution()
    variables_dict["solversWithSolution"] = inst_succes

    (figure_name, dict_all_solvers,
        dict_actual_parallel_portfolio_penalty_time_on_each_instance) = (
        get_figure_parallel_portfolio_sparkle_vs_sbs(target_directory,
                                                     parallel_portfolio_path, instances))
    variables_dict["figure-parallel-portfolio-sparkle-vs-sbs"] = figure_name

    variables_dict["resultsTable"] = get_results_table(
        dict_all_solvers, parallel_portfolio_path,
        dict_actual_parallel_portfolio_penalty_time_on_each_instance,
        solvers_with_solution, unsolved_instances, len(instances))

    if (sgh.settings.get_general_sparkle_objectives()[0].PerformanceMeasure
            == PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION):
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
    upper_bound = float(penalty_time) * 1.5
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

    sgrh.generate_gnuplot(output_gnuplot_script, target_directory)
    sgrh.generate_pdf(output_eps_file, target_directory)
    Path(output_gnuplot_script).unlink(missing_ok=True)


def generate_report_parallel_portfolio(parallel_portfolio_path: Path,
                                       instances: list[str]) -> None:
    """Generate a report for a parallel algorithm portfolio.

    Args:
        parallel_portfolio_path: Parallel portfolio path.
        instances: List of instances.
    """
    target_path = sgh.selection_output_analysis
    target_path.mkdir(parents=True, exist_ok=True)
    dict_variable_to_value = parallel_report_variables(
        target_path, parallel_portfolio_path, instances)

    sgrh.generate_report(sgh.sparkle_latex_dir,
                         "template-Sparkle-for-parallel-portfolio.tex",
                         target_path,
                         "Sparkle_Report_Parallel_Portfolio",
                         dict_variable_to_value)
    sl.add_output(str(target_path), "Sparkle parallel portfolio report")
