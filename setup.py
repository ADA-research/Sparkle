"""Setup file for Sparkle."""
from setuptools import setup, find_packages

from global_variables import sparkle_version

setup(name="sparkle",
      version=sparkle_version,
      packages=find_packages())
