#!/usr/bin/env python3
"""Definitions of constants broadly used in Sparkle."""

import fcntl
import ast
from pathlib import Path, PurePath

from sparkle.CLI.help.reporting_scenario import ReportingScenario


# TODO: Handle different seed requirements; for the moment this is a dummy function
def get_seed() -> int:
    """Return a seed."""
    return 1


__latest_scenario = None


def latest_scenario() -> ReportingScenario:
    """Function to get the global latest scenario object."""
    global __latest_scenario
    if __latest_scenario is None:
        __latest_scenario = ReportingScenario()
    return __latest_scenario


__settings = None

# Add (property?) method for settings?

output_dir = Path("Output")
snapshot_dir = Path("Snapshots")
feature_data_dir = Path("Feature_Data")
performance_data_dir = Path("Performance_Data")

# Log that keeps track of which commands were executed and where output details can be
# found
sparkle_global_log_dir = Path("Log")
sparkle_global_log_path = output_dir / "sparkle.log"

sparkle_latex_dir = Path("sparkle/Components/Sparkle-latex-source")
sparkle_report_bibliography_path = sparkle_latex_dir / "SparkleReport.bib"

# Default settings
default_settings_path = PurePath("sparkle/Components/sparkle_settings.ini")

# Directories for CLI commands
configuration_output_general = output_dir / "Configuration"
parallel_portfolio_output_general = output_dir / "Parallel_Portfolio"
selection_output_general = output_dir / "Selection"
validation_output_general = output_dir / "Validation"
ablation_output_general = output_dir / "Ablation"

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

feature_data_csv_path = feature_data_dir / "sparkle_feature_data.csv"
performance_data_csv_path = performance_data_dir / "sparkle_performance_data.csv"

reference_list_dir = Path("Reference_Lists")
# NOTE: These data structures seem to be only written to / removed from but not read/used
# NOTE: This could be a bug though, should test before removing stuff!
extractor_nickname_list_path = reference_list_dir / "sparkle_extractor_nickname_list.txt"
solver_nickname_list_path = reference_list_dir / "sparkle_solver_nickname_list.txt"
instances_nickname_path = reference_list_dir / "sparkle_instance_nickname_list.txt"

working_dirs = [output_dir,
                feature_data_dir, performance_data_dir, reference_list_dir]

file_storage_data_mapping = {solver_nickname_list_path: {},
                             instances_nickname_path: {},
                             extractor_nickname_list_path: {}
                             }

for data_path in file_storage_data_mapping.keys():
    if data_path.exists():
        with data_path.open("r+") as fo:
            fcntl.flock(fo.fileno(), fcntl.LOCK_EX)
            file_storage_data_mapping[data_path] = ast.literal_eval(fo.read())

solver_nickname_mapping = file_storage_data_mapping[solver_nickname_list_path]
