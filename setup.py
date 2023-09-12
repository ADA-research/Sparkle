"""Setup file for Sparkle."""
from setuptools import setup, find_packages

from Commands import about

setup(name="sparkle",
      version=about.__version__,
      packages=find_packages())
