"""Setup file for Sparkle."""
import os
from setuptools import setup, find_packages
from sparkle.about import version

setup(name="SparkleAI",
      version=version,
      url="https://github.com/thijssnelleman/Sparkle",
      author="Thijs Snelleman",
      author_email="fkt_sparkle@aim.rwth-aachen.de",
      description="Sparkle is a Programming by Optimisation (PbO)-based problem-solving platform designed to enable the widespread and effective use of PbO techniques for improving the state-of-the-art in solving a broad range of prominent AI problems, including SAT and AI Planning.",
      long_description=open("README.MD", "r").read() if os.path.exists("README.MD") else "",
      long_description_content_type="text/markdown",
      packages=find_packages(),
      entry_points={"console_scripts": ["sparkle=sparkle.cli:main"], },
)
