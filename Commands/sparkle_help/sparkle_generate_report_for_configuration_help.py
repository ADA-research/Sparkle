#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for algorithm configuration report generation."""

from __future__ import annotations

import sys
import shutil
from pathlib import Path

from Commands.sparkle_help import sparkle_configure_solver_help as scsh
from Commands.sparkle_help import sparkle_file_help as sfh
from Commands.sparkle_help import sparkle_global_help as sgh
from Commands.sparkle_help import sparkle_instances_help as sih
from Commands.sparkle_help import sparkle_generate_report_help as sgrh
from Commands.sparkle_help import sparkle_run_ablation_help as sah
from Commands.sparkle_help import sparkle_tex_help as stex
from Commands.sparkle_help.sparkle_generate_report_help import generate_comparison_plot


def get_num_instance_in_instance_set_smac_dir(instance_set_name: str) -> str:
    """Return the number of instances for an instance set used by SMAC.

    Args:
        instance_set_name: Name of the instance set

    Returns:
        A string containing the number of instances
    """
    str_value = ""
    # For multi-file instances count based on the reference list
    if sih.check_existence_of_reference_instance_list(instance_set_name):
        instance_count = sih.count_instances_in_reference_list(instance_set_name)
        str_value = str(instance_count)
    # For single-file instances just count the number of instance files
    else:
        inst_path = sgh.settings.get_general_sparkle_configurator().instances_path
        instance_dir = inst_path / instance_set_name
        list_instance = [x.name for x in
                         sfh.get_list_all_filename_recursive(instance_dir)]

        # If there is only an instance file and not the actual instances in the
        # directory, count number of lines in instance file
        if f"{instance_set_name}_train.txt" in list_instance:
            str_value = str(len((instance_dir / f"{instance_set_name}_train.txt")
                                .open("r").readlines()))
        elif f"{instance_set_name}_test.txt" in list_instance:
            str_value = str(len((instance_dir / f"{instance_set_name}_test.txt")
                                .open("r").readlines()))
        else:
            str_value = str(len(list_instance))

    return str_value


def get_par_performance(results_file: str, cutoff: int) -> float:
    """Return the PAR score for a given results file and cutoff time.

    Args:
        results_file: Name of the result file
        cutoff: Cutoff value

    Returns:
        PAR performance value
    """
    list_instance_and_par = construct_list_instance_and_performance(results_file,
                                                                    cutoff)
    sum_par = 0.0
    num_instances = 0

    for item in list_instance_and_par:
        num_instances += 1
        sum_par += float(item[1])

    mean_par = float(sum_par / num_instances)

    return mean_par


# Retrieve instances and corresponding performance values from smac validation objective
# matrix
def construct_list_instance_and_performance(result_file: str,
                                            cutoff: int) -> list[list[str | float]]:
    """Extracts a list of [instance, performance] pairs from a result file.

    Args:
        results_file: Name of the result file
        cutoff: Cutoff value

    Returns:
        A list containing the performance for each instance
    """
    list_instance_and_performance = []

    csv_lines = Path(result_file).open("r").readlines()
    csv_lines = csv_lines[1:]  # Skip column titles

    for csv_line in csv_lines:
        values = csv_line.strip().split(",")
        instance = Path(values[0].strip('"')).name
        performance = float(values[2].strip('"'))

        # If the objective is runtime, compute the PAR score; otherwise don't modify
        # the value
        smac_run_obj, _, _, _, _, _ = scsh.get_smac_settings()

        if smac_run_obj == "RUNTIME":
            # TODO: Verifiy/explain why this is Incorrect/Correct flow
            # Minimum runtime. Is lower than this not accurate?
            if performance < 0.01001:
                performance = 0.01001
            elif performance >= cutoff:
                penalty = sgh.settings.get_general_penalty_multiplier()
                performance = float(cutoff) * penalty

        list_instance_and_performance.append([instance, performance])
    return list_instance_and_performance


def get_dict_instance_to_performance(results_file: str, cutoff: int) -> dict[str, float]:
    """Return a dictionary of instance names and their performance.

    Args:
        results_file: Name of the result file
        cutoff: Cutoff value

    Returns:
        A dictionary containing the performance for each instance
    """
    list_instance_and_performance = construct_list_instance_and_performance(
        results_file, float(cutoff))

    dict_instance_to_performance = {}

    for item in list_instance_and_performance:
        instance = Path(item[0]).name
        performance_value = item[1]
        dict_instance_to_performance[instance] = performance_value

    return dict_instance_to_performance


