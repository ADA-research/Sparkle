"""Setup file for Sparkle."""
from pathlib import Path
from setuptools import setup, find_packages
from sparkle.about import version

# read the contents of README file
long_description = (Path(__file__).parent / "README.md").read_text()

setup(name="Sparkle",
      version=version,
      url="https://github.com/ADA-research/Sparkle",
      author="Thijs Snelleman",
      author_email="fkt_sparkle@aim.rwth-aachen.de",
      keywords="ai sat planning",
      description="Sparkle is a Programming by Optimisation (PbO)-based problem-solving "
                  "platform designed to enable the widespread and effective use of PbO "
                  "techniques for improving the state-of-the-art in solving a broad "
                  "range of prominent AI problems, including SAT and AI Planning.",
      long_description=long_description,
      long_description_content_type="text/markdown",
      packages=find_packages(exclude=["tests"]),
      install_requires=[
          "numpy>=1.26.4",
          "pandas==2.2.2",
          "filelock==3.15.1",
          "tabulate==0.9.0",
          "pytermgui==7.7.2",
          "tqdm==4.66.5",
          "smac==2.2.0",
          "RunRunner==0.2.0.3",
          "asf-lib==0.0.1.15",
          # ASF requirements
          "xgboost==2.1.3",
          "scikit-learn==1.3.2",
          # Reporting packages
          "plotly==5.24.1",
          "kaleido==0.2.1",
      ],
      include_package_data=True,
      # Setup 'sparkle' as a CLI command
      entry_points={"console_scripts": ["sparkle=sparkle.CLI._cli_:main"], },)
