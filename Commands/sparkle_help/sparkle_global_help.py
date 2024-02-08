#!/usr/bin/env python3
"""Definitions of constants broadly used in Sparkle."""

import fcntl
import ast
from pathlib import Path
from pathlib import PurePath
from enum import Enum
from sparkle import about


# TODO: Handle different seed requirements; for the moment this is a dummy function
def get_seed() -> int:
    """Return a seed."""
    return 1


latest_scenario = None

sparkle_version = str(about.about_info["version"])

sparkle_maximum_int = 2147483647
sparkle_missing_value = -(sparkle_maximum_int - 1)
sparkle_minimum_int = -(sparkle_maximum_int - 2)

sparkle_special_string = "__@@SPARKLE@@__"

python_executable = "python3"

sparkle_default_settings_path = "Settings/sparkle_default_settings.txt"
sparkle_smac_settings_path = "Settings/sparkle_smac_settings.txt"
sparkle_slurm_settings_path = "Settings/sparkle_slurm_settings.txt"

sparkle_global_output_dir = Path("Output")


class ReportType(str, Enum):
    """enum for separating different types of reports."""
    ALGORITHM_SELECTION = "algorithm_selection"
    ALGORITHM_CONFIGURATION = "algorithm_configuration"
    PARALLEL_PORTFOLIO = "parallel_portfolio"


# Log that keeps track of which commands were executed and where output details can be
# found
sparkle_global_log_file = "sparkle.log"

sparkle_global_log_dir = "Log/"

sparkle_global_log_path = PurePath(sparkle_global_output_dir / sparkle_global_log_file)

sparkle_tmp_path = "Tmp/"

sparkle_log_path = sparkle_tmp_path + "sparkle_log.out"
sparkle_err_path = sparkle_tmp_path + "sparkle_log.err"

sparkle_system_log_path = "Log/sparkle_system_log_path.txt"

snapshot_dir = Path("Snapshots/")
sparkle_algorithm_selector_dir = Path("Sparkle_Portfolio_Selector/")

sparkle_algorithm_selector_name = f"sparkle_portfolio_selector{sparkle_special_string}"

sparkle_algorithm_selector_path = (
    sparkle_algorithm_selector_dir / sparkle_algorithm_selector_name)

output_dir = Path("Output/")
instance_dir = Path("Instances/")
solver_dir = Path("Solvers/")
test_data_dir = Path("Test_Data/")
extractor_dir = Path("Extractors/")
feature_data_dir = Path("Feature_Data/")
performance_data_dir = Path("Performance_Data")

sparkle_parallel_portfolio_dir = Path("Sparkle_Parallel_Portfolio/")
sparkle_parallel_portfolio_name = Path("sparkle_parallel_portfolio/")

sparkle_parallel_portfolio_path = (
    sparkle_parallel_portfolio_dir / sparkle_parallel_portfolio_name)

sparkle_marginal_contribution_perfect_path = (
    sparkle_algorithm_selector_dir / "margi_contr_perfect.csv")

sparkle_marginal_contribution_actual_path = (
    sparkle_algorithm_selector_dir / "margi_contr_actual.csv")

sparkle_last_test_file_name = "last_test_configured_default.txt"

sparkle_report_path = "Components/Sparkle-latex-generator/Sparkle_Report.pdf"

runsolver_path = "Components/runsolver/src/runsolver"
sat_verifier_path = "Components/Sparkle-SAT-verifier/SAT"
autofolio_path = "Components/AutoFolio/scripts/autofolio"

smac_dir = "Components/smac-v2.10.03-master-778/"
smac_results_dir = smac_dir + "results/"

sparkle_run_default_wrapper = "sparkle_run_default_wrapper.py"

sparkle_run_generic_wrapper = "sparkle_run_generic_wrapper.py"

sparkle_run_configured_wrapper = "sparkle_run_configured_wrapper.sh"

smac_target_algorithm = "smac_target_algorithm.py"
sparkle_solver_wrapper = "sparkle_solver_wrapper.py"

ablation_dir = "Components/ablationAnalysis-0.9.4/"

