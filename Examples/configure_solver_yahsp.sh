#!/bin/bash

# Navigate to the Sparkle directory

# Initialise a new Sparkle platform
Commands/initialise.py

# Add instances from a given directory, without running solvers or feature extractors yet
# Both a set of training instances (here in the Examples/Resources/Instances/Depots_train_few/ directory), and a set of testing instances (here in the Examples/Resources/Instances/Depots_test_few/ directory) should be provided
Commands/add_instances.py --run-solver-later --run-extractor-later Examples/Resources/Instances/Depots_train_few/
Commands/add_instances.py --run-solver-later --run-extractor-later Examples/Resources/Instances/Depots_test_few/

# Add solver with a wrapper containing the executable name of the solver and a string of command line parameters, without running the solver yet
# The directory should contain the following:
# - The algorithm executable (cpt_yahsp)
# - A PCS file (params.pcs) containing configurable parameters of the algorithm, their types, range, and default value
# - 'runsolver' executable
# - 'sprakle_smac_wrapper.py' - A wrapper to use by the configurator to call your algorithm
# - Files required by the specific problem/solver, here: 'generate_domain_file.py', HEADER, OP1, OP2, OP3, OP4, OP5, PREDICATES
Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/Yahsp3/

# Configure a solver with a given instance set.
Commands/configure_solver.py --solver Solvers/Yahsp3 --instance-set-train Instances/Depots_train_few/

# Compare the configured solver and the default solver to each other
Commands/validate_configured_vs_default.py --solver Solvers/Yahsp3 --instance-set-train Instances/Depots_train_few/ --instance-set-test Instances/Depots_test_few/

# Generate an experimental report for the latest run of test_configured_solver_and_default_solver. It will be located at:
# Configuration_Reports/<datetime>_<solver_name>Sparkle-latex-generator-for-configuration/Sparkle_Report_for_Configuration.pdf.
Commands/generate_report_for_configuration.py --solver Solvers/Yahsp3

# Alternatively generate a report for a given train and test set (for which test_configured_solver_and_default_solver has been executed previously)
Commands/generate_report_for_configuration.py --solver Solvers/Yahsp3 --instance-set-train Instances/Depots_train_few/ --instance-set-test Instances/Depots_test_few/
