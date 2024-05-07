#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for algorithm configuration."""
import global_variables as gv
from sparkle.types.objective import PerformanceMeasure


def get_smac_run_obj() -> str:
    """Return the SMAC run objective.

    Returns:
        A string that represents the run objective set in the settings.
    """
    # Get smac_run_obj from general settings
    smac_run_obj = gv.settings.get_general_sparkle_objectives()[0].PerformanceMeasure

    # Convert to SMAC format
    if smac_run_obj == PerformanceMeasure.RUNTIME:
        smac_run_obj = smac_run_obj.name
    elif smac_run_obj == PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION:
        smac_run_obj = "QUALITY"
    elif smac_run_obj == PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION:
        print("Warning: Performance measure not available for SMAC: {smac_run_obj}")
    else:
        print("Warning: Unknown performance measure", smac_run_obj,
              "! This is a bug in Sparkle.")

    return smac_run_obj


def get_smac_settings() -> tuple[str]:
    """Return the SMAC settings.

    Returns:
        A tuple containing all settings important to SMAC.
    """
    smac_each_run_cutoff_length = gv.settings.get_smac_target_cutoff_length()
    smac_run_obj = get_smac_run_obj()
    smac_whole_time_budget = gv.settings.get_config_budget_per_run()
    smac_each_run_cutoff_time = gv.settings.get_general_target_cutoff_time()
    num_of_smac_run = gv.settings.get_config_number_of_runs()
    num_of_smac_run_in_parallel = gv.settings.get_slurm_number_of_runs_in_parallel()

    return (smac_run_obj, smac_whole_time_budget, smac_each_run_cutoff_time,
            smac_each_run_cutoff_length, num_of_smac_run, num_of_smac_run_in_parallel)
