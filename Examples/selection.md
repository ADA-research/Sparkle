## Algorithm Selection

Sparkle also offers various tools to apply algorithm selection, where we, given an objective, train another algorithm to determine which solver is best to use based on an instance. 

These steps can also be found as a Bash script in `Examples/selection.sh`

### Initialise the Sparkle platform

```bash
sparkle initialise
```

### Add instances
First, we add instance files (in this case in CNF format) to the platform by specifying the path.

```bash
sparkle add instances Examples/Resources/Instances/PTN/
```

### Add solvers

Now we add solvers to the platform as possible options for our selection. Each solver directory should contain the solver wrapper.

```bash
sparkle add solver Examples/Resources/Solvers/CSCCSat/
sparkle add solver Examples/Resources/Solvers/PbO-CCSAT-Generic/
sparkle add solver Examples/Resources/Solvers/MiniSAT/
```

### Add feature extractor
To run the selector, we need certain features to represent our instances. To that end, we add a feature extractor to the platform that creates vector representations of our instances.

```bash
sparkle add feature extractor Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle/
```

### Compute features
Now we can run our features with the following command:

```bash
sparkle compute features
```

### Run the solvers
Similarly, we can now also compute our objective values for our solvers, in this case PAR10 as specified in the settings file. We run the run solvers command with the `--performance-data`, so Sparkle will compute all empty values in the performance data frame.

```bash
sparkle run solvers --performance-data
```

### Construct a portfolio selector
To make sure feature computation and solver performance computation are done before constructing the portfolio use the `jobs` command

```bash
sparkle jobs
```

Now we can construct a portfolio selector, using the previously computed features and the objective value results of running the solvers. We can specify an objective to select on with the `--objective` flag, but if we do not, Sparkle will default to the first objective specified in the Settings file. The `--selector-timeout` argument determines for how many seconds we will train our selector for. We can set the flag `--solver-ablation` for actual marginal contribution computation later.

```bash
sparkle construct portfolio selector --selector-timeout 1000 --solver-ablation
sparkle jobs  # Wait for the constructor to complete its computations
```

### Generate a report

Generate an experimental report detailing the experimental procedure and performance information; this will be located at `Output/Selection/Sparkle_Report.pdf`

```bash
sparkle generate report
```

### Run the portfolio selector

#### Run on a single instance

Run the portfolio selector on a *single* testing instance; the result will be printed to the command line if you add `--run-on local` to the command.

```bash
sparkle run portfolio selector Examples/Resources/Instances/PTN2/plain7824.cnf --run-on local
```

### Run on an instance set

Run the portfolio selector on a testing instance *set*

```bash
sparkle run portfolio selector Examples/Resources/Instances/PTN2/
sparkle jobs  # Wait for the portfolio selector to be done running on the testing instance set
```

#### Generate a report including results on the test set

Generate an experimental report that includes the results on the test set, and as before the experimental procedure and performance information; this will be located at `Output/Selection/Sparkle_Report_For_Test.pdf`

```bash
sparkle generate report
```

By default the `generate_report` command will create a report for the most recent instance set. To generate a report for an older instance set, the desired instance set can be specified with: `--test-case-directory Test_Cases/PTN2/`

### Comparing against SATZilla 2024

If you wish to compare two feature extractors against one another, you need to remove the previous extractor from the platform (Or create a new platform from scratch) by running:

```bash
sparkle remove feature extractor SAT-features-competition2012_revised_without_SatELite_sparkle
```

Otherwise, Sparkle will interpret adding the other feature extractor as creating a combined feature vector per instance from all present extractors in Sparkle. Now we can add SATZilla 2024 from the Examples directory
Note that this feature extractor requires GCC (any version, tested with 13.2.0) to run.

```bash
sparkle add feature extractor Examples/Resources/Extractors/SAT-features-competition2024
```

We can also investigate a different data set, SAT Competition 2023 for which Sparkle has a subset.

```bash
sparkle remove instances PTN
sparkle add instances Examples/Resources/Instances/SATCOMP2023_SUB
```

We compute the features for the new extractor and new instances.

```bash
sparkle compute features
sparkle jobs  # Wait for it to complete before continuing
```

And run the solvers on the new data set.

```bash
sparkle run solvers --performance-data
sparkle jobs
```

Now we can train a selector based on these features.

```bash
sparkle construct portfolio selector --selector-timeout 1000
sparkle jobs  # Wait for the computation to be done
```

And generate the report. When running on the PTN/PTN2 data sets, you can compare the two to see the impact of different feature extractors.

```bash
sparkle generate report
```
