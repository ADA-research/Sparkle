#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
from pathlib import Path

from sparkle_help import sparkle_configure_solver_help as scsh
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_instances_help as sih
from sparkle_help import sparkle_generate_report_help as sgrh
from sparkle_help import sparkle_run_ablation_help as sah
from sparkle_help import sparkle_tex_help as stex
from sparkle_help.sparkle_generate_report_help import generate_comparison_plot
from sparkle_help.sparkle_configure_solver_help import get_smac_solver_dir


def get_num_instance_in_instance_set_smac_dir(instance_set_name: str) -> str:
    str_value = ''

    # For multi-file instances count based on the reference list
    if sih.check_existence_of_reference_instance_list(instance_set_name):
        instance_count = sih.count_instances_in_reference_list(instance_set_name)
        str_value = str(instance_count)
    # For single-file instances just count the number of instance files
    else:
        instance_dir = f'{sgh.smac_dir}/example_scenarios/instances/{instance_set_name}/'
        list_instance = sfh.get_list_all_filename(instance_dir)
        str_value = str(len(list_instance))

    return str_value


def get_par10_performance(results_file, cutoff):
    list_instance_and_par10 = construct_list_instance_and_performance(results_file,
                                                                      cutoff)
    sum_par10 = 0.0
    num_instances = 0

    for item in list_instance_and_par10:
        num_instances += 1
        sum_par10 += float(item[1])

    mean_par10 = float(sum_par10 / num_instances)

    return mean_par10


def get_optimised_configuration_testing_performance_par10(solver_name, instance_set_name,
                                                          smac_each_run_cutoff_time):
    str_value = ''
    smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + '/'
    configured_results_dir = (
        f'{smac_solver_dir}results/'
        f'{sgh.sparkle_run_configured_wrapper}_{instance_set_name}/')
    script_calc_par10_time_path = f'{sgh.smac_dir}/example_scenarios/calc_par10_time.py'
    command_line = (f'{script_calc_par10_time_path} {configured_results_dir} '
                    f'{str(smac_each_run_cutoff_time)}')
    output = os.popen(command_line).readlines()
    str_value = output[0].strip().split()[2]
    return str_value


def get_default_configuration_testing_performance_par10(solver_name, instance_set_name,
                                                        smac_each_run_cutoff_time):
    str_value = ''
    smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + '/'
    default_results_dir = (f'{smac_solver_dir}results/{sgh.sparkle_run_default_wrapper}_'
                           f'{instance_set_name}/')
    script_calc_par10_time_path = f'{sgh.smac_dir}/example_scenarios/calc_par10_time.py'
    command_line = (f'{script_calc_par10_time_path} {default_results_dir} '
                    f'{str(smac_each_run_cutoff_time)}')
    output = os.popen(command_line).readlines()
    str_value = output[0].strip().split()[2]
    return str_value


def get_optimised_configuration_training_performance_par10(solver_name,
                                                           instance_set_name,
                                                           smac_each_run_cutoff_time):
    str_value = ''
    smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + '/'
    configured_results_dir = (
        f'{smac_solver_dir}results_train/'
        f'{sgh.sparkle_run_configured_wrapper}_{instance_set_name}/')
    script_calc_par10_time_path = f'{sgh.smac_dir}/example_scenarios/calc_par10_time.py'
    command_line = (f'{script_calc_par10_time_path} {configured_results_dir} '
                    f'{str(smac_each_run_cutoff_time)}')
    output = os.popen(command_line).readlines()
    str_value = output[0].strip().split()[2]
    return str_value


def get_default_configuration_training_performance_par10(solver_name, instance_set_name,
                                                         smac_each_run_cutoff_time):
    str_value = ''
    smac_solver_dir = sgh.smac_dir + '/example_scenarios/' + solver_name + '/'
    default_results_dir = (f'{smac_solver_dir}results_train/'
                           f'{sgh.sparkle_run_default_wrapper}_{instance_set_name}/')
    script_calc_par10_time_path = f'{sgh.smac_dir}/example_scenarios/calc_par10_time.py'
    command_line = (f'{script_calc_par10_time_path} {default_results_dir} '
                    f'{str(smac_each_run_cutoff_time)}')
    output = os.popen(command_line).readlines()
    str_value = output[0].strip().split()[2]
    return str_value


