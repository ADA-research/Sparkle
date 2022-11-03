#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''Helper functions for marginal contribution computation.'''

import os
import csv
from pathlib import Path

from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_performance_data_csv_help as spdcsv
from sparkle_help.sparkle_performance_data_csv_help import SparklePerformanceDataCSV
from sparkle_help import sparkle_construct_portfolio_selector_help as scps
from sparkle_help import sparkle_run_portfolio_selector_help as srps
from sparkle_help import sparkle_logging as sl
from sparkle_help.sparkle_settings import PerformanceMeasure


def read_marginal_contribution_csv(path: Path) -> list[tuple[str, float]]:
    '''Read the marginal contriutions from a CSV file.'''
    content = []

    with path.open('r') as input_file:
        reader = csv.reader(input_file)
        for row in reader:
            # 0 is the solver, 1 the marginal contribution
            content.append((row[0], row[1]))

    return content


def write_marginal_contribution_csv(path: Path, content: list[tuple[str, float]]):
    '''Write the marginal contributions to a CSV file.'''
    with path.open('w') as output_file:
        writer = csv.writer(output_file)
        writer.writerows(content)

        # Add file to log
        sl.add_output(str(path),
                      'Marginal contributions to the portfolio selector per solver.')


def get_capvalue_list(performance_data_csv: SparklePerformanceDataCSV) -> list[float]:
    '''Return a list of capvalues it the performance measure is QUALITY, else None.'''
    performance_measure = sgh.settings.get_general_performance_measure()

    # If QUALITY_ABSOLUTE is the performance measure, use the maximum performance per
    # instance as capvalue; otherwise the cutoff time is used
    if performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE:
        capvalue_list = performance_data_csv.get_maximum_performance_per_instance()
    else:
        capvalue_list = None

    return capvalue_list


def compute_perfect_selector_marginal_contribution(
        performance_data_csv_path=sgh.performance_data_csv_path,
        flag_recompute: bool = False) -> list[tuple[str, float]]:
    '''Return the marginal contributions of solvers for the VBS.'''
    perfect_margi_cont_path = sgh.sparkle_marginal_contribution_perfect_path

    # If the marginal contribution already exists in file, read it and return
    if not flag_recompute and perfect_margi_cont_path.is_file():
        print('Marginal contribution for the perfect selector already computed, reading '
              'from file instead! Use --recompute to force recomputation.')
        rank_list = read_marginal_contribution_csv(perfect_margi_cont_path)

        return rank_list

    cutoff_time_str = str(sgh.settings.get_general_target_cutoff_time())
    print(f'In this calculation, cutoff time for each run is {cutoff_time_str} seconds')

    rank_list = []
    performance_data_csv = spdcsv.SparklePerformanceDataCSV(performance_data_csv_path)
    num_instances = performance_data_csv.get_row_size()
    num_solvers = performance_data_csv.get_column_size()
    capvalue_list = get_capvalue_list(performance_data_csv)

    print('Computing virtual best performance for portfolio selector with all solvers '
          '...')
    virtual_best_performance = (
        performance_data_csv.calc_virtual_best_performance_of_portfolio(
            num_instances, num_solvers, capvalue_list))
    print('Virtual best performance for portfolio selector with all solvers is '
          f'{str(virtual_best_performance)}')
    print('Computing done!')

    for solver in performance_data_csv.list_columns():
        print('Computing virtual best performance for portfolio selector excluding '
              f'solver {sfh.get_last_level_directory_name(solver)} ...')
        tmp_performance_data_csv = spdcsv.SparklePerformanceDataCSV(
            performance_data_csv_path)
        tmp_performance_data_csv.delete_column(solver)
        tmp_virtual_best_performance = (
            tmp_performance_data_csv.calc_virtual_best_performance_of_portfolio(
                num_instances, num_solvers, capvalue_list))
        print('Virtual best performance for portfolio selector excluding solver '
              f'{sfh.get_last_level_directory_name(solver)} is '
              f'{str(tmp_virtual_best_performance)}')
        print('Computing done!')
        marginal_contribution = virtual_best_performance - tmp_virtual_best_performance
        solver_tuple = (solver, marginal_contribution)
        rank_list.append(solver_tuple)
        print('Marginal contribution (to Perfect Selector) for solver '
              f'{sfh.get_last_level_directory_name(solver)} is '
              f'{str(marginal_contribution)}')

    rank_list.sort(key=lambda marginal_contribution: marginal_contribution[1],
                   reverse=True)

    # Write perfect selector contributions to file
    write_marginal_contribution_csv(perfect_margi_cont_path, rank_list)

    return rank_list


