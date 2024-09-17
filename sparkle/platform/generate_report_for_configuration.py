#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for algorithm configuration report generation."""
from __future__ import annotations

import sys
from pathlib import Path

from sparkle.platform import latex as stex
from sparkle.solver.ablation import AblationScenario
from sparkle.solver.validator import Validator
from sparkle.configurator.configurator import Configurator, ConfigurationScenario
from sparkle.solver import Solver
from sparkle.instance import InstanceSet
from sparkle.configurator.implementations import SMAC2
from sparkle.types import SparkleObjective
from sparkle import about


def get_features_bool(configurator_scenario: ConfigurationScenario,
                      solver_name: str, train_set: InstanceSet) -> str:
    """Return a bool string for latex indicating whether features were used.

    True if a feature file is given in the scenario file, false otherwise.

    Args:
        solver_name: Name of the solver
        instance_set_train_name: Name of the instance set used for training

    Returns:
        A string describing whether features are used
    """
    scenario_file = configurator_scenario.directory \
        / f"{solver_name}_{train_set.name}_scenario.txt"

    for line in scenario_file.open("r").readlines():
        if line.split(" ")[0] == "feature_file":
            return "\\featurestrue"
    return "\\featuresfalse"


def get_average_performance(results: list[list[str]],
                            objective: SparkleObjective) -> float:
    """Return the PAR score for a given results file and cutoff time.

    Args:
        results_file: Name of the result file
        objective: The objective to average

    Returns:
        Average performance value
    """
    instance_per_dict = get_dict_instance_to_performance(results,
                                                         objective)
    num_instances = len(instance_per_dict.keys())
    sum_par = sum(float(instance_per_dict[instance]) for instance in instance_per_dict)
    return float(sum_par / num_instances)


def get_dict_instance_to_performance(results: list[list[str]],
                                     objective: SparkleObjective) -> dict[str, float]:
    """Return a dictionary of instance names and their performance.

    Args:
        results: Results from CSV
        objective: The Sparkle Objective we are converting for
    Returns:
        A dictionary containing the performance for each instance
    """
    value_column = results[0].index(objective.name)
    results_per_instance = {}
    for row in results[1:]:
        value = float(row[value_column])
        results_per_instance[Path(row[3]).name] = value
    return results_per_instance


def get_ablation_bool(scenario: AblationScenario) -> str:
    """Return the ablation bool as LaTeX string.

    Args:
        solver: The solver object
        instance_train_name: Name of the trianing instance set
        instance_test_name: Name of the testing instance set

    Returns:
        A string describing whether ablation was run or not
    """
    if scenario.check_for_ablation():
        return "\\ablationtrue"
    return "\\ablationfalse"


def get_data_for_plot(configured_results: list[list[str]],
                      default_results: list[list[str]],
                      objective: SparkleObjective) -> list:
    """Return the required data to plot.

    Creates a nested list of performance values algorithm runs with default and
    configured parameters on instances in a given instance set.

    Args:
        configured_results_dir: Directory of results for configured solver
        default_results_dir: Directory of results for default solver
        run_cutoff_time: Cutoff time

    Returns:
        A list of lists containing data points
    """
    dict_instance_to_par_default = get_dict_instance_to_performance(
        default_results, objective)
    dict_instance_to_par_configured = get_dict_instance_to_performance(
        configured_results, objective)

    instances = (dict_instance_to_par_default.keys()
                 & dict_instance_to_par_configured.keys())
    if (len(dict_instance_to_par_default) != len(instances)):
        print("""ERROR: Number of instances does not match
         the number of performance values for the default configuration.""")
        sys.exit(-1)
    points = []
    for instance in instances:
        point = [dict_instance_to_par_default[instance],
                 dict_instance_to_par_configured[instance]]
        points.append(point)

    return points


def get_figure_configure_vs_default(configured_results: list[list[str]],
                                    default_results: list[list[str]],
                                    target_directory: Path,
                                    figure_filename: str,
                                    performance_measure: str,
                                    run_cutoff_time: float,
                                    objective: SparkleObjective) -> str:
    """Create a figure comparing the configured and default solver.

    Base function to create a comparison plot of a given instance set between the default
    and configured performance.

    Args:
        configured_results_dir: Directory of results for configured solver
        default_results_dir: Directory of results for default solver
        target_directory: Directory for the configuration reports
        figure_filename: Filename for the figure
        run_cutoff_time: Cutoff time

    Returns:
        A string containing the latex command to include the figure
    """
    points = get_data_for_plot(configured_results, default_results,
                               objective)

    plot_params = {"xlabel": f"Default parameters [{performance_measure}]",
                   "ylabel": f"Configured parameters [{performance_measure}]",
                   "scale": "linear",
                   "limit_min": 1.5,
                   "limit_max": 1.5,
                   "limit": "relative",
                   "replace_zeros": False,
                   "output_dir": target_directory
                   }
    if performance_measure[0:3] == "PAR":
        plot_params["scale"] = "log"
        plot_params["limit_min"] = 0.25
        plot_params["limit_max"] = 0.25
        plot_params["limit"] = "magnitude"
        plot_params["replace_zeros"] = True

    stex.generate_comparison_plot(points,
                                  figure_filename,
                                  **plot_params)

    return f"\\includegraphics[width=0.6\\textwidth]{{{figure_filename}}}"