def get_performance_measure() -> str:
    """Return the performance measure as LaTeX string.

    Returns:
        A string containing the performance measure
    """
    performance_measure = ""

    smac_run_obj, _, _, _, _, _ = scsh.get_smac_settings()

    if smac_run_obj == "RUNTIME":
        penalty = sgh.settings.get_general_penalty_multiplier()
        performance_measure = f"PAR{penalty}"
    elif smac_run_obj == "QUALITY":
        performance_measure = "performance"

    return performance_measure


def get_runtime_bool() -> str:
    """Return the runtime bool as LaTeX string.

    Returns:
        A string containing the runtime boolean
    """
    runtime_bool = ""

    smac_run_obj, _, _, _, _, _ = scsh.get_smac_settings()

    if smac_run_obj == "RUNTIME":
        runtime_bool = r"\runtimetrue"
    elif smac_run_obj == "QUALITY":
        runtime_bool = r"\runtimefalse"

    return runtime_bool


def get_ablation_bool(solver_name: str, instance_train_name: str,
                      instance_test_name: str) -> str:
    """Return the ablation bool as LaTeX string.

    Args:
        solver_name: Name of the solver
        instance_train_name: Name of the trianing instance set
        instance_test_name: Name of the testing instance set

    Returns:
        A string describing whether ablation was run or not
    """
    ablation_bool = ""

    if sah.check_for_ablation(solver_name, instance_train_name, instance_test_name):
        ablation_bool = r"\ablationtrue"
    else:
        ablation_bool = r"\ablationfalse"

    return ablation_bool


def get_features_bool(solver_name: str, instance_set_train_name: str) -> str:
    """Return a bool string for latex indicating whether features were used.

    True if a feature file is given in the scenario file, false otherwise.

    Args:
        solver_name: Name of the solver
        instance_set_train_name: Name of the instance set used for training

    Returns:
        A string describing whether features are used
    """
    scenario_file = sgh.settings.get_general_sparkle_configurator().scenario.directory \
        / f"{solver_name}_{instance_set_train_name}_scenario.txt"
    features_bool = r"\featuresfalse"

    with scenario_file.open("r") as f:
        for line in f.readlines():
            if line.split(" ")[0] == "feature_file":
                features_bool = r"\featurestrue"
                break

    return features_bool


def get_data_for_plot(configured_results_dir: str, default_results_dir: str,
                      smac_each_run_cutoff_time: float) -> list:
    """Return the required data to plot.

    Creates a nested list of performance values algorithm runs with default and
    configured parameters on instances in a given instance set.

    Args:
        configured_results_dir: Directory of results for configured solver
        default_results_dir: Directory of results for default solver
        smac_each_run_cutoff_time: Cutoff time

    Returns:
        A list of lists containing data points
    """
    dict_instance_to_par_default = get_dict_instance_to_performance(
        default_results_dir, smac_each_run_cutoff_time)
    dict_instance_to_par_configured = get_dict_instance_to_performance(
        configured_results_dir, smac_each_run_cutoff_time)

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


def get_figure_configure_vs_default(configured_results_dir: str,
                                    default_results_dir: str,
                                    configuration_reports_directory: str,
                                    figure_filename: str,
                                    smac_each_run_cutoff_time: float) -> str:
    """Create a figure comparing the configured and default solver.

    Base function to create a comparison plot of a given instance set between the default
    and configured performance.

    Args:
        configured_results_dir: Directory of results for configured solver
        default_results_dir: Directory of results for default solver
        configuration_reports_directory: Directory for the configuration reports
        figure_filename: Filename for the figure
        smac_each_run_cutoff_time: Cutoff time

    Returns:
        A string containing the latex command to include the figure
    """
    latex_directory_path = (
        configuration_reports_directory + "Sparkle-latex-generator-for-configuration/")
    points = get_data_for_plot(configured_results_dir, default_results_dir,
                               smac_each_run_cutoff_time)

    performance_measure = get_performance_measure()

    plot_params = {"xlabel": f"Default parameters [{performance_measure}]",
                   "ylabel": f"Configured parameters [{performance_measure}]",
                   "output_dir": latex_directory_path,
                   "scale": "linear",
                   "limit_min": 1.5,
                   "limit_max": 1.5,
                   "limit": "relative",
                   "replace_zeros": False,
                   }
    if performance_measure[0:3] == "PAR":
        plot_params["scale"] = "log"
        plot_params["limit_min"] = 0.25
        plot_params["limit_max"] = 0.25
        plot_params["limit"] = "magnitude"
        plot_params["penalty_time"] = sgh.settings.get_penalised_time()
        plot_params["replace_zeros"] = True

    generate_comparison_plot(points,
                             figure_filename,
                             **plot_params)

    str_value = f"\\includegraphics[width=0.6\\textwidth]{{{figure_filename}}}"

    return str_value


