#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for algorithm configuration report generation."""
from __future__ import annotations

import sys
from pathlib import Path

from scipy.stats import linregress

from sparkle.platform import latex as stex
from sparkle.configurator.ablation import AblationScenario
from sparkle.configurator.configurator import ConfigurationScenario
from sparkle.instance import InstanceSet
from sparkle.structures import PerformanceDataFrame
from sparkle.types import SolverStatus
from sparkle import about

from sparkle.platform.output.configuration_output import ConfigurationOutput


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


def plot_configured_vs_default(
        config_output: ConfigurationOutput,
        config_scenario: ConfigurationScenario,
        target_directory: Path,
        test_mode: bool = False,) -> str:
    """Create a figure comparing the configured and default solver.

    Base function to create a comparison plot of a given instance set between the default
    and configured performance.

    Args:
        config_output: Object representation of the ConfigurationOutput
        config_scenario: ConfigurationScenario
        target_directory: Directory for the configuration reports
        instance_set: InstanceSet to plot

    Returns:
        A string containing the latex command to include the figure
    """
    instance_set_name = (config_output.instance_set_train.name
                         if not test_mode else config_output.instance_set_test.name)
    figure_filename =\
        f"data_{config_output.solver.name}_configured_vs_default_on_{instance_set_name}"
    if not test_mode:
        points = [p for p in zip(config_output.default_performance_per_instance_train,
                  config_output.best_conf_performance_per_instance_train)]
    else:
        points = [p for p in zip(config_output.default_performance_per_instance_train,
                  config_output.best_conf_performance_per_instance_test)]
    objective_name = config_scenario.sparkle_objective.name
    plot_params = {"xlabel": f"Default parameters [{objective_name}]",
                   "ylabel": f"Configured parameters [{objective_name}]",
                   "scale": "linear",
                   "limit_min": 1.5,
                   "limit_max": 1.5,
                   "replace_zeros": False,
                   "output_dir": target_directory
                   }
    # Check if the scale of the axis can be considered linear
    x_points = [p[0] for p in points]
    y_points = [p[1] for p in points]
    if not len(set(x_points)) == 1 and not len(set(y_points)) == 1:
        linearity_x = linregress(x_points, range(len(points))).rvalue > 0.5
        linearity_y = linregress(y_points, range(len(points))).rvalue > 0.5
        if not linearity_x or not linearity_y:
            plot_params["scale"] = "log"
            plot_params["replace_zeros"] = True

    stex.generate_comparison_plot(points,
                                  figure_filename,
                                  **plot_params)

    return f"\\includegraphics[width=0.6\\textwidth]{{{figure_filename}}}"


def get_timeouts_instanceset(config_output: ConfigurationOutput,
                             instance_set: InstanceSet) -> tuple[int, int, int]:
    """Return the number of timeouts by configured, default and both on the instance set.

    Args:
        configuration_scenario: ConfigurationScenario
        config_output: ConfigurationOutput

    Returns:
        A tuple containing the number of timeouts for the different configurations
    """
    solver_key = str(config_output.solver.directory)
    instance_keys = [str(instance) for instance in instance_set.instance_paths]
    # Determine status objective name
    objective = [o for o in config_output.performance_data.objectives
                 if o.stem.lower() == "status"][0]
    _, configured_status = config_output.performance_data.configuration_performance(
        solver_key,
        configuration=config_output.best_configuration,
        objective=objective,
        instances=instance_keys,
        per_instance=True)
    _, default_status = config_output.performance_data.configuration_performance(
        solver_key,
        configuration=PerformanceDataFrame.missing_value,
        objective=objective,
        instances=instance_keys,
        per_instance=True)

    default_timeouts, configured_timeouts, shared = 0, 0, 0
    for configured_status, default_status in zip(configured_status, default_status):
        configured_status, default_status =\
            SolverStatus(configured_status), SolverStatus(default_status)
        if configured_status == SolverStatus.TIMEOUT:
            configured_timeouts += 1
        if default_status == SolverStatus.TIMEOUT:
            default_timeouts += 1
        if (configured_status == SolverStatus.TIMEOUT
                and default_status == SolverStatus.TIMEOUT):
            shared += 1
    return configured_timeouts, default_timeouts, shared


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