def get_instance_path_from_path(results_dir, path):
    instance_path = Path(path)
    instance_name = instance_path.name
    # TODO: Check what this was supposed to do, or whehter it can be deleted:
    # if results_dir[-1] != '/':
    # 	results_dir += '/'
    # instance_path = path.replace(results_dir, '')
    # pos_right_slash = instance_path.rfind('/')
    # instance_path_1 = instance_path[:pos_right_slash+1]
    # instance_path_2 = instance_path[pos_right_slash+1:]
    #
    # key_str_wrapper = 'wrapper'
    # pos_wrapper = instance_path_2.find(key_str_wrapper)
    # instance_path_2 = instance_path_2[pos_wrapper+1:]
    # pos_underscore_first = instance_path_2.find('_')
    # instance_path_2 = instance_path_2[pos_underscore_first+1:]
    # pos_underscore_last = instance_path_2.rfind('_')
    # instance_path_2 = instance_path_2[:pos_underscore_last]
    # instance_path = instance_path_1 + instance_path_2
    return instance_name


def construct_list_instance_and_par10_recursive(list_instance_and_par10, path, cutoff):
    if os.path.isfile(path):
        file_extension = sfh.get_file_least_extension(path)
        if file_extension == 'res':
            fin = open(path, 'r')
            while True:
                myline = fin.readline()
                if myline:
                    mylist = myline.strip().split()
                    if len(mylist) <= 1:
                        continue
                    if mylist[1] == 's':
                        run_time = float(mylist[0].split('/')[0])
                        # Minimum runtime. Is lower than this not accurate?
                        if run_time < 0.01001:
                            run_time = 0.01001
                        if run_time > cutoff:
                            continue
                        if mylist[2] == 'SATISFIABLE':
                            list_instance_and_par10.append([path, run_time])
                            break
                        elif mylist[2] == 'UNSATISFIABLE':
                            list_instance_and_par10.append([path, run_time])
                            break
                else:
                    run_time = cutoff * 10
                    list_instance_and_par10.append([path, run_time])
                    break
        return

    elif os.path.isdir(path):
        if path[-1] != '/':
            this_path = path + '/'
        else:
            this_path = path
        list_all_items = os.listdir(this_path)
        for item in list_all_items:
            construct_list_instance_and_par10_recursive(list_instance_and_par10,
                                                        this_path + item, cutoff)
    return


# Retrieve instances and corresponding performance values from smac validation objective
# matrix
def construct_list_instance_and_performance(result_file, cutoff):
    list_instance_and_performance = []

    fin = open(result_file, 'r')
    fin.readline()  # Skip column titles

    while True:
        myline = fin.readline()

        if not myline.strip():
            break

        mylist = myline.split(',')
        instance_path = mylist[0].strip('"')
        instance = instance_path.split('/')[-1]
        performance = float(mylist[2].replace('"', ''))

        # If the objective is runtime, compute the PAR10 score; otherwise don't modify
        # the value
        smac_run_obj, _, _, _, _, _ = scsh.get_smac_settings()

        if smac_run_obj == 'RUNTIME':
            # Minimum runtime. Is lower than this not accurate?
            if performance < 0.01001:
                performance = 0.01001
            elif performance >= float(cutoff):
                performance = float(cutoff) * 10

        list_instance_and_performance.append([instance, performance])

    return list_instance_and_performance


# Return a dictionary of instance names and their performance
def get_dict_instance_to_performance(results_file, cutoff):
    list_instance_and_performance = construct_list_instance_and_performance(
        results_file, float(cutoff))

    dict_instance_to_performance = {}

    for item in list_instance_and_performance:
        instance = get_instance_path_from_path(results_file, item[0])
        performance_value = item[1]
        dict_instance_to_performance[instance] = performance_value

    return dict_instance_to_performance


def get_performance_measure():
    performance_measure = ''

    smac_run_obj, _, _, _, _, _ = scsh.get_smac_settings()

    if smac_run_obj == 'RUNTIME':
        performance_measure = 'PAR10'
    elif smac_run_obj == 'QUALITY':
        performance_measure = 'performance'

    return performance_measure


def get_runtime_bool():
    runtime_bool = ''

    smac_run_obj, _, _, _, _, _ = scsh.get_smac_settings()

    if smac_run_obj == 'RUNTIME':
        runtime_bool = r'\runtimetrue'
    elif smac_run_obj == 'QUALITY':
        runtime_bool = r'\runtimefalse'

    return runtime_bool


def get_ablation_bool(solver_name, instance_train_name, instance_test_name):
    ablation_bool = ''

    if sah.check_for_ablation(solver_name, instance_train_name, instance_test_name):
        ablation_bool = r'\ablationtrue'
    else:
        ablation_bool = r'\ablationfalse'

    return ablation_bool


