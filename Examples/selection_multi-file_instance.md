# Use Sparkle for algorithm selection with multi-file instances

## Initialise the Sparkle platform

`sparkle initialise`

## Add instances

Add instance files in a given directory, without running solvers or feature extractors yet. In addition to the instance files, the directory should contain a file `sparkle_instance_list.txt` where each line contains a space separated list of files that together form an instance.

`sparkle add_instances Examples/Resources/CCAG/Instances/CCAG/`

## Add solvers

Add solvers (here for the constrained covering array generation (CCAG) problem) with a wrapper containing the executable name of the solver and a string of command line parameters, without running the solvers yet

Each solver directory should contain the solver executable and a wrapper

`sparkle add_solver --deterministic 0 Examples/Resources/CCAG/Solvers/TCA/`

`sparkle add_solver --deterministic 0 Examples/Resources/CCAG/Solvers/FastCA/`

## Add feature extractor

Similarly, add a feature extractor, without immediately running it on the instances

`sparkle add_feature_extractor Examples/Resources/CCAG/Extractors/CCAG-features_sparkle/`

## Compute features

Compute features for all the instances; add the `--parallel` option to run in parallel

`sparkle compute_features`

## Run the solvers

Run the solvers on all instances; add the `--parallel` option to run in parallel. For the CCAG (Constrained Covering Array Generation) problem we measure the absolute quality performance by setting the `--performance-measure` option, to avoid needing this for every command it can also be set in `Settings/sparkle_settings.ini`.

`sparkle run_solvers --performance-measure QUALITY_ABSOLUTE`

## Construct a portfolio selector

To make sure feature computation and solver performance computation are done before constructing the portfolio use the `wait` command

`sparkle wait`

Construct a portfolio selector, using the previously computed features and the results of running the solvers. We again set the performance measure to absolute quality.

`sparkle construct_sparkle_portfolio_selector --performance-measure QUALITY_ABSOLUTE`

## [Coming soon] Generate a report

***This is not yet implemented for quality performance***

Generate an experimental report detailing the experimental procedure and performance information; this will be located at `Components/Sparkle-latex-generator/Sparkle_Report.pdf`. We again set the performance measure to absolute quality.

`sparkle generate_report --performance-measure QUALITY_ABSOLUTE`

## [Coming soon] Run the portfolio selector (e.g. on the test set)

***This is not yet implemented for quality performance***

***This is not yet implemented for multi-file instances***

### Run on a single instance

Run the portfolio selector on a *single* testing instance; the result will be printed to the command line. We again set the performance measure to absolute quality.

`sparkle run_sparkle_portfolio_selector Examples/Resources/CCAG/Instances/CCAG2/Banking2.model Examples/Resources/CCAG/Instances/CCAG2/Banking2.constraints --performance-measure QUALITY_ABSOLUTE`

### Run on an instance set

Run the portfolio selector on a testing instance *set*. We again set the performance measure to absolute quality.

`sparkle run_sparkle_portfolio_selector Examples/Resources/CCAG/Instances/CCAG2/ --performance-measure QUALITY_ABSOLUTE`

## Generate a report including results on the test set

Wait for the portfolio selector to be done running on the testing instance set

`sparkle wait`

Generate an experimental report that includes the results on the test set, and as before the experimental procedure and performance information; this will be located at `Components/Sparkle-latex-generator/Sparkle_Report_For_Test.pdf`. We again set the performance measure to absolute quality.

`sparkle generate_report --performance-measure QUALITY_ABSOLUTE`

By default the `generate_report` command will create a report for the most recent instance set. To generate a report for an older instance set, the desired instance set can be specified with: `--test-case-directory Test_Cases/CCAG2/`