def configuration_report_variables(config_scenario: ConfigurationScenario,
                                   config_output: ConfigurationOutput,
                                   target_dir: Path,
                                   bib_path: Path,
                                   extractor_dir: Path,
                                   extractor_cutoff: int,
                                   ablation: AblationScenario = None) -> dict:
    """Return a dict matching LaTeX variables and their values.

    Args:
        config_scenario: Object representation of the ConfigurationScenario
        config_output: Object representation of the ConfigurationOutput
        target_dir: Target directory
        bib_path: Path to the latex bib file.
        extractor_dir: General platform extractor Directory
        extractactor_cutoff: Extractor cut off time.
        ablation: Whether or not ablation is used. Defaults to True.

    Returns:
        A dictionary containing the variables and values
    """
    has_test = config_output.instance_set_test is not None
    full_dict = {"bibliographypath": bib_path.absolute(),
                 "sparkleVersion": about.version}

    full_dict.update(get_dict_variable_to_value_common(config_scenario,
                                                       config_output,
                                                       ablation,
                                                       target_dir))

    if has_test:
        test_dict = get_dict_variable_to_value_test(config_output,
                                                    config_scenario,
                                                    target_dir,
                                                    ablation)
        full_dict.update(test_dict)
    full_dict["testBool"] = f"\\test{str(has_test).lower()}"

    if ablation is None:
        full_dict["ablationBool"] = "\\ablationfalse"

    if full_dict["featuresBool"] == "\\featurestrue":
        full_dict["numFeatureExtractors"] =\
            len([p for p in extractor_dir.iterdir()])
        full_dict["featureExtractorList"] =\
            stex.list_to_latex([(p.name, "") for p in extractor_dir.iterdir()])
        full_dict["featureComputationCutoffTime"] = extractor_cutoff

    return full_dict


def get_dict_variable_to_value_common(config_scenario: ConfigurationScenario,
                                      config_output: ConfigurationOutput,
                                      ablation: AblationScenario,
                                      target_directory: Path) -> dict:
    """Return a dict matching LaTeX variables and values used for all config. reports.

    Args:
        config_scenario: Configuration scenario
        config_output: configuration output
        ablation: Ablation scenario, if ran
        target_directory: Path to directory with configuration reports

    Returns:
        A dictionary containing the variables and values
    """
    objective = config_scenario.sparkle_objective

    latex_dict = {"objectiveName": objective.name,
                  "configuratorName": config_output.configurator.name,
                  "configuratorVersion": config_output.configurator.version,
                  "configuratorFullName": config_output.configurator.full_name}

    if objective.time:
        latex_dict["runtimeBool"] = "\\runtimetrue"
        latex_dict["objectiveType"] = "RUNTIME"
    else:
        latex_dict["runtimeBool"] = "\\runtimefalse"
        latex_dict["objectiveType"] = "QUALITY"
    if objective.minimise:
        latex_dict["minMaxAdjective"] = "lowest"
    else:
        latex_dict["minMaxAdjective"] = "highest"

    latex_dict["solver"] = config_output.solver.name
    latex_dict["instanceSetTrain"] = config_scenario.instance_set.name
    latex_dict["numInstanceInTrainingInstanceSet"] = config_scenario.instance_set.size

    latex_dict["numConfiguratorRuns"] = config_scenario.number_of_runs
    if hasattr(config_scenario, "tuner_timeout"):  # ParamILS
        latex_dict["wholeTimeBudget"] = config_scenario.tuner_timeout
    elif hasattr(config_scenario, "wallclock_time"):  # SMAC2 / IRACE
        latex_dict["wholeTimeBudget"] = config_scenario.wallclock_time
    elif hasattr(config_scenario, "smac3_scenario"):  # SMAC3
        latex_dict["wholeTimeBudget"] = config_scenario.smac3_scenario.walltime_limit
    else:
        latex_dict["wholeTimeBudget"] = config_scenario.max_time
    latex_dict["eachRunCutoffTime"] = config_scenario.cutoff_time

    opt_config_list = [f"{key}: {value}" for key, value in
                       config_output.best_configuration.items()]
    latex_dict["optimisedConfiguration"] = stex.list_to_latex(opt_config_list)
    latex_dict["optimisedConfigurationTrainingPerformance"] =\
        config_output.best_performance_train
    latex_dict["defaultConfigurationTrainingPerformance"] =\
        config_output.default_performance_train

    latex_dict["figure-configured-vs-default-train"] = plot_configured_vs_default(
        config_output,
        config_scenario,
        target_directory)

    # Retrieve timeout numbers for the training instances
    configured_timeouts_train, default_timeouts_train, overlapping_timeouts_train =\
        get_timeouts_instanceset(
            config_output,
            config_output.instance_set_train)

    latex_dict["timeoutsTrainDefault"] = default_timeouts_train
    latex_dict["timeoutsTrainConfigured"] = configured_timeouts_train
    latex_dict["timeoutsTrainOverlap"] = overlapping_timeouts_train
    latex_dict["ablationBool"] = get_ablation_bool(ablation)
    latex_dict["ablationPath"] = get_ablation_table(ablation)
    latex_dict["featuresBool"] = get_features_bool(
        config_scenario, config_output.solver.name, config_scenario.instance_set)

    return latex_dict


