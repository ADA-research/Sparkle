#!/bin/bash

# Navigate to the Sparkle directory

# Initialise a new Sparkle platform
Commands/initialise.py

# Add instances from a given directory, without running solvers or feature extractors yet
# (TODO: Check if this must be done before add_solver or if they can be in either order)
Commands/add_instances.py -run-solver-later -run-extractor-later Examples/Resources/Instances/PTN/

# Add a feature extractor, but do not run it yet
Commands/add_feature_extractor.py -run-extractor-later Examples/Resources/Extractors/SAT-features-competition2012_revised_without_SatELite_sparkle/

# Run the feature extractor on instances for which no features have been computed yet
Commands/compute_features.py