def get_figure_configured_vs_default_on_instance_set(solver: Solver,
                                                     instance_set_name: str,
                                                     res_default: list[list[str]],
                                                     res_conf: list[list[str]],
                                                     target_directory: Path,
                                                     smac_objective: str,
                                                     run_cutoff_time: float,
                                                     objective: SparkleObjective,
                                                     data_type: str = "train") -> str:
    """Create a figure comparing the configured and default solver on the training set.

    Manages the creation of a comparison plot of the instances in the train instance set
    for the report by gathering the proper files and choosing the plotting parameters
    based on the performance measure.

    Args:
        solver: The solver object
        instance_set_train_name: Name of the instance set for training
        configuration_reports_directory: Directory to the configuration reports
        run_cutoff_time: Cutoff time

    Returns:
        A string containing the latex comand to include the figure
    """
    data_plot_configured_vs_default_on_instance_set_filename = (
        f"data_{solver.name}_configured_vs_default_on_{instance_set_name}_{data_type}")
    return get_figure_configure_vs_default(
        res_conf, res_default, target_directory,
        data_plot_configured_vs_default_on_instance_set_filename,
        smac_objective,
        run_cutoff_time,
        objective)


def get_timeouts_instanceset(solver: Solver,
                             instance_set: InstanceSet,
                             configurator: Configurator,
                             validator: Validator,
                             cutoff: float) -> tuple[int, int, int]:
    """Return the number of timeouts by configured, default and both on the testing set.

    Args:
        solver: The solver object
        instance_set: Instance Set
        configurator: Configurator
        validator: Validator
        cutoff: Cutoff time

    Returns:
        A tuple containing the number of timeouts for the different configurations
    """
    objective = configurator.scenario.sparkle_objective
    _, config = configurator.get_optimal_configuration(
        solver, instance_set, objective)
    res_default = validator.get_validation_results(solver,
                                                   instance_set,
                                                   config="")
    res_conf = validator.get_validation_results(solver,
                                                instance_set,
                                                config=config)
    dict_instance_to_par_configured = get_dict_instance_to_performance(
        res_conf, objective)
    dict_instance_to_par_default = get_dict_instance_to_performance(
        res_default, objective)

    return get_timeouts(dict_instance_to_par_configured,
                        dict_instance_to_par_default, cutoff)


def get_timeouts(instance_to_par_configured: dict,
                 instance_to_par_default: dict,
                 cutoff: float) -> tuple[int, int, int]:
    """Return the number of timeouts for given dicts.

    Args:
        dict_instance_to_par_configured: _description_
        dict_instance_to_par_default: _description_
        cutoff: Cutoff value

    Returns:
        A tuple containing timeout values
    """
    configured_timeouts = 0
    default_timeouts = 0
    overlapping_timeouts = 0

    for instance in instance_to_par_configured:
        configured_par = instance_to_par_configured[instance]
        default_par = instance_to_par_default[instance]
        # Count the amount of values that are equal to timeout
        configured_timeouts += (configured_par > cutoff)
        default_timeouts += (default_par > cutoff)
        overlapping_timeouts += (configured_par > cutoff
                                 and default_par > cutoff)

    return configured_timeouts, default_timeouts, overlapping_timeouts


def get_ablation_table(scenario: AblationScenario) -> str:
    """Generate a LaTeX table of the ablation path.

    This is the result of the ablation analysis to determine the parameter importance.

    Args:
        solver: The solver object
        instance_set_train_name: Name of the instance set for training
        instance_set_test_name: Name of the instance set for testing

    Returns:
        A string containing the LaTeX table code of the ablation path
    """
    results = scenario.read_ablation_table()
    table_string = r"\begin{tabular}{rp{0.25\linewidth}rrr}"
    # "Round", "Flipped parameter", "Source value", "Target value", "Validation result"
    for i, line in enumerate(results):
        # If this fails something has changed in the representation of ablation tables
        if len(line) != 5:
            print("""ERROR: something has changed with the representation
                   of ablation tables""")
            sys.exit(-1)
        if i == 0:
            line = [f"\\textbf{{{word}}}" for word in line]

        # Put multiple variable changes in one round on a seperate line
        if (len(line[1].split(",")) > 1
           and len(line[1].split(",")) == len(line[2].split(","))
           and len(line[1].split(",")) == len(line[3].split(","))):
            params = line[1].split(",")
            default_values = line[2].split(",")
            flipped_values = line[3].split(",")

            sublines = len(params)
            for subline in range(sublines):
                round = "" if subline != 0 else line[0]
                result = "" if subline + 1 != sublines else line[-1]
                printline = [round, params[subline], default_values[subline],
                             flipped_values[subline], result]
                table_string += " & ".join(printline) + " \\\\ "
        else:
            table_string += " & ".join(line) + " \\\\ "
        if i == 0:
            table_string += "\\hline "
    table_string += "\\end{tabular}"

    return table_string


