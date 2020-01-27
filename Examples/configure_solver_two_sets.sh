#!/bin/bash

# Before starting Sparkle, please install the following packages with the specific versions:
# pip3 install ConfigSpace==0.3.9 --user
# pip3 install smac==0.6.0 --user
# pip3 install install git+https://github.com/mlindauer/ASlibScenario --user
# pip3 install sphinx-bootstrap-theme==0.6.0 --user

# Also, please install the following software:
# pdflatex, latex, bibtex, swig, gnuplot, gnuplot-x11




# Navigate to the Sparkle directory

# Initialise a new Sparkle platform
Commands/initialise.py

# Add instances from a given directory, without running solvers or feature extractors yet
# Both a set of training instances (here in the Examples/Resources/Instances/PTN/ directory), and a set of testing instances (here in the Examples/Resources/Instances/PTN2/ directory) should be provided
Commands/add_instances.py -run-solver-later -run-extractor-later Examples/Resources/Instances/PTN/
Commands/add_instances.py -run-solver-later -run-extractor-later Examples/Resources/Instances/PTN2/

# Add solver with a wrapper containing the executable name of the solver and a string of command line parameters, without running the solver yet
# The directory should contain the following:
# - The algorithm executable
# - A wrapper for Sparkle to call the algorithm named 'sparkle_run_default_wrapper.py'
# - A PCS file containing configurable parameters of the algorithm, their types and range
# - 'runsolver' executable
# - 'sparkle_run_generic_wrapper.py'
# - 'sprakle_smac_wrapper.py'
# Not needed:
# - A scenario file containing configuration settings (generated with defaults)
Commands/add_solver.py -run-solver-later -deterministic 0 Examples/Resources/Solvers/PbO-CCSAT-Generic/

# Configure a solver with a given instance set.
Commands/configure_solver.py -solver Solvers/PbO-CCSAT-Generic -instances-train Instances/PTN/

# Compare the configured solver and the default solver to each other
Commands/test_configured_solver_and_default_solver.py -solver Solvers/PbO-CCSAT-Generic -instances-train Instances/PTN/ -instances-test Instances/PTN2/
# Testing a single instance set is also possible


# Generate an experimental report for the latest run of test_configured_solver_and_default_solver. It will be located at:
# Configuration_Reports/<datetime>_<solver_name>Sparkle-latex-generator-for-configuration/Sparkle_Report_for_Configuration.pdf.
Commands/generate_report_for_configuration.py -solver Solvers/PbO-CCSAT-Generic