def get_figure_configured_vs_default_on_test_instance_set(
        solver_name: str, instance_set_train_name: str, instance_set_test_name: str,
        smac_each_run_cutoff_time: float) -> str:
    """Create a figure comparing the configured and default solver on the training set.

    Manages the creation of a comparison plot of the instances in a test set for the
    report by gathering the proper files and choosing the plotting parameters based on
    the performance measure.

    Args:
        solver_name: Name of the solver
        instance_set_train_name: Name of the instance set for training
        instance_set_test_name: Name of the instance set for testing
        smac_each_run_cutoff_time: Cutoff time

    Returns:
        A string containing the latex command to include the figure
    """
    configured_results_file = (
        "validationObjectiveMatrix-configuration_for_validation-walltime.csv")
    default_results_file = "validationObjectiveMatrix-cli-1-walltime.csv"
    scen_path = sgh.settings.get_general_sparkle_configurator().scenarios_path
    smac_solver_dir = str(scen_path) +\
        f"/{solver_name}_{instance_set_train_name}/"
    configured_results_dir = (f"{smac_solver_dir}/outdir_{instance_set_test_name}"
                              f"_test_configured/{configured_results_file}")
    default_results_dir = (f"{smac_solver_dir}/outdir_{instance_set_test_name}"
                           f"_test_default/{default_results_file}")

    configuration_reports_directory = (f"Configuration_Reports/{solver_name}_"
                                       f"{instance_set_train_name}_"
                                       f"{instance_set_test_name}/")
    data_plot_configured_vs_default_on_test_instance_set_filename = (
        f"data_{solver_name}_configured_vs_default_on_{instance_set_test_name}_test")

    return get_figure_configure_vs_default(
        configured_results_dir, default_results_dir, configuration_reports_directory,
        data_plot_configured_vs_default_on_test_instance_set_filename,
        smac_each_run_cutoff_time)


def get_figure_configured_vs_default_on_train_instance_set(
        solver_name: str, instance_set_train_name: str,
        configuration_reports_directory: str, smac_each_run_cutoff_time: float) -> str:
    """Create a figure comparing the configured and default solver on the training set.

    Manages the creation of a comparison plot of the instances in the train instance set
    for the report by gathering the proper files and choosing the plotting parameters
    based on the performance measure.

    Args:
        solver_name: Name of the solver
        instance_set_train_name: Name of the instance set for training
        configuration_reports_directory: Directory to the configuration reports
        smac_each_run_cutoff_time: Cutoff time

    Returns:
        A string containing the latex comand to include the figure
    """
    _, _, optimised_configuration_seed = scsh.get_optimised_configuration(
        solver_name, instance_set_train_name)
    configured_results_file = ("validationObjectiveMatrix-traj-run-"
                               f"{optimised_configuration_seed}-walltime.csv")
    default_results_file = "validationObjectiveMatrix-cli-1-walltime.csv"
    scen_path = sgh.settings.get_general_sparkle_configurator().scenario.directory
    configured_results_dir = (f"{scen_path}/outdir_train_configuration/"
                              f"{solver_name}_{instance_set_train_name}_scenario/"
                              f"{configured_results_file}")
    default_res_dir = f"{scen_path}/outdir_train_default/{default_results_file}"

    data_plot_configured_vs_default_on_train_instance_set_filename = (
        f"data_{solver_name}_configured_vs_default_on_{instance_set_train_name}_train")
    return get_figure_configure_vs_default(
        configured_results_dir, default_res_dir, configuration_reports_directory,
        data_plot_configured_vs_default_on_train_instance_set_filename,
        smac_each_run_cutoff_time)


