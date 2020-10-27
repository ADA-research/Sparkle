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

# Test about
Commands/test/about.sh

# Test system status
Commands/test/system_status.sh

# Test run status
Commands/test/run_status.sh

# Test initialise
Commands/test/initialise.sh

# Test add feature extractor
Commands/test/add_feature_extractor.sh

# Test add instances
Commands/test/add_instances.sh

# Test add solver
Commands/test/add_solver.sh

# Test cleanup current sparkle platform
Commands/test/cleanup_current_sparkle_platform.sh

# Test cleanup temporary files
Commands/test/cleanup_temporary_files.sh

# Test compute features
Commands/test/compute_features.sh

# Test compute features parallel
Commands/test/compute_features_parallel.sh

# Test compute marginal contribution
Commands/test/compute_marginal_contribution.sh

# Test configure solver
Commands/test/configure_solver.sh

# Test construct sparkle portfolio selector
Commands/test/construct_sparkle_portfolio_selector.sh

# Test generate report
Commands/test/generate_report.sh

# Test save record
Commands/test/save_record.sh

# Test load record
Commands/test/load_record.sh

# Test remove record
Commands/test/remove_record.sh

# Test remove feature extractor
Commands/test/remove_feature_extractor.sh

# Test remove instances
Commands/test/remove_instances.sh

# Test remove solver
Commands/test/remove_solver.sh

# Test validate configured vs default
Commands/test/validate_configured_vs_default.sh

