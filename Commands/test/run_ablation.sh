#!/bin/bash

# Execute this script from the Sparkle directory

#SBATCH --job-name=test/configure_solver.sh
#SBATCH --output=TMP/configure_solver.sh.txt
#SBATCH --error=TMP/configure_solver.sh.err
#SBATCH --partition=graceADA
#SBATCH --mem-per-cpu=3gb
#SBATCH --exclude=
#SBATCH --ntasks=1
#SBATCH --nodes=1

# Activate environment
source activate sparkle_test &> /dev/null

# Prerequisites
# - Initialise.py
# - Added instances
# - Added solver
# - Configuration run

# Prepare for test
instances_path="Examples/Resources/Instances/PTN/"
solver_path="Examples/Resources/Solvers/PbO-CCSAT-Generic/"

# Run ablation
output=$(Commands/run_ablation.py --solver $solver_path --instance-set-train $instances_path | tail -1)

if [[ $output =~ [0-9] ]];
then
	echo "[success] run_ablation test succeeded"
else              
	echo "[failure] run_ablation test failed with output:"
	echo $output
fi