def get_timeouts_test(instance_set_test_name: str, cutoff: int) -> tuple[int, int, int]:
    """Return the number of timeouts by configured, default and both on the testing set.

    Args:
        instance_set_test_name: Name of the testing instance set
        cutoff: Cutoff time

    Returns:
        A tuple containing the number of timeouts for the different configurations
    """
    # Retrieve instances and PAR values
    configured_results_file = (
        "validationObjectiveMatrix-configuration_for_validation-walltime.csv")
    default_results_file = "validationObjectiveMatrix-cli-1-walltime.csv"
    scen_path = sgh.settings.get_general_sparkle_configurator().scenario.directory
    configured_results_dir = (f"{scen_path}/outdir_{instance_set_test_name}"
                              f"_test_configured/{configured_results_file}")
    default_results_dir = (f"{scen_path}/outdir_{instance_set_test_name}"
                           f"_test_default/{default_results_file}")
    dict_instance_to_par_configured = get_dict_instance_to_performance(
        configured_results_dir, cutoff)
    dict_instance_to_par_default = get_dict_instance_to_performance(
        default_results_dir, cutoff)

    return get_timeouts(dict_instance_to_par_configured,
                        dict_instance_to_par_default, cutoff)


def get_timeouts_train(solver_name: str, instance_set_name: str,
                       cutoff: int) -> tuple[int, int, int]:
    """Return the number timeouts by configured, default and both on the training set.

    Args:
        solver_name: Name of the solver
        instance_set_name: Name of the instance set for testing
        cutoff: Cutoff value

    Returns:
        A tuple containing the number of timeouts for the different configurations
    """
    (optimised_configuration_str, optimised_configuration_performance_par,
     optimised_configuration_seed) = scsh.get_optimised_configuration(
        solver_name, instance_set_name)
    configured_results_file = ("validationObjectiveMatrix-traj-run-"
                               f"{optimised_configuration_seed}-walltime.csv")
    default_results_file = "validationObjectiveMatrix-cli-1-walltime.csv"
    scen_path = sgh.settings.get_general_sparkle_configurator().scenario.directory

    configured_results_dir = (f"{scen_path}/outdir_train_configuration/"
                              f"{solver_name}_{instance_set_name}_scenario/"
                              f"{configured_results_file}")
    default_results_dir = f"{scen_path}/outdir_train_default/{default_results_file}"
    dict_instance_to_par_configured = get_dict_instance_to_performance(
        configured_results_dir, cutoff)
    dict_instance_to_par_default = get_dict_instance_to_performance(
        default_results_dir, cutoff)

    return get_timeouts(dict_instance_to_par_configured,
                        dict_instance_to_par_default, cutoff)


def get_timeouts(dict_instance_to_par_configured: dict,
                 dict_instance_to_par_default: dict,
                 cutoff: int) -> tuple[int, int, int]:
    """Return the number of timeouts for given dicts.

    Args:
        dict_instance_to_par_configured: _description_
        dict_instance_to_par_default: _description_
        cutoff: Cutoff value

    Returns:
        A tuple containing timeout values
    """
    penalty = sgh.settings.get_general_penalty_multiplier()
    timeout_value = cutoff * penalty

    configured_timeouts = 0
    default_timeouts = 0
    overlapping_timeouts = 0

    for instance in dict_instance_to_par_configured:
        configured_par_value = dict_instance_to_par_configured[instance]
        default_par_value = dict_instance_to_par_default[instance]

        if configured_par_value == timeout_value:
            configured_timeouts += 1
        if default_par_value == timeout_value:
            default_timeouts += 1
        if (configured_par_value == timeout_value
           and default_par_value == timeout_value):
            overlapping_timeouts += 1

    return configured_timeouts, default_timeouts, overlapping_timeouts