def configuration_report_variables(target_dir: Path,
                                   solver: Solver,
                                   configurator: Configurator,
                                   validator: Validator,
                                   extractor_dir: Path,
                                   bib_path: Path,
                                   instance_set_train: InstanceSet,
                                   extractor_cuttoff: int,
                                   instance_set_test: InstanceSet = None,
                                   ablation: AblationScenario = None) -> dict:
    """Return a dict matching LaTeX variables and their values.

    Args:
        solver: Object representation of the Solver
        instance_set_train: Path of the instance set for training
        instance_set_test: Path of the instance set for testing. Defaults to None.
        ablation: Whether or not ablation is used. Defaults to True.

    Returns:
        A dictionary containing the variables and values
    """
    has_test = instance_set_test is not None

    full_dict = get_dict_variable_to_value_common(solver,
                                                  configurator,
                                                  validator,
                                                  ablation,
                                                  bib_path,
                                                  instance_set_train,
                                                  target_dir)

    if has_test:
        test_dict = get_dict_variable_to_value_test(target_dir,
                                                    solver,
                                                    configurator,
                                                    validator,
                                                    ablation,
                                                    instance_set_train,
                                                    instance_set_test)
        full_dict.update(test_dict)
    full_dict["testBool"] = f"\\test{str(has_test).lower()}"

    if ablation is None:
        full_dict["ablationBool"] = "\\ablationfalse"

    if full_dict["featuresBool"] == "\\featurestrue":
        full_dict["numFeatureExtractors"] =\
            len([p for p in extractor_dir.iterdir()])
        full_dict["featureExtractorList"] =\
            stex.list_to_latex([(p.name, "") for p in extractor_dir.iterdir()])
        full_dict["featureComputationCutoffTime"] = extractor_cuttoff

    return full_dict


def get_dict_variable_to_value_common(solver: Solver,
                                      configurator: Configurator,
                                      validator: Validator,
                                      ablation: AblationScenario,
                                      bibliography_path: Path,
                                      train_set: InstanceSet,
                                      target_directory: Path) -> dict:
    """Return a dict matching LaTeX variables and values used for all config. reports.

    Args:
        Solver: The solver object
        instance_set_train: Path of the instance set for training
        instance_set_test: Path of the instance set for testing
        target_directory: Path to directory with configuration reports

    Returns:
        A dictionary containing the variables and values
    """
    objective = configurator.scenario.sparkle_objective
    _, opt_config = configurator.get_optimal_configuration(
        solver, train_set, objective)
    res_default = validator.get_validation_results(
        solver, train_set, config="")
    res_conf = validator.get_validation_results(
        solver, train_set, config=opt_config)
    instance_names = set([res[3] for res in res_default])

    latex_dict = {"bibliographypath": bibliography_path.absolute()}
    latex_dict["performanceMeasure"] = objective.name
    smac_run_obj = SMAC2.get_smac_run_obj(objective)

    if smac_run_obj == "RUNTIME":
        latex_dict["runtimeBool"] = "\\runtimetrue"
    elif smac_run_obj == "QUALITY":
        latex_dict["runtimeBool"] = "\\runtimefalse"

    latex_dict["solver"] = solver.name
    latex_dict["instanceSetTrain"] = train_set.name
    latex_dict["sparkleVersion"] = about.version
    latex_dict["numInstanceInTrainingInstanceSet"] = len(instance_names)

    run_cutoff_time = configurator.scenario.cutoff_time
    latex_dict["numSmacRuns"] = configurator.scenario.number_of_runs
    latex_dict["smacObjective"] = smac_run_obj
    latex_dict["smacWholeTimeBudget"] = configurator.scenario.wallclock_time
    latex_dict["smacEachRunCutoffTime"] = run_cutoff_time
    latex_dict["optimisedConfiguration"] = opt_config
    latex_dict["optimisedConfigurationTrainingPerformancePAR"] =\
        get_average_performance(res_conf, objective)
    latex_dict["defaultConfigurationTrainingPerformancePAR"] =\
        get_average_performance(res_default, objective)

    str_value = get_figure_configured_vs_default_on_instance_set(
        solver, train_set.name, res_default, res_conf, target_directory,
        smac_run_obj, float(run_cutoff_time), objective)
    latex_dict["figure-configured-vs-default-train"] = str_value

    # Retrieve timeout numbers for the training instances
    configured_timeouts_train, default_timeouts_train, overlapping_timeouts_train =\
        get_timeouts_instanceset(solver, train_set, configurator, validator,
                                 run_cutoff_time)

    latex_dict["timeoutsTrainDefault"] = default_timeouts_train
    latex_dict["timeoutsTrainConfigured"] = configured_timeouts_train
    latex_dict["timeoutsTrainOverlap"] = overlapping_timeouts_train
    latex_dict["ablationBool"] = get_ablation_bool(ablation)
    latex_dict["ablationPath"] = get_ablation_table(ablation)
    latex_dict["featuresBool"] = get_features_bool(
        configurator.scenario, solver.name, train_set)

    return latex_dict


