### Use Sparkle for algorithm selection

#### Initialise the Sparkle platform

`Commands/initialise.py`

#### Add instances

Add instances in a given directory, without running solvers or feature extractors yet. The directory should contain a file `sparkle_instance_list.txt` describing which files together form an instance.

`Commands/add_instances.py --run-solver-later --run-extractor-later Examples/Resources/Instances/CCAG/`

#### Add solvers

Add solvers with a wrapper containing the executable name of the solver and a string of command line parameters, without running the solvers yet

(the directory should contain both the executable and the wrapper)

`Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/CCAG/Solvers/TCA/`

`Commands/add_solver.py --run-solver-later --deterministic 0 Examples/Resources/CCAG/Solvers/FastCA/`

#### Add feature extractor

Similarly, add a feature extractor, without immediately running it on the instances

`Commands/add_feature_extractor.py --run-extractor-later Examples/Resources/CCAG/Extractors/CCAG-features_sparkle/`

#### Compute features

Compute features for all the instances; add the `--parallel` option to run in parallel

`Commands/compute_features.py`

#### Run the solvers

Run the solvers on all instances; add the `--parallel` option to run in parallel. For the CCAG (Constrained Covering Array Generation) problem we measure the quality performance by setting the `--performance-measure` option.

`Commands/run_solvers.py --performance-measure QUALITY_ABSOLUTE`

#### Create a portfolio selector

Construct a portfolio selector, using the previously computed features and the results of running the solvers. We again set the performance measure to quality, to avoid needing this for every command it can also be set in `Settings/sparkle_settings.ini`.

`Commands/construct_sparkle_portfolio_selector.py --performance-measure QUALITY_ABSOLUTE`

#### [Coming soon] Generate a report

***This is not yet implemented for quality performance***

Generate an experimental report detailing the experimental procedure and performance information; this will be located at `Components/Sparkle-latex-generator/Sparkle_Report.pdf`

`Commands/generate_report.py --performance-measure QUALITY_ABSOLUTE`

### [Coming soon] Run on the test set

Run the portfolio selector on a single testing instance; the result will be printed to the command line

`Commands/run_sparkle_portfolio_selector.py Examples/Resources/Instances/CCAG2/ --performance-measure QUALITY_ABSOLUTE`

Run the portfolio selector on a testing instance *set*

`Commands/run_sparkle_portfolio_selector.py Examples/Resources/Instances/CCAG2/ --performance-measure QUALITY_ABSOLUTE`

Generate an experimental report detailing the results on the test set, and as before the experimental procedure and performance information; this will be located at `Components/Sparkle-latex-generator/Sparkle_Report_For_Test.pdf`

`Commands/generate_report_for_test.py Test_Cases/CCAG2/ --performance-measure QUALITY_ABSOLUTE`