def get_ablation_table(solver_name: str, instance_set_train_name: str,
                       instance_set_test_name: str = None) -> str:
    """Generate a LaTeX table of the ablation path.

    This is the result of the ablation analysis to determine the parameter importance.

    Args:
        solver_name: Name of the solver
        instance_set_train_name: Name of the instance set for training
        instance_set_test_name: Name of the instance set for testing

    Returns:
        A string containing the LaTeX table code of the ablation path
    """
    results = sah.get_ablation_table(solver_name, instance_set_train_name,
                                     instance_set_test_name)
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


def get_dict_variable_to_value(solver_name: str, instance_set_train_name: str,
                               instance_set_test_name: str = None,
                               ablation: bool = True) -> dict:
    """Return a dict matching LaTeX variables and their values.

    Args:
        solver_name: Name of the solver
        instance_set_train_name: Name of the instance set for training
        instance_set_test_name: Name of the instance set for testing. Defaults to None.
        ablation: Whether or not ablation is used. Defaults to True.

    Returns:
        A dictionary containing the variables and values
    """
    full_dict = {}

    if instance_set_test_name is not None:
        configuration_reports_directory = (
            f"Configuration_Reports/{solver_name}_{instance_set_train_name}_"
            f"{instance_set_test_name}/")
    else:
        configuration_reports_directory = (
            "Configuration_Reports/" + solver_name + "_" + instance_set_train_name + "/")

    common_dict = get_dict_variable_to_value_common(solver_name, instance_set_train_name,
                                                    instance_set_test_name,
                                                    configuration_reports_directory)
    full_dict.update(common_dict)

    variable = "testBool"

    if instance_set_test_name is not None:
        test_dict = get_dict_variable_to_value_test(solver_name, instance_set_train_name,
                                                    instance_set_test_name)
        full_dict.update(test_dict)
        str_value = r"\testtrue"
    else:
        str_value = r"\testfalse"
    full_dict[variable] = str_value

    if not ablation:
        full_dict["ablationBool"] = r"\ablationfalse"

    if full_dict["featuresBool"] == r"\featurestrue":
        variable = "numFeatureExtractors"
        str_value = sgrh.get_num_feature_extractors()
        full_dict[variable] = str_value

        variable = "featureExtractorList"
        str_value = sgrh.get_feature_extractor_list()
        full_dict[variable] = str_value

        variable = "featureComputationCutoffTime"
        str_value = sgrh.get_feature_computation_cutoff_time()
        full_dict[variable] = str_value

    return full_dict