def get_features_bool(solver_name: str, instance_set_train_name: str) -> str:
    '''
    Returns a bool string for latex indicating whether features were used.

    True if a feature file is given in the scenario file, false otherwise.
    '''
    scenario_file = (f'{get_smac_solver_dir(solver_name, instance_set_train_name)}'
                     f'{solver_name}_{instance_set_train_name}_scenario.txt')
    features_bool = r'\featuresfalse'

    with open(scenario_file, 'r') as f:
        for line in f.readlines():
            if line.split(' ')[0] == 'feature_file':
                features_bool = r'\featurestrue'

    return features_bool


def get_data_for_plot(configured_results_dir: str, default_results_dir: str,
                      smac_each_run_cutoff_time: float) -> list:
    '''
    Creates a nested list of performance values algorithm runs with default and
    configured parameters on instances in a given instance set.

    @return List of Lists containing performance values for default and configured
    algorithms
    '''
    dict_instance_to_par10_default = get_dict_instance_to_performance(
        default_results_dir, smac_each_run_cutoff_time)
    dict_instance_to_par10_configured = get_dict_instance_to_performance(
        configured_results_dir, smac_each_run_cutoff_time)

    instances = (dict_instance_to_par10_default.keys()
                 & dict_instance_to_par10_configured.keys())
    assert (len(dict_instance_to_par10_default) == len(instances))
    points = []
    for instance in instances:
        point = [dict_instance_to_par10_default[instance],
                 dict_instance_to_par10_configured[instance]]
        points.append(point)

    return points


def get_figure_configure_vs_default(configured_results_dir: str,
                                    default_results_dir: str,
                                    configuration_reports_directory: str,
                                    figure_filename: str,
                                    smac_each_run_cutoff_time: float) -> str:
    '''
    Base function to create a comparison plot of a given instance set between the default
    and configured performance.

    @return the LaTeX code to include the figure.
    '''
    latex_directory_path = (
        configuration_reports_directory + 'Sparkle-latex-generator-for-configuration/')
    points = get_data_for_plot(configured_results_dir, default_results_dir,
                               smac_each_run_cutoff_time)

    performance_measure = get_performance_measure()

    plot_params = {'xlabel': f'Default parameters [{performance_measure}]',
                   'ylabel': f'Configured parameters [{performance_measure}]',
                   'cwd': latex_directory_path,
                   'scale': 'linear',
                   'limit_min': 1.5,
                   'limit_max': 1.5,
                   'limit': 'relative',
                   'replace_zeros': False,
                   }
    if performance_measure == 'PAR10':
        plot_params['scale'] = 'log'
        plot_params['limit_min'] = 0.25
        plot_params['limit_max'] = 0.25
        plot_params['limit'] = 'magnitude'
        plot_params['penalty_time'] = sgh.settings.get_penalised_time()
        plot_params['replace_zeros'] = True

    generate_comparison_plot(points,
                             figure_filename,
                             **plot_params)

    str_value = f'\\includegraphics[width=0.6\\textwidth]{{{figure_filename}}}'

    return str_value


def get_figure_configured_vs_default_on_test_instance_set(
        solver_name: str, instance_set_train_name: str, instance_set_test_name: str,
        smac_each_run_cutoff_time: float) -> str:
    '''
    Manages the creation of a comparison plot of the instances in a test set for the
    report by gathering the proper files and choosing the plotting parameters based on
    the performance measure.

    @return the LaTeX code to include the figure.
    '''
    configured_results_file = (
        'validationObjectiveMatrix-configuration_for_validation-walltime.csv')
    default_results_file = 'validationObjectiveMatrix-cli-1-walltime.csv'
    smac_solver_dir = (
        f'{sgh.smac_dir}/example_scenarios/{solver_name}_{instance_set_train_name}/')
    configured_results_dir = (f'{smac_solver_dir}outdir_{instance_set_test_name}'
                              f'_test_configured/{configured_results_file}')
    default_results_dir = (f'{smac_solver_dir}outdir_{instance_set_test_name}'
                           f'_test_default/{default_results_file}')

    configuration_reports_directory = (f'Configuration_Reports/{solver_name}_'
                                       f'{instance_set_train_name}_'
                                       f'{instance_set_test_name}/')
    data_plot_configured_vs_default_on_test_instance_set_filename = (
        f'data_{solver_name}_configured_vs_default_on_{instance_set_test_name}_test')

    return get_figure_configure_vs_default(
        configured_results_dir, default_results_dir, configuration_reports_directory,
        data_plot_configured_vs_default_on_test_instance_set_filename,
        smac_each_run_cutoff_time)


