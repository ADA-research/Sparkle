"""Setup file for Sparkle."""
import os
from setuptools import setup, find_packages
from sparkle.about import version

setup(name="SparkleAI",
      version=version,
      url="https://github.com/thijssnelleman/Sparkle",
      author="Thijs Snelleman",
      author_email="fkt_sparkle@aim.rwth-aachen.de",
      keywords="ai sat planning",
      description="Sparkle is a Programming by Optimisation (PbO)-based problem-solving "
                  "platform designed to enable the widespread and effective use of PbO "
                  "techniques for improving the state-of-the-art in solving a broad "
                  "range of prominent AI problems, including SAT and AI Planning.",
      long_description=open("README.MD", "r").read() if os.path.exists("README.MD") else "",
      long_description_content_type="text/markdown",
      packages=find_packages(exclude=["tests"]),
      install_requires=[
          "numpy>=1.26.4",
          "pandas==2.2.2",
          "filelock==3.15.1",
          "tabulate==0.9.0",
          "tqdm==4.66.5",
          "RunRunner==0.1.6.4",
          # Reporting packages
          "plotly==5.23.0",
          "kaleido==0.2.1",
          # Autofolio packages
          "xgboost==2.0.3",
          "scikit-learn==1.3.2",
          "liac-arff==2.5.0",
          "smac==2.2.0"
      ],
      include_package_data=True,
      entry_points={"console_scripts": ["sparkle=sparkle.CLI.cli:main"], },)