def get_dict_variable_to_value_common(solver_name: str, instance_set_train_name: str,
                                      instance_set_test_name: str,
                                      configuration_reports_directory: str) -> dict:
    """Return a dict matching LaTeX variables and values used for all config. reports.

    Args:
        solver_name: Name of the solver
        instance_set_train_name: Name of the instance set for training
        instance_set_test_name: Name of the instance set for testing
        configuration_reports_directory: Path to directory with configuration reports

    Returns:
        A dictionary containing the variables and values
    """
    common_dict = {}
    common_dict["performanceMeasure"] = get_performance_measure()
    common_dict["runtimeBool"] = get_runtime_bool()
    common_dict["customCommands"] = sgrh.get_custom_commands()
    common_dict["sparkle"] = sgrh.get_sparkle()
    common_dict["solver"] = solver_name
    common_dict["instanceSetTrain"] = instance_set_train_name
    common_dict["sparkleVersion"] = sgh.sparkle_version
    common_dict["numInstanceInTrainingInstanceSet"] = \
        get_num_instance_in_instance_set_smac_dir(instance_set_train_name)

    (smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time,
     _, num_of_smac_run_str, _) = scsh.get_smac_settings()

    common_dict["numSmacRuns"] = str(num_of_smac_run_str)
    common_dict["smacObjective"] = str(smac_run_obj)
    common_dict["smacWholeTimeBudget"] = str(smac_whole_time_budget)
    common_dict["smacEachRunCutoffTime"] = str(smac_each_run_cutoff_time)

    (optimised_configuration_str, _,
     optimised_configuration_seed) = scsh.get_optimised_configuration(
        solver_name, instance_set_train_name)

    common_dict["optimisedConfiguration"] = str(optimised_configuration_str)
    scen_path = sgh.settings.get_general_sparkle_configurator().scenario.directory
    (optimised_configuration_str, _,
     optimised_configuration_seed) = scsh.get_optimised_configuration(
        solver_name, instance_set_train_name)
    configured_results_train_file = "validationObjectiveMatrix-traj-run-" + str(
        optimised_configuration_seed) + "-walltime.csv"
    configured_results_train_dir = (f"{scen_path}/outdir_train_configuration/"
                                    f"{solver_name}_{instance_set_train_name}_scenario/"
                                    f"{configured_results_train_file}")
    str_value = get_par_performance(configured_results_train_dir,
                                    smac_each_run_cutoff_time)
    common_dict["optimisedConfigurationTrainingPerformancePAR"] = str(str_value)

    default_results_train_file = "validationObjectiveMatrix-cli-1-walltime.csv"
    default_results_train_dir = (f"{scen_path}/outdir_train_default/"
                                f"{default_results_train_file}")
    str_value = get_par_performance(default_results_train_dir,
                                    smac_each_run_cutoff_time)
    common_dict["defaultConfigurationTrainingPerformancePAR"] = str(str_value)

    str_value = get_figure_configured_vs_default_on_train_instance_set(
        solver_name, instance_set_train_name, configuration_reports_directory,
        float(smac_each_run_cutoff_time))
    common_dict["figure-configured-vs-default-train"] = str_value

    # Retrieve timeout numbers for the training instances
    configured_timeouts_train, default_timeouts_train, overlapping_timeouts_train = (
        get_timeouts_train(solver_name, instance_set_train_name,
                           float(smac_each_run_cutoff_time)))

    common_dict["timeoutsTrainDefault"] = str(default_timeouts_train)
    common_dict["timeoutsTrainConfigured"] = str(configured_timeouts_train)
    common_dict["timeoutsTrainOverlap"] = str(overlapping_timeouts_train)

    ablation_validation_name = instance_set_test_name
    if ablation_validation_name is None:
        ablation_validation_name = instance_set_train_name
    common_dict["ablationBool"] = get_ablation_bool(solver_name, instance_set_train_name,
                                                    ablation_validation_name)
    common_dict["ablationPath"] = get_ablation_table(
        solver_name, instance_set_train_name, ablation_validation_name)
    common_dict["featuresBool"] = get_features_bool(solver_name, instance_set_train_name)

    return common_dict


def get_dict_variable_to_value_test(solver_name: str, instance_set_train_name: str,
                                    instance_set_test_name: str) -> dict:
    """Return a dict matching test set specific latex variables with their values.

    Args:
        solver_name: Name of the solver
        instance_set_train_name: Name of the instance set for training
        instance_set_test_name: Name of the instance set for testing

    Returns:
        A dictionary containting the variables and their values
    """
    test_dict = {}

    variable = "instanceSetTest"
    str_value = instance_set_test_name
    test_dict[variable] = str_value

    variable = "numInstanceInTestingInstanceSet"
    str_value = get_num_instance_in_instance_set_smac_dir(instance_set_test_name)
    test_dict[variable] = str_value

    (_, _, smac_each_run_cutoff_time, _, _, _) = scsh.get_smac_settings()
    scen_path = sgh.settings.get_general_sparkle_configurator().scenario.directory

    configured_results_test_file = (
        "validationObjectiveMatrix-configuration_for_validation-walltime.csv")
    configured_results_test_dir = (f"{scen_path}/outdir_{instance_set_test_name}"
                                   f"_test_configured/{configured_results_test_file}")
    str_value = get_par_performance(configured_results_test_dir,
                                    smac_each_run_cutoff_time)
    test_dict["optimisedConfigurationTestingPerformancePAR"] = str(str_value)

    default_results_test_file = "validationObjectiveMatrix-cli-1-walltime.csv"
    default_results_test_dir = (f"{scen_path}/outdir_{instance_set_test_name}"
                                f"_test_default/{default_results_test_file}")
    str_value = get_par_performance(default_results_test_dir,
                                    smac_each_run_cutoff_time)
    test_dict["defaultConfigurationTestingPerformancePAR"] = str(str_value)

    str_value = get_figure_configured_vs_default_on_test_instance_set(
        solver_name, instance_set_train_name, instance_set_test_name,
        float(smac_each_run_cutoff_time))
    test_dict["figure-configured-vs-default-test"] = str_value

    # Retrieve timeout numbers for the testing instances
    configured_timeouts_test, default_timeouts_test, overlapping_timeouts_test = (
        get_timeouts_test(solver_name, instance_set_train_name, instance_set_test_name,
                          float(smac_each_run_cutoff_time)))

    test_dict["timeoutsTestDefault"] = str(default_timeouts_test)
    test_dict["timeoutsTestConfigured"] = str(configured_timeouts_test)
    test_dict["timeoutsTestOverlap"] = str(overlapping_timeouts_test)
    test_dict["ablationBool"] = get_ablation_bool(solver_name, instance_set_train_name,
                                                  instance_set_test_name)
    test_dict["ablationPath"] = get_ablation_table(solver_name, instance_set_train_name,
                                                   instance_set_test_name)
    return test_dict


