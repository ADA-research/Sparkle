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

# Test run parallel portfolio
tests/CLI/run_parallel_portfolio.sh

# Test generate report (selection)
tests/CLI/generate_report_for_selection.sh

# Test generate report for parallel portfolio
tests/CLI/generate_report_parallel_portfolio.sh
