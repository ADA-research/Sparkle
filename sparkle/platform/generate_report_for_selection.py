#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for selection report generation."""
import sys
from pathlib import Path
from collections import Counter

from sparkle.CLI.compute_marginal_contribution\
    import compute_selector_marginal_contribution

from sparkle.platform import latex as stex
from sparkle.structures import PerformanceDataFrame, FeatureDataFrame
from sparkle.types.objective import SparkleObjective


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
    instance_list = [Path(instance_path).parent.name for instance_path in instance_list]
    count = Counter(instance_list)
    rows = [(inst_key, f", constisting of {count[inst_key]} instances")
            for inst_key in count]
    return stex.list_to_latex(rows)


def solver_ranked_latex_list(solver_ranking: list[tuple[str, float]],
                             objective: SparkleObjective = None) -> str:
    """Convert a list of the solvers ranked by performance to LaTeX.

    Returns:
        The list of solvers ranked as LaTeX str.
    """
    objective_str = f"{objective}: " if objective is not None else ""
    return stex.list_to_latex([(row[0], f", {objective_str} {row[1]}")
                               for row in solver_ranking])


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
        sbs_solver: str) -> str:
    """Create a LaTeX plot comparing the selector and the SBS.

    The plot compares the performance on each instance of the portfolio selector created
    by Sparkle and the SBS (single best solver).

    Returns:
        LaTeX str to include the comparison plot in a LaTeX report.
    """
    # We create a point of x,y form (SBS performance, portfolio performance)
    selector = portfolio_selector_performance.solvers[0]
    points = [[float(train_data.get_value(sbs_solver, instance, objective.name)),
               float(portfolio_selector_performance.get_value(selector,
                                                              instance,
                                                              objective.name))]
              for instance in portfolio_selector_performance.instances]

    figure_filename = "figure_portfolio_selector_sparkle_vs_sbs"
    sbs_solver_name = Path(sbs_solver).name

    stex.generate_comparison_plot(points,
                                  figure_filename,
                                  xlabel=f"SBS ({sbs_solver_name}) [{objective}]",
                                  ylabel=f"Sparkle Selector [{objective}]",
                                  limit="magnitude",
                                  limit_min=0.25,
                                  limit_max=0.25,
                                  replace_zeros=True,
                                  output_dir=output_dir)
    return f"\\includegraphics[width=0.6\\textwidth]{{{figure_filename}}}"


def get_figure_portfolio_selector_sparkle_vs_vbs(
        output_dir: Path,
        objective: SparkleObjective,
        train_data: PerformanceDataFrame,
        actual_portfolio_selector_penalty: PerformanceDataFrame) -> str:
    """Create a LaTeX plot comparing the selector and the VBS.

    The plot compares the performance on each instance of the portfolio selector created
    by Sparkle and the VBS (virtual best solver).

    Returns:
        LaTeX str to include the comparison plot in a LaTeX report.
    """
    vbs_performance = train_data.best_instance_performance(objective=objective.name)
    instances = actual_portfolio_selector_penalty.instances
    solver = actual_portfolio_selector_penalty.solvers[0]
    points = [(vbs_performance[instance],
               actual_portfolio_selector_penalty.get_value(solver,
                                                           instance,
                                                           objective.name))
              for instance in instances]

    figure_filename = "figure_portfolio_selector_sparkle_vs_vbs"

    stex.generate_comparison_plot(points,
                                  figure_filename,
                                  xlabel=f"VBS [{objective}]",
                                  ylabel=f"Sparkle Selector [{objective.name}]",
                                  limit="magnitude",
                                  limit_min=0.25,
                                  limit_max=0.25,
                                  replace_zeros=True,
                                  output_dir=output_dir)
    return f"\\includegraphics[width=0.6\\textwidth]{{{figure_filename}}}"