def check_results_exist(solver_name: str, instance_set_train_name: str,
                        instance_set_test_name: str = None) -> None:
    """Check whether configuration results exist.

    Args:
        solver_name: Name of the solver
        instance_set_train_name: Name of the instance set for training
        instance_set_test_name: Name of the instance set for testing. Defaults to None.
    """
    all_good = True
    err_str = ""
    configurator  = sgh.settings.get_general_sparkle_configurator()
    scen_path = configurator.scenario.directory
    inst_path = configurator.instances_path
    # Check train instance dir exists
    instance_train_dir = str(
        inst_path / instance_set_train_name)

    if not Path(instance_train_dir).exists():
        all_good = False
        err_str += (" training set not found in configuration directory "
                    f"{instance_train_dir};")

    # Check train results exist: configured+default
    configured_results_train_dir = (f"{scen_path}/outdir_train_configuration/"
                                    f"{solver_name}_{instance_set_train_name}_scenario/")
    default_results_train_dir = f"{scen_path}/outdir_train_default/"

    if not Path(configured_results_train_dir).exists():
        err_str += (" configured parameter results on the training set not found in "
                    f"{configured_results_train_dir};")
        all_good = False
    if not Path(default_results_train_dir).exists():
        err_str += (" default parameter results on the training set not found in "
                    f"{default_results_train_dir};")
        all_good = False

    if instance_set_test_name is not None:
        # Check test instance dir exists
        instance_test_dir = str(
            inst_path / instance_set_test_name)
        if not Path(instance_test_dir).exists():
            all_good = False
            err_str += (" testing set not found in configuration directory "
                        f"{instance_test_dir};")

        # Check test results exist: configured+default
        configured_results_test_dir = (
            str(scen_path) + "/outdir_" + instance_set_test_name + "_test_configured/")
        default_results_test_dir = (
            str(scen_path) + "/outdir_" + instance_set_test_name + "_test_default/")

        if not Path(configured_results_test_dir).exists():
            err_str += (" configured parameter results on the testing set not found in "
                        f"{configured_results_test_dir};")
            all_good = False
        if not Path(default_results_test_dir).exists():
            err_str += (" default parameter results on the testing set not found in "
                        f"{default_results_test_dir};")
            all_good = False

    if not all_good:
        print("Error: Results not found for the given solver and instance set(s) "
              'combination. Make sure the "configure_solver" and '
              '"validate_configured_vs_default" commands were correctly executed. '
              f"\nDetected errors:\n{err_str}")
        sys.exit(-1)

    return


def get_most_recent_test_run(solver_name: str) -> tuple[str, str, bool, bool]:
    """Return the instance sets used most recently to configure a given solver.

    Args:
        solver_name: Name of the solver

    Returns:
        A tuple containg the training and test instance sets
    """
    instance_set_train = ""
    instance_set_test = ""
    flag_instance_set_train = False
    flag_instance_set_test = False

    # Read most recent run from file
    last_test_file_path =\
        sgh.settings.get_general_sparkle_configurator().scenario.directory
    # TODO: Bugfix, this if produces failures in the pytest.
    # The file does not exist in the pytest, but its unclear why
    """if False and not last_test_file_path.exists():
        # Report error when file does not exist
        print("Error: The most recent results do not match the given solver. Please "
              "specify which instance sets you want a report for with this solver. "
              'Alternatively, make sure the "test_configured_solver_and_default_solver" '
              "command was executed for this solver.")
        sys.exit(-1)"""

    with last_test_file_path.open("r") as fin:
        test_file_lines = fin.read().splitlines()
        for myline in test_file_lines:
            words = myline.split()
            if words[0] == "train":
                instance_set_train = words[1]
                if instance_set_train != "":
                    flag_instance_set_train = True
            elif words[0] == "test":
                instance_set_test = words[1]
                if instance_set_test != "":
                    flag_instance_set_test = True
    return (instance_set_train, instance_set_test, flag_instance_set_train,
            flag_instance_set_test)