def get_list_predict_schedule(actual_portfolio_selector_path, feature_data_csv,
                              instance):
    '''Return the solvers schedule suggested by the selector as a list.'''
    list_predict_schedule = []
    python_executable = sgh.python_executable
    if not os.path.exists('Tmp/'):
        os.mkdir('Tmp/')
    feature_vector_string = feature_data_csv.get_feature_vector_string(instance)

    predit_schedule_file = ('predict_schedule_'
                            f'{sparkle_basic_help.get_time_pid_random_string()}.predres')
    log_file = 'predict_schedule_autofolio.out'
    err_file = 'predict_schedule_autofolio.err'
    predict_schedule_result_path_str = (
        str(Path(sl.caller_log_dir / predit_schedule_file)))
    log_path = Path(sl.caller_log_dir / log_file)
    err_path_str = str(Path(sl.caller_log_dir / err_file))

    command_line = (f'{python_executable} {sgh.autofolio_path} --load '
                    f'{actual_portfolio_selector_path} --feature_vec "'
                    f'{feature_vector_string}" 1> {predict_schedule_result_path_str}'
                    f' 2> {err_path_str}')

    with log_path.open('a+') as log_file:
        print('Running command below to get predicted schedule from autofolio:\n',
              command_line, file=log_file)

    os.system(command_line)

    list_predict_schedule = (
        srps.get_list_predict_schedule_from_file(predict_schedule_result_path_str))

    # If there is error output log temporary files for analsysis, otherwise remove them
    with open(err_path_str) as file_content:
        lines = file_content.read().splitlines()
    if len(lines) > 1 or lines[0] != 'INFO:AutoFolio:Predict on Test':
        sl.add_output(str(log_path), 'Predicted portfolio schedule command line call')
        sl.add_output(predict_schedule_result_path_str, 'Predicted portfolio schedule')
        sl.add_output(err_path_str, 'Predicted portfolio schedule error output')
    else:
        os.system('rm -f ' + predict_schedule_result_path_str)
        os.system('rm -f ' + err_path_str)
        os.system('rm -f ' + str(log_path))

    return list_predict_schedule


def compute_actual_selector_performance(
        actual_portfolio_selector_path, performance_data_csv_path, feature_data_csv_path,
        num_instances: int, num_solvers: int, capvalue_list: list[float] = None):
    '''Return the performance of the selector over all instances.'''
    cutoff_time = sgh.settings.get_general_target_cutoff_time()
    performance_data_csv = spdcsv.SparklePerformanceDataCSV(performance_data_csv_path)

    actual_selector_performance = 0

    for instance_idx in range(0, len(performance_data_csv.list_rows())):
        instance = performance_data_csv.get_row_name(instance_idx)

        if capvalue_list is None:
            # RUNTIME
            capvalue = cutoff_time
            performance_this_instance, flag_successfully_solving = (
                compute_actual_used_time_for_instance(
                    actual_portfolio_selector_path, instance, feature_data_csv_path,
                    performance_data_csv))
        else:
            # QUALITY_ABSOLUTE
            capvalue = capvalue_list[instance_idx]
            performance_this_instance, flag_successfully_solving = (
                compute_actual_performance_for_instance(
                    actual_portfolio_selector_path, instance, feature_data_csv_path,
                    performance_data_csv))

        if flag_successfully_solving:
            score_this_instance = (1 + (capvalue - performance_this_instance)
                                   / (num_instances * num_solvers * capvalue + 1))
        else:
            score_this_instance = 0

        actual_selector_performance = actual_selector_performance + score_this_instance

    return actual_selector_performance