feature_data_csv_path = "Feature_Data/sparkle_feature_data.csv"
feature_data_id_path = "Feature_Data/sparkle_feature_data.id"
performance_data_csv_path = "Performance_Data/sparkle_performance_data.csv"
performance_data_id_path = "Performance_Data/sparkle_performance_data.id"
pap_performance_data_tmp_path = Path("Performance_Data/Tmp_PaP/")
pap_sbatch_tmp_path = Path(f"{sparkle_tmp_path}SBATCH_Parallel_Portfolio_Jobs/")
run_solvers_sbatch_tmp_path = Path(f"{sparkle_tmp_path}SBATCH_Solver_Jobs/")

reference_list_dir = Path("Reference_Lists/")
instance_list_postfix = "_instance_list.txt"
extractor_nickname_list_path = (
    f"{str(reference_list_dir)}/sparkle_extractor_nickname_list.txt")
extractor_list_path = str(reference_list_dir) + "/sparkle_extractor_list.txt"
extractor_feature_vector_size_list_path = (
    f"{str(reference_list_dir)}/extractor_feature_vector_size_list.txt")
solver_nickname_list_path = str(reference_list_dir) + "/sparkle_solver_nickname_list.txt"
solver_list_path = str(reference_list_dir) + "/sparkle_solver_list.txt"
instance_list_file = Path("sparkle" + instance_list_postfix)
instance_list_path = Path(reference_list_dir / instance_list_file)

working_dirs = [instance_dir, output_dir, solver_dir, extractor_dir,
                feature_data_dir, performance_data_dir, reference_list_dir,
                sparkle_algorithm_selector_dir, sparkle_parallel_portfolio_dir,
                test_data_dir]

solver_list = []
solver_nickname_mapping = {}
extractor_list = []
extractor_nickname_mapping = {}
extractor_feature_vector_size_mapping = {}
instance_list = []

file_storage_data_mapping = {Path(solver_list_path): solver_list,
                             Path(solver_nickname_list_path): solver_nickname_mapping,
                             Path(extractor_list_path): extractor_list,
                             Path(extractor_nickname_list_path): extractor_nickname_mapping,
                             Path(extractor_feature_vector_size_list_path): extractor_feature_vector_size_mapping,
                             instance_list_path: instance_list}

if Path(solver_list_path).exists():
    with Path(solver_list_path).open("r+") as fo:
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        solver_list = ast.literal_eval(fo.read())
        #lines = [line.strip() for line in fo.readlines()]
        #solver_list.extend(lines)

if Path(solver_nickname_list_path).exists():
    with Path(solver_nickname_list_path).open("r+") as fo:
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        solver_nickname_mapping = ast.literal_eval(fo.read())
        #lines = [line.strip().split() for line in fo.readlines()]
        #for nickname, solver in lines:
        #    solver_nickname_mapping[nickname] = solver

if Path(extractor_list_path).exists():
    with Path(extractor_list_path).open("r+") as fo:
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        extractor_list = ast.literal_eval(fo.readlines())
        #lines = [line.strip() for line in fo.readlines()]
        #extractor_list.extend(lines)

if Path(extractor_nickname_list_path).exists():
    with Path(extractor_nickname_list_path).open("r+") as fo:
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        extractor_nickname_mapping = ast.literal_eval(fo.read())
        #lines = [line.strip().split() for line in fo.readlines()]
        #for nickname, extractor in lines:
        #    extractor_nickname_mapping[nickname] = extractor

if Path(extractor_feature_vector_size_list_path).exists():
    with Path(extractor_feature_vector_size_list_path).open("r+") as fo:
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        extractor_feature_vector_size_mapping = ast.literal_eval(fo.read())
        #lines = [line.strip().split() for line in fo.readlines()]
        #for extractor, vector_size in lines:
        #    extractor_feature_vector_size_mapping[extractor] = int(vector_size)

if instance_list_path.exists():
    with instance_list_path.open("r+") as fo:
        fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
        instance_list = ast.literal_eval(fo.read())
        #lines = [line.strip() for line in fo.readlines()]
        #instance_list.extend(lines)
