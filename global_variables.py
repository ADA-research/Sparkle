#!/usr/bin/env python3
"""Definitions of constants broadly used in Sparkle."""

import fcntl
import ast
from pathlib import Path

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


sparkle_special_string = "__@@SPARKLE@@__"

python_executable = "python3"

sparkle_slurm_settings_path = Path("Settings/sparkle_slurm_settings.txt")

sparkle_global_output_dir = Path("Output")

# Log that keeps track of which commands were executed and where output details can be
# found
sparkle_global_log_dir = Path("Log")
sparkle_global_log_path = sparkle_global_output_dir / "sparkle.log"

sparkle_tmp_path = Path("Tmp")

sparkle_err_path = sparkle_tmp_path / "sparkle_log.err"

sparkle_system_log_path = sparkle_global_log_dir / "sparkle_system_log_path.txt"

snapshot_dir = Path("Snapshots")
sparkle_algorithm_selector_dir = Path("Sparkle_Portfolio_Selector")

sparkle_algorithm_selector_name = f"sparkle_portfolio_selector{sparkle_special_string}"

sparkle_algorithm_selector_path =\
    sparkle_algorithm_selector_dir / sparkle_algorithm_selector_name

output_dir = Path("Output")
instance_dir = Path("Instances")
solver_dir = Path("Solvers")
extractor_dir = Path("Extractors")
feature_data_dir = Path("Feature_Data")
performance_data_dir = Path("Performance_Data")

sparkle_parallel_portfolio_dir = Path("Sparkle_Parallel_Portfolio")
sparkle_parallel_portfolio_name = Path("sparkle_parallel_portfolio")

sparkle_marginal_contribution_perfect_path =\
    sparkle_algorithm_selector_dir / "marginal_contribution_perfect.csv"

sparkle_marginal_contribution_actual_path =\
    sparkle_algorithm_selector_dir / "marginal_contribution_actual.csv"

sparkle_latex_dir = Path("Components/Sparkle-latex-generator")
sparkle_report_bibliography_path = sparkle_latex_dir / "SparkleReport.bib"

# Directories for CLI commands
configuration_output_general = output_dir / "Configuration"
parallel_portfolio_output_general = output_dir / "Parallel_Portfolio"
selection_output_general = output_dir / "Selection"
validation_output_general = output_dir / "Validation"

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

runsolver_dir = Path("Components/runsolver/src/")
runsolver_path = runsolver_dir / "runsolver"
autofolio_exec_path = Path("Components/AutoFolio/scripts/autofolio")

sparkle_solver_wrapper = "sparkle_solver_wrapper.py"
sparkle_extractor_wrapper = "sparkle_extractor_wrapper.py"

ablation_dir = Path("Components/ablationAnalysis-0.9.4/")

feature_data_csv_path = Path("Feature_Data/sparkle_feature_data.csv")
performance_data_csv_path = Path("Performance_Data/sparkle_performance_data.csv")
pap_sbatch_tmp_path = sparkle_tmp_path / "SBATCH_Parallel_Portfolio_Jobs"
run_solvers_sbatch_tmp_path = sparkle_tmp_path / "SBATCH_Solver_Jobs"

reference_list_dir = Path("Reference_Lists")
instance_list_postfix = "_instance_list.txt"
# NOTE: These data structures seem to be only written to / removed from but not read/used
# NOTE: This could be a bug though, should test before removing stuff!
extractor_nickname_list_path = reference_list_dir / "sparkle_extractor_nickname_list.txt"
extractor_list_path = reference_list_dir / "sparkle_extractor_list.txt"
extractor_feature_dim_list_path = reference_list_dir / "extractor_feature_dim_list.txt"
solver_nickname_list_path = reference_list_dir / "sparkle_solver_nickname_list.txt"

working_dirs = [instance_dir, output_dir, solver_dir, extractor_dir,
                feature_data_dir, performance_data_dir, reference_list_dir,
                sparkle_algorithm_selector_dir, sparkle_parallel_portfolio_dir]

file_storage_data_mapping = {solver_nickname_list_path: {},
                             extractor_list_path: [],
                             extractor_nickname_list_path: {},
                             extractor_feature_dim_list_path: {}
                             }

for data_path in file_storage_data_mapping.keys():
    if data_path.exists():
        with data_path.open("r+") as fo:
            fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
            file_storage_data_mapping[data_path] = ast.literal_eval(fo.read())

solver_nickname_mapping = file_storage_data_mapping[solver_nickname_list_path]
extractor_list = file_storage_data_mapping[extractor_list_path]
extractor_feature_vector_size_mapping =\
    file_storage_data_mapping[extractor_feature_dim_list_path]