def compute_actual_performance_for_instance(
        actual_portfolio_selector_path: str, instance: str, feature_data_csv_path: str,
        performance_data_csv: SparklePerformanceDataCSV) -> tuple[float, bool]:
    '''Return the best performance of the selector on a given instance.'''
    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(feature_data_csv_path)
    list_predict_schedule = get_list_predict_schedule(actual_portfolio_selector_path,
                                                      feature_data_csv, instance)
    performance_this_instance = sgh.sparkle_maximum_int
    flag_successfully_solving = True

    for i in range(0, len(list_predict_schedule)):
        solver = list_predict_schedule[i][0]
        performance = performance_data_csv.get_value(instance, solver)

        # Take best performance from the scheduled solvers
        if performance < performance_this_instance:
            performance_this_instance = performance

    return performance_this_instance, flag_successfully_solving


def compute_actual_used_time_for_instance(
        actual_portfolio_selector_path: str, instance: str, feature_data_csv_path: str,
        performance_data_csv: SparklePerformanceDataCSV) -> tuple[float, bool]:
    '''Return the total time used by the solver schedule on an instance.'''
    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(feature_data_csv_path)
    list_predict_schedule = get_list_predict_schedule(actual_portfolio_selector_path,
                                                      feature_data_csv, instance)
    cutoff_time = sgh.settings.get_general_target_cutoff_time()
    used_time_for_this_instance = 0
    flag_successfully_solving = False

    for i in range(0, len(list_predict_schedule)):
        if used_time_for_this_instance >= cutoff_time:
            flag_successfully_solving = False
            break

        solver = list_predict_schedule[i][0]
        scheduled_cutoff_time_this_run = list_predict_schedule[i][1]
        required_time_this_run = performance_data_csv.get_value(instance, solver)

        if required_time_this_run <= scheduled_cutoff_time_this_run:
            used_time_for_this_instance = (
                used_time_for_this_instance + required_time_this_run)
            if used_time_for_this_instance > cutoff_time:
                flag_successfully_solving = False
            else:
                flag_successfully_solving = True
            break
        else:
            used_time_for_this_instance = (
                used_time_for_this_instance + scheduled_cutoff_time_this_run)
            continue

    return used_time_for_this_instance, flag_successfully_solving


