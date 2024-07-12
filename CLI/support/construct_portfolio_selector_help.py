#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for portfolio selector construction."""
import subprocess
import sys
import shutil
from pathlib import Path

import global_variables as gv
import tools.general as tg
from sparkle.platform import file_help as sfh
from sparkle.structures import FeatureDataFrame
from sparkle.structures.performance_dataframe import PerformanceDataFrame
import sparkle_logging as sl
from sparkle.types.objective import PerformanceMeasure


def construct_sparkle_portfolio_selector(selector_path: Path,
                                         performance_data_csv_path: str,
                                         feature_data_csv_path: Path,
                                         flag_recompute: bool = False,
                                         selector_timeout: int = None) -> bool:
    """Create the Sparkle portfolio selector.

    Args:
        selector_path: Portfolio selector path.
        performance_data_csv_path: Performance data csv path.
        feature_data_csv_path: Feature data csv path.
        flag_recompute: Whether or not to recompute if the selector exists and no data
            was changed. Defaults to False.
        selector_timeout: The cuttoff time to configure the algorithm selector. If None
            uses the default selector configuration. Defaults to None.

    Returns:
        True if portfolio construction is successful.
    """
    # If the selector exists and the data didn't change, do nothing;
    # unless the recompute flag is set
    if selector_path.exists() and not flag_recompute:
        print("Portfolio selector already exists. Set the recompute flag to re-create.")

        # Nothing to do, success!
        return True

    # Remove contents of- and the selector path to ensure everything is (re)computed
    # for the new selector when required
    shutil.rmtree(selector_path.parent, ignore_errors=True)

    # (Re)create the path to the selector
    selector_path.parent.mkdir(parents=True, exist_ok=True)

    cutoff_time = gv.settings.get_general_target_cutoff_time()
    cutoff_time_minimum = 2

    # AutoFolio cannot handle cutoff time less than 2, adjust if needed
    if cutoff_time < cutoff_time_minimum:
        print(f"Warning: A cutoff time of {cutoff_time} is too small for AutoFolio, "
              f"setting it to {cutoff_time_minimum}")
        cutoff_time = cutoff_time_minimum

    cutoff_time_str = str(cutoff_time)
    python_executable = gv.python_executable
    perf_measure = gv.settings.get_general_sparkle_objectives()[0].PerformanceMeasure
    if perf_measure == PerformanceMeasure.RUNTIME:
        objective_function = "--objective runtime"
    elif perf_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION or\
            perf_measure == PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION:
        objective_function = "--objective solution_quality"
    else:
        print("ERROR: Unknown performance measure in "
              "construct_sparkle_portfolio_selector")
        sys.exit(-1)

    if not Path("Tmp").exists():
        Path("Tmp").mkdir()

    feature_data = FeatureDataFrame(feature_data_csv_path)
    bool_exists_missing_value = feature_data.has_missing_value()

    if bool_exists_missing_value:
        print("****** WARNING: There are missing values in the feature data, and all "
              "missing values will be imputed as the mean value of all other non-missing"
              " values! ******")
        print("Imputing all missing values...")
        feature_data.impute_missing_values()
        impute_feature_data_csv_path = Path(
            f"{feature_data_csv_path}_{tg.get_time_pid_random_string()}"
            "_impute.csv")
        feature_data.save_csv(impute_feature_data_csv_path)
        feature_data_csv_path = impute_feature_data_csv_path

    log_file = selector_path.parent.name + "_autofolio.out"
    err_file = selector_path.parent.name + "_autofolio.err"
    log_path_str = str(Path(sl.caller_log_dir / log_file))
    err_path_str = str(Path(sl.caller_log_dir / err_file))
    performance_data = PerformanceDataFrame(performance_data_csv_path)
    p_data_autofolio_path = performance_data.to_autofolio()
    f_data_autofolio_path = feature_data.to_autofolio()
    cmd_list = [python_executable, gv.autofolio_exec_path, "--performance_csv",
                p_data_autofolio_path, "--feature_csv", f_data_autofolio_path,
                objective_function, "--save", str(selector_path)]
    if selector_timeout is not None:
        cmd_list += ["--runtime_cutoff", cutoff_time_str, "--tune",
                     "--wallclock_limit", str(selector_timeout)]
    # Write command line to log
    print("Running command below:\n", " ".join([str(c) for c in cmd_list]),
          file=open(log_path_str, "a+"))
    sl.add_output(log_path_str, "Command line used to construct portfolio through "
                  "AutoFolio and associated output")
    sl.add_output(err_path_str,
                  "Error output from constructing portfolio through AutoFolio")

    process = subprocess.run(cmd_list,
                             stdout=Path(log_path_str).open("w+"),
                             stderr=Path(err_path_str).open("w+"))
    sfh.rmfiles("runhistory.json")

    if bool_exists_missing_value:
        sfh.rmfiles(impute_feature_data_csv_path)

    # Check if the selector was constructed successfully
    if process.returncode != 0 or not selector_path.is_file():
        print("Sparkle portfolio selector is not successfully constructed!")
        print("There might be some errors!")
        print("Standard output log:", log_path_str)
        print("Error output log:", err_path_str)
        sys.exit(-1)

    # Remove the data copy for AutoFolio
    p_data_autofolio_path.unlink()
    f_data_autofolio_path.unlink()
    return True