def get_figure_configured_vs_default_on_train_instance_set(
        solver_name: str, instance_set_train_name: str,
        configuration_reports_directory: str, smac_each_run_cutoff_time: float) -> str:
    '''
    Manages the creation of a comparison plot of the instances in the train instance set
    for the report by gathering the proper files and choosing the plotting parameters
    based on the performance measure.

    @return the LaTeX code to include the figure.
    '''
    _, _, optimised_configuration_seed = scsh.get_optimised_configuration(
        solver_name, instance_set_train_name)
    configured_results_file = ('validationObjectiveMatrix-traj-run-'
                               f'{optimised_configuration_seed}-walltime.csv')
    default_results_file = 'validationObjectiveMatrix-cli-1-walltime.csv'
    smac_solver_dir = (
        f'{sgh.smac_dir}/example_scenarios/{solver_name}_{instance_set_train_name}/')
    configured_results_dir = (f'{smac_solver_dir}outdir_train_configuration/'
                              f'{solver_name}_{instance_set_train_name}_scenario/'
                              f'{configured_results_file}')
    default_results_dir = f'{smac_solver_dir}outdir_train_default/{default_results_file}'

    data_plot_configured_vs_default_on_train_instance_set_filename = (
        f'data_{solver_name}_configured_vs_default_on_{instance_set_train_name}_train')
    return get_figure_configure_vs_default(
        configured_results_dir, default_results_dir, configuration_reports_directory,
        data_plot_configured_vs_default_on_train_instance_set_filename,
        smac_each_run_cutoff_time)


def get_timeouts_test(solver_name, instance_set_train_name, instance_set_name, cutoff):
    configured_timeouts = 0
    default_timeouts = 0
    overlapping_timeouts = 0

    # Retrieve instances and PAR10 values
    configured_results_file = (
        'validationObjectiveMatrix-configuration_for_validation-walltime.csv')
    default_results_file = 'validationObjectiveMatrix-cli-1-walltime.csv'
    smac_solver_dir = (
        f'{sgh.smac_dir}/example_scenarios/{solver_name}_{instance_set_train_name}/')
    configured_results_dir = (f'{smac_solver_dir}outdir_{instance_set_name}'
                              f'_test_configured/{configured_results_file}')
    default_results_dir = (f'{smac_solver_dir}outdir_{instance_set_name}_test_default/'
                           f'{default_results_file}')
    dict_instance_to_par10_configured = get_dict_instance_to_performance(
        configured_results_dir, cutoff)
    dict_instance_to_par10_default = get_dict_instance_to_performance(
        default_results_dir, cutoff)

    # Count default timeouts, configured timeouts, and overlapping timeouts
    timeout_value = cutoff * 10

    for instance in dict_instance_to_par10_configured:
        configured_par10_value = dict_instance_to_par10_configured[instance]
        default_par10_value = dict_instance_to_par10_default[instance]

        if configured_par10_value == timeout_value:
            configured_timeouts += 1
        if default_par10_value == timeout_value:
            default_timeouts += 1
        if (configured_par10_value == timeout_value
           and default_par10_value == timeout_value):
            overlapping_timeouts += 1

    return configured_timeouts, default_timeouts, overlapping_timeouts


def get_timeouts_train(solver_name, instance_set_name, cutoff):
    configured_timeouts = 0
    default_timeouts = 0
    overlapping_timeouts = 0

    # Retrieve instances and PAR10 values
    (optimised_configuration_str, optimised_configuration_performance_par10,
     optimised_configuration_seed) = scsh.get_optimised_configuration(
        solver_name, instance_set_name)
    configured_results_file = ('validationObjectiveMatrix-traj-run-'
                               f'{optimised_configuration_seed}-walltime.csv')
    default_results_file = 'validationObjectiveMatrix-cli-1-walltime.csv'
    smac_solver_dir = (
        f'{sgh.smac_dir}/example_scenarios/{solver_name}_{instance_set_name}/')
    configured_results_dir = (f'{smac_solver_dir}outdir_train_configuration/'
                              f'{solver_name}_{instance_set_name}_scenario/'
                              f'{configured_results_file}')
    default_results_dir = f'{smac_solver_dir}outdir_train_default/{default_results_file}'
    dict_instance_to_par10_configured = get_dict_instance_to_performance(
        configured_results_dir, cutoff)
    dict_instance_to_par10_default = get_dict_instance_to_performance(
        default_results_dir, cutoff)

    # Count default timeouts, configured timeouts, and overlapping timeouts
    timeout_value = cutoff * 10

    for instance in dict_instance_to_par10_configured:
        configured_par10_value = dict_instance_to_par10_configured[instance]
        default_par10_value = dict_instance_to_par10_default[instance]

        if configured_par10_value == timeout_value:
            configured_timeouts += 1
        if default_par10_value == timeout_value:
            default_timeouts += 1
        if (configured_par10_value == timeout_value
           and default_par10_value == timeout_value):
            overlapping_timeouts += 1

    return configured_timeouts, default_timeouts, overlapping_timeouts