def compute_actual_selector_marginal_contribution(
        performance_data_csv_path=sgh.performance_data_csv_path,
        feature_data_csv_path=sgh.feature_data_csv_path,
        flag_recompute: bool = False) -> list[tuple[str, float]]:
    '''Compute the marginal contributions of solvers in the selector.'''
    actual_margi_cont_path = sgh.sparkle_marginal_contribution_actual_path

    # If the marginal contribution already exists in file, read it and return
    if not flag_recompute and actual_margi_cont_path.is_file():
        print('Marginal contribution for the actual selector already computed, reading '
              'from file instead! Use --recompute to force recomputation.')
        rank_list = read_marginal_contribution_csv(actual_margi_cont_path)

        return rank_list

    cutoff_time_str = str(sgh.settings.get_general_target_cutoff_time())
    print(f'In this calculation, cutoff time for each run is {cutoff_time_str} seconds')

    rank_list = []

    # Get values from CSV while all solvers and instances are included
    performance_data_csv = spdcsv.SparklePerformanceDataCSV(performance_data_csv_path)
    num_instances = performance_data_csv.get_row_size()
    num_solvers = performance_data_csv.get_column_size()
    capvalue_list = get_capvalue_list(performance_data_csv)

    if not os.path.exists('Tmp/'):
        os.mkdir('Tmp/')

    # Compute performance of actual selector
    print('Computing actual performance for portfolio selector with all solvers ...')
    actual_portfolio_selector_path = sgh.sparkle_portfolio_selector_path
    scps.construct_sparkle_portfolio_selector(actual_portfolio_selector_path,
                                              performance_data_csv_path,
                                              feature_data_csv_path)

    if not os.path.exists(actual_portfolio_selector_path):
        print(f'****** WARNING: {actual_portfolio_selector_path} does not exist! ******')
        print('****** WARNING: AutoFolio constructing the actual portfolio selector with'
              ' all solvers failed! ******')
        print('****** WARNING: Using virtual best performance instead of actual '
              'performance for this portfolio selector! ******')
        virtual_best_performance = (
            performance_data_csv.calc_virtual_best_performance_of_portfolio(
                num_instances, num_solvers, capvalue_list))
        actual_selector_performance = virtual_best_performance
    else:
        actual_selector_performance = (
            compute_actual_selector_performance(
                actual_portfolio_selector_path, performance_data_csv_path,
                feature_data_csv_path, num_instances, num_solvers, capvalue_list))

    print('Actual performance for portfolio selector with all solvers is '
          f'{str(actual_selector_performance)}')
    print('Computing done!')

    # Compute contribution per solver
    for solver in performance_data_csv.list_columns():
        solver_name = sfh.get_last_level_directory_name(solver)
        print('Computing actual performance for portfolio selector excluding solver '
              f'{solver_name} ...')
        tmp_performance_data_csv = (
            spdcsv.SparklePerformanceDataCSV(performance_data_csv_path))
        tmp_performance_data_csv.delete_column(solver)
        tmp_performance_data_csv_file = (
            f'tmp_performance_data_csv_without_{solver_name}_'
            f'{sparkle_basic_help.get_time_pid_random_string()}.csv')
        tmp_performance_data_csv_path = (
            str(Path(sl.caller_log_dir / tmp_performance_data_csv_file)))
        sl.add_output(tmp_performance_data_csv_path,
                      '[written] Temporary performance data')
        tmp_performance_data_csv.save_csv(tmp_performance_data_csv_path)
        tmp_actual_portfolio_selector_path = (
            'Tmp/tmp_actual_portfolio_selector_'
            f'{sparkle_basic_help.get_time_pid_random_string()}')
        tmp_actual_portfolio_selector_path = (
            f'{sgh.sparkle_portfolio_selector_dir}without_{solver_name}/'
            f'{sgh.sparkle_portfolio_selector_name}')

        if len(tmp_performance_data_csv.list_columns()) >= 1:
            scps.construct_sparkle_portfolio_selector(
                tmp_actual_portfolio_selector_path, tmp_performance_data_csv_path,
                feature_data_csv_path)
        else:
            print('****** WARNING: No solver exists ! ******')

        if not os.path.exists(tmp_actual_portfolio_selector_path):
            print(f'****** WARNING: {tmp_actual_portfolio_selector_path} does not exist!'
                  ' ******')
            print('****** WARNING: AutoFolio constructing the actual portfolio selector '
                  f'excluding solver {solver_name} failed! ******')
            print('****** WARNING: Using virtual best performance instead of actual '
                  'performance for this portfolio selector! ******')
            tmp_virtual_best_performance = (
                tmp_performance_data_csv.calc_virtual_best_performance_of_portfolio(
                    num_instances, num_solvers, capvalue_list))
            tmp_actual_selector_performance = tmp_virtual_best_performance
        else:
            tmp_actual_selector_performance = (
                compute_actual_selector_performance(
                    tmp_actual_portfolio_selector_path, tmp_performance_data_csv_path,
                    feature_data_csv_path, num_instances, num_solvers, capvalue_list))

        print(f'Actual performance for portfolio selector excluding solver {solver_name}'
              f' is {str(tmp_actual_selector_performance)}')
        os.system('rm -f ' + tmp_performance_data_csv_path)
        sl.add_output(tmp_performance_data_csv_path,
                      '[removed] Temporary performance data')
        print('Computing done!')

        marginal_contribution = (
            actual_selector_performance - tmp_actual_selector_performance)

        solver_tuple = (solver, marginal_contribution)
        rank_list.append(solver_tuple)
        print(f'Marginal contribution (to Actual Selector) for solver {solver_name} is '
              f'{str(marginal_contribution)}')

    rank_list.sort(key=lambda marginal_contribution: marginal_contribution[1],
                   reverse=True)

    # Write actual selector contributions to file
    write_marginal_contribution_csv(actual_margi_cont_path, rank_list)

#    os.system(r'rm -f ' + actual_portfolio_selector_path)
    return rank_list


def print_rank_list(rank_list, mode):
    '''Print the solvers ranked by marginal contribution.'''
    my_string = ''
    if mode == 1:
        my_string = 'perfect selector'
    elif mode == 2:
        my_string = 'actual selector'
    else:
        pass
    print('******')
    print('Solver ranking list via marginal contribution (Margi_Contr) with regards to '
          f'{my_string}')
    for i in range(0, len(rank_list)):
        solver = rank_list[i][0]
        marginal_contribution = rank_list[i][1]
        print(f'#{str(i+1)}: {sfh.get_last_level_directory_name(solver)}\t Margi_Contr: '
              f'{str(marginal_contribution)}')
    print('******')

    return
