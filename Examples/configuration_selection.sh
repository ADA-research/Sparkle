#!/usr/bin/env bash
# Auto-Generated .sh files from the original .md by Sparkle 0.9.5

## Algorithm Runtime Configuration and Selection

# In this example, we will use Automated Algorithm Configuration to create multiple configurations for a Solver, and afterwards treat the configurations as a portfolio to perform selection on.

# These steps can also be found as a Bash script in `Examples/configuration_selection.sh`

### Initialise the Sparkle platform

sparkle initialise

### Add instances

# Add train instances (in this case in CNF format) in a given directory

sparkle add_instances Examples/Resources/Instances/PTN/

### Add a configurable solver

# Add a configurable solver (here for SAT solving) with a wrapper containing the executable name of the solver and a string of command line parameters, without running the solver yet

# The solver directory should contain the solver executable, the `sparkle_solver_wrapper` wrapper, and a `.pcs` file describing the configurable parameters. In this example, we are running a SAT solver, and we can add the argument for a solution verifier to check each solution presented by the solver, and update its status acccordingly.

sparkle add_solver Examples/Resources/Solvers/PbO-CCSAT-Generic/ --solution-verifier SATVerifier

# If needed solvers can also include additional files or scripts in their directory, but keeping additional files to a minimum speeds up copying.

### Configure the solver

# To perform configuration on the solver to obtain a target configuration we run it on the training set `PTN`:

sparkle configure_solver --solver Solvers/PbO-CCSAT-Generic/ --instance-set-train Instances/PTN/

# This step should take about ~10 minutes, although it is of course very cluster / slurm settings dependant. If you are using the default settings, this will use SMAC2 as configurator. If you wish to run with a different configurator, we also supply default settings for the other configurators for this scenario. You can simply change the configurator name in `sparkle_settings.ini` under the `general` section.

# We have to wait for the algorithm configuration to be completed, to get live updates on your terminal we can simply run:

sparkle jobs

### Feature extractor
# To run the selector, we need certain features to represent our instances. To that end, we add a feature extractor to the platform that creates vector representations of our instances.

sparkle add feature extractor Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite/

#### Compute features
# Now we can run our features with the following command:

sparkle compute features

# To make sure feature computation is done before constructing the portfolio use the `jobs` command

sparkle jobs

### Construct the Selector

# Now we can construct a portfolio selector, using the previously computed features and the objective value results of running the solvers. We can specify an objective to select on with the `--objective` flag, but if we do not, Sparkle will default to the first objective specified in the Settings file. We can set the flag `--solver-ablation` for actual marginal contribution computation later. We set the flag `--all-configurations` to use each found configuration for the portfolio. We could also choose to only use the `--default-configuration` or `--best-configuration` instead, which will reduce the reperesentation of our solver in the portfolio to one, in which case we should make sure to add other solvers instead. As we added two instance sets two Sparkle, we specify on which set the selector must be trained.

sparkle construct portfolio selector --instance-set-train PTN --all-configurations --solver-ablation
sparkle jobs  # Wait for the constructor to complete its computations

### Generate a report

# Generate an experimental report detailing the experimental procedure and performance information; this will be located at `Output/Analysis/`

sparkle generate report

### Run the portfolio selector

#### Run on a single instance

# Run the portfolio selector on a *single* testing instance; the result will be printed to the command line if you add `--run-on local` to the command.

sparkle run portfolio selector --selection-scenario Output/Selection/MultiClassClassifier_RandomForestClassifier/PbO-CCSAT-G
eneric/ --instance Examples/Resources/Instances/PTN2/plain7824.cnf --run-on local

### Run on an instance set

# Run the portfolio selector on a testing instance *set*

 sparkle run portfolio selector --selection-scenario Output/Selection/MultiClassClassifier_RandomForestClassifier/PbO-CCSAT-G
eneric/ --instance-set Examples/Resources/Instances/PTN2/
sparkle jobs  # Wait for the portfolio selector to be done running on the testing instance set

#### Generate a report including results on the test set

# Generate an experimental report that includes the results on the test set, and as before the experimental procedure and performance information; this will be located at `Output/Analysis/report.pdf`

sparkle generate report
