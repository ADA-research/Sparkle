#!/usr/bin/env bash
# Auto-Generated .sh files from the original .md by Sparkle 0.9.2

## Configuring Random Forest on Iris

# We can also use Sparkle for Machine Learning approaches, such as Random Forest for the Iris data set. Note that in this case, the entire data set is considered as being one instance.

### Initialise the Sparkle platform

sparkle initialise

### Add instances

sparkle add_instances Examples/Resources/Instances/Iris

### Add solver

sparkle add_solver Examples/Resources/Solvers/RandomForest

### Configure the solver on the data set

sparkle configure_solver --solver RandomForest --instance-set-train Iris --objectives accuracy:max

### Generate a report

# Wait for configuration to be completed

sparkle jobs

# Generate a report detailing the results on the training (and optionally testing) set.

sparkle generate_report
