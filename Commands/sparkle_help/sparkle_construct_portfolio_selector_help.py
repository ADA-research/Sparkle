#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
from pathlib import Path
from pathlib import PurePath

from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_file_help as sfh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_run_solvers_help as srsh
from sparkle_help import sparkle_compute_features_help as scfh
from sparkle_help import sparkle_logging as sl
from sparkle_help.sparkle_settings import PerformanceMeasure


def data_unchanged(sparkle_portfolio_selector_path: Path) -> bool:
    unchanged = False
    pd_id = srsh.get_performance_data_id()
    fd_id = scfh.get_feature_data_id()
    selector_dir = sparkle_portfolio_selector_path.parent
    selector_pd_id = get_selector_pd_id(selector_dir)
    selector_fd_id = get_selector_fd_id(selector_dir)

    if pd_id == selector_pd_id and fd_id == selector_fd_id:
        unchanged = True

    return unchanged


def write_selector_pd_id(sparkle_portfolio_selector_path: Path):
    # Get pd_id
    pd_id = srsh.get_performance_data_id()

    # Write pd_id
    pd_id_path = Path(sparkle_portfolio_selector_path.parent / 'pd.id')

    with pd_id_path.open('w') as pd_id_file:
        pd_id_file.write(str(pd_id))

        # Add file to log
        sl.add_output(str(pd_id_path), 'ID of the performance data used to construct '
                      'the portfolio selector.')

    return


def get_selector_pd_id(selector_dir: PurePath) -> int:
    pd_id = -1
    pd_id_path = Path(selector_dir / 'pd.id')

    try:
        with pd_id_path.open('r') as pd_id_file:
            pd_id = int(pd_id_file.readline())
    except FileNotFoundError:
        pd_id = -1

    return pd_id


def write_selector_fd_id(sparkle_portfolio_selector_path: Path):
    # Get fd_id
    fd_id = scfh.get_feature_data_id()

    # Write fd_id
    fd_id_path = Path(sparkle_portfolio_selector_path.parent / 'fd.id')

    with fd_id_path.open('w') as fd_id_file:
        fd_id_file.write(str(fd_id))

        # Add file to log
        sl.add_output(str(fd_id_path),
                      'ID of the feature data used to construct the portfolio selector.')

    return


def get_selector_fd_id(selector_dir: PurePath) -> int:
    fd_id = -1
    fd_id_path = Path(selector_dir / 'fd.id')

    try:
        with fd_id_path.open('r') as fd_id_file:
            fd_id = int(fd_id_file.readline())
    except FileNotFoundError:
        fd_id = -1

    return fd_id


def selector_exists(sparkle_portfolio_selector_path: Path) -> bool:
    exists = sparkle_portfolio_selector_path.is_file()

    return exists


def construct_sparkle_portfolio_selector(sparkle_portfolio_selector_path: str,
                                         performance_data_csv_path: str,
                                         feature_data_csv_path: str,
                                         flag_recompute: bool = False):
    # Convert to pathlib Path (remove when everything is pathlib compliant)
    selector_path = Path(sparkle_portfolio_selector_path)

    # If the selector exists and the data didn't change, do nothing; unless the recompute
    # flag is set
    if(selector_exists(selector_path) and data_unchanged(selector_path)
       and not flag_recompute):
        print('Portfolio selector already exists for the current feature and performance'
              ' data.')

        # Nothing to do, success!
        return True

    # Remove contents of- and the selector path to ensure everything is (re)computed
    # for the new selector when required
    sfh.rmtree(selector_path.parent)

    # (Re)create the path to the selector
    selector_path.parent.mkdir(parents=True, exist_ok=True)

    cutoff_time = sgh.settings.get_general_target_cutoff_time()
    cutoff_time_minimum = 2

    # AutoFolio cannot handle cutoff time less than 2, adjust if needed
    if cutoff_time < cutoff_time_minimum:
        print(f'Warning: A cutoff time of {cutoff_time} is too small for AutoFolio, '
              f'setting it to {cutoff_time_minimum}')
        cutoff_time = cutoff_time_minimum

    cutoff_time_str = str(cutoff_time)
    python_executable = sgh.python_executable
    performance_measure = sgh.settings.get_general_performance_measure()
    if performance_measure == PerformanceMeasure.RUNTIME:
        objective_function = '--objective runtime'
    elif performance_measure == PerformanceMeasure.QUALITY_ABSOLUTE:
        objective_function = '--objective solution_quality'
    else:
        print('ERROR: Unknown performance measure in '
              'construct_sparkle_portfolio_selector')
        sys.exit(-1)

    if not os.path.exists(r'Tmp/'):
        os.mkdir(r'Tmp/')

    feature_data_csv = sfdcsv.SparkleFeatureDataCSV(feature_data_csv_path)
    bool_exists_missing_value = feature_data_csv.bool_exists_missing_value()

    if bool_exists_missing_value:
        print('****** WARNING: There are missing values in the feature data, and all '
              'missing values will be imputed as the mean value of all other non-missing'
              ' values! ******')
        print('Imputing all missing values starts ...')
        feature_data_csv.impute_missing_value_of_all_columns()
        print('Imputing all missing values done!')
        impute_feature_data_csv_path = (
            f'{feature_data_csv_path}_{sparkle_basic_help.get_time_pid_random_string()}'
            '_impute.csv')
        feature_data_csv.save_csv(impute_feature_data_csv_path)
        feature_data_csv_path = impute_feature_data_csv_path

    log_file = selector_path.parent.name + '_autofolio.out'
    err_file = selector_path.parent.name + '_autofolio.err'
    log_path_str = str(Path(sl.caller_log_dir / log_file))
    err_path_str = str(Path(sl.caller_log_dir / err_file))
    command_line = (f'{python_executable} {sgh.autofolio_path} --performance_csv '
                    f'{performance_data_csv_path} --feature_csv {feature_data_csv_path} '
                    f'{objective_function} --runtime_cutoff {cutoff_time_str} --tune '
                    f'--save {sparkle_portfolio_selector_path} 1>> {log_path_str} 2>> '
                    f'{err_path_str}')

    # Write command line to log
    print('Running command below:\n', command_line, file=open(log_path_str, 'a+'))
    sl.add_output(log_path_str, 'Command line used to construct portfolio through '
                  'AutoFolio and associated output')
    sl.add_output(err_path_str,
                  'Error output from constructing portfolio through AutoFolio')

    os.system(command_line)
    # Remove autofolio output from root Sparkle directory
    os.system('rm -f runhistory.json')

    if bool_exists_missing_value:
        os.system(r'rm -f ' + impute_feature_data_csv_path)

    # Check if the selector was constructed successfully
    if not selector_path.is_file():
        print('Sparkle portfolio selector is not successfully constructed!')
        print('There might be some errors!')
        print('Standard output log:', log_path_str)
        print('Error output log:', err_path_str)
        sys.exit()

    # Update data IDs associated with this selector
    write_selector_pd_id(Path(sparkle_portfolio_selector_path))
    write_selector_fd_id(Path(sparkle_portfolio_selector_path))

    # If we reach this point portfolio construction should be successful
    return True
