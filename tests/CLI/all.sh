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

# Test configure solver
tests/CLI/configure_solver.sh

# Test configure solver with validate option
tests/CLI/configure_solver_validate.sh

# Test construct sparkle portfolio selector
tests/CLI/construct_portfolio_selector.sh

# Test run sparkle portfolio selector
tests/CLI/run_portfolio_selector.sh

# Test ablation run configured vs default
tests/CLI/run_ablation.sh

# Test run configured solver
tests/CLI/run_configured_solver.sh

# Test run parallel portfolio
tests/CLI/run_parallel_portfolio.sh

# Test generate report (selection)
tests/CLI/generate_report_for_selection.sh

# Test generate report for configuration
tests/CLI/generate_report_for_configuration.sh

# Test generate report for parallel portfolio
tests/CLI/generate_report_parallel_portfolio.sh
