## Algorithm selection with multi-file instances

We can also run Sparkle on problems with instances that use multiple files. In this tutorial we will perform algorithm selection on instance sets with multiple files.

### Initialise the Sparkle platform

```bash
sparkle initialise
```

Afterwards, update the objective in the `Settings/sparkle_settings.ini` (See general section): Replace `PAR10` with `quality`.

### Add instances

Add instance files in a given directory, without running solvers or feature extractors yet. In addition to the instance files, the directory should contain a file `instances.csv` where each line contains a space separated list of files that together form an instance.

```bash
sparkle add_instances Examples/Resources/CCAG/Instances/CCAG/
```

### Add solvers

Add solvers (here for the constrained covering array generation (CCAG) problem) with a wrapper containing the executable name of the solver and a string of command line parameters, without running the solvers yet

Each solver directory should contain the solver executable and a wrapper

```bash
sparkle add_solver Examples/Resources/CCAG/Solvers/TCA/
sparkle add_solver Examples/Resources/CCAG/Solvers/FastCA/
```

### Add feature extractor

Similarly, add a feature extractor, without immediately running it on the instances

```bash
sparkle add_feature_extractor Examples/Resources/CCAG/Extractors/CCAG-features_sparkle/
```

### Compute features

Compute features for all the instances

```bash
sparkle compute_features
```

### Run the solvers
Run the solvers on all instances. For the CCAG (Constrained Covering Array Generation) problem we measure the quality by setting the objective in `Settings/sparkle_settings.ini` to quality. Note that you need to set this right after initialising the platform, see the instructions at the top.

```bash
sparkle run_solvers --performance-data
```

### Construct a portfolio selector

Make sure feature computation and solver performance computation are done before constructing the portfolio.

```bash
sparkle jobs
```

Construct a portfolio selector, using the previously computed features and the results of running the solvers. We again set the objective measure to quality.

```bash
sparkle construct_portfolio_selector
```

### Running the selector

#### Run on a single instance

Run the portfolio selector on a *single* testing instance; the result will be printed to the command line if you add `--run-on local` to the command. We again set the objective to quality. Note: Currently only works for added instances.

```bash
sparkle run_portfolio_selector --selection-scenario Output/Selection/MultiClassClassifier_RandomForestClassifier/FastCA_TCA/ --instance Examples/Resources/CCAG/Instances/CCAG/Banking1 --run-on local
```

#### Run on an instance set

Run the portfolio selector on a testing instance *set*. We again set the objective to quality. Note: Currently only works for added instances.

```bash
sparkle run_portfolio_selector --selection-scenario Output/Selection/MultiClassClassifier_RandomForestClassifier/FastCA_TCA/scenario.txt --instance Examples/Resources/CCAG/Instances/CCAG/
```

#### Generate a report

Wait for the portfolio selector to be done running on the testing instance set

```bash
sparkle jobs
```

And run the generate report command

```bash
sparkle generate report
```