def get_dict_variable_to_value_test(
        config_output: ConfigurationOutput,
        configuration_scenario: ConfigurationScenario,
        target_dir: Path,
        ablation: AblationScenario) -> dict:
    """Return a dict matching test set specific latex variables with their values.

    Args:
        config_output: Configuration output
        configuration_scenario: Configuration scenario
        target_dir: Path to where output should go
        ablation: Ablation scenario, if ran

    Returns:
        A dictionary containting the variables and their values
    """
    test_dict = {"instanceSetTest": config_output.instance_set_test.name}
    test_dict["numInstanceInTestingInstanceSet"] = config_output.instance_set_test.size
    test_dict["optimisedConfigurationTestingPerformance"] =\
        config_output.best_performance_test
    test_dict["defaultConfigurationTestingPerformance"] =\
        config_output.default_performance_test

    test_dict["figure-configured-vs-default-test"] =\
        plot_configured_vs_default(
        config_output, configuration_scenario,
        target_dir, test_mode=True)

    # Retrieve timeout numbers for the testing instances
    configured_timeouts_test, default_timeouts_test, overlapping_timeouts_test =\
        get_timeouts_instanceset(config_output,
                                 config_output.instance_set_test)

    test_dict["timeoutsTestDefault"] = default_timeouts_test
    test_dict["timeoutsTestConfigured"] = configured_timeouts_test
    test_dict["timeoutsTestOverlap"] = overlapping_timeouts_test
    test_dict["ablationBool"] = get_ablation_bool(ablation)
    test_dict["ablationPath"] = get_ablation_table(ablation)
    return test_dict


def generate_report_for_configuration(config_scenario: ConfigurationScenario,
                                      config_output: ConfigurationOutput,
                                      extractor_dir: Path,
                                      target_path: Path,
                                      latex_template_path: Path,
                                      bibliography_path: Path,
                                      extractor_cuttoff: int,
                                      ablation: AblationScenario = None) -> None:
    """Generate a report for algorithm configuration.

    Args:
        config_scenario: The configuration scenario to report
        config_output: The configuration output object of the scenario
        extractor_dir: Path to the extractor used
        target_path: Where the report files will be placed.
        latex_template_path: Path to the template to use for the report
        bibliography_path: The bib corresponding to the latex template
        extractor_cuttoff: Cut off for extractor
        ablation: The ablation scenario if ablation was run.
    """
    target_path.mkdir(parents=True, exist_ok=True)
    variables_dict = configuration_report_variables(
        config_scenario, config_output, target_path, bibliography_path, extractor_dir,
        extractor_cuttoff, ablation)
    stex.generate_report(latex_template_path,
                         "template-Sparkle-for-configuration.tex",
                         target_path,
                         "Sparkle_Report_for_Configuration",
                         variables_dict)