def get_ablation_table(solver_name: str, instance_set_train_name: str,
                       instance_set_test_name: str = None) -> str:
    '''
    Generates a LaTeX table of the ablation path as a result of the ablation analysis to
    determine the parameter importance.

    @return A string containing the LaTeX table code of the ablation path
    '''
    results = sah.get_ablation_table(solver_name, instance_set_train_name,
                                     instance_set_test_name)
    table_string = r'\begin{tabular}{rp{0.25\linewidth}rrr}'
    # "Round", "Flipped parameter", "Source value", "Target value", "Validation result"
    for i, line in enumerate(results):
        # If this fails something has changed in the representation of ablation tables
        assert len(line) == 5
        if i == 0:
            line = ['\\textbf{{{0}}}'.format(word) for word in line]

        # Put multiple variable changes in one round on a seperate line
        if (len(line[1].split(',')) > 1
           and len(line[1].split(',')) == len(line[2].split(','))
           and len(line[1].split(',')) == len(line[3].split(','))):
            params = line[1].split(',')
            default_values = line[2].split(',')
            flipped_values = line[3].split(',')

            sublines = len(params)
            for subline in range(sublines):
                round = '' if subline != 0 else line[0]
                result = '' if subline + 1 != sublines else line[-1]
                printline = [round, params[subline], default_values[subline],
                             flipped_values[subline], result]
                table_string += ' & '.join(printline) + ' \\\\ '
        else:
            table_string += ' & '.join(line) + ' \\\\ '
        if i == 0:
            table_string += '\\hline '
    table_string += '\\end{tabular}'

    return table_string


def get_dict_variable_to_value(solver_name, instance_set_train_name,
                               instance_set_test_name=None, ablation=True):
    full_dict = {}

    if instance_set_test_name is not None:
        configuration_reports_directory = (
            f'Configuration_Reports/{solver_name}_{instance_set_train_name}_'
            f'{instance_set_test_name}/')
    else:
        configuration_reports_directory = (
            'Configuration_Reports/' + solver_name + '_' + instance_set_train_name + '/')

    common_dict = get_dict_variable_to_value_common(solver_name, instance_set_train_name,
                                                    instance_set_test_name,
                                                    configuration_reports_directory)
    full_dict.update(common_dict)

    variable = 'testBool'

    if instance_set_test_name is not None:
        test_dict = get_dict_variable_to_value_test(solver_name, instance_set_train_name,
                                                    instance_set_test_name)
        full_dict.update(test_dict)
        str_value = r'\testtrue'
    else:
        str_value = r'\testfalse'
    full_dict[variable] = str_value

    if not ablation:
        full_dict['ablationBool'] = r'\ablationfalse'

    if full_dict['featuresBool'] == r'\featurestrue':
        variable = 'numFeatureExtractors'
        str_value = sgrh.get_num_feature_extractors()
        full_dict[variable] = str_value

        variable = 'featureExtractorList'
        str_value = sgrh.get_feature_extractor_list()
        full_dict[variable] = str_value

        variable = 'featureComputationCutoffTime'
        str_value = sgrh.get_feature_computation_cutoff_time()
        full_dict[variable] = str_value

    return full_dict


