#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''Helper functions to record and restore a Sparkle platform.'''

import os
import sys
from pathlib import Path

from sparkle_help import sparkle_basic_help as sbh
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_file_help as sfh


global record_log_file_path
record_log_file_path = sgh.sparkle_err_path


def detect_current_sparkle_platform_exists() -> bool:
    '''Return whether a Sparkle platform is currently active.'''
    my_flag_anyone = False
    if os.path.exists('Instances/'):
        my_flag_anyone = True
    if os.path.exists('Solvers/'):
        my_flag_anyone = True
    if os.path.exists('Extractors/'):
        my_flag_anyone = True
    if os.path.exists('Feature_Data/'):
        my_flag_anyone = True
    if os.path.exists('Performance_Data/'):
        my_flag_anyone = True
    if os.path.exists('Reference_Lists/'):
        my_flag_anyone = True
    if os.path.exists('Sparkle_Portfolio_Selector/'):
        my_flag_anyone = True
    if sgh.sparkle_parallel_portfolio_dir.exists():
        my_flag_anyone = True

    return my_flag_anyone


def save_current_sparkle_platform(my_record_filename) -> None:
    '''Store the current Sparkle platform in a .zip file.'''
    my_flag_instances = False
    my_flag_solvers = False
    my_flag_extractors = False
    my_flag_feature_data = False
    my_flag_performance_data = False
    my_flag_reference_lists = False
    my_flag_sparkle_portfolio_selector = False
    my_flag_sparkle_parallel_portfolio = False

    if os.path.exists('Instances/'):
        my_flag_instances = True
    if os.path.exists('Solvers/'):
        my_flag_solvers = True
    if os.path.exists('Extractors/'):
        my_flag_extractors = True
    if os.path.exists('Feature_Data/'):
        my_flag_feature_data = True
    if os.path.exists('Performance_Data/'):
        my_flag_performance_data = True
    if os.path.exists('Reference_Lists/'):
        my_flag_reference_lists = True
    if os.path.exists('Sparkle_Portfolio_Selector/'):
        my_flag_sparkle_portfolio_selector = True
    if sgh.sparkle_parallel_portfolio_dir.exists():
        my_flag_sparkle_parallel_portfolio = True

    if not os.path.exists(sgh.sparkle_tmp_path):
        os.mkdir(sgh.sparkle_tmp_path)

    my_record_filename_exist = os.path.exists(my_record_filename)
    if not my_record_filename_exist:
        if my_flag_instances:
            my_record_filename_exist = True
            print('Now recording current Sparkle platform in file '
                  f'{my_record_filename} ...')
            os.system(f'zip -r {my_record_filename} Instances/ >> '
                      f'{record_log_file_path}')
    else:
        if my_flag_instances:
            os.system(f'zip -g -r {my_record_filename} Instances/ >> '
                      f'{record_log_file_path}')

    if not my_record_filename_exist:
        if my_flag_solvers:
            my_record_filename_exist = True
            print('Now recording current Sparkle platform in file '
                  f'{my_record_filename} ...')
            os.system(f'zip -r {my_record_filename} Solvers/ >> '
                      f'{record_log_file_path}')
    else:
        if my_flag_solvers:
            os.system(f'zip -g -r {my_record_filename} Solvers/ >> '
                      f'{record_log_file_path}')

    if not my_record_filename_exist:
        if my_flag_extractors:
            my_record_filename_exist = True
            print('Now recording current Sparkle platform in file '
                  f'{my_record_filename} ...')
            os.system(f'zip -r {my_record_filename} Extractors/ >> '
                      f'{record_log_file_path}')
    else:
        if my_flag_extractors:
            os.system(f'zip -g -r {my_record_filename} Extractors/ >> '
                      f'{record_log_file_path}')

    if not my_record_filename_exist:
        if my_flag_feature_data:
            my_record_filename_exist = True
            print('Now recording current Sparkle platform in file '
                  f'{my_record_filename} ...')
            os.system(f'zip -r {my_record_filename} Feature_Data/ >> '
                      f'{record_log_file_path}')
    else:
        if my_flag_feature_data:
            os.system(f'zip -g -r {my_record_filename} Feature_Data/ >> '
                      f'{record_log_file_path}')

    if not my_record_filename_exist:
        if my_flag_performance_data:
            my_record_filename_exist = True
            print('Now recording current Sparkle platform in file '
                  f'{my_record_filename} ...')
            os.system(f'zip -r {my_record_filename} Performance_Data/ >> '
                      f'{record_log_file_path}')
    else:
        if my_flag_performance_data:
            os.system(f'zip -g -r {my_record_filename} Performance_Data/ >> '
                      f'{record_log_file_path}')

    if not my_record_filename_exist:
        if my_flag_reference_lists:
            my_record_filename_exist = True
            print('Now recording current Sparkle platform in file '
                  f'{my_record_filename} ...')
            os.system(f'zip -r {my_record_filename} Reference_Lists/ >> '
                      f'{record_log_file_path}')
    else:
        if my_flag_reference_lists:
            os.system(f'zip -g -r {my_record_filename} Reference_Lists/ >> '
                      f'{record_log_file_path}')

    if not my_record_filename_exist:
        if my_flag_sparkle_portfolio_selector:
            my_record_filename_exist = True
            print('Now recording current Sparkle platform in file '
                  f'{my_record_filename} ...')
            os.system(f'zip -r {my_record_filename} Sparkle_Portfolio_Selector/ >> '
                      f'{record_log_file_path}')
    else:
        if my_flag_sparkle_portfolio_selector:
            os.system(f'zip -g -r {my_record_filename} Sparkle_Portfolio_Selector/ >> '
                      f'{record_log_file_path}')

    if not my_record_filename_exist:
        if my_flag_sparkle_parallel_portfolio:
            my_record_filename_exist = True
            print('Now recording current Sparkle platform in file '
                  f'{my_record_filename} ...')
            os.system(
                f'zip -r {my_record_filename} '
                f'{sgh.sparkle_parallel_portfolio_dir}/ >> {record_log_file_path}')
    else:
        if my_flag_sparkle_parallel_portfolio:
            os.system(
                f'zip -g -r {my_record_filename} '
                f'{sgh.sparkle_parallel_portfolio_dir}/ >> {record_log_file_path}')

    os.system('rm -f ' + record_log_file_path)

    return


