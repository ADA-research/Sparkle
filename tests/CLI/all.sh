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
tests/CLI/about.sh

# Test system status
tests/CLI/system_status.sh

# Test initialise
tests/CLI/initialise.sh

# Test add feature extractor
tests/CLI/add_feature_extractor.sh

# Test add instances
tests/CLI/add_instances.sh

# Test add solver
tests/CLI/add_solver.sh

# Test save snapshot
tests/CLI/save_snapshot.sh

# Test load snapshot
tests/CLI/load_snapshot.sh

# Test remove feature extractor
tests/CLI/remove_feature_extractor.sh

# Test remove instances
tests/CLI/remove_instances.sh

# Test remove solver
tests/CLI/remove_solver.sh

# Test run solvers
tests/CLI/run_solvers.sh

# Test cleanup temporary files
tests/CLI/cleanup_temporary_files.sh

# Test compute features
tests/CLI/compute_features.sh

# Test compute marginal contribution
tests/CLI/compute_marginal_contribution.sh

# Test configure solver
tests/CLI/configure_solver.sh

# Test configure solver with validate option
tests/CLI/configure_solver_validate.sh

# Test construct sparkle portfolio selector
tests/CLI/construct_portfolio_selector.sh

# Test run sparkle portfolio selector
tests/CLI/run_portfolio_selector.sh

# Test validate configured vs default
tests/CLI/validate_configured_vs_default.sh

# Test ablation run configured vs default
tests/CLI/run_ablation.sh

# Test run configured solver
tests/CLI/run_configured_solver.sh

# Test run parallel portfolio
tests/CLI/run_parallel_portfolio.sh

# Test generate report (selection)
tests/CLI/generate_report__for_selection.sh

# Test generate report for configuration
tests/CLI/generate_report_for_configuration.sh

# Test generate report for parallel portfolio
tests/CLI/generate_report_parallel_portfolio.sh