def get_dict_variable_to_value_test(target_dir: Path,
                                    solver: Solver,
                                    configurator: Configurator,
                                    validator: Validator,
                                    ablation: AblationScenario,
                                    train_set: InstanceSet,
                                    test_set: InstanceSet) -> dict:
    """Return a dict matching test set specific latex variables with their values.

    Args:
        target_dir: Path to where output should go
        solver: The solver object
        configurator: Configurator for which the report is generated
        validator: Validator that provided the data set results
        train_set: Instance set for training
        test_set: Instance set for testing

    Returns:
        A dictionary containting the variables and their values
    """
    _, config = configurator.get_optimal_configuration(
        solver, train_set, configurator.scenario.sparkle_objective)
    res_default = validator.get_validation_results(
        solver, test_set, config="")
    res_conf = validator.get_validation_results(
        solver, test_set, config=config)
    instance_names = set([res[3] for res in res_default])
    run_cutoff_time = configurator.scenario.cutoff_time
    objective = configurator.scenario.sparkle_objective
    test_dict = {"instanceSetTest": test_set.name}
    test_dict["numInstanceInTestingInstanceSet"] = len(instance_names)
    test_dict["optimisedConfigurationTestingPerformancePAR"] =\
        get_average_performance(res_conf, objective)
    test_dict["defaultConfigurationTestingPerformancePAR"] =\
        get_average_performance(res_default, objective)
    smac_run_obj = SMAC2.get_smac_run_obj(
        configurator.scenario.sparkle_objective)
    test_dict["figure-configured-vs-default-test"] =\
        get_figure_configured_vs_default_on_instance_set(
        solver, test_set.name, res_default, res_conf, target_dir, smac_run_obj,
        float(run_cutoff_time),
        configurator.scenario.sparkle_objective, data_type="test")

    # Retrieve timeout numbers for the testing instances
    configured_timeouts_test, default_timeouts_test, overlapping_timeouts_test =\
        get_timeouts_instanceset(solver,
                                 test_set,
                                 configurator,
                                 validator,
                                 run_cutoff_time)

    test_dict["timeoutsTestDefault"] = default_timeouts_test
    test_dict["timeoutsTestConfigured"] = configured_timeouts_test
    test_dict["timeoutsTestOverlap"] = overlapping_timeouts_test
    test_dict["ablationBool"] = get_ablation_bool(ablation)
    test_dict["ablationPath"] = get_ablation_table(ablation)
    return test_dict


def generate_report_for_configuration(solver: Solver,
                                      configurator: Configurator,
                                      validator: Validator,
                                      extractor_dir: Path,
                                      target_path: Path,
                                      latex_template_path: Path,
                                      bibliography_path: Path,
                                      train_set: InstanceSet,
                                      extractor_cuttoff: int,
                                      test_set: InstanceSet = None,
                                      ablation: AblationScenario = None) -> None:
    """Generate a report for algorithm configuration.

    Args:
        solver: Object representation of the solver
        configurator: Configurator for the report
        validator: Validator that validated the configurator
        extractor_dir: Path to the extractor used
        target_path: Where the report files will be placed.
        latex_template_path: Path to the template to use for the report
        bibliography_path: The bib corresponding to the latex template
        train_set: Instance set for training
        extractor_cuttoff: Cut off for extractor
        test_set: Instance set for testing
        ablation: Whether or not ablation is used. Defaults to True.
    """
    target_path.mkdir(parents=True, exist_ok=True)
    variables_dict = configuration_report_variables(
        target_path, solver, configurator, validator, extractor_dir, bibliography_path,
        train_set, extractor_cuttoff, test_set,
        ablation)
    stex.generate_report(latex_template_path,
                         "template-Sparkle-for-configuration.tex",
                         target_path,
                         "Sparkle_Report_for_Configuration",
                         variables_dict)
