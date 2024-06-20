#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Helper functions for interaction with Slurm."""
from __future__ import annotations
from pathlib import Path

import global_variables as gv


def get_slurm_options_list(path_modifier: str = None) -> list[str]:
    """Return a list with the Slurm options given in the Slurm settings file.

    Args:
      path_modifier: An optional prefix path for the sparkle Slurm settings.
        Default is None which is interpreted as an empty prefix.

    Returns:
      List of strings (the actual Slurm settings, e.g., ['--mem-per-cpu=3000']).
    """
    if path_modifier is None:
        path_modifier = ""

    slurm_options_list = []
    sparkle_slurm_settings_path = Path(path_modifier) / gv.sparkle_slurm_settings_path
    with sparkle_slurm_settings_path.open("r") as settings_file:
        slurm_options_list.extend([line.strip() for line in settings_file.readlines()
                                   if line.startswith("-")])

    return slurm_options_list
