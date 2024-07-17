#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/all.sh
#SBATCH --output=Tmp/all.sh.txt
#SBATCH --error=Tmp/all.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Test about
CLI/test/about.sh

# Test system status
CLI/test/system_status.sh

# Test run status
CLI/test/run_status.sh

# Test initialise
CLI/test/initialise.sh

# Test add feature extractor
CLI/test/add_feature_extractor.sh

# Test add instances
CLI/test/add_instances.sh

# Test add solver
CLI/test/add_solver.sh
# Test save snapshot
CLI/test/save_snapshot.sh

# Test load snapshot
CLI/test/load_snapshot.sh

# Test remove feature extractor
CLI/test/remove_feature_extractor.sh

# Test remove instances
CLI/test/remove_instances.sh

# Test remove solver
CLI/test/remove_solver.sh

# Test run solvers
CLI/test/run_solvers.sh

# Test cleanup temporary files
CLI/test/cleanup_temporary_files.sh

# Test compute features
CLI/test/compute_features.sh

# Test compute marginal contribution
CLI/test/compute_marginal_contribution.sh

# Test configure solver
CLI/test/configure_solver.sh

# Test configure solver with validate option
CLI/test/configure_solver_validate.sh

# Test construct sparkle portfolio selector
CLI/test/construct_sparkle_portfolio_selector.sh

# Test run sparkle portfolio selector
CLI/test/run_sparkle_portfolio_selector.sh

# Test validate configured vs default
CLI/test/validate_configured_vs_default.sh

# Test ablation run configured vs default
CLI/test/run_ablation.sh

# Test run configured solver
CLI/test/run_configured_solver.sh

# Test run parallel portfolio
CLI/test/run_parallel_portfolio.sh

# Test generate report (selection)
CLI/test/generate_report_selection.sh

# Test generate report (selection) for test set
CLI/test/generate_report_for_test.sh

# Test generate report for configuration
CLI/test/generate_report_for_configuration.sh

# Test generate report for parallel portfolio
CLI/test/generate_report_parallel_portfolio.sh
