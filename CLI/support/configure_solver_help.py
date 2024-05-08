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
        return smac_run_obj.name
    elif smac_run_obj == PerformanceMeasure.QUALITY_ABSOLUTE_MINIMISATION:
        return "QUALITY"
    elif smac_run_obj == PerformanceMeasure.QUALITY_ABSOLUTE_MAXIMISATION:
        print("Warning: Performance measure not available for SMAC: {smac_run_obj}")
    else:
        print(f"Warning: Unknown SMAC objective {smac_run_obj}")
    return smac_run_obj