# Retrieve variables relevant to all configuration reports
def get_dict_variable_to_value_common(solver_name, instance_set_train_name,
                                      instance_set_test_name,
                                      configuration_reports_directory):
    common_dict = {}

    variable = 'performanceMeasure'
    str_value = get_performance_measure()
    common_dict[variable] = str_value

    variable = 'runtimeBool'
    str_value = get_runtime_bool()
    common_dict[variable] = str_value

    variable = 'customCommands'
    str_value = sgrh.get_custom_commands()
    common_dict[variable] = str_value

    variable = 'sparkle'
    str_value = sgrh.get_sparkle()
    common_dict[variable] = str_value

    variable = 'solver'
    str_value = solver_name
    common_dict[variable] = str_value

    variable = 'instanceSetTrain'
    str_value = instance_set_train_name
    common_dict[variable] = str_value

    variable = 'sparkleVersion'
    str_value = sgh.sparkle_version
    common_dict[variable] = str_value

    variable = 'numInstanceInTrainingInstanceSet'
    str_value = get_num_instance_in_instance_set_smac_dir(instance_set_train_name)
    common_dict[variable] = str_value

    (smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time,
     smac_each_run_cutoff_length, num_of_smac_run_str, num_of_smac_run_in_parallel_str
     ) = scsh.get_smac_settings()

    variable = 'numSmacRuns'
    common_dict[variable] = str(num_of_smac_run_str)

    variable = 'smacObjective'
    common_dict[variable] = str(smac_run_obj)

    variable = 'smacWholeTimeBudget'
    common_dict[variable] = str(smac_whole_time_budget)

    variable = 'smacEachRunCutoffTime'
    common_dict[variable] = str(smac_each_run_cutoff_time)

    (optimised_configuration_str, optimised_configuration_performance_par10,
     optimised_configuration_seed) = scsh.get_optimised_configuration(
        solver_name, instance_set_train_name)

    variable = 'optimisedConfiguration'
    common_dict[variable] = str(optimised_configuration_str)

    smac_solver_dir = (
        f'{sgh.smac_dir}/example_scenarios/{solver_name}_{instance_set_train_name}/')

    variable = 'optimisedConfigurationTrainingPerformancePAR10'
    (optimised_configuration_str, optimised_configuration_performance_par10,
     optimised_configuration_seed) = scsh.get_optimised_configuration(
        solver_name, instance_set_train_name)
    configured_results_train_file = 'validationObjectiveMatrix-traj-run-' + str(
        optimised_configuration_seed) + '-walltime.csv'
    configured_results_train_dir = (f'{smac_solver_dir}outdir_train_configuration/'
                                    f'{solver_name}_{instance_set_train_name}_scenario/'
                                    f'{configured_results_train_file}')
    str_value = get_par10_performance(configured_results_train_dir,
                                      smac_each_run_cutoff_time)
    common_dict[variable] = str(str_value)

    variable = 'defaultConfigurationTrainingPerformancePAR10'
    default_results_train_file = 'validationObjectiveMatrix-cli-1-walltime.csv'
    default_results_train_dir = (
        smac_solver_dir + 'outdir_train_default/' + default_results_train_file)
    str_value = get_par10_performance(default_results_train_dir,
                                      smac_each_run_cutoff_time)
    common_dict[variable] = str(str_value)

    variable = 'figure-configured-vs-default-train'
    str_value = get_figure_configured_vs_default_on_train_instance_set(
        solver_name, instance_set_train_name, configuration_reports_directory,
        float(smac_each_run_cutoff_time))
    common_dict[variable] = str_value

    # Retrieve timeout numbers for the training instances
    configured_timeouts_train, default_timeouts_train, overlapping_timeouts_train = (
        get_timeouts_train(solver_name, instance_set_train_name,
                           float(smac_each_run_cutoff_time)))

    variable = 'timeoutsTrainDefault'
    common_dict[variable] = str(default_timeouts_train)

    variable = 'timeoutsTrainConfigured'
    common_dict[variable] = str(configured_timeouts_train)

    variable = 'timeoutsTrainOverlap'
    common_dict[variable] = str(overlapping_timeouts_train)

    variable = 'ablationBool'
    ablation_validation_name = (instance_set_test_name
                                if instance_set_test_name is not None
                                else instance_set_train_name)
    common_dict[variable] = get_ablation_bool(solver_name, instance_set_train_name,
                                              ablation_validation_name)

    variable = 'ablationPath'
    common_dict[variable] = get_ablation_table(solver_name, instance_set_train_name,
                                               ablation_validation_name)

    variable = 'featuresBool'
    common_dict[variable] = get_features_bool(solver_name, instance_set_train_name)

    return common_dict


