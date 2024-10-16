#!/usr/bin/env bash
# Auto-Generated .sh files from the original .md by Sparkle 0.8.4

## Algorithm Quality Configuration
# We can configure an algorithm too based on some quality objective, that can be defined by the user. See the {ref}`SparkleObjective <sparkle-objective>` page for all options regarding objective defintions.
# These steps can also be found as a Bash script in `Examples/configuration_qualty.sh`

### Initialise the Sparkle platform

sparkle initialise

### Add instances

# Now we add train, and optionally test, instances for configuring our algorithm (in this case for the VRP). The instance sets are placed in a given directory.

sparkle add_instances Examples/Resources/CVRP/Instances/X-1-10/
sparkle add_instances Examples/Resources/CVRP/Instances/X-11-20/

### Add a configurable solver

# Add a configurable solver (In this tutorial its an algorithm for vehicle routing) with a wrapper containing the executable name of the solver and a string of command line parameters.

# The solver directory should contain the `sparkle_solver_wrapper.py` wrapper, and a `.pcs` file describing the configurable parameters.

sparkle add_solver Examples/Resources/CVRP/Solvers/VRP_SISRs/

# In this case the source directory also contains an executable, as the algorithm has been compiled from another programming language (`C++`). If needed solvers can also include additional files or scripts in their directory, but keeping additional files to a minimum speeds up copying.

### Configure the solver

# Perform configuration on the solver to obtain a target configuration. For the VRP we measure the absolute quality performance by setting the `--objectives` option, to avoid needing this for every command it can also be set in `Settings/sparkle_settings.ini`.

sparkle configure_solver --solver Solvers/VRP_SISRs/ --instance-set-train Instances/X-1-10/ --objectives quality

### Validate the configuration

# To make sure configuration is completed before running validation you can use the `sparkle wait` command

sparkle wait

# Validate the performance of the best found parameter configuration. The test set is optional. We again set the performance measure to absolute quality.

sparkle validate_configured_vs_default --solver Solvers/VRP_SISRs/ --instance-set-train Instances/X-1-10/ --instance-set-test Instances/X-11-20/ --objective quality

### Generate a report

# Wait for validation to be completed

sparkle wait

# Generate a report detailing the results on the training (and optionally testing) set. This includes the experimental procedure and performance information; this will be located in a `Configuration_Reports/` subdirectory for the solver, training set, and optionally test set like `VRP_SISRs_X-1-10_X-11-20/Sparkle-latex-generator-for-configuration/`. We again set the performance measure to absolute quality.

sparkle generate_report --objective quality

# By default the `generate_report` command will create a report for the most recent solver and instance set(s). To generate a report for older solver-instance set combinations, the desired solver can be specified with `--solver Solvers/VRP_SISRs/`, the training instance set with `--instance-set-train Instances/X-1-10/`, and the testing instance set with `--instance-set-test Instances/X-11-20/`.

