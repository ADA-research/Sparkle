### Use Sparkle for algorithm selection

Initialise the Sparkle platform

`Commands/initialise.py`

Add instances (in this case in CNF format) in a given directory, without running solvers or feature extractors yet

`Commands/add_instances.py --run-solver-later --run-extractor-later Examples/Resources/Instances/PTN/`

Add solvers (here for SAT solving) with a wrapper containing the executable name of the solver and a string of command line parameters, without running the solvers yet

(the directory should contain both the executable and the wrapper)

`Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/CSCCSat/`

`Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/Lingeling/`

`Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/Solvers/MiniSAT/`

Similarly, add a feature extractor, without immediately running it on the instances

`Commands/add_feature_extractor.py --run-extractor-later Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle/`

Compute features for all the instances; add the `--parallel` option to run in parallel

`Commands/compute_features.py`

Run the solvers on all instances; add the `--parallel` option to run in parallel

`Commands/run_solvers.py`

Construct a portfolio selector, using the previously computed features and the results of running the solvers

`Commands/construct_sparkle_portfolio_selector.py`

Generate an experimental report detailing the experimental procedure and performance information; this will be located at `Components/Sparkle-latex-generator/Sparkle_Report.pdf`

`Commands/generate_report.py`

### Run the portfolio selector (e.g. on a test set)

Run the portfolio selector on a *single* testing instance; the result will be printed to the command line

`Commands/run_sparkle_portfolio_selector.py Examples/Resources/Instances/PTN2/plain7824.cnf`

Run the portfolio selector on a testing instance *set*

`Commands/run_sparkle_portfolio_selector.py Examples/Resources/Instances/PTN2/`

Generate an experimental report that includes the results on the test set, and as before the experimental procedure and performance information; this will be located at `Components/Sparkle-latex-generator/Sparkle_Report_For_Test.pdf`

`Commands/generate_report.py`

By default the `generate_report` command will create a report for the most recent instance set. To generate a report for an older instance set, the desired instance set can be specified with: `--test-case-directory Test_Cases/PTN2/`