def generate_report_for_configuration_prep(configuration_reports_directory: str) -> None:
    """Prepare for the generation of an algorithm configuration report.

    Args:
        configuration_reports_directory: Directory for the configuration reports
    """
    print("Generating report for configuration ...")
    full_conf_reports_dir = Path(configuration_reports_directory
                                 + "/Sparkle-latex-generator-for-configuration")
    template_latex_path = Path("Components/Sparkle-latex-generator-for-configuration")
    shutil.copytree(template_latex_path, full_conf_reports_dir, dirs_exist_ok=True)


def generate_report_for_configuration_train(solver_name: str,
                                            instance_set_train_name: str,
                                            ablation: bool = True) -> None:
    """Generate a report for algorithm configuration with only a training set.

    Args:
        solver_name: Name of the solver
        instance_set_train_name: Name of the instance set for training
        ablation: Whether or not ablation is used. Defaults to True.
    """
    configuration_reports_directory = (f"Configuration_Reports/{solver_name}_"
                                       f"{instance_set_train_name}/")
    generate_report_for_configuration_prep(configuration_reports_directory)
    dict_variable_to_value = get_dict_variable_to_value(
        solver_name, instance_set_train_name, ablation=ablation)

    generate_report_for_configuration_common(configuration_reports_directory,
                                             dict_variable_to_value)


def generate_report_for_configuration(solver_name: str, instance_set_train_name: str,
                                      instance_set_test_name: str,
                                      ablation: bool = True) -> None:
    """Generate a report for algorithm configuration.

    Args:
        solver_name: Name of the solver
        instance_set_train_name: Name of the instance set for training
        instance_set_test_name: Name of the instance set for testing
        ablation: Whether or not ablation is used. Defaults to True.
    """
    configuration_reports_directory = (f"Configuration_Reports/{solver_name}_"
                                       f"{instance_set_train_name}_"
                                       f"{instance_set_test_name}/")
    generate_report_for_configuration_prep(configuration_reports_directory)
    dict_variable_to_value = (
        get_dict_variable_to_value(solver_name, instance_set_train_name,
                                   instance_set_test_name, ablation=ablation))

    generate_report_for_configuration_common(configuration_reports_directory,
                                             dict_variable_to_value)


def generate_report_for_configuration_common(configuration_reports_directory: str,
                                             dict_variable_to_value: dict) -> None:
    """Generate the common part of all algorithm configuration reports.

    Args:
        configuration_reports_directory: Directory for the configuration reports
        dict_variable_to_value: Dictionary containing values for LaTeX
    """
    latex_directory_path = Path(
        f"{configuration_reports_directory}Sparkle-latex-generator-for-configuration/")
    latex_template_filename = "template-Sparkle-for-configuration.tex"
    latex_report_filename = Path("Sparkle_Report_for_Configuration")

    # Read in the report template from file
    latex_template_filepath = Path(latex_directory_path / latex_template_filename)
    report_content = Path(latex_template_filepath).open("r").read()

    # Replace variables in the report template with their value
    for variable_key, str_value in dict_variable_to_value.items():
        variable = "@@" + variable_key + "@@"
        if (variable_key != "figure-configured-vs-default-test") and (
                variable_key != "figure-configured-vs-default-train"):
            str_value = str_value.replace("_", r"\textunderscore ")
        report_content = report_content.replace(variable, str_value)

    # Write the completed report to a tex file
    latex_report_filepath = Path(latex_directory_path / latex_report_filename)
    latex_report_filepath = latex_report_filepath.with_suffix(".tex")
    with Path(latex_report_filepath).open("w+") as fout:
        fout.write(report_content)

    stex.check_tex_commands_exist(latex_directory_path)

    # Compile the report
    report_path = stex.compile_pdf(latex_directory_path, latex_report_filename)

    print(f"Report is placed at: {report_path}")
    print("Generating report for configuration done!")
