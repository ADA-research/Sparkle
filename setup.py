"""Setup file for Sparkle."""
from setuptools import setup, find_packages

from CLI.sparkle_help.sparkle_global_help import sparkle_version

setup(name="sparkle",
      version=sparkle_version,
      packages=find_packages())