def selection_report_variables(
        target_dir: Path,
        bibliograpghy_path: Path,
        extractor_path: Path,
        selection_scenario: Path,
        performance_data: PerformanceDataFrame,
        feature_data: FeatureDataFrame,
        objective: SparkleObjective,
        extractor_cutoff: int,
        cutoff: int,
        test_case_data: PerformanceDataFrame = None) -> dict[str, str]:
    """Returns: a dict matching variables in the LaTeX template with their values.

    Args:
        target_dir: Output path
        bibliography_path: Path to the bib file
        test_case_directory: Path to the test case directory.

    Returns:
        A dict matching str variables in the LaTeX template with their value str.
    """
    actual_performance_data = get_portfolio_selector_performance(selection_scenario)
    solver_performance_ranking = performance_data.get_solver_ranking(
        objective=objective)
    single_best_solver = solver_performance_ranking[0][0]
    latex_dict = {"bibliographypath": bibliograpghy_path.absolute(),
                  "numSolvers": performance_data.num_solvers,
                  "solverList": stex.list_to_latex([(s, "")
                                                    for s in performance_data.solvers])}
    latex_dict["numFeatureExtractors"] = len(
        [p for p in extractor_path.iterdir() if p.is_dir()])
    stex.list_to_latex([(f, "") for f in extractor_path.iterdir()])
    latex_dict["featureExtractorList"] = stex.list_to_latex(
        [(f, "") for f in extractor_path.iterdir()])
    latex_dict["numInstanceClasses"] = get_num_instance_sets(performance_data.instances)
    latex_dict["instanceClassList"] =\
        get_instance_set_count_list(performance_data.instances)
    latex_dict["featureComputationCutoffTime"] = extractor_cutoff
    latex_dict["performanceComputationCutoffTime"] = cutoff
    rank_list_perfect = performance_data.marginal_contribution(objective, sort=True)
    rank_list_actual = compute_selector_marginal_contribution(performance_data,
                                                              feature_data,
                                                              selection_scenario,
                                                              objective)
    latex_dict["solverPerfectRankingList"] = solver_ranked_latex_list(rank_list_perfect)
    latex_dict["solverActualRankingList"] = solver_ranked_latex_list(rank_list_actual)
    latex_dict["PARRankingList"] = solver_ranked_latex_list(solver_performance_ranking,
                                                            objective)
    latex_dict["VBSPAR"] = objective.instance_aggregator(
        performance_data.best_instance_performance(objective=objective.name))
    latex_dict["actualPAR"] = actual_performance_data.mean(objective=objective.name)
    latex_dict["metric"] = objective.name
    latex_dict["figure-portfolio-selector-sparkle-vs-sbs"] =\
        get_figure_portfolio_selector_vs_sbs(
            target_dir, objective, performance_data,
            actual_performance_data, single_best_solver)
    latex_dict["figure-portfolio-selector-sparkle-vs-vbs"] =\
        get_figure_portfolio_selector_sparkle_vs_vbs(target_dir,
                                                     objective,
                                                     performance_data,
                                                     actual_performance_data)
    latex_dict["testBool"] = r"\testfalse"

    # Train and test
    if test_case_data is not None:
        latex_dict["testInstanceClass"] =\
            f"\\textbf{ {test_case_data.csv_filepath.parent.name} }"
        latex_dict["numInstanceInTestInstanceClass"] =\
            test_case_data.num_instances
        latex_dict["testActualPAR"] = test_case_data.mean(objective=objective.name)
        latex_dict["testBool"] = r"\testtrue"

    return latex_dict


def generate_report_selection(target_path: Path,
                              latex_dir: Path,
                              latex_template: Path,
                              bibliography_path: Path,
                              extractor_path: Path,
                              selection_scenario: Path,
                              feature_data: FeatureDataFrame,
                              train_data: PerformanceDataFrame,
                              objective: SparkleObjective,
                              extractor_cutoff: int,
                              cutoff: int,
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
        objective: The objective for the selector
        extractor_cutoff: The maximum time for the selector to run
        cutoff: The cutoff per solver
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
                                                        objective,
                                                        extractor_cutoff,
                                                        cutoff,
                                                        test_case_data)
    stex.generate_report(latex_dir,
                         latex_template,
                         target_path,
                         latex_report_filename,
                         dict_variable_to_value)
