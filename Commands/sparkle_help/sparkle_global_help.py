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
from pathlib import Path
from pathlib import PurePath


# TODO: Handle different seed requirements; for the moment this is a dummy function
def get_seed():
	return 1


flag_first_call = True

sparkle_maximum_int = 2147483647

sparkle_special_string = r'__@@SPARKLE@@__'

sparkle_missing_value = -(sparkle_maximum_int-1)

sparkle_minimum_int = -(sparkle_maximum_int-2)

python_executable = r'python3'

sparkle_default_settings_path = r'Settings/sparkle_default_settings.txt'

sparkle_smac_settings_path = r'Settings/sparkle_smac_settings.txt'

sparkle_slurm_settings_path = r'Settings/sparkle_slurm_settings.txt'

sparkle_global_output_dir = Path('Output')

# Log that keeps track of which commands were executed and where output details can be found
sparkle_global_log_file = 'sparkle.log'

sparkle_global_log_dir = 'Log/'

sparkle_global_log_path = PurePath(sparkle_global_output_dir / sparkle_global_log_file)

sparkle_tmp_path = 'Tmp/'

sparkle_log_path = sparkle_tmp_path + r'sparkle_log.out'

sparkle_err_path = sparkle_tmp_path + r'sparkle_log.err'

sparkle_system_log_path = r'Log/sparkle_system_log_path.txt'

sparkle_portfolio_selector_dir = 'Sparkle_Portfolio_Selector/'

sparkle_portfolio_selector_name = 'sparkle_portfolio_selector' + sparkle_special_string

sparkle_portfolio_selector_path = sparkle_portfolio_selector_dir + sparkle_portfolio_selector_name

sparkle_marginal_contribution_perfect_path = Path(sparkle_portfolio_selector_dir + 'margi_contr_perfect.csv')

sparkle_marginal_contribution_actual_path = Path(sparkle_portfolio_selector_dir + 'margi_contr_actual.csv')

sparkle_last_test_file_name = r'last_test_configured_default.txt'

sparkle_last_configuration_file_name = r'last_configuration.txt'

sparkle_report_path = r'Components/Sparkle-latex-generator/Sparkle_Report.pdf'

runsolver_path = r'Components/runsolver/src/runsolver'
SAT_verifier_path = r'Components/Sparkle-SAT-verifier/SAT'
autofolio_path = r'Components/AutoFolio-master/scripts/autofolio'

smac_dir = 'Components/smac-v2.10.03-master-778/'

sparkle_run_default_wrapper = r'sparkle_run_default_wrapper.py'

sparkle_run_generic_wrapper = r'sparkle_run_generic_wrapper.py'

sparkle_run_configured_wrapper = r'sparkle_run_configured_wrapper.sh'

sparkle_smac_wrapper = r'sparkle_smac_wrapper.py'


ablation_dir = r"Components/ablationAnalysis-0.9.4/"


feature_data_csv_path = r'Feature_Data/sparkle_feature_data.csv'
feature_data_id_path = 'Feature_Data/sparkle_feature_data.id'
performance_data_csv_path = r'Performance_Data/sparkle_performance_data.csv'
performance_data_id_path = 'Performance_Data/sparkle_performance_data.id'


reference_list_dir = Path('Reference_Lists/')
instance_list_postfix = '_instance_list.txt'
extractor_nickname_list_path = str(reference_list_dir) + '/sparkle_extractor_nickname_list.txt'
extractor_list_path = str(reference_list_dir) + '/sparkle_extractor_list.txt'
extractor_feature_vector_size_list_path = str(reference_list_dir) + '/extractor_feature_vector_size_list.txt'
solver_nickname_list_path = str(reference_list_dir) + '/sparkle_solver_nickname_list.txt'
solver_list_path = str(reference_list_dir) + '/sparkle_solver_list.txt'
instance_list_file = Path('sparkle' + instance_list_postfix)
instance_list_path = Path(reference_list_dir / instance_list_file)


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

