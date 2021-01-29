#!/bin/bash

# Navigate to the Sparkle directory

# Initialise a new Sparkle platform
Commands/initialise.py

# Add instances from a given directory, without running solvers or feature extractors yet
# Both a set of training instances (here in the Examples/Resources/Instances/X/ directory), and a set of testing instances (here in the Examples/Resources/Instances/X2/ directory) should be provided
Commands/add_instances.py --run-solver-later --run-extractor-later Examples/Resources/Instances/X/
Commands/add_instances.py --run-solver-later --run-extractor-later Examples/Resources/Instances/X2/

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
Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/VRP_SISRs/

# Configure a solver with a given instance set.
# NOTE: Before running the next command, the option 'performance_measure = QUALITY_ABSOLUTE'
# must be set in 'Settings/sparkle_settings.ini'
Commands/configure_solver.py --solver Solvers/VRP_SISRs --instance-set-train Instances/X/

# Compare the configured solver and the default solver to each other
Commands/validate_configured_vs_default.py --solver Solvers/VRP_SISRs --instance-set-train Instances/X/ --instance-set-test Instances/X2/
# Testing a single instance set is also possible


# Generate an experimental report for the latest run of test_configured_solver_and_default_solver. It will be located at:
# Configuration_Reports/<datetime>_<solver_name>Sparkle-latex-generator-for-configuration/Sparkle_Report_for_Configuration.pdf.
Commands/generate_report.py --solver Solvers/VRP_SISRs