# Retrieve variables specific to the testing set
def get_dict_variable_to_value_test(solver_name, instance_set_train_name,
                                    instance_set_test_name):
    test_dict = {}

    variable = 'instanceSetTest'
    str_value = instance_set_test_name
    test_dict[variable] = str_value

    variable = 'numInstanceInTestingInstanceSet'
    str_value = get_num_instance_in_instance_set_smac_dir(instance_set_test_name)
    test_dict[variable] = str_value

    (smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time,
     smac_each_run_cutoff_length, num_of_smac_run_str,
     num_of_smac_run_in_parallel_str) = scsh.get_smac_settings()

    smac_solver_dir = (
        f'{sgh.smac_dir}/example_scenarios/{solver_name}_{instance_set_train_name}/')

    variable = 'optimisedConfigurationTestingPerformancePAR10'
    configured_results_test_file = (
        'validationObjectiveMatrix-configuration_for_validation-walltime.csv')
    configured_results_test_dir = (f'{smac_solver_dir}outdir_{instance_set_test_name}'
                                   f'_test_configured/{configured_results_test_file}')
    str_value = get_par10_performance(configured_results_test_dir,
                                      smac_each_run_cutoff_time)
    test_dict[variable] = str(str_value)

    variable = 'defaultConfigurationTestingPerformancePAR10'
    default_results_test_file = 'validationObjectiveMatrix-cli-1-walltime.csv'
    default_results_test_dir = (f'{smac_solver_dir}outdir_{instance_set_test_name}'
                                f'_test_default/{default_results_test_file}')
    str_value = get_par10_performance(default_results_test_dir,
                                      smac_each_run_cutoff_time)
    test_dict[variable] = str(str_value)

    variable = 'figure-configured-vs-default-test'
    str_value = get_figure_configured_vs_default_on_test_instance_set(
        solver_name, instance_set_train_name, instance_set_test_name,
        float(smac_each_run_cutoff_time))
    test_dict[variable] = str_value

    # Retrieve timeout numbers for the testing instances
    configured_timeouts_test, default_timeouts_test, overlapping_timeouts_test = (
        get_timeouts_test(solver_name, instance_set_train_name, instance_set_test_name,
                          float(smac_each_run_cutoff_time)))

    variable = 'timeoutsTestDefault'
    test_dict[variable] = str(default_timeouts_test)

    variable = 'timeoutsTestConfigured'
    test_dict[variable] = str(configured_timeouts_test)

    variable = 'timeoutsTestOverlap'
    test_dict[variable] = str(overlapping_timeouts_test)

    variable = 'ablationBool'
    test_dict[variable] = get_ablation_bool(solver_name, instance_set_train_name,
                                            instance_set_test_name)

    variable = 'ablationPath'
    test_dict[variable] = get_ablation_table(solver_name, instance_set_train_name,
                                             instance_set_test_name)

    return test_dict


def check_results_exist(solver_name, instance_set_train_name,
                        instance_set_test_name=None):
    all_good = True
    err_str = ''

    # Check train instance dir exists
    instance_train_dir = (
        f'{sgh.smac_dir}/example_scenarios/instances/{instance_set_train_name}/')

    if not os.path.exists(instance_train_dir):
        all_good = False
        err_str += (' training set not found in configuration directory '
                    f'{instance_train_dir};')

    # Check train results exist: configured+default
    smac_solver_dir = (
        f'{sgh.smac_dir}/example_scenarios/{solver_name}_{instance_set_train_name}/')
    configured_results_train_dir = (f'{smac_solver_dir}outdir_train_configuration/'
                                    f'{solver_name}_{instance_set_train_name}_scenario/')
    default_results_train_dir = smac_solver_dir + 'outdir_train_default/'

    if not os.path.exists(configured_results_train_dir):
        err_str += (' configured parameter results on the training set not found in '
                    f'{configured_results_train_dir};')
        all_good = False
    if not os.path.exists(default_results_train_dir):
        err_str += (' default parameter results on the training set not found in '
                    f'{default_results_train_dir};')
        all_good = False

    if instance_set_test_name is not None:
        # Check test instance dir exists
        instance_test_dir = (
            f'{sgh.smac_dir}/example_scenarios/instances/{instance_set_test_name}/')
        if not os.path.exists(instance_test_dir):
            all_good = False
            err_str += (' testing set not found in configuration directory '
                        f'{instance_test_dir};')

        # Check test results exist: configured+default
        smac_solver_dir = (f'{sgh.smac_dir}/example_scenarios/{solver_name}_'
                           f'{instance_set_train_name}/')
        configured_results_test_dir = (
            smac_solver_dir + 'outdir_' + instance_set_test_name + '_test_configured/')
        default_results_test_dir = (
            smac_solver_dir + 'outdir_' + instance_set_test_name + '_test_default/')

        if not os.path.exists(configured_results_test_dir):
            err_str += (' configured parameter results on the testing set not found in '
                        f'{configured_results_test_dir};')
            all_good = False
        if not os.path.exists(default_results_test_dir):
            err_str += (' default parameter results on the testing set not found in '
                        f'{default_results_test_dir};')
            all_good = False

    if not all_good:
        print('Error: Results not found for the given solver and instance set(s) '
              'combination. Make sure the "configure_solver" and '
              '"validate_configured_vs_default" commands were correctly executed. '
              f'Detected errors:{err_str}')
        sys.exit()

    return


