#!/usr/bin/env python3
"""Definitions of constants broadly used in Sparkle."""

import fcntl
import ast
from pathlib import Path
from pathlib import PurePath
from enum import Enum
import math

from sparkle import about
from sparkle.solver.solver import Solver
from CLI.help.reporting_scenario import ReportingScenario


# TODO: Handle different seed requirements; for the moment this is a dummy function
def get_seed() -> int:
    """Return a seed."""
    return 1


_latest_scenario = None


def latest_scenario() -> ReportingScenario:
    """Function to get the global latest scenario object."""
    global _latest_scenario
    if _latest_scenario is None:
        _latest_scenario = ReportingScenario()
    return _latest_scenario


sparkle_version = str(about.version)

sparkle_special_string = "__@@SPARKLE@@__"

python_executable = "python3"

sparkle_missing_value = math.nan

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

sparkle_marginal_contribution_perfect_path = (
    sparkle_algorithm_selector_dir / "margi_contr_perfect.csv")

sparkle_marginal_contribution_actual_path = (
    sparkle_algorithm_selector_dir / "margi_contr_actual.csv")

sparkle_last_test_file_name = "last_test_configured_default.txt"

sparkle_report_path = "Components/Sparkle-latex-generator/Sparkle_Report.pdf"
sparkle_latex_dir = Path("Components/Sparkle-latex-generator")
sparkle_report_bibliography_path = sparkle_latex_dir / "SparkleReport.bib"

# Directories for CLI commands
configuration_output_general = output_dir / "Configuration"
parallel_portfolio_output_general = output_dir / "Parallel_Portfolio"
selection_output_general = output_dir / "Selection"

# Raw output
rawdata_dir_name = Path("Raw_Data")
configuration_output_raw = configuration_output_general / rawdata_dir_name
parallel_portfolio_output_raw = parallel_portfolio_output_general / rawdata_dir_name
selection_output_raw = selection_output_general / rawdata_dir_name

# Analysis directories
analysis_dir_name = Path("Analysis")
configuration_output_analysis = configuration_output_general / analysis_dir_name
parallel_portfolio_output_analysis =\
    parallel_portfolio_output_general / analysis_dir_name
selection_output_analysis = selection_output_general / analysis_dir_name

runsolver_path = "Components/runsolver/src/runsolver"
sat_verifier_path = "Components/Sparkle-SAT-verifier/SAT"
autofolio_path = "Components/AutoFolio/scripts/autofolio"

sparkle_run_default_wrapper = "sparkle_run_default_wrapper.py"

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
solver_list_path = str(Solver.solver_list_path)
instance_list_file = Path("sparkle" + instance_list_postfix)
instance_list_path = Path(reference_list_dir / instance_list_file)

working_dirs = [instance_dir, output_dir, solver_dir, extractor_dir,
                feature_data_dir, performance_data_dir, reference_list_dir,
                sparkle_algorithm_selector_dir, sparkle_parallel_portfolio_dir,
                test_data_dir]

file_storage_data_mapping = {Solver.solver_list_path: Solver.get_solver_list(),
                             Path(solver_nickname_list_path): {},
                             Path(extractor_list_path): [],
                             Path(extractor_nickname_list_path): {},
                             Path(extractor_feature_vector_size_list_path): {},
                             instance_list_path: []}

for data_path in file_storage_data_mapping.keys():
    if data_path.exists():
        with data_path.open("r+") as fo:
            fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
            file_storage_data_mapping[data_path] = ast.literal_eval(fo.read())

solver_list = file_storage_data_mapping[Solver.solver_list_path]
solver_nickname_mapping = file_storage_data_mapping[Path(solver_nickname_list_path)]
extractor_list = file_storage_data_mapping[Path(extractor_list_path)]
extractor_nickname_mapping =\
    file_storage_data_mapping[Path(extractor_nickname_list_path)]
extractor_feature_vector_size_mapping =\
    file_storage_data_mapping[Path(extractor_feature_vector_size_list_path)]
instance_list = file_storage_data_mapping[instance_list_path]