def cleanup_current_sparkle_platform() -> None:
    '''Remove the current Sparkle platform.'''
    if os.path.exists('Instances/'):
        sfh.rmtree(Path('Instances/'))
    if os.path.exists('Solvers/'):
        sfh.rmtree(Path('Solvers/'))
    if os.path.exists('Extractors/'):
        sfh.rmtree(Path('Extractors/'))
    if os.path.exists('Feature_Data/'):
        sfh.rmtree(Path('Feature_Data/'))
    if os.path.exists('Performance_Data/'):
        sfh.rmtree(Path('Performance_Data/'))
    if os.path.exists('Reference_Lists/'):
        sfh.rmtree(Path('Reference_Lists/'))
    if os.path.exists('Sparkle_Portfolio_Selector'):
        sfh.rmtree(Path('Sparkle_Portfolio_Selector/'))
    if sgh.sparkle_parallel_portfolio_dir.exists():
        sfh.rmtree(sgh.sparkle_parallel_portfolio_dir)
    ablation_scenario_dir = f'{sgh.ablation_dir}scenarios/'
    if os.path.exists(ablation_scenario_dir):
        sfh.rmtree(Path(ablation_scenario_dir))
    return


def extract_sparkle_record(my_record_filename) -> None:
    '''Restore a Sparkle platform from a record.'''
    if not os.path.exists(my_record_filename):
        sys.exit()

    my_suffix = sbh.get_time_pid_random_string()
    my_tmp_directory = f'tmp_directory_{my_suffix}'

    if not os.path.exists(sgh.sparkle_tmp_path):
        os.mkdir(sgh.sparkle_tmp_path)

    os.system(f'unzip -o {my_record_filename} -d {my_tmp_directory} >> '
              f'{record_log_file_path}')
    os.system(r'cp -r ' + my_tmp_directory + '/* ' + './')
    sfh.rmtree(Path(my_tmp_directory))
    os.system(r'rm -f ' + record_log_file_path)

    return
