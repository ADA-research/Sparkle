#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
Software: 	Sparkle (Platform for evaluating empirical algorithms/solvers)

Authors: 	Chuan Luo, chuanluosaber@gmail.com
			Holger H. Hoos, hh@liacs.nl

Contact: 	Chuan Luo, chuanluosaber@gmail.com
'''

import os
import fcntl
from enum import Enum
from pathlib import Path
from pathlib import PurePath


# TODO: Handle different seed requirements; for the moment this is a dummy function
def get_seed():
	return 1


global settings

global latest_scenario

flag_first_call = True

global sparkle_maximum_int
sparkle_maximum_int = 2147483647

global sparkle_special_string
sparkle_special_string = r'__@@SPARKLE@@__'

global sparkle_missing_value
sparkle_missing_value = -(sparkle_maximum_int-1)

global sparkle_minimum_int
sparkle_minimum_int = -(sparkle_maximum_int-2)

global python_executable
python_executable = r'python3'
#python_executable = r'~/usr/python/python3.5.4/bin/python3'

global sparkle_default_settings_path
sparkle_default_settings_path = r'Settings/sparkle_default_settings.txt'

global sparkle_smac_settings_path
sparkle_smac_settings_path = r'Settings/sparkle_smac_settings.txt'

global sparkle_slurm_settings_path
sparkle_slurm_settings_path = r'Settings/sparkle_slurm_settings.txt'

global sparkle_global_output_dir
sparkle_global_output_dir = Path('Output')

# Log that keeps track of which commands were executed and where output details can be found
global sparkle_global_log_file
sparkle_global_log_file = 'sparkle.log'

global sparkle_global_log_dir
sparkle_global_log_dir = 'Log/'

global sparkle_global_log_path
sparkle_global_log_path = PurePath(sparkle_global_output_dir / sparkle_global_log_file)

global sparkle_tmp_path
sparkle_tmp_path = 'Tmp/'

global sparkle_log_path
sparkle_log_path = sparkle_tmp_path + r'sparkle_log.out'

global sparkle_err_path
sparkle_err_path = sparkle_tmp_path + r'sparkle_log.err'

global sparkle_system_log_path
sparkle_system_log_path = r'Log/sparkle_system_log_path.txt'

global sparkle_portfolio_selector_dir
sparkle_portfolio_selector_dir = 'Sparkle_Portfolio_Selector/'

global sparkle_portfolio_selector_name
sparkle_portfolio_selector_name = 'sparkle_portfolio_selector' + sparkle_special_string

global sparkle_portfolio_selector_path
sparkle_portfolio_selector_path = sparkle_portfolio_selector_dir + sparkle_portfolio_selector_name

global sparkle_marginal_contribution_perfect_path
sparkle_marginal_contribution_perfect_path = Path(sparkle_portfolio_selector_dir + 'margi_contr_perfect.csv')

global sparkle_marginal_contribution_actual_path
sparkle_marginal_contribution_actual_path = Path(sparkle_portfolio_selector_dir + 'margi_contr_actual.csv')

global sparkle_last_test_file_name
sparkle_last_test_file_name = r'last_test_configured_default.txt'

global sparkle_last_configuration_file_name
sparkle_last_configuration_file_name = r'last_configuration.txt'

global sparkle_report_path
sparkle_report_path = r'Components/Sparkle-latex-generator/Sparkle_Report.pdf'

global runsolver_path
global SAT_verifier_path
global autofolio_path
runsolver_path = r'Components/runsolver/src/runsolver'
SAT_verifier_path = r'Components/Sparkle-SAT-verifier/SAT'
autofolio_path = r'Components/AutoFolio-master/scripts/autofolio'

global smac_dir
smac_dir = 'Components/smac-v2.10.03-master-778/'

global sparkle_run_default_wrapper
sparkle_run_default_wrapper = r'sparkle_run_default_wrapper.py'

global sparkle_run_generic_wrapper
sparkle_run_generic_wrapper = r'sparkle_run_generic_wrapper.py'

global sparkle_run_configured_wrapper
sparkle_run_configured_wrapper = r'sparkle_run_configured_wrapper.sh'

global sparkle_smac_wrapper
sparkle_smac_wrapper = r'sparkle_smac_wrapper.py'


global ablation_dir
ablation_dir = r"Components/ablationAnalysis-0.9.4/"

global feature_data_csv_path
global feature_data_id_path
global performance_data_csv_path
global performance_data_id_path

feature_data_csv_path = r'Feature_Data/sparkle_feature_data.csv'
feature_data_id_path = 'Feature_Data/sparkle_feature_data.id'
performance_data_csv_path = r'Performance_Data/sparkle_performance_data.csv'
performance_data_id_path = 'Performance_Data/sparkle_performance_data.id'

global reference_list_dir
global extractor_nickname_list_path
global extractor_feature_vector_size_list_path
global extractor_list_path
global solver_nickname_list_path
global solver_list_path
global instance_list_path

reference_list_dir = Path('Reference_Lists/')
instance_list_postfix = '_instance_list.txt'
extractor_nickname_list_path = str(reference_list_dir) + '/sparkle_extractor_nickname_list.txt'
extractor_list_path = str(reference_list_dir) + '/sparkle_extractor_list.txt'
extractor_feature_vector_size_list_path = str(reference_list_dir) + '/extractor_feature_vector_size_list.txt'
solver_nickname_list_path = str(reference_list_dir) + '/sparkle_solver_nickname_list.txt'
solver_list_path = str(reference_list_dir) + '/sparkle_solver_list.txt'
instance_list_file = Path('sparkle' + instance_list_postfix)
instance_list_path = Path(reference_list_dir / instance_list_file)

global solver_list
global solver_nickname_mapping
global extractor_list
global extractor_feature_vector_size_mapping
global extractor_nickname_mapping
global instance_list

solver_list = []
solver_nickname_mapping = {}
extractor_list = []
extractor_nickname_mapping = {}
extractor_feature_vector_size_mapping = {}
instance_list = []

if os.path.exists(extractor_nickname_list_path):
	fo = open(extractor_nickname_list_path, 'r+')
	fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
	while True:
		myline = fo.readline()
		myline = myline.strip()
		if not myline: break
		mylist = myline.split()
		extractor_nickname_mapping[mylist[0]] = mylist[1]
	fo.close()

if os.path.exists(extractor_feature_vector_size_list_path):
	fo = open(extractor_feature_vector_size_list_path, 'r+')
	fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
	while True:
		myline = fo.readline().strip()
		if not myline: break
		mylist = myline.split()
		extractor_feature_vector_size_mapping[mylist[0]] = int(mylist[1])
	fo.close()

if os.path.exists(extractor_list_path):
	fo = open(extractor_list_path, 'r+')
	fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
	while True:
		myline = fo.readline()
		myline = myline.strip()
		if not myline: break
		extractor_list.append(myline)
	fo.close()

if os.path.exists(solver_nickname_list_path):
	fo = open(solver_nickname_list_path, 'r+')
	fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
	while True:
		myline = fo.readline()
		myline = myline.strip()
		if not myline: break
		mylist = myline.split()
		solver_nickname_mapping[mylist[0]] = mylist[1]
	fo.close()

if os.path.exists(solver_list_path):
	fo = open(solver_list_path, 'r+')
	fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
	while True:
		myline = fo.readline()
		if not myline: break
		myline = myline.strip()
		mylist = myline.split()
		solver_list.append(mylist[0])
	fo.close()

if os.path.exists(str(instance_list_path)):
	fo = open(str(instance_list_path), 'r+')
	fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
	while True:
		myline = fo.readline()
		myline = myline.strip()
		if not myline: break
		instance_list.append(myline)
	fo.close()

