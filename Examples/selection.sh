#!/bin/bash

Commands/initialise.py

# Add instances (in CNF format) in a given directory, without running solvers or feature extractors yet
Commands/add_instances.py --run-solver-later --run-extractor-later Examples/Resources/Instances/PTN/

# Add solver with a wrapper containing the executable name of the solver and a string of command line parameters, without running the solver yet
# (the directory should contain both the executable and the wrapper)
Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/CSCCSat/

Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/Lingeling/

Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/MiniSAT/

Commands/add_feature_extractor.py --run-extractor-later Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle/

Commands/compute_features.py

Commands/run_solvers.py

Commands/construct_sparkle_portfolio_selector.py

Commands/generate_report.py

# After executing the above commands, an experimental report will be generated and located at Components/Sparkle-latex-generator/Sparkle_Report.pdf.
