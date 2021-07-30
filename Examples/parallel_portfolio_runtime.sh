#!/bin/bash

### Use Sparkle for parallel algorithm portfolio
### This the runtime example uses runtime as measurement

#### Initialise the Sparkle platform

Commands/initialise.py

#### Add instances 

# Add instances (in this case for the portfolio) in a given directory, without running solvers or feature extractors

Commands/add_instances.py --run-solver-later --run-extractor-later Examples/Resources/Instances/PTN/

#### Add solvers

# Add a configurable solver (here for vehicle routing) with a wrapper containing the executable name of the solver and a string of command line parameters, without running the solver yet

# The solver directory should contain the solver executable, the `sparkle_smac_wrapper.py` wrapper, and a `.pcs` file describing the configurable parameters

Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/CSCCSat/
Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/MiniSAT/
Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/PbO-CCSAT-Generic/

# If needed solvers can also include additional files or scripts in their directory, but keeping additional files to a minimum speeds up copying.

#### Construct the portfolio

# The construction uses all solvers and keeps in mind the given settings 
# Without specifying --solver` all solvers will be added, if you want, for example, only a subset of solvers you can use --solver Solvers/CSCCSat Solvers/MiniSAT

Commands/construct_sparkle_parallel_portfolio.py --nickname runtime_experiment

#### Run the portfolio 

# add --portfolio-name to specify a portfolio otherwise it will select the latest constructed portfolio

Commands/run_sparkle_parallel_portfolio.py --instance-paths Instances/PTN/ --portfolio-name runtime_experiment

#### Generate the report

# The report details the experimental procedure and performance information; this will be located at Components/Sparkle-latex-generator/Sparkle_Report.pdf

Commands/generate_report.py
