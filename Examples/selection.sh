#!/bin/bash

### Use Sparkle for algorithm selection

#### Initialise the Sparkle platform

sparkle initialise

#### Add instances

# Add instance files (in this case in CNF format) in a given directory, without running solvers or feature extractors yet

sparkle add_instances Examples/Resources/Instances/PTN/

#### Add solvers

# Add solvers (here for SAT solving) with a wrapper containing the executable name of the solver and a string of command line parameters, without running the solvers yet

# Each solver directory should contain the solver executable and a wrapper

sparkle add_solver --deterministic 0 Examples/Resources/Solvers/CSCCSat/

sparkle add_solver --deterministic 0 Examples/Resources/Solvers/PbO-CCSAT-Generic/

sparkle add_solver --deterministic 0 Examples/Resources/Solvers/MiniSAT/

#### Add feature extractor

# Similarly, add a feature extractor, without immediately running it on the instances

sparkle add_feature_extractor Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle/

#### Compute features

# Compute features for all the instances; add the `--parallel` option to run in parallel

sparkle compute_features

#### Run the solvers

# Run the solvers on all instances; add the `--parallel` option to run in parallel

sparkle run_solvers

#### Construct a portfolio selector

# To make sure feature computation and solver performance computation are done before constructing the portfolio use the sparkle wait command

sparkle wait

# Construct a portfolio selector, using the previously computed features and the results of running the solvers

sparkle construct_sparkle_portfolio_selector

#### Generate a report

# Generate an experimental report detailing the experimental procedure and performance information; this will be located at `Components/Sparkle-latex-generator/Sparkle_Report.pdf`

sparkle generate_report

### Run the portfolio selector (e.g. on a test set)

#### Run on a single instance

# Run the portfolio selector on a *single* testing instance; the result will be printed to the command line

sparkle run_sparkle_portfolio_selector Examples/Resources/Instances/PTN2/plain7824.cnf

#### Run on an instance set

# Run the portfolio selector on a testing instance *set*

sparkle run_sparkle_portfolio_selector Examples/Resources/Instances/PTN2/

#### Generate a report including results on the test set

# Wait for the portfolio selector to be done running on the testing instance set

sparkle wait

# Generate an experimental report that includes the results on the test set, and as before the experimental procedure and performance information; this will be located at `Components/Sparkle-latex-generator/Sparkle_Report_For_Test.pdf`

sparkle generate_report

# By default the `generate_report` command will create a report for the most recent instance set. To generate a report for an older instance set, the desired instance set can be specified with: `--test-case-directory Test_Cases/PTN2/`

