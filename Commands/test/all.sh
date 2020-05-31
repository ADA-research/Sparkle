#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/all.sh
#SBATCH --output=TMP/all.sh.txt
#SBATCH --error=TMP/all.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Activate environment
source activate sparkle_test &> /dev/null

# Test add feature extractor
Commands/test/add_feature_extractor.sh

# Test add instances
Commands/test/add_instances.sh

# Test add solver
Commands/test/add_solver.sh

