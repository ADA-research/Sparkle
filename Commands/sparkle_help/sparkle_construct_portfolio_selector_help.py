#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import os
from pathlib import Path
from pathlib import PurePath

from sparkle_help import sparkle_basic_help
from sparkle_help import sparkle_global_help as sgh
from sparkle_help import sparkle_feature_data_csv_help as sfdcsv
from sparkle_help import sparkle_run_solvers_help as srsh
from sparkle_help import sparkle_compute_features_help as scfh
from sparkle_help import sparkle_logging as sl


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
		sl.add_output(str(pd_id_path), 'ID of the performance data used to construct the portfolio selector.')

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
		sl.add_output(str(fd_id_path), 'ID of the feature data used to construct the portfolio selector.')

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


def construct_sparkle_portfolio_selector(sparkle_portfolio_selector_path: str, performance_data_csv_path, feature_data_csv_path):
	# Convert to pathlib Path (remove when everything is pathlib compliant)
	selector_path = Path(sparkle_portfolio_selector_path)

	# Make sure the path to the selector exists
	selector_path.parent.mkdir(parents=True, exist_ok=True)

	# If the selector exists and the data didn't change, do nothing
	if selector_exists(selector_path) and data_unchanged(selector_path):
		print('c Portfolio selector already exists for the current feature and performance data.')

		return

	# Remove possible old marginal contribution files to ensure they will be computed for the new selector when required
	try:
		sgh.sparkle_marginal_contribution_perfect_path.unlink()#TODO: Use in new python version instead of catching the exception: missing_ok=True)
	except FileNotFoundError:
		pass
	try:
		sgh.sparkle_marginal_contribution_actual_path.unlink()#TODO: Add in new python version missing_ok=True)
	except FileNotFoundError:
		pass

	cutoff_time_str = str(sgh.settings.get_general_target_cutoff_time())
	python_executable = sgh.python_executable
	objective_function = r'--objective runtime'
	if not os.path.exists(r'Tmp/'): os.mkdir(r'Tmp/')

	feature_data_csv = sfdcsv.Sparkle_Feature_Data_CSV(feature_data_csv_path)
	bool_exists_missing_value = feature_data_csv.bool_exists_missing_value()
	if bool_exists_missing_value:
		print('c ****** WARNING: There are missing values in the feature data, and all missing values will be imputed as the mean value of all other non-missing values! ******')
		print('c Imputing all missing values starts ...')
		feature_data_csv.impute_missing_value_of_all_columns()
		print('c Imputing all missing values done!')
		impute_feature_data_csv_path = feature_data_csv_path + r'_' + sparkle_basic_help.get_time_pid_random_string() + r'_impute.csv'
		feature_data_csv.save_csv(impute_feature_data_csv_path)
		feature_data_csv_path = impute_feature_data_csv_path

	command_line = python_executable + r' ' + sgh.autofolio_path + r' ' + r'--performance_csv' + r' ' + performance_data_csv_path + r' ' + r'--feature_csv' + r' ' + feature_data_csv_path + r' ' + objective_function + r' ' + r'--runtime_cutoff' + r' ' + cutoff_time_str + r' ' + r'--tune' + r' ' + r'--save' + r' ' + sparkle_portfolio_selector_path + r' 1>> ' + sgh.sparkle_log_path + r' 2>> ' + sgh.sparkle_err_path

	# Write command line to log
	# TODO: Move output to Log/ or Output/<command>_<timestamp>/Log/
	print('Running command below:\n', command_line, file=open(sgh.sparkle_log_path, 'a+'))
	sl.add_output(sgh.sparkle_log_path, 'Command line used to construct portfolio through AutoFolio')

	#print 'c ' + command_line
	os.system(command_line)

	if bool_exists_missing_value:
		os.system(r'rm -f ' + impute_feature_data_csv_path)

	# Update data IDs associated with this selector
	write_selector_pd_id(Path(sparkle_portfolio_selector_path))
	write_selector_fd_id(Path(sparkle_portfolio_selector_path))

	return