def get_most_recent_test_run(solver_name: str):
    instance_set_train = ''
    instance_set_test = ''
    flag_instance_set_train = False
    flag_instance_set_test = False

    # Read most recent run from file
    last_test_file_path = (f'{sgh.smac_dir}/example_scenarios/{solver_name}_'
                           f'{sgh.sparkle_last_test_file_name}')
    try:
        fin = open(last_test_file_path, 'r')
    except IOError:
        # Report error when file does not exist
        print('Error: The most recent results do not match the given solver. Please '
              'specify which instance sets you want a report for with this solver. '
              'Alternatively, make sure the "test_configured_solver_and_default_solver" '
              'command was executed for this solver.')
        sys.exit()

    while True:
        myline = fin.readline()
        if not myline:
            break
        words = myline.split()

        if words[0] == 'train':
            instance_set_train = words[1]
            if instance_set_train != '':
                flag_instance_set_train = True
        if words[0] == 'test':
            instance_set_test = words[1]
            if instance_set_test != '':
                flag_instance_set_test = True
    fin.close()

    return (instance_set_train, instance_set_test, flag_instance_set_train,
            flag_instance_set_test)


def generate_report_for_configuration_prep(configuration_reports_directory):
    print('Generating report for configuration ...')

    template_latex_directory_path = (
        'Components/Sparkle-latex-generator-for-configuration/')
    if not os.path.exists(configuration_reports_directory):
        os.system('mkdir -p ' + configuration_reports_directory)
    os.system(f'cp -r {template_latex_directory_path} {configuration_reports_directory}')

    return


def generate_report_for_configuration_train(solver_name, instance_set_train_name,
                                            ablation=True):
    configuration_reports_directory = (f'Configuration_Reports/{solver_name}_'
                                       f'{instance_set_train_name}/')
    generate_report_for_configuration_prep(configuration_reports_directory)
    dict_variable_to_value = get_dict_variable_to_value(
        solver_name, instance_set_train_name, ablation=ablation)

    generate_report_for_configuration_common(configuration_reports_directory,
                                             dict_variable_to_value)

    return


def generate_report_for_configuration(solver_name, instance_set_train_name,
                                      instance_set_test_name, ablation=True):
    configuration_reports_directory = (f'Configuration_Reports/{solver_name}_'
                                       f'{instance_set_train_name}_'
                                       f'{instance_set_test_name}/')
    generate_report_for_configuration_prep(configuration_reports_directory)
    dict_variable_to_value = (
        get_dict_variable_to_value(solver_name, instance_set_train_name,
                                   instance_set_test_name, ablation=ablation))

    generate_report_for_configuration_common(configuration_reports_directory,
                                             dict_variable_to_value)

    return


def generate_report_for_configuration_common(configuration_reports_directory,
                                             dict_variable_to_value):
    latex_directory_path = (
        f'{configuration_reports_directory}Sparkle-latex-generator-for-configuration/')
    latex_template_filename = 'template-Sparkle-for-configuration.tex'
    latex_report_filename = 'Sparkle_Report_for_Configuration'

    # Read in the report template from file
    latex_template_filepath = latex_directory_path + latex_template_filename
    report_content = ''
    fin = open(latex_template_filepath, 'r')

    while True:
        myline = fin.readline()
        if not myline:
            break
        report_content += myline
    fin.close()

    # Replace variables in the report template with their value
    for variable_key, str_value in dict_variable_to_value.items():
        variable = '@@' + variable_key + '@@'
        if (variable_key != 'figure-configured-vs-default-test') and (
                variable_key != 'figure-configured-vs-default-train'):
            str_value = str_value.replace('_', r'\textunderscore ')
        report_content = report_content.replace(variable, str_value)

    # print(report_content)

    # Write the completed report to a tex file
    latex_report_filepath = latex_directory_path + latex_report_filename + '.tex'
    fout = open(latex_report_filepath, 'w+')
    fout.write(report_content)
    fout.close()

    # Compile the report
    if stex.check_tex_commands_exist() is False:
        print('Error: It seems like latex is not available on your system.\n'
              f'You can find all source files in {latex_directory_path}\n'
              'Copy these on your local machine to generate the report.')
        return

    report_path = stex.compile_pdf(latex_directory_path, latex_report_filename)

    print(f'Report is placed at: {report_path}')
    print('Generating report for configuration done!')

    return
