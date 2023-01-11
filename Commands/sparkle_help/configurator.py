#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Configurator class to use different configurators like SMAC."""

from pathlib import Path


class Configurator:
    """Generic class to use different configurators like SMAC."""

    def __init__(self, configurator_path: Path):
        """Initialize Configurator."""
        self.configurator_path = configurator_path
        return

    def add_instances(self, instance_directory: Path):
        """Add instances."""
        # Either copy instances to configurator directory or remember current location
        return

    def add_solver(self):
        """Add solver."""
        # Either copy solver to configurator directory or remember current location
        return

    def create_script(self):
        """Create sbatch script."""
        # Add SBTACH options
        sbatch_options = self.__get_sbatch_options__()

        # Add params list
        params_list = self.__get_params_list__()

        # Add srun command
        srun_command = self.__get_srun_command__()

        file_content = sbatch_options + params_list + srun_command

        return file_content

    def configure(self):
        """Run sbatch script."""
        # Submit SBATCH script
        return

    def __get_sbatch_options__(self):
        """Get sbtach options."""
        return

    def __get_params_list__(self):
        """Get parameter list."""
        return

    def __get_srun_command__(self):
        """Get srun command."""
        return
